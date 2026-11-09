"""Recompute some wind-grid cells of one hole at the card tee (refined solver, as the nccga-v2 job) and write them
into that which's v2/wind_grid.json. Usage: gridpatch.py <repo> <which> <hole> <speeds e.g. 0,5,10> [out]"""
import os, sys, json, time
W, which, hole, speeds = sys.argv[1:5]
sys.path.insert(0, os.path.join(W, "course_data", "courses"))
import v2_course as vc
course, meta, M, D = vc.activate(os.environ.get("SLUG", "gateway_national"), which)
import wind_grid as WG
WG.osm_bearings = lambda: {}
import wind_grid_v2 as WG2
WG2.N = 2500
solve = vc.refined_solver(M, D, WG2, 16000)
import geom
geom.set_geometry("")
path = os.path.join(W, "course_data", "courses", os.environ.get("SLUG", "gateway_national"), which, "v2", "wind_grid.json")
g = json.load(open(path))
h = int(hole); hd = M.HOLES[h]
R = M.Raster(hd)
z = M.draws_z(WG2.N, 31)
sp_list = [int(x) for x in speeds.split(",")]
for T in [float(t) for t in g["temps"]]:
    P = M.central(temp_f=T)
    S = R.strokes(P, hd["length"])
    cells = g["holes"][str(h)][f"{T:g}"]
    for sp in sp_list:
        for rel in ([0] if sp == 0 else WG2.DIRS):
            t0 = time.time()
            r = solve(h, P, R, S, z, sp, rel)
            r["patched"] = "2026-11-06 local (lidar flight trees, green putting)"
            old = cells.get(f"{sp}_{rel}", {})
            cells[f"{sp}_{rel}"] = r
            print(which, h, T, sp, rel, old.get("pick"), "->", r["pick"], r["clubs"][r["pick"]]["aim"], "m=%.4f" % r["margin"], "%.0fs" % (time.time() - t0), flush=True)
    json.dump(g, open(sys.argv[5] if len(sys.argv) > 5 else path, "w"))
print("wrote")
