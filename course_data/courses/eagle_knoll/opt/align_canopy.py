"""Lidar crowns vs the hand-map trees per hole (OPTIMIZE.md 12a). Usage: align_canopy.py <repo root> <which>"""
import os, sys, numpy as np
from scipy import ndimage
W = sys.argv[1]; which = sys.argv[2]
sys.path.insert(0, os.path.join(W, "course_data", "courses"))
import v2_course as vc
course, meta, M, D = vc.activate("eagle_knoll", which)
cof = M._engine_opts["_canopy_of"]
for h in M.HOLES:
    hd = M.HOLES[h]; R = M.Raster(hd)
    ga, gl, top, base = cof(hd)
    AA, LL = np.meshgrid(ga, gl, indexing="ij")
    lie = R.lie_at(AA, LL)
    win = (AA >= 150) & (AA <= 340) & (np.abs(LL) <= 55)
    mt = (lie == M.CODE["recovery"]) & win
    lt = (top > 0) & win
    # best shift of lidar vs map (yds), +-4
    best = None
    for da in range(-4, 5, 2):
        for dl in range(-4, 5, 2):
            sh = np.roll(np.roll(top > 0, da, 0), dl, 1) & win
            iou = (sh & mt).sum() / max((sh | mt).sum(), 1)
            if best is None or iou > best[0]: best = (iou, da, dl)
    iou = (lt & mt).sum() / max((lt | mt).sum(), 1)
    over_open = (lt & ~mt & (lie != M.CODE["water"])).sum() / max(lt.sum(), 1)
    print(h, "map-tree %.2f lidar-tree %.2f IoU %.2f (best %.2f at %+d,%+d) lidar on open lies %.2f  map trees w/o lidar %.2f  top p50/p90 in map trees %.0f/%.0f yds" % (
        mt.sum() / win.sum(), lt.sum() / win.sum(), iou, best[0], best[1], best[2], over_open,
        (mt & ~lt).sum() / max(mt.sum(), 1), np.percentile(top[mt & lt], 50) if (mt & lt).any() else 0,
        np.percentile(top[mt & lt], 90) if (mt & lt).any() else 0))
