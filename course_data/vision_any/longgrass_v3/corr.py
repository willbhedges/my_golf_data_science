import numpy as np, sys
from common import *
from sklearn.metrics import roc_auc_score
P = np.load(sys.argv[1])
rows = []
for c in COURSES:
    d = load(c); p = P[c + "_p"]
    df = d["X"][:, list(d["names"]).index("d_fairway")]
    for r in np.unique(d["ref"]):
        m = (d["ref"] == r) & (d["along"] >= 180) & (d["along"] <= 320) & (np.abs(d["lat"]) <= 50) & np.isin(d["cls"], [NATIVE, ROUGH, FC])
        if m.sum() < 500: continue
        nat = (d["cls"][m] == NATIVE).sum()
        band = m & (df > 5)
        rows.append((c, r, nat, (p[m] >= .5).mean(), np.mean(p[band]) if band.sum() else 0, np.percentile(p[band], 75) if band.sum() else 0, m.sum()))
nat = np.array([x[2] > 250 for x in rows])
for k, nm in [(3, "share P>=.5"), (4, "mean P band"), (5, "p75 band")]:
    v = np.array([x[k] for x in rows]); print(nm, "corridor AUC %.3f" % roc_auc_score(nat, v))
rows.sort(key=lambda x: -x[4])
for x in rows[:45]: print(f"{x[0][:12]:12s} {x[1]:>3s} native_m2 {x[2]:6d} share {x[3]:.3f} meanP {x[4]:.3f} p75 {x[5]:.3f}")
