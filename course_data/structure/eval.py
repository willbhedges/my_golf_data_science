"""Evaluate course-structure inference with every OSM hole hint and the scorecard hidden.

    python course_data/structure/eval.py --split dev               # tuning set only (what may be looked at)
    python course_data/structure/eval.py --all                     # dev + held-out: eval/*.json + eval/summary.md
    python course_data/structure/eval.py --slug dwan_mn -v         # one course, per-hole table

Courses: course_data/structure/sets.json + data/<slug>/ (fetch.py, Actions), plus the generalize study's cached
fully mapped courses (course_data/generalize/courses/<slug>/osm_golf.geojson, all from the tuning states -> dev).
A course is scored when its golf=hole ways carry each ref 1..N exactly once (N = 9 or 18; 27/36 reported apart).

Metrics (per hole, N per course):
  formation   the routed hole (any number) is a true hole: same green (the green polygon nearest the true line's
              end, <= 25 yds) and its tee: a box of the routed hole within 35 yds of the true line's start, or the
              routed back tee within 25 yds of the first 60 % of the true line
  number      routed hole n is true hole n (formation + same number)
  course      every hole number right ("fully correct")
  nine-swap   number accuracy after swapping the nines when that is better (diagnostic: front / back ambiguity)
  par         inferred par = OSM par tag (where tagged)
  calibration per-hole `confidence` vs number-correct: Brier, ECE (10 bins), reliability table
Configurations (ablations): full (paths + clubhouse, no card), no_paths, no_clubhouse, card (pars + yards from the
hidden OSM ways: the card prior), degraded (perception-quality stand-in: scene.degrade), degraded_no_clubhouse.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import scene as S                                                    # noqa: E402
import solver as V                                                   # noqa: E402

OUT = os.path.join(HERE, "eval")
CONFIGS = {
    "full": dict(),
    "no_paths": dict(use_paths=False),
    "no_clubhouse": dict(use_clubhouse=False),
    "card": dict(card=True),
    "degraded": dict(degrade=1.0),
    "degraded_no_clubhouse": dict(degrade=1.0, use_clubhouse=False),
    "degraded_card": dict(degrade=1.0, card=True),
}


def courses(split=None):
    """[(slug, split, kind, state, fc, course)]"""
    out = []
    sp = os.path.join(HERE, "sets.json")
    seen = set()
    if os.path.exists(sp):
        for c in json.load(open(sp))["courses"]:
            p = os.path.join(HERE, "data", c["slug"], "osm.geojson.gz")
            if not os.path.exists(p):
                continue
            if split and c["split"] != split:
                continue
            out.append(dict(slug=c["slug"], split=c["split"], kind=c["kind"], state=c["state"], path=p,
                            course=os.path.join(HERE, "data", c["slug"], "course.json")))
            seen.add(c["osm"])
    if split in (None, "dev"):
        for p in sorted(glob.glob(os.path.join(CD, "generalize", "courses", "*", "osm_golf.geojson"))):
            d = os.path.dirname(p)
            cj = os.path.join(d, "course.json")
            if not os.path.exists(cj):
                continue
            out.append(dict(slug=os.path.basename(d), split="dev", kind=None, state=None, path=p, course=cj,
                            src="generalize"))
    return out


def load(entry):
    fc = S.load_fc(entry["path"])
    course = json.load(open(entry["course"])) if os.path.exists(entry["course"]) else {}
    sc = S.scene_from_osm(fc, course.get("boundary"))
    truth = S.truth_from_osm(fc, sc.proj)
    refs = [h["ref"] for h in truth]
    ok_n = None
    if refs and len(set(refs)) == len(refs) and sorted(refs) == list(range(1, len(refs) + 1)):
        ok_n = len(refs)
    return sc, truth, ok_n, course


def card_from_truth(truth):
    pars = [h["par"] for h in truth]
    yards = [round(h["length"]) for h in truth]
    return dict(schema="scorecard/1", par=pars if all(pars) else None, tee_sets={"back": dict(yards=yards)})


def _seg_dist(p, line):
    a, b = line[:-1], line[1:]
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab ** 2).sum(1), 1e-9), 0, 1)
    return float(np.hypot(*(a + ab * t[:, None] - p).T).min())


def _first(line, frac=0.6):
    seg = np.hypot(*np.diff(line, axis=0).T)
    cum = np.r_[0, np.cumsum(seg)]
    L = cum[-1] * frac
    k = int(np.searchsorted(cum, L))
    if k >= len(line):
        return line
    pts = list(line[:k])
    if k > 0:
        f = (L - cum[k - 1]) / max(seg[k - 1], 1e-9)
        pts.append(line[k - 1] + f * (line[k] - line[k - 1]))
    return np.array(pts) if len(pts) >= 2 else line[:2]


def match(res, sc, truth):
    """-> per routed hole: (true ref of its physical hole or None)."""
    G = np.array([g["c"] for g in sc.greens])
    tid = {t["id"]: t["c"] for t in sc.tees}
    gid = {g["id"]: i for i, g in enumerate(sc.greens)}
    tg = []
    for h in truth:
        d = np.hypot(*(G - h["green"]).T) if len(G) else np.array([1e9])
        # nearest green polygon (contains or edge) to the line end
        i = int(np.argmin(d))
        tg.append(i if d[i] <= 25 else None)
    out = []
    for h in res["holes"]:
        gi = gid.get(h["green"])
        ref = None
        for j, t in enumerate(truth):
            if tg[j] is None or tg[j] != gi:
                continue
            boxes = [tid[b] for b in h["boxes"] if b in tid]
            dmin = min((float(np.hypot(*(b - t["tee"]))) for b in boxes), default=1e9)
            ok = dmin <= 35 or _seg_dist(np.asarray(h["tee_xy"]), _first(t["line"])) <= 25
            if ok:
                ref = t["ref"]
                break
        out.append(ref)
    return out


def score_course(res, sc, truth, N):
    m = match(res, sc, truth)
    nums = [h["number"] for h in res["holes"]]
    form = sum(1 for r in m if r is not None)
    num_ok = [int(r is not None and r == n) for r, n in zip(m, nums)]
    # nine swap
    swap = 0
    if N == 18:
        sw = [int(r is not None and r == ((n + 8) % 18) + 1) for r, n in zip(m, nums)]
        swap = max(sum(num_ok), sum(sw))
    else:
        swap = sum(num_ok)
    truth_par = {t["ref"]: t["par"] for t in truth}
    par_ok = [int(h["par"] == truth_par.get(r)) for h, r in zip(res["holes"], m) if r is not None and truth_par.get(r)]
    return dict(N=N, routed=len(res["holes"]), formation=form, number=sum(num_ok), swap=swap,
                all_correct=int(sum(num_ok) == N and len(res["holes"]) == N),
                all_formed=int(form == N), par_ok=sum(par_ok), par_n=len(par_ok),
                conf=[h["confidence"] for h in res["holes"]], correct=num_ok,
                formed=[int(r is not None) for r in m], refs=m)


def run(entries, configs, verbose=False, seed=0):
    rows = []
    for e in entries:
        try:
            sc0, truth, N, course = load(e)
        except Exception as ex:                                      # noqa: BLE001
            print("load failed", e["slug"], ex)
            continue
        if N not in (9, 18):
            continue
        if len(sc0.greens) < N - 2 or len(sc0.tees) < N - 2:
            continue
        for cname in configs:
            cfg = dict(CONFIGS[cname])
            sc = sc0
            if cfg.pop("degrade", None):
                sc = S.degrade(sc0, random.Random(f"{seed}-{e['slug']}"), level=1.0)
            card = card_from_truth(truth) if cfg.pop("card", False) else None
            t0 = time.time()
            try:
                res = V.solve(sc, card=card, n_holes=None, **cfg)
            except Exception as ex:                                  # noqa: BLE001
                import traceback
                traceback.print_exc()
                print("solve failed", e["slug"], cname, ex)
                continue
            r = score_course(res, sc, truth, N)
            r.update(slug=e["slug"], split=e["split"], config=cname, state=e.get("state") or course.get("state"),
                     n_guess=res["n_holes"], seconds=round(time.time() - t0, 2), ch=res.get("clubhouse", {}).get("how"))
            rows.append(r)
            if verbose:
                print(f"{e['slug'][:26]:26s} {cname:22s} N={N} guess={res['n_holes']} form {r['formation']:2d} "
                      f"num {r['number']:2d} swap {r['swap']:2d} par {r['par_ok']}/{r['par_n']} {r['seconds']}s "
                      f"ch={r['ch']} refs={r['refs']}", flush=True)
    return rows


def summarise(rows):
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        by[(r["split"], r["config"])].append(r)
    table = []
    for (split, cfg), rs in sorted(by.items()):
        holes = sum(r["N"] for r in rs)
        conf = np.array([c for r in rs for c in r["conf"]])
        cor = np.array([c for r in rs for c in r["correct"]])
        k = min(len(conf), len(cor))
        conf, cor = conf[:k], cor[:k]
        ece, brier = calib(conf, cor)
        table.append(dict(split=split, config=cfg, courses=len(rs), holes=holes,
                          formation=sum(r["formation"] for r in rs) / holes,
                          number=sum(r["number"] for r in rs) / holes,
                          swap=sum(r["swap"] for r in rs) / holes,
                          all_correct=float(np.mean([r["all_correct"] for r in rs])),
                          all_formed=float(np.mean([r["all_formed"] for r in rs])),
                          par=sum(r["par_ok"] for r in rs) / max(1, sum(r["par_n"] for r in rs)),
                          n_ok=float(np.mean([r["n_guess"] == r["N"] for r in rs])),
                          ece=ece, brier=brier, mean_conf=float(conf.mean()) if len(conf) else None,
                          sec=float(np.mean([r["seconds"] for r in rs]))))
    return table


def calib(conf, cor, bins=10):
    if not len(conf):
        return None, None
    brier = float(np.mean((conf - cor) ** 2))
    e = 0.0
    for b in range(bins):
        m = (conf >= b / bins) & (conf < (b + 1) / bins + (1e-9 if b == bins - 1 else 0))
        if m.any():
            e += m.mean() * abs(conf[m].mean() - cor[m].mean())
    return float(e), brier


def reliability(rows, split, cfg, bins=5):
    conf = np.array([c for r in rows if r["split"] == split and r["config"] == cfg for c in r["conf"]])
    cor = np.array([c for r in rows if r["split"] == split and r["config"] == cfg for c in r["correct"]])
    out = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        m = (conf >= lo) & ((conf < hi) | (b == bins - 1))
        if m.any():
            out.append(dict(bin=f"{lo:.1f}-{hi:.1f}", n=int(m.sum()), conf=float(conf[m].mean()), acc=float(cor[m].mean())))
    return out


def md_table(table):
    hdr = "| split | config | courses | holes | formation | hole number | number (nine-swap ok) | fully correct | all formed | par | N right | ECE | Brier | s/course |"
    lines = [hdr, "|" + "---|" * 14]
    for t in table:
        lines.append(f"| {t['split']} | {t['config']} | {t['courses']} | {t['holes']} | {t['formation']:.1%} | {t['number']:.1%} | "
                     f"{t['swap']:.1%} | {t['all_correct']:.1%} | {t['all_formed']:.1%} | {t['par']:.1%} | {t['n_ok']:.0%} | "
                     f"{t['ece']:.3f} | {t['brier']:.3f} | {t['sec']:.1f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "heldout"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--slug")
    ap.add_argument("--configs", default=",".join(CONFIGS))
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    ents = courses(None if a.all else a.split)
    if a.slug:
        ents = [e for e in ents if e["slug"] == a.slug]
    if a.limit:
        ents = ents[:a.limit]
    cfgs = a.configs.split(",")
    rows = run(ents, cfgs, verbose=a.v or bool(a.slug))
    table = summarise(rows)
    print(md_table(table))
    if a.all or a.out != OUT:
        os.makedirs(a.out, exist_ok=True)
        json.dump(dict(made_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), table=table, rows=rows,
                       reliability={f"{s}/{c}": reliability(rows, s, c) for s in ("dev", "heldout") for c in cfgs}),
                  open(os.path.join(a.out, "results.json"), "w"), indent=1, default=float)
        open(os.path.join(a.out, "summary.md"), "w").write(md_table(table) + "\n")


if __name__ == "__main__":
    main()
