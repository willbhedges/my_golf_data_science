"""zero_tap_bench: score any method's per-course output (zero_tap_result/1) against the benchmark's OSM truth.

  python course_data/zero_tap/bench.py score RESULTS [RESULTS ...] [--split dev|test|all] [--json out.json]
        RESULTS: a directory of <slug>.json files, or a .jsonl file (one zero_tap_result/1 per line). The method and
        tier come from the records.
  python course_data/zero_tap/bench.py scoreboard        every results/<method>/<tier>/ -> scoreboard.json + SCOREBOARD.md
  python course_data/zero_tap/bench.py inputs <slug> --tier osm_card     what a method may see (debug print)

Contract, metrics and rules: BENCH.md. Library use (a method's runner):
  import bench as B
  for row in B.courses("dev"):                       # never tune on "test"
      x = B.inputs(row, "osm_card")                  # fc (holes hidden), course, card, segment, pads, scene
      ...  -> B.write_result(dict(schema="zero_tap_result/1", ...), out_dir)
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import truth as TR  # noqa: E402

MANIFEST = os.path.join(HERE, "benchmark.json")
RESULTS = os.path.join(HERE, "results")
TIERS = ("osm_card", "unmapped_card", "nocard", "unmapped_nocard")
TIER_DOC = {"osm_card": "OSM greens / tees (holes hidden) + scorecard",
            "unmapped_card": "no OSM golf features (imagery / lidar / scene only) + scorecard",
            "nocard": "OSM greens / tees (holes hidden), no scorecard",
            "unmapped_nocard": "no OSM golf features, no scorecard"}
GREEN_EDGE_TOL = 12.0      # yds from the true green's edge (centroid - equal-area radius)
GREEN_END_TOL = 20.0       # ... or from the true hole line's end
TEE_START_TOL = 35.0       # yds from the true line's start
TEE_LINE_TOL = 30.0        # ... or from the first 60 % of the true line extended 90 yds back (back tees)
FAIL_ORDER = ("no_result", "count", "pairing", "missed_tee", "nine_swap", "start_hole", "order", "par")


# ----------------------------------------------------------------------------- data access
def _rd(p):
    if not p:
        return None
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    if not os.path.exists(p):
        return None
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as fh:
        return json.load(fh)


def manifest():
    return json.load(open(MANIFEST))


def courses(split=None, tier=None):
    """Benchmark rows (benchmark.json) of a split ('dev' / 'test' / None = both) whose inputs exist for `tier`."""
    rows = [r for r in manifest()["courses"] if r["in_bench"] and (split in (None, "all") or r["split"] == split)]
    if tier and tier.startswith("unmapped"):
        rows = [r for r in rows if r["files"].get("segment") or r["files"].get("scene")]
    return rows


def truth(slug):
    return _rd(os.path.join(HERE, "truth", slug + ".json"))


def card_for(row):
    """The card a card tier gets: the web card when its hole count fits the course, else one derived from the OSM
    truth (pars where tagged + hole-line lengths as tee set 'osm'). -> (card scorecard/1, 'web:<src>' | 'osm-derived')."""
    if row.get("card") and row["card"].get("fits"):
        sc = _rd(row["files"]["card"])
        ch = sc.get("chosen")
        c = next((c for c in sc["cards"] if c["source"] == ch), sc["cards"][0])
        return c["card"], "web:" + c["source"]
    t = truth(row["slug"])
    hs = sorted(t["holes"], key=lambda h: h["ref"])
    if t["kind"] not in (9, 18):
        hs = hs[:18] if t["kind"] == 36 else hs
    pars = [h["par"] for h in hs]
    yards = [int(round(h["length_yd"])) for h in hs]
    return dict(schema="scorecard/1", par=pars if all(pars) else None,
                tee_sets={"osm": dict(yards=yards, par=pars if all(pars) else None)}, derived="osm"), "osm-derived"


def inputs(row, tier):
    """What a method may see on `tier`: fc (OSM golf file with golf=hole / pin dropped and refs hidden; on the
    unmapped tiers every golf=* feature dropped), course (resolve output: name, boundary, bbox), card (card tiers),
    segment (NAIP model fc), pads (lidar tee pads), scene (perception course_scene/1), card_kind."""
    fc = _rd(row["files"]["osm"])
    fc = TR.strip_golf(fc) if tier.startswith("unmapped") else TR.hide(fc)
    card, kind = card_for(row) if tier.endswith("_card") else (None, "none")
    return dict(slug=row["slug"], fc=fc, course=_rd(row["files"]["course"]) or {}, card=card, card_kind=kind,
                segment=_rd(row["files"].get("segment")), pads=_rd(row["files"].get("pads")),
                scene=_rd(row["files"].get("scene")) if tier.startswith("unmapped") else None, kind=row["kind"])


def write_result(res, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(os.path.join(out_dir, res["slug"] + ".json"), "w"), separators=(",", ":"))


def load_results(path):
    out = []
    if os.path.isdir(path):
        for f in sorted(os.listdir(path)):
            if f.endswith(".json"):
                out.append(json.load(open(os.path.join(path, f))))
    else:
        for line in open(path):
            if line.strip():
                out.append(json.loads(line))
    return out


# ----------------------------------------------------------------------------- matching
def _first_ext(line, frac=0.6, back=90.0):
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(line[:-1], line[1:])]
    L = sum(seg) * frac
    pts, acc = [line[0]], 0.0
    for (a, b), s in zip(zip(line[:-1], line[1:]), seg):
        if acc + s >= L:
            f = (L - acc) / max(s, 1e-9)
            pts.append((a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])))
            break
        pts.append(b)
        acc += s
    ux, uy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    n = math.hypot(ux, uy) or 1.0
    return [(pts[0][0] - back * ux / n, pts[0][1] - back * uy / n)] + pts


class Matcher:
    def __init__(self, t):
        hs = t["holes"]
        lon0 = sum(h["green_ll"][0] for h in hs) / len(hs)
        lat0 = sum(h["green_ll"][1] for h in hs) / len(hs)
        self.pj = TR.Proj(lon0, lat0)
        self.holes = []
        for h in hs:
            line = [self.pj.fwd(*q) for q in h["line"]]
            self.holes.append(dict(ref=h["ref"], par=h["par"], g=self.pj.fwd(*h["green_ll"]), r=h["green_r_yd"],
                                   end=line[-1], start=line[0], ext=_first_ext(line)))

    def green_ok(self, j, p):
        h = self.holes[j]
        if h["r"] is not None and math.hypot(p[0] - h["g"][0], p[1] - h["g"][1]) - h["r"] <= GREEN_EDGE_TOL:
            return True
        return math.hypot(p[0] - h["end"][0], p[1] - h["end"][1]) <= GREEN_END_TOL

    def tee_ok(self, j, pts):
        h = self.holes[j]
        return any(math.hypot(p[0] - h["start"][0], p[1] - h["start"][1]) <= TEE_START_TOL or
                   TR.seg_dist(p, h["ext"]) <= TEE_LINE_TOL for p in pts)

    def match(self, ph):
        """-> (true hole index or None, failure kind or None) for one predicted hole."""
        g = ph.get("green_ll")
        tees = [x for x in [ph.get("tee_ll")] + list(ph.get("tee_boxes_ll") or []) if x]
        if not g:
            return None, "pairing"
        gp = self.pj.fwd(*g[:2])
        tp = [self.pj.fwd(*x[:2]) for x in tees]
        gj = [j for j in range(len(self.holes)) if self.green_ok(j, gp)]
        if not gj:
            return None, "pairing"
        ok = [j for j in gj if tp and self.tee_ok(j, tp)]
        if ok:
            num = ph.get("number")
            ok.sort(key=lambda j: (self.holes[j]["ref"] != num, j))
            return ok[0], None
        if tp and any(self.tee_ok(j, tp) for j in range(len(self.holes)) if j not in gj):
            return None, "pairing"
        return None, "missed_tee"


def _explain(pairs, N):
    """pairs [(number, true ref)] of formed holes -> best explanation of the numbering: identity / nine_swap /
    start_hole / order, and the holes it leaves wrong."""
    def fits(f):
        return sum(1 for n, r in pairs if f(n) == r)
    cands = [("identity", lambda n: n)]
    if N == 18:
        cands.append(("nine_swap", lambda n: (n + 8) % 18 + 1))
    if N in (9, 18, 27, 36):
        for k in range(1, N):
            cands.append(("start_hole", lambda n, k=k: (n - 1 + k) % N + 1))
        for k in range(N):
            cands.append(("order", lambda n, k=k: (k - n) % N + 1))       # reversed loop
    best = max(cands, key=lambda c: (fits(c[1]), c[0] == "identity"))
    return best[0]


def score_course(res, t):
    """One course: per hole outcomes + course-level verdict."""
    N = t["n_holes"]
    if res is None or res.get("error") or not res.get("holes"):
        return dict(slug=t["slug"], N=N, kind=t["kind"], n_pred=0, formed=0, number=0, par_ok=0, par_n=0,
                    course_ok=False, holes_ok=False, certain=bool(res and res.get("certain")),
                    confidence=float((res or {}).get("confidence") or 0.0), primary="no_result",
                    fails=dict(missing=N), hole_conf=[], hole_correct=[])
    M = Matcher(t)
    used = set()
    fails = Counter()
    formed = []                                   # (pred hole, true index)
    for ph in res["holes"]:
        j, why = M.match(ph)
        if j is not None and j in used:
            j, why = None, "pairing"              # the same true hole twice
        if j is None:
            fails[why] += 1
        else:
            used.add(j)
            formed.append((ph, j))
    nums = [(int(ph.get("number") or 0), M.holes[j]["ref"]) for ph, j in formed]
    num_ok = [n == r for n, r in nums]
    expl = _explain(nums, N) if t["kind"] in (9, 18) else "identity"
    wrong_num = sum(1 for x in num_ok if not x)
    if wrong_num:
        fails["order" if expl == "identity" else expl] += wrong_num
    par_n = par_ok = 0
    for ph, j in formed:
        tp = M.holes[j]["par"]
        if tp:
            par_n += 1
            if ph.get("par") is not None and int(ph["par"]) == tp:
                par_ok += 1
            else:
                fails["par"] += 1
    missing = N - len(used)
    if missing > 0:
        fails["missing"] += missing
    holes_ok = len(res["holes"]) == N and sum(num_ok) == N
    course_ok = holes_ok and par_ok == par_n
    if course_ok:
        primary = None
    elif len(res["holes"]) != N:
        primary = "count"
    else:
        primary = next((k for k in FAIL_ORDER if fails.get(k)), "order")
    hc, hcor = [], []
    pos = {id(ph): j for ph, j in formed}
    for ph in res["holes"]:
        j = pos.get(id(ph))
        hcor.append(int(j is not None and M.holes[j]["ref"] == int(ph.get("number") or 0)))
        hc.append(ph.get("confidence"))
    return dict(slug=t["slug"], N=N, kind=t["kind"], n_pred=len(res["holes"]), formed=len(used), number=sum(num_ok),
                par_ok=par_ok, par_n=par_n, holes_ok=holes_ok, course_ok=course_ok, certain=bool(res.get("certain")),
                confidence=float(res.get("confidence") or 0.0), primary=primary, explanation=expl,
                fails=dict(fails), hole_conf=hc, hole_correct=hcor)


# ----------------------------------------------------------------------------- aggregation
def curve(rows, points=(0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0)):
    """Coverage vs precision when every course with confidence >= c is marked certain (c swept)."""
    rs = sorted(rows, key=lambda r: -r["confidence"])
    n = len(rs)
    out, best = [], {0.99: 0.0, 0.95: 0.0, 0.9: 0.0}
    ok = 0
    for i, r in enumerate(rs, 1):
        ok += r["course_ok"]
        prec = ok / i
        if i < n and rs[i]["confidence"] == r["confidence"]:
            continue                                         # ties: only whole thresholds
        for p in best:
            if prec >= p:
                best[p] = max(best[p], i / n)
    for c in points:
        k = max(1, int(round(c * n)))
        sub = rs[:k]
        out.append(dict(coverage=round(k / n, 3), precision=round(sum(r["course_ok"] for r in sub) / k, 3),
                        min_conf=round(sub[-1]["confidence"], 4)))
    return out, {f"coverage_at_p{int(p * 100)}": round(v, 3) for p, v in best.items()}


def aggregate(rows):
    n = len(rows)
    if not n:
        return dict(n=0)
    holes = sum(r["N"] for r in rows)
    cert = [r for r in rows if r["certain"]]
    cur, best = curve(rows)
    prim = Counter(r["primary"] for r in rows if r["primary"])
    hf = Counter()
    for r in rows:
        hf.update(r["fails"])
    hc = [(c, k) for r in rows for c, k in zip(r["hole_conf"], r["hole_correct"]) if c is not None]
    ece = None
    if hc:
        bins = defaultdict(list)
        for c, k in hc:
            bins[min(int(float(c) * 10), 9)].append((float(c), k))
        ece = round(sum(abs(sum(c for c, _ in b) / len(b) - sum(k for _, k in b) / len(b)) * len(b)
                        for b in bins.values()) / len(hc), 3)
    return dict(
        n=n, holes=holes,
        hole_number_acc=round(sum(r["number"] for r in rows) / holes, 3),
        formed_acc=round(sum(r["formed"] for r in rows) / holes, 3),
        par_acc=round(sum(r["par_ok"] for r in rows) / max(sum(r["par_n"] for r in rows), 1), 3),
        courses_holes_right=round(sum(r["holes_ok"] for r in rows) / n, 3),
        courses_fully_right=round(sum(r["course_ok"] for r in rows) / n, 3),
        certain_n=len(cert), zero_tap_coverage=round(len(cert) / n, 3),
        zero_tap_precision=round(sum(r["course_ok"] for r in cert) / len(cert), 3) if cert else None,
        curve=cur, **best, hole_ece=ece,
        course_failures=dict(prim.most_common()), hole_failures=dict(hf.most_common()),
        no_result=sum(1 for r in rows if r["primary"] == "no_result"))


def score(results, split="all", method=None, tier=None):
    """results: [zero_tap_result/1] of ONE method x tier -> {split: aggregate, by kind, by card kind, rows}."""
    by_slug = {r["slug"]: r for r in results}
    method = method or next((r.get("method") for r in results), "?")
    tier = tier or next((r.get("tier") for r in results), "?")
    rows = []
    for c in courses(None if split == "all" else split, tier):
        t = truth(c["slug"])
        r = score_course(by_slug.get(c["slug"]), t)
        r.update(split=c["split"], state=c["state"], region=c["region"],
                 card_kind=(by_slug.get(c["slug"]) or {}).get("card_kind"))
        rows.append(r)
    out = dict(method=method, tier=tier, version=next((r.get("version") for r in results if r.get("version")), None))
    for sp in ("dev", "test"):
        rs = [r for r in rows if r["split"] == sp]
        if rs:
            out[sp] = aggregate(rs)
            out[sp]["by_kind"] = {str(k): aggregate([r for r in rs if r["kind"] == k])
                                  for k in sorted({r["kind"] for r in rs})}
            for k in out[sp]["by_kind"].values():
                k.pop("curve", None)
    out["rows"] = [{k: v for k, v in r.items() if k not in ("hole_conf", "hole_correct")} for r in rows]
    return out


# ----------------------------------------------------------------------------- scoreboard
def _pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def md(board):
    L = ["# Zero-tap benchmark scoreboard", "",
         f"Benchmark: {board['bench']['courses']} courses ({board['bench']['by_split']}), built {board['bench']['built']}. "
         "Contract and rules: [BENCH.md](BENCH.md). Test = held-out states: report, never tune.", ""]
    for sp in ("test", "dev"):
        L += [f"## {sp}", "",
              "| method | tier | courses | hole number | formed | par | fully right | certain: coverage | certain: precision "
              "| cov @ P>=99% | cov @ P>=95% | top course failures |", "|" + "---|" * 12]
        for e in board["entries"]:
            a = e.get(sp)
            if not a or not a.get("n"):
                continue
            tf = ", ".join(f"{k} {v}" for k, v in list(a["course_failures"].items())[:4])
            L.append(f"| {e['method']} | {e['tier']} | {a['n']} | {_pct(a['hole_number_acc'])} | {_pct(a['formed_acc'])} | "
                     f"{_pct(a['par_acc'])} | {_pct(a['courses_fully_right'])} | {_pct(a['zero_tap_coverage'])} "
                     f"({a['certain_n']}) | {_pct(a['zero_tap_precision'])} | {_pct(a['coverage_at_p99'])} | "
                     f"{_pct(a['coverage_at_p95'])} | {tf} |")
        L.append("")
    L += ["## Coverage vs precision (test)", "", "Courses sorted by the method's course confidence; precision of the "
          "top-k (fully right incl. par).", ""]
    for e in board["entries"]:
        a = e.get("test")
        if a and a.get("curve"):
            L.append(f"- **{e['method']} / {e['tier']}**: " + "; ".join(
                f"cov {_pct(c['coverage'])} -> {_pct(c['precision'])}" for c in a["curve"]))
    L += ["", "## Hole failure types (test, holes)", "",
          "| method | tier | " + " | ".join(("pairing", "missed_tee", "nine_swap", "start_hole", "order", "par", "missing")) + " |",
          "|" + "---|" * 9]
    for e in board["entries"]:
        a = e.get("test")
        if a and a.get("n"):
            hf = a["hole_failures"]
            L.append(f"| {e['method']} | {e['tier']} | " + " | ".join(str(hf.get(k, 0)) for k in (
                "pairing", "missed_tee", "nine_swap", "start_hole", "order", "par", "missing")) + " |")
    L += ["", "## By facility size (test: hole number / fully right)", ""]
    for e in board["entries"]:
        a = e.get("test")
        if a and a.get("by_kind"):
            L.append(f"- {e['method']} / {e['tier']}: " + "; ".join(
                f"{k}-hole n={v['n']} {_pct(v['hole_number_acc'])} / {_pct(v['courses_fully_right'])}"
                for k, v in a["by_kind"].items()))
    return "\n".join(L) + "\n"


def scoreboard(results_root=RESULTS):
    m = manifest()
    entries = []
    for meth in sorted(os.listdir(results_root)) if os.path.isdir(results_root) else []:
        for tier in sorted(os.listdir(os.path.join(results_root, meth))):
            d = os.path.join(results_root, meth, tier)
            if not os.path.isdir(d):
                continue
            res = load_results(d)
            if not res:
                continue
            e = score(res, "all", meth, tier)
            os.makedirs(os.path.join(HERE, "scores"), exist_ok=True)
            json.dump(e, open(os.path.join(HERE, "scores", f"{meth}__{tier}.json"), "w"), indent=1)
            e.pop("rows")
            entries.append(e)
    order = {t: i for i, t in enumerate(TIERS)}
    entries.sort(key=lambda e: (order.get(e["tier"], 9), e["method"]))
    board = dict(schema="zero_tap_scoreboard/1", bench=dict(courses=m["summary"]["courses"], by_split=m["summary"]["by_split"],
                                                            built=m["built_utc"]), entries=entries)
    json.dump(board, open(os.path.join(HERE, "scoreboard.json"), "w"), indent=1)
    open(os.path.join(HERE, "SCOREBOARD.md"), "w").write(md(board))
    print(md(board))
    return board


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["score", "scoreboard", "inputs"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--split", default="all")
    ap.add_argument("--tier", default="osm_card")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.cmd == "scoreboard":
        scoreboard()
    elif a.cmd == "inputs":
        row = next(r for r in manifest()["courses"] if r["slug"] == a.args[0])
        x = inputs(row, a.tier)
        print({k: (len(v["features"]) if isinstance(v, dict) and "features" in v else
                   (type(v).__name__ if v is not None else None)) for k, v in x.items()}, x["card_kind"])
    else:
        res = [r for p in a.args for r in load_results(p)]
        out = score(res, a.split)
        if a.json:
            json.dump(out, open(a.json, "w"), indent=1)
        rows = out.pop("rows")
        for sp in ("dev", "test"):
            if out.get(sp):
                s = {k: v for k, v in out[sp].items() if k not in ("by_kind",)}
                print(sp, json.dumps(s))
        print(len(rows), "courses scored")


if __name__ == "__main__":
    main()
