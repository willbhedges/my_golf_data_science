import json, os, sys, pickle, warnings
warnings.filterwarnings("ignore")
import numpy as np
WT = "/home/user/my_golf_data_science"; CD = os.path.join(WT, "course_data")
for p in ("mapper", "product", "platform"): sys.path.insert(0, os.path.join(CD, p))
import native_auto as NA, mowing_line as ML, mow_self as MS
EV = json.load(open(os.path.join(CD, "mapper", "eval_native_auto.json")))["courses"]
PAR = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
for slug in sys.argv[1].split(","):
    e = EV[slug]; sides = NA.sides_from_p(e["p"], e["thr"]); G = pickle.load(open(f"mow/{slug}.pkl", "rb"))["holes"]
    for ref, ss in sides.items():
        if ref not in G or "foot" not in G[ref]: continue
        g = G[ref]; f, m = ML.features(g); sh = g["shape"]; X = np.tile(ML.XS, (sh[0], 1)); A = np.repeat(ML.AS, sh[1]).reshape(sh); d = m["d"]
        for s in ss:
            p, sep = MS.side_score(g, f, m, s, params=PAR, ret_sep=True); ln = ML.detect(g, p, s, m, PAR)
            sm = ((X < 0) if s == "L" else (X > 0)) & g["foot"].reshape(sh) & (d > 0) & m["open"] & (A >= 150) & (A <= 345)
            tn = g["t_native"].reshape(sh) & sm; en = []; dts = []
            for a0 in np.arange(150, 345, 5):
                q = tn & (A >= a0) & (A < a0 + 5)
                if q.sum() < 10: continue
                dt = np.percentile(d[q], 5); jj = int((a0 + 2.5 - ML.AS[0]) // ML.STEP_A); v = ln["e"][jj]
                en.append((v if v is not None else 50) - dt); dts.append(dt)
            ev = [v for v in ln["e"] if v is not None]
            print(f"{slug[:8]} {ref:>2}{s} p {e['p'][ref][s]:.2f} truth_native_cells {int(tn.sum()):5d} sep {sep:6.1f} line med {np.median(ev) if ev else -1:5.1f} none {len(ln['e'])-len(ev):2d} | truth edge med {np.median(dts) if dts else -1:5.1f}  err new med {np.median(en) if en else 0:+6.1f} old {10-np.median(dts) if dts else 0:+6.1f}")
