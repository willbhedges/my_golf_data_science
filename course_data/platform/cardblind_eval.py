"""Card-blind scoreboard: with NO scorecard, how close is the tee-shot plan to the plan built with the true card?

  python3 course_data/platform/cardblind_eval.py --out-dir /tmp/cb                  # every course, n=4000
  python3 course_data/platform/cardblind_eval.py --out-dir /tmp/cb --courses blue_hills --n 2000
  python3 course_data/platform/cardblind_eval.py --out-dir /tmp/cb --from-builds    # re-score existing builds
  -> course_data/platform/cardblind_eval.json + the table printed for CARDBLIND.md (--md writes CARDBLIND.md)

Re-run after improving tees/cardless.py (synthetic card) or zero_tap/pathroute (routing): nothing here needs
editing; package.py's "card": "none" mode picks the module up (cardless_card).

Per course, two packages are built offline from the same committed raw OSM (no network):
  ref    the true card: the hand-truth package (course_data/courses/<slug>/truth/package.json) where one exists,
         else a normal package.py build (web card + review overrides from the request)
  blind  package.py with request "card": "none" (every card input and card-based review override stripped)
Both go through product/package.load -> product/decide.run(mode="quick") for the BACK set (longest on each
package's card) and the 2ND set (second longest). Per hole (ref numbering):
  routing   blind hole of that number has green within 20 yds and the set's tee within 40 yds of ref (routing.score)
  par       blind par == ref par
  tee_err   yds between the two packages' tee for that set rank
  len_err   blind length - ref length (yds)
  club      blind tee club == ref tee club (par 4/5 holes the ref plans; a blind par 3 there = no plan)
  aim_d     the blind aim point (its carry along its own tee line + its aim) seen from the REF tee, re-expressed
            as an aim at the blind club's carry on the ref tee line, minus the ref aim (yds)
  regret    EV on the ref geometry of (blind club, that aim) - EV of the ref plan (strokes; common random numbers)
  hit10     same club and |aim_d| <= 10 yds   (the headline)
Library courses (reviewed, review.json) are scored on their review-OK holes only, from a cached OSM snapshot
(osm_inventory.json) when the library raw/ has no osm.geojson.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import gzip
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
OUT_JSON = os.path.join(HERE, "cardblind_eval.json")
OUT_MD = os.path.join(HERE, "CARDBLIND.md")

# slug -> where the raw data and the request come from; truth = hand-truth package (optional)
PKG_COURSES = ["blue_hills", "coldwater", "eagle_knoll", "ellis", "gateway_national", "hot_springs_arlington",
               "hot_springs_park", "jayhawk_club", "mozingo_lake", "national_kc", "oaks_margaritaville",
               "pine_dunes", "spirit_hollow", "tomahawk_hills", "veenker", "wakonda"]
HAND_TRUTH = {"blue_hills": "course_data/courses/blue_hills/truth/package.json",
              "eagle_knoll": "course_data/courses/eagle_knoll/truth/package.json"}
LIB_COURSES = ["creekmoor", "finkbine", "sycamore_ridge"]       # reviewed library courses with a cached OSM snapshot
ROUTE_GREEN_YD, ROUTE_TEE_YD = 20.0, 40.0
HIT_AIM_YD = 10.0
STRIP_REVIEW = ("tee_overrides", "hole_renumber", "green_overrides")   # hand fixes a zero-input golfer never has


def course_list():
    out = [dict(slug=s, group="package", raw=os.path.join(CD, "packages", s, "raw"),
                imagery=os.path.join(CD, "packages", s, "imagery"),
                req=os.path.join(CD, "requests", f"package_{s}.json"), truth=HAND_TRUTH.get(s)) for s in PKG_COURSES]
    for s in LIB_COURSES:
        out.append(dict(slug=s, group="library", raw=os.path.join(CD, "library", s, "raw"), imagery=None,
                        req=os.path.join(CD, "library", s, "package_request.json"), truth=None,
                        review=os.path.join(CD, "library", s, "review.json")))
    return out


def snapshot_for(raw):
    c = json.load(open(os.path.join(raw, "course.json")))
    oid = f"{c['osm']['type']}/{c['osm']['id']}"
    inv = json.load(open(os.path.join(HERE, "osm_inventory.json")))["snapshots"]
    for s in sorted(inv, key=lambda s: s.get("date", ""), reverse=True):
        if s["osm"] == oid and os.path.exists(os.path.join(ROOT, s["path"])):
            return os.path.join(ROOT, s["path"])
    return None


# ----------------------------------------------------------------------------- build (child process)
def build(slug, variant, out_root):
    cfg = next(c for c in course_list() if c["slug"] == slug)
    dst = os.path.join(out_root, variant, slug)
    os.makedirs(dst, exist_ok=True)
    rdst = os.path.join(dst, "raw")
    if not os.path.exists(rdst):
        if os.path.exists(os.path.join(cfg["raw"], "osm.geojson")):
            os.symlink(cfg["raw"], rdst)
        else:                                  # library: raw/ minus osm.geojson -> add the cached snapshot
            snap = snapshot_for(cfg["raw"])
            if not snap:
                raise SystemExit(f"{slug}: no osm.geojson and no cached snapshot")
            os.makedirs(rdst)
            for f in os.listdir(cfg["raw"]):
                p = os.path.join(cfg["raw"], f)
                os.symlink(p, os.path.join(rdst, f))
            op = gzip.open if snap.endswith(".gz") else open
            fc = json.load(op(snap, "rt"))
            for f in fc["features"]:
                f.setdefault("properties", {}).setdefault("inside_course", True)
            json.dump(fc, open(os.path.join(rdst, "osm.geojson"), "w"))
    if cfg.get("imagery") and os.path.isdir(cfg["imagery"]) and not os.path.exists(os.path.join(dst, "imagery")):
        os.symlink(cfg["imagery"], os.path.join(dst, "imagery"))
    sys.path[:0] = [HERE]
    import package as P
    req = json.load(open(cfg["req"]))
    req.setdefault("allow_substitute", True)
    if variant == "blind":
        req = {k: v for k, v in req.items() if k not in STRIP_REVIEW}
        req["card"] = "none"
    with contextlib.redirect_stdout(io.StringIO()):
        pkg = P.build_package(req, dst)
        P.write(pkg, dst)
    return os.path.join(dst, "package.json")


# ----------------------------------------------------------------------------- scoring (parent process)
def _yd(a, b):
    kx = math.cos(math.radians((a[1] + b[1]) / 2)) * 111320 / 0.9144
    return math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * 111320 / 0.9144)


def ranked_sets(pkg):
    ts = pkg.get("tee_sets") or {}
    return sorted(ts, key=lambda k: -(ts[k].get("total") or sum(y for y in (ts[k].get("yards") or []) if y) or 0))


def hole_tee(h, s):
    t = (h.get("tees") or {}).get(s) or {}
    return t.get("tee_ll") or t.get("ll") or (h.get("tee_ll") if not h.get("tees") else None)


def set_len(h, s):
    t = (h.get("tees") or {}).get(s) or {}
    return t.get("length") or t.get("card_yards") or t.get("yards") or t.get("measured_yards") or h.get("length")


def plan(path, set_name, n, tag):
    import decide
    import package as PK
    C = PK.load(path, set_name)
    with tempfile.TemporaryDirectory() as td:
        mp = os.path.join(td, "course.py")
        PK.write_module(C, mp)
        mod = PK.import_module(mp, name=f"cb_{tag}".replace(" ", "_").replace("/", "_"))
    holes = copy.deepcopy(mod.HOLES)
    res = decide.run(copy.deepcopy(holes), "quick", log=lambda *a: None, n=n) if holes else {}
    return C, holes, {str(k): v for k, v in res.items()}


def score_set(ref_path, blind_path, ref_pkg, blind_pkg, rank, n, ok_holes=None, slug=""):
    import numpy as np
    import decide
    import render as R
    import tee_strategy as t
    rs, bs = ranked_sets(ref_pkg), ranked_sets(blind_pkg)
    if len(rs) <= rank:
        return None
    rset = rs[rank]
    bset = bs[min(rank, len(bs) - 1)] if bs else None
    Cr, Hr, Pr = plan(ref_path, rset, n, f"{slug}_ref_{rank}")
    Cb, Hb, Pb = plan(blind_path, bset, n, f"{slug}_blind_{rank}")
    rows = []
    decide.bind(copy.deepcopy(Hr))
    decide.set_prior_means()
    z = decide._z(n, 31)
    for ref in sorted(ref_pkg["holes"], key=lambda r: str(r).zfill(3)):
        if ok_holes is not None and str(ref) not in ok_holes:
            continue
        hr = ref_pkg["holes"][ref]
        hb = (blind_pkg.get("holes") or {}).get(ref)
        row = dict(hole=str(ref), ref_par=hr.get("par"), ref_len=None, routed=False)
        tr = hole_tee(hr, rset)
        row["ref_len"] = set_len(hr, rset)
        if hb is None:
            row["fail"] = "blind package has no such hole"
            rows.append(row)
            continue
        tb = hole_tee(hb, bset)
        gr, gb = hr.get("green_ll"), hb.get("green_ll")
        row["blind_par"] = hb.get("par")
        row["par_ok"] = hb.get("par") == hr.get("par")
        row["blind_len"] = set_len(hb, bset)
        if row["ref_len"] and row["blind_len"]:
            row["len_err"] = int(row["blind_len"]) - int(row["ref_len"])
        if tr and tb:
            row["tee_err"] = round(_yd(tr[:2], tb[:2]), 1)
        if gr and gb:
            row["green_err"] = round(_yd(gr[:2], gb[:2]), 1)
        row["routed"] = bool(row.get("green_err") is not None and row["green_err"] <= ROUTE_GREEN_YD
                             and row.get("tee_err") is not None and row["tee_err"] <= ROUTE_TEE_YD)
        k = str(decide_key(ref))
        pr = Pr.get(k)
        if pr is None:                                     # the ref plan has no tee-shot decision (par 3)
            row["shot"] = False
            rows.append(row)
            continue
        row.update(shot=True, ref_club=pr["pick"], ref_aim=pr["aim"], ref_ev=round(pr["ev"], 4), ref_tie=pr["tie"],
                   ref_runner=pr["runner"])
        pb = Pb.get(k)
        if pb is None:
            row["fail"] = row.get("fail") or "blind plan has no tee-shot decision here (par 3 or no tee)"
            row["hit10"] = False
            rows.append(row)
            continue
        row.update(blind_club=pb["pick"], blind_aim=pb["aim"], same_club=pb["pick"] == pr["pick"],
                   tie_ok=pb["pick"] == pr["pick"] or (pr["tie"] and pb["pick"] == pr["runner"]))
        # blind aim point -> lat/lon -> ref frame -> equivalent aim at the blind club's carry from the REF tee
        try:
            kb = decide_key(ref)
            fb = R.Frame.from_json(Cb.frames[kb])
            fr = R.Frame.from_json(Cr.frames[kb])
            hdb = Hb[kb]
            tee, fwd, right, ppy = t.hole_frame(hdb)
            c = decide._carry(pb["pick"])
            P_px = tee + (c * fwd + pb["aim"] * right) * ppy
            P_ll = fb.px_to_ll(np.array([P_px]))[0]
            teer, fwdr, rightr, ppyr = t.hole_frame(Hr[kb])
            q = (fr.ll_to_px(np.array([P_ll]))[0] - teer) / ppyr
            along, lat = float(q @ fwdr), float(q @ rightr)
            aim_eq = c * lat / along if along > 30 else lat
            row["aim_eq"] = round(aim_eq, 1)
            row["aim_d"] = round(aim_eq - pr["aim"], 1)
            ev = float(t.simulate(kb, pb["pick"], aim_eq, z=z)[3].mean())
            ev_ref = float(t.simulate(kb, pr["pick"], pr["aim"], z=z)[3].mean())
            row["regret"] = round(ev - ev_ref, 4)
        except Exception as e:                              # noqa: BLE001
            row["fail"] = f"aim transfer: {type(e).__name__}: {e}"[:200]
        row["hit10"] = bool(row["same_club"] and row.get("aim_d") is not None and abs(row["aim_d"]) <= HIT_AIM_YD)
        rows.append(row)
    return dict(ref_set=rset, blind_set=bset, rows=rows)


def decide_key(ref):
    return int(ref) if str(ref).isdigit() else str(ref)


def summarise(rows):
    import numpy as np
    n = len(rows)
    sh = [r for r in rows if r.get("shot")]
    te = [r["tee_err"] for r in rows if r.get("tee_err") is not None]
    rg = [r["regret"] for r in sh if r.get("regret") is not None]
    ad = [abs(r["aim_d"]) for r in sh if r.get("same_club") and r.get("aim_d") is not None]
    le = [abs(r["len_err"]) for r in rows if r.get("len_err") is not None]
    return dict(holes=n, routed=sum(bool(r.get("routed")) for r in rows), par_ok=sum(bool(r.get("par_ok")) for r in rows),
                tee_med=round(float(np.median(te)), 1) if te else None,
                tee_10=sum(x <= 10 for x in te), tee_n=len(te),
                len_med=round(float(np.median(le)), 1) if le else None,
                shots=len(sh), same_club=sum(bool(r.get("same_club")) for r in sh),
                tie_ok=sum(bool(r.get("tie_ok")) for r in sh), hit10=sum(bool(r.get("hit10")) for r in sh),
                no_plan=sum(r.get("blind_club") is None for r in sh),
                aim_med=round(float(np.median(ad)), 1) if ad else None,
                regret_mean=round(float(np.mean(rg)), 3) if rg else None,
                regret_total=round(float(np.sum(rg)), 2) if rg else None, regret_n=len(rg))


def ok_holes_of(cfg):
    if not cfg.get("review"):
        return None
    d = json.load(open(cfg["review"]))["course_review/1"]
    return {str(h["n"]) for h in d.get("holes", []) if str(h.get("verdict", "")).lower().startswith("ok")}


def causes(rows):
    """Failure tag per tee-shot hole the blind plan gets wrong (first that applies)."""
    out = {}
    for r in rows:
        if not r.get("shot") or r.get("hit10"):
            continue
        if not r.get("routed"):
            c = "routing / tee >40 yds off" if r.get("green_err") is not None and r["green_err"] <= ROUTE_GREEN_YD else "routing (wrong green)"
        elif r.get("blind_club") is None:
            c = "par wrong (blind par 3)"
        elif r.get("par_ok") is False:
            c = "par wrong"
        elif r.get("tee_err") is not None and r["tee_err"] > 15:
            c = "tee position >15 yds"
        elif r.get("len_err") is not None and abs(r["len_err"]) > 15:
            c = "length >15 yds (same tee area)"
        elif not r.get("same_club"):
            c = "club flip (geometry ~same)" if not r.get("tie_ok") else "club flip on a ref tie"
        else:
            c = "aim >10 yds (same club)"
        out[r["hole"]] = c
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--courses")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--from-builds", action="store_true", help="reuse packages already in --out-dir")
    ap.add_argument("--build", nargs=2, metavar=("SLUG", "VARIANT"))
    ap.add_argument("--md", action="store_true", help="also rewrite CARDBLIND.md's generated table")
    a = ap.parse_args()
    if a.build:
        print(build(a.build[0], a.build[1], a.out_dir))
        return
    for p in (os.path.join(CD, "product"), os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
        sys.path.insert(0, p)
    want = set(a.courses.split(",")) if a.courses else None
    prev = json.load(open(OUT_JSON)) if os.path.exists(OUT_JSON) else {}
    out = dict(schema="cardblind_eval/1", made_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), n=a.n,
               doc="platform/CARDBLIND.md", courses=dict(prev.get("courses") or {}) if want else {})
    for cfg in course_list():
        s = cfg["slug"]
        if want and s not in want:
            continue
        t0 = time.time()
        rec = dict(group=cfg["group"], ref="hand truth package" if cfg.get("truth") else "normal build (true card)")
        paths = {}
        try:
            for v in ("ref", "blind"):
                if v == "ref" and cfg.get("truth"):
                    paths[v] = os.path.join(ROOT, cfg["truth"])
                    continue
                p = os.path.join(a.out_dir, v, s, "package.json")
                if not (a.from_builds and os.path.exists(p)):
                    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--build", s, v, "--out-dir", a.out_dir],
                                       capture_output=True, text=True)
                    if r.returncode:
                        raise RuntimeError(f"{v} build failed: {(r.stderr or r.stdout).strip().splitlines()[-1:]}")
                paths[v] = p
            ref_pkg, blind_pkg = json.load(open(paths["ref"])), json.load(open(paths["blind"]))
            rec["blind_card"] = (blind_pkg.get("scorecard") or {}).get("source")
            rec["blind_holes_method"] = ((blind_pkg.get("pipeline") or {}).get("holes") or {}).get("method")
            okh = ok_holes_of(cfg)
            rec["scored_holes"] = "review-OK holes only" if okh is not None else "all"
            for rank, name in ((0, "back"), (1, "second")):
                with contextlib.redirect_stdout(io.StringIO()):
                    r = score_set(paths["ref"], paths["blind"], ref_pkg, blind_pkg, rank, a.n, okh, s)
                if r:
                    r["summary"] = summarise(r["rows"])
                    r["causes"] = causes(r["rows"])
                    rec[name] = r
                    sm = r["summary"]
                    print(f"{s:22s} {name:6s} ref={r['ref_set']:12s} blind={r['blind_set']:8s} route {sm['routed']}/{sm['holes']} "
                          f"par {sm['par_ok']}/{sm['holes']} tee_med {sm['tee_med']} club {sm['same_club']}/{sm['shots']} "
                          f"hit10 {sm['hit10']}/{sm['shots']} regret {sm['regret_mean']}", flush=True)
        except Exception as e:                              # noqa: BLE001
            rec["error"] = f"{type(e).__name__}: {e}"[:400]
            print(s, "ERROR", rec["error"], flush=True)
        rec["seconds"] = round(time.time() - t0, 1)
        out["courses"][s] = rec
        json.dump(out, open(OUT_JSON, "w"), indent=1, default=str)
    out["totals"] = totals(out["courses"])
    json.dump(out, open(OUT_JSON, "w"), indent=1, default=str)
    md = table_md(out)
    print(md)
    if a.md:
        write_md(md)


def totals(courses):
    tot = {}
    for name in ("back", "second"):
        rows = [r for c in courses.values() for r in (c.get(name) or {}).get("rows", [])]
        if not rows:
            continue
        tot[name] = summarise(rows)
        cz = {}
        for c in courses.values():
            for v in ((c.get(name) or {}).get("causes") or {}).values():
                cz[v] = cz.get(v, 0) + 1
        tot[name]["causes"] = dict(sorted(cz.items(), key=lambda kv: -kv[1]))
    return tot


def _pct(a, b):
    return f"{a}/{b} ({100 * a / b:.0f} %)" if b else "-"


def table_md(out):
    L = ["| course | set (ref / blind) | ref | routing right | par right | back-tee err med (<=10 yds) | |len err| med | "
         "same club | same club + aim <=10 | no plan | aim diff med (same club) | regret / tee shot |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s, c in out["courses"].items():
        if c.get("error"):
            L.append(f"| {s} | build failed: {c['error'][:90]} | | | | | | | | | | |")
            continue
        for name in ("back", "second"):
            r = c.get(name)
            if not r:
                continue
            m = r["summary"]
            L.append(f"| {s}{' (review-OK holes)' if c.get('scored_holes') != 'all' else ''} | {name}: {r['ref_set']} / {r['blind_set']} | "
                     f"{'hand' if c['ref'].startswith('hand') else 'card'} | {m['routed']}/{m['holes']} | {m['par_ok']}/{m['holes']} | "
                     f"{m['tee_med']} ({m['tee_10']}/{m['tee_n']}) | {m['len_med']} | {m['same_club']}/{m['shots']} | "
                     f"**{m['hit10']}/{m['shots']}** | {m['no_plan']} | {m['aim_med']} | {m['regret_mean']} |")
    for name, m in (out.get("totals") or {}).items():
        L.append(f"| **all** | **{name}** | | {_pct(m['routed'], m['holes'])} | {_pct(m['par_ok'], m['holes'])} | "
                 f"{m['tee_med']} ({_pct(m['tee_10'], m['tee_n'])}) | {m['len_med']} | {_pct(m['same_club'], m['shots'])} | "
                 f"**{_pct(m['hit10'], m['shots'])}** | {m['no_plan']} | {m['aim_med']} | {m['regret_mean']} |")
    L.append("")
    for name, m in (out.get("totals") or {}).items():
        miss = m["shots"] - m["hit10"]
        L.append(f"Failure causes, {name} set ({miss} tee shots not same club + aim <= 10 yds): " +
                 "; ".join(f"{k} {v}" for k, v in m["causes"].items()))
        L.append("")
    return "\n".join(L)


BEGIN, END = "<!-- cardblind_eval:begin -->", "<!-- cardblind_eval:end -->"


def write_md(md):
    txt = open(OUT_MD).read() if os.path.exists(OUT_MD) else f"# Card-blind scoreboard\n\n{BEGIN}\n{END}\n"
    if BEGIN in txt and END in txt:
        a, rest = txt.split(BEGIN, 1)
        _, b = rest.split(END, 1)
        txt = f"{a}{BEGIN}\n{md}\n{END}{b}"
    open(OUT_MD, "w").write(txt)


if __name__ == "__main__":
    main()
