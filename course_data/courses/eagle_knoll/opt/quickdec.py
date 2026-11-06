"""Reduced calm-day decide (decide.bayes on a club subset + shares), same record format as v2_decisions.json.
Usage: quickdec.py <repo> <which> <hole> <clubs comma> <draws> <out>"""
import os, sys, json, time
W, which, hole, clubs, S, out = sys.argv[1:7]
sys.path.insert(0, os.path.join(W, "course_data", "courses"))
import v2_course as vc
course, meta, M, D = vc.activate("eagle_knoll", which)
keep = clubs.split(",")
M.REAL_CLUBS[:] = [c for c in M.REAL_CLUBS if c in keep]
M.ALL_CLUBS[:] = [c for c in M.ALL_CLUBS if c in keep or c == M.HYBRID]
h = int(hole); t0 = time.time()
r = D.bayes(h, int(S), 3000)
r["shares"] = D.shares_at(h, D.central(h), r["pick"], r["aim"])
r["geometry"] = []
r["reduced"] = dict(clubs=M.REAL_CLUBS, draws=int(S), when="2026-11-06 local (OPTIMIZE.md 12)",
                    why="the full decide (256 draws, every club) does not fit the deadline on the shared CPU")
json.dump({str(h): r}, open(out, "w"), indent=1, default=float)
print(which, h, r["pick"], r["aim"], r["window"], "m=%.4f se=%.4f p=%.2f" % (r["margin"], r["margin_se"], r["p_pick_beats_runner"]), r["runner"], "%.0fs" % (time.time() - t0), flush=True)
