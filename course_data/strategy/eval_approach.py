"""Offline evaluation of the approach layer on existing packages (read-only) -> output/approach_eval.json.

    python3 course_data/strategy/eval_approach.py [--courses blue_hills,eagle_knoll] [--workers 4]

Per par 4 / par 5:
  1. approach picks from the tee-only pick's own finishing spots (tee_strategy.simulate, the published
     objective's best club + aim): best club + aim point (pin-averaged) vs "aim at the green centre",
     the EV gain, the aim offset and P(green); plus one worked example from the median fairway finish
     and a tucked-pin example (the pin farthest from the green centre) vs "aim at the flag";
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
    reach = [r for r in rows if r.get("ev_centre") is not None]
    summ = dict(n=len(rows), n_green_reachable=len(reach))
    if reach:
        g = np.array([r["gain"] for r in reach])
        summ.update(mean_gain=round(float(g.mean()), 4), max_gain=round(float(g.max()), 4),
                    share_gain_over_002=round(float(np.mean(g > 0.02)), 3),
                    share_club_differs=round(float(np.mean([r["best_club"] != r["centre_club"] for r in reach])), 3),
                    mean_abs_offset=round(float(np.mean([np.hypot(r["off_long"], r["off_right"]) for r in reach])), 1),
                    share_aim_off_green=round(float(np.mean([not r["on_green_target"] for r in reach])), 3))
    return summ


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
        lname = "fairway" if lie[i] == "first_cut" else str(lie[i])
        r = A.solve(hole, xy[i], lname, n=300)
        if not r["best"] or not r["centre"]:
            rows.append(dict(lie=lname, dist=round(float(np.hypot(*(xy[i] - hole.green_c))), 1),
                             best_club=r["best"]["club"] if r["best"] else None, centre=None))
            continue
        b, c = r["best"], r["centre"]
        rows.append(dict(lie=lname, dist=round(float(np.hypot(*(xy[i] - hole.green_c))), 1),
                         best_club=b["club"], centre_club=c["club"], ev_best=b["ev"], ev_centre=c["ev"],
                         gain=round(c["ev"] - b["ev"], 4), off_long=b["vs_centre_long"],
                         off_right=b["vs_centre_right"], on_green_target=b["lie_at_target"] == "green",
                         p_green_best=round(b["p_green"], 3), p_green_centre=round(c["p_green"], 3)))
    summ = summarise(rows)
    # worked examples: the median-distance fairway finish, unknown pin and the most tucked pin
    fw = [i for i in idx if lie[i] in ("fairway", "first_cut")]
    ex = {}
    if fw:
        d = np.array([np.hypot(*(xy[i] - hole.green_c)) for i in fw])
        i = fw[int(np.argsort(d)[len(d) // 2])]
        r = A.solve(hole, xy[i], "fairway", n=600)
        ex["median_fairway"] = {k: r.get(k) for k in ("start", "best", "centre")}
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
    gains = [r["approach"]["summary"]["mean_gain"] for r in res if "mean_gain" in r["approach"]["summary"]]
    return dict(holes=n, tee_club_changes=sum(not r["tee"]["same_club"] for r in res),
                tee_pick_changes=sum((not r["tee"]["same_club"]) or r["tee"]["aim_shift"] != 0 for r in res),
                mean_regret=round(float(np.mean([r["tee"]["regret_whole"] for r in res])), 4),
                max_regret=round(float(max(r["tee"]["regret_whole"] for r in res)), 4),
                mean_approach_gain=round(float(np.mean(gains)), 4) if gains else None)


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
                  f" | approach gain {r['approach']['summary'].get('mean_gain')} ({r['secs']} s)", flush=True)
            res.append(r)
    res.sort(key=lambda r: (r["slug"], int(r["hole"])))
    summ = course_summary(res)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(dict(summary=summ, holes=res), fh, indent=1)
    print(json.dumps(summ))


if __name__ == "__main__":
    main()
