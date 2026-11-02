import sys, numpy as np, warnings
warnings.simplefilter("ignore")
import s2lib as S2, common
P = np.load(sys.argv[1]); thr = 0.5
for c in sorted({f[:-2] for f in P.files if f.endswith("_g")}):
    g = S2.load_g10(c); pg = P[c + "_g"]
    fw = np.nan_to_num(g["fairway"]) >= 0.7
    el = (np.nan_to_num(g["elig"]) > 0.5) & (np.nan_to_num(g["course"]) > 0.5) & (np.nan_to_num(g["fairway"]) < 0.3)
    rf = el & (np.nan_to_num(g["mown"]) == 0) & (np.nan_to_num(g["canopy"]) < 0.05) & (g["dfw_mean"] >= 5) & (g["dfw_mean"] <= 25)
    far = el & (g["dfw_mean"] > 40) & (np.nan_to_num(g["canopy"]) < 0.05)
    d = common.load(c); cell = S2.map_1m(d["idx"], g)
    nat = np.zeros(pg.size, bool); u, n = np.unique(cell[d["cls"] == 4], return_counts=True); nat[u[n >= 50]] = True; nat = nat.reshape(pg.shape)
    print(f"{c:22s} P>=.5: rf-band {np.mean(pg[rf] >= thr):.2f} far {np.mean(pg[far] >= thr):.2f} all-elig {np.mean(pg[el] >= thr):.2f} | "
          f"P median rf {np.median(pg[rf]):.2f} far {np.median(pg[far]):.2f} | truth native share of rf {np.mean(nat[rf]):.2f} | elig ha {el.sum()/100:.1f}")
