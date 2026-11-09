"""Where are the lidar crowns relative to each tee shot? Per hole: crown cells (lidar top >= min_tree_m, + growth,
OB masked; the Meta fill on mapped trees) within the descent corridor of the driver / long-iron flights
(along 150-320, |x| <= 45), their heights, the share on mapped tree / other lies, and Meta-vs-lidar growth.
Usage: canopy_check.py [which]"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "course_data", "courses"))
import v2_course as vc
which = sys.argv[1] if len(sys.argv) > 1 else "truth"
course, meta, M, D = vc.activate(os.environ.get("SLUG", "gateway_national"), which)
o = M._lidar_opts
out = {}
for k in [k for k in course.ORDER if k in course.HOLES]:
    hd = M.HOLES[k]; R = M.Raster(hd)
    ga, gl, top, base = vc.canopy_grid(M, hd, course.FRAMES[k], os.path.join(ROOT, o["chm"]), o, R=R)
    AA, LL = np.meshgrid(ga, gl, indexing="ij")
    lie = R.lie_at(AA, LL)
    cor = (AA >= 150) & (AA <= 320) & (np.abs(LL) <= 45)
    near = (AA >= 150) & (AA <= 320) & (np.abs(LL) <= 25)
    t = (top > 0) & cor
    rec = dict(cells=int(t.sum()), near25=int(((top > 0) & near).sum()),
               on_trees=int((t & (lie == M.CODE["recovery"])).sum()),
               mapped_trees=int(((lie == M.CODE["recovery"]) & cor).sum()),
               top_med=round(float(np.median(top[t])), 1) if t.any() else 0,
               top_p90=round(float(np.percentile(top[t], 90)), 1) if t.any() else 0,
               lies={M.LIES[i]: int((t & (lie == i)).sum()) for i in np.unique(lie[t])} if t.any() else {})
    out[str(k)] = rec
    print(k, rec, flush=True)
json.dump(out, open(os.path.join(os.environ.get("OUT", "/tmp"), f"canopy_{which}.json"), "w"), indent=1)
