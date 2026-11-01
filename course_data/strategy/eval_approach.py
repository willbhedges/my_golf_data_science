"""Offline evaluation of the approach layer on existing packages (read-only) -> output/approach_eval.json.

    python3 course_data/strategy/eval_approach.py [--courses blue_hills,eagle_knoll] [--workers 4]

Per par 4 / par 5:
  1. approach picks from the tee-only pick's own finishing spots (tee_strategy.simulate, the published
     objective's best club + aim): the DECADE pick (club + box-centre aim, or the DECADE lay-up) vs "aim at
     the green centre" (EV check, + = DECADE better), the aim offset (+long / +right), P(green), and for
     reference the old EV-optimal aim (solve(opt=True)); plus one worked example from the median fairway
     finish and a tucked-pin example (the pin farthest from the green centre) vs "aim at the flag";
  2. whole-hole tee choice: every tee club x aim scored by 1 + V(approach solver) instead of
     1 + expected_strokes(lie, yds to green) -> does the tee pick change, and what the tee-only pick costs.
Nothing here feeds any page.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from course_data.strategy import approach as A     # noqa: E402

OUT = os.path.join(HERE, "output", "approach_eval.json")


def summarise(rows):
    go = [r for r in rows if r.get("kind") == "decade"]
    summ = dict(n=len(rows), n_go=len(go), n_layup=sum(r.get("kind") == "layup" for r in rows))
    chk = [r for r in rows if r.get("ev_centre") is not None and r.get("ev_best") is not None]
    if chk:
        g = np.array([r["gain"] for r in chk])
        summ.update(mean_ev_check=round(float(g.mean()), 4), min_ev_check=round(float(g.min()), 4),
                    share_club_differs=round(float(np.mean([r["best_club"] != r["centre_club"] for r in chk])), 3))
    if go:
        summ.update(mean_off_long=round(float(np.mean([r["off_long"] for r in go])), 2),
                    mean_off_right=round(float(np.mean([r["off_right"] for r in go])), 2),
                    mean_abs_offset=round(float(np.mean([np.hypot(r["off_long"], r["off_right"]) for r in go])), 1),
                    clubs=dict(sorted({c: sum(r["best_club"] == c for r in go)
                                       for c in {r["best_club"] for r in go}}.items(), key=lambda kv: -kv[1])))
    opt = [r for r in rows if r.get("ev_opt") is not None and r.get("ev_best") is not None]
    if opt:
        summ.update(mean_cost_vs_ev_opt=round(float(np.mean([r["ev_best"] - r["ev_opt"] for r in opt])), 4),
                    ev_opt_mean_off_long=round(float(np.mean([r["opt_off_long"] for r in opt])), 2))
    return summ


def _row(lname, dist, r):
    b, c, o = r.get("best"), r.get("centre"), r.get("ev_opt")
    row = dict(lie=lname, dist=dist, kind=b["kind"] if b else None, best_club=b["club"] if b else None)
    if b:
        row.update(ev_best=b["ev"], off_long=b["vs_centre_long"], off_right=b["vs_centre_right"],
                   plays_like=b["plays_like"], on_green_target=b["lie_at_target"] == "green",
                   p_green_best=round(b["p_green"], 3))
        if b["kind"] == "layup":
            row["leaves"] = b["layup"]["leaves"]
    if c:
        row.update(centre_club=c["club"], ev_centre=c["ev"], p_green_centre=round(c["p_green"], 3),
                   gain=round(c["ev"] - b["ev"], 4) if b else None)
    if o:
        row.update(ev_opt=o["ev"], opt_club=o["club"], opt_off_long=o["vs_centre_long"],
                   opt_off_right=o["vs_centre_right"])
    return row


def approach_from_tee(slug, key, tee_pick, n_spots=40, mod=None):
    hole = A.Hole.from_package(slug, key)
    mod = mod or A.load_course_module(slug)
    saved = A.t.HOLES
    A.t.HOLES = mod.HOLES
    k = int(key) if str(key).isdigit() else key
    try:
        hd = mod.HOLES[k]
        pts, lie, _, _ = A.t.simulate(k, tee_pick["club"], tee_pick["aim"], z=A.z_draws(2000, 5))
    finally:
        A.t.HOLES = saved
    xy = (pts - np.array(hd["tee"], float)) / float(hd["px_per_yd"])
    ok = np.isin(lie, ["fairway", "rough", "sand", "first_cut"])
    idx = np.flatnonzero(ok)[:n_spots]
    rows = []
    for i in idx:
        lname = str(lie[i])
        r = A.solve(hole, xy[i], lname, n=300, opt=True)
        rows.append(_row(lname, round(float(np.hypot(*(xy[i] - hole.green_c))), 1), r))
    summ = summarise(rows)
    fw = [i for i in idx if lie[i] in ("fairway", "first_cut")]
    ex = {}
    if fw:
        d = np.array([np.hypot(*(xy[i] - hole.green_c)) for i in fw])
        i = fw[int(np.argsort(d)[len(d) // 2])]
        r = A.solve(hole, xy[i], "fairway", n=600, opt=True)
        ex["median_fairway"] = {k: r.get(k) for k in ("start", "best", "centre", "ev_opt", "decade", "ev_check")}
        pins = hole.pins()
        tuck = pins[int(np.argmax(np.hypot(*(pins - hole.green_c).T)))]
        r = A.solve(hole, xy[i], "fairway", pin=tuck, n=600)
        ex["tucked_pin"] = dict(pin=[round(float(v), 1) for v in tuck], best=r["best"], flag=r.get("flag"),
                                centre=r["centre"])
    return dict(summary=summ, examples=ex, spots=rows)


def run_hole(args):
    slug, key = args
    t0 = time.time()
    tc = A.tee_compare(slug, key, grid=10.0, n_tee=1000)
    ap = approach_from_tee(slug, key, tc["tee_only"])
    rows = tc.pop("rows")
    tc["n_options"] = len(rows)
    return dict(slug=slug, hole=str(key), tee=tc, approach=ap, secs=round(time.time() - t0, 1))


def resummarise(path=OUT):
    """Recompute the per-hole approach summaries from the saved spots (and the course summary)."""
    d = json.load(open(path))
    for r in d["holes"]:
        r["approach"]["summary"] = summarise(r["approach"]["spots"])
    d["summary"] = course_summary(d["holes"])
    with open(path, "w") as fh:
        json.dump(d, fh, indent=1)
    return d


def course_summary(res):
    n = len(res)
    gains = [r["approach"]["summary"]["mean_ev_check"] for r in res if "mean_ev_check" in r["approach"]["summary"]]
    go = [s for r in res for s in r["approach"]["spots"] if s.get("kind") == "decade"]
    return dict(holes=n, tee_club_changes=sum(not r["tee"]["same_club"] for r in res),
                tee_pick_changes=sum((not r["tee"]["same_club"]) or r["tee"]["aim_shift"] != 0 for r in res),
                mean_regret=round(float(np.mean([r["tee"]["regret_whole"] for r in res])), 4),
                max_regret=round(float(max(r["tee"]["regret_whole"] for r in res)), 4),
                mean_ev_check_decade_vs_centre=round(float(np.mean(gains)), 4) if gains else None,
                mean_off_long_all_go=round(float(np.mean([s["off_long"] for s in go])), 2) if go else None,
                mean_off_right_all_go=round(float(np.mean([s["off_right"] for s in go])), 2) if go else None,
                n_go=len(go), n_layup=sum(s.get("kind") == "layup" for r in res for s in r["approach"]["spots"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--courses", default="blue_hills,eagle_knoll")
    ap.add_argument("--holes", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--resummarise", action="store_true")
    a = ap.parse_args()
    if a.resummarise:
        print(json.dumps(resummarise()["summary"]))
        return
    jobs = []
    for slug in a.courses.split(","):
        pkg = A.load_package(slug)
        for k, h in pkg["holes"].items():
            if h["par"] >= 4 and (not a.holes or k in a.holes.split(",")):
                jobs.append((slug, k))
    with mp.Pool(a.workers) as pool:
        res = []
        for r in pool.imap_unordered(run_hole, jobs):
            tc = r["tee"]
            print(f"{r['slug']} {r['hole']:>2} par {tc['par']}: tee-only {tc['tee_only']['club']} {tc['tee_only']['aim']:+.0f}"
                  f" | whole {tc['whole_hole']['club']} {tc['whole_hole']['aim']:+.0f} regret {tc['regret_whole']:.3f}"
                  f" | DECADE vs centre {r['approach']['summary'].get('mean_ev_check')}"
                  f" depth {r['approach']['summary'].get('mean_off_long')} ({r['secs']} s)", flush=True)
            res.append(r)
    res.sort(key=lambda r: (r["slug"], int(r["hole"])))
    summ = course_summary(res)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(dict(summary=summ, holes=res), fh, indent=1)
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
