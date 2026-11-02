"""Corridor precision/recall/IoU per course from LOCO preds (pixel level, unsmoothed). python3 evalp.py pred.npz"""
import numpy as np, sys
from common import *
P = np.load(sys.argv[1])
NAT = ["gateway_national", "spirit_hollow", "coldwater", "ellis", "mozingo"]
print("course".ljust(22), "thr  share_course  corr: prec  rec  iou   pred_m2  truth_m2")
for thr in [float(t) for t in (sys.argv[2] if len(sys.argv) > 2 else "0.5,0.7,0.85").split(",")]:
    TP = FP = FN = 0; FPno = 0
    for c in COURSES:
        d = load(c); p = P[c + "_p"]; pc = P[c + "_pc"]
        cor = (d["along"] >= 180) & (d["along"] <= 320) & (np.abs(d["lat"]) <= 50) & np.isin(d["cls"], [NATIVE, ROUGH, FC])
        y = d["cls"][cor] == NATIVE; pr = p[cor] >= thr
        tp, fp, fn = (y & pr).sum(), (~y & pr).sum(), (y & ~pr).sum()
        TP += tp; FP += fp; FN += fn
        if c not in NAT: FPno += fp
        print(c.ljust(22), thr, " %.3f" % (pc >= thr).mean(), "      %.2f %.2f %.2f %8d %8d" % (tp / max(tp + fp, 1), tp / max(tp + fn, 1), tp / max(tp + fp + fn, 1), tp + fp, tp + fn))
    print("POOLED".ljust(22), thr, "prec %.3f rec %.3f iou %.3f  FP on no-native courses %d m2" % (TP / max(TP + FP, 1), TP / max(TP + FN, 1), TP / max(TP + FP + FN, 1), FPno))
    print()
