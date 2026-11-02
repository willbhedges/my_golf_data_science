"""python3 loco.py <featset> [drop,feats]"""
import numpy as np, sys
import model_lib as ML
from common import *
FS = sys.argv[1]
if len(sys.argv) > 2: ML.DROP.update(sys.argv[2].split(","))
out = {}
for test in COURSES:
    clf, N = ML.fit_loco(FS, test)
    D = ML.course(FS, test)
    out[test + "_p"] = clf.predict_proba(D["X"])[:, 1].astype(np.float32)
    out[test + "_pc"] = clf.predict_proba(D["Xc"])[:, 1].astype(np.float32)
    if test == COURSES[0]:
        imp = sorted(zip(clf.booster_.feature_importance("gain"), N), reverse=True)[:20]
        print("top gain:", ", ".join(f"{n}" for _, n in imp), flush=True)
np.savez_compressed(f"pred_{FS}{'_d' if len(sys.argv) > 2 else ''}.npz", **out)
print("saved")
