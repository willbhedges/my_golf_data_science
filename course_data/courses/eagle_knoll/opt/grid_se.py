"""MC precision of the wind-grid picks: per cell, paired per-swing SE of (runner - best) at the grid's own swings
(seed 31, N=2500) and stored aims, plus an independent re-estimate with fresh swings (N_CHECK) on a local aim grid."""
import json, os, sys, time
import numpy as np
WT, slug, which = sys.argv[1], sys.argv[2], sys.argv[3]
holes = [h for h in sys.argv[4].split(",") if h]
temps = [float(t) for t in sys.argv[5].split(",")]
speeds = [int(s) for s in sys.argv[6].split(",")]
out_path = sys.argv[7]
NCHK = int(os.environ.get("N_CHECK", 20000))
sys.path.insert(0, os.path.join(WT, "course_data", "courses"))
import v2_course as vc
course, meta, M, D = vc.activate(slug, which)
import wind_grid as WG
WG.osm_bearings = lambda: {}
import wind_grid_v2 as WG2
grid = json.load(open(vc.cdir(slug, which, "v2", "wind_grid.json")))
N = int(os.environ.get("N_GRID", 2500))
z = M.draws_z(N, int(os.environ.get("SEED_GRID", 31)))
z2 = M.draws_z(NCHK, 777)
res = {}
for hs in holes or [k for k in grid["holes"]]:
    h = int(hs); hd = M.HOLES[h]
    R = M.Raster(hd)
    for T in temps:
        P = M.central(temp_f=T)
        S = R.strokes(P, hd["length"])
        g = grid["holes"][hs][f"{T:g}"]
        for sp in speeds:
            for rel in ([0] if sp == 0 else WG2.DIRS):
                key = f"{sp}_{rel}"
                cell = g[key]; cl = cell["clubs"]
                real = sorted([c for c in cl if c not in M.HYPOTHETICAL], key=lambda c: cl[c]["ev"])
                top = real[:3]
                vals, vals2, ev2 = {}, {}, {}
                for c in top:
                    hook = WG2.wind_hook(c, sp, rel) if sp else None
                    _, (a, l, lie, s) = M.ev_curve(R, S, hd, c, P, z, np.array([cl[c]["aim"]]), wind=hook)
                    vals[c] = 1.0 + s[:, 0]
                    aims = cl[c]["aim"] + np.arange(-6, 6.01, 1.0)
                    e, (a2, l2, lie2, s2) = M.ev_curve(R, S, hd, c, P, z2, aims, wind=hook)
                    j = int(np.argmin(e)); ev2[c] = float(e[j]); vals2[c] = 1.0 + s2[:, j]
                b, r = top[0], top[1]
                d = vals[r] - vals[b]
                d2 = vals2[r] - vals2[b]
                best2 = min(top, key=lambda c: ev2[c])
                res[f"{hs}|{T:g}|{key}"] = dict(best=b, runner=r, third=top[2], m=float(cl[r]["ev"] - cl[b]["ev"]),
                    m_here=float(d.mean()), se=float(d.std(ddof=1) / np.sqrt(N)),
                    m3=float(cl[top[2]]["ev"] - cl[b]["ev"]),
                    m_chk=float(ev2[r] - ev2[b]), se_chk=float(d2.std(ddof=1) / np.sqrt(NCHK)), best_chk=best2,
                    ev_chk={c: round(ev2[c], 4) for c in top})
        print(hs, T, "done", flush=True)
json.dump(res, open(out_path, "w"), indent=0)
