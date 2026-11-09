import sys, json, os, copy, numpy as np
ROOT = "/home/user/my_golf_data_science"
sys.path.insert(0, os.path.join(ROOT, "course_data", "qa"))
import scoreboard as SB
S = os.environ.get("SH1109_DIR", "/tmp/sh1109")  # needs $S/pk/d06e6acee.json = git show d06e6acee:course_data/packages/spirit_hollow/package.json
base = json.load(open(f"{S}/pk/d06e6acee.json"))
final = SB.final_truth()
def side_of(h, z):
    t = np.array(h["tee_ll"], float); g = np.array(h["green_ll"], float)
    c = np.mean(np.array(z["poly"], float), 0)
    k = np.cos(np.radians(t[1]))
    d = (g - t) * [k, 1]; v = (c - t) * [k, 1]
    return "L" if d[0] * v[1] - d[1] * v[0] > 0 else "R"
holes = sys.argv[1].split(",")
for drop in ("L", "R"):
    p = copy.deepcopy(base)
    for ref in holes:
        h = p["holes"][ref]
        h["zones_ll"] = [z for z in h["zones_ll"] if not (z.get("src") == "auto:native_side" and side_of(h, z) == drop)]
    f = f"{S}/pk/var_drop{drop}.json"; json.dump(p, open(f, "w"))
    cfg = dict(SB.COURSES[0]); cfg["package"] = f
    res, C, s = SB.product_plan(cfg, "Black", keys=set(holes), n=8000)
    for k in holes:
        r = res[k]
        print("drop", drop, k, r["pick"], round(float(r["aim"]), 1), round(float(r["margin"]), 3), "truth", final[k]["pick"], SB.regret(r, final[k]), flush=True)
