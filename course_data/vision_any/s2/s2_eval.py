"""Corridor pixel precision / recall / IoU (1 m, landing corridors 180-320 yds +/-50) and corridor-side native extent.
python3 s2_eval.py pred_X.npz thr,... [--json out.json]
Modes: 'pix' = P >= thr per cell; 'ext' = per hole side, native = every cell >= N yds off the OSM fairway, with
N = argmax_N sum_{cells >= N}(P - thr) (none if the max is <= 0): the "native starts N yds off, this side" layer.
Side truth: hand native >= 250 m2 on that side of the landing corridor; start = 10th pct of its distance to fairway."""
import sys, json, numpy as np
import s2lib as S2, common
YD = 0.9144
P = np.load(sys.argv[1]); thrs = [float(t) for t in sys.argv[2].split(",")]
jout = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
COURSES = [c for c in S2.COURSES if c + "_p" in P.files]
NAT = {"gateway_national", "spirit_hollow", "coldwater", "ellis", "mozingo", "annbriar"}
MIN_AREA = 250


def ext_fill(dyd, p, thr):
    o = np.argsort(-dyd); s = np.cumsum((p - thr)[o])            # cells sorted far -> near: prefix = "beyond N"
    k = int(np.argmax(s))
    if s[k] <= 0: return np.zeros(len(p), bool), None
    m = np.zeros(len(p), bool); m[o[:k + 1]] = True
    return m, float(dyd[o[k]])


def evaluate(mode, thr):
    rows, sides = {}, []
    for c in COURSES:
        d = common.load(c); p = P[c + "_p"]
        dyd = d["X"][:, list(d["names"]).index("d_fairway")] / YD
        cor = (d["along"] >= 180) & (d["along"] <= 320) & (np.abs(d["lat"]) <= 50)
        lab = np.isin(d["cls"], [S2.NATIVE, S2.ROUGH, S2.FC])
        pred = np.zeros(len(p), bool)
        for ref in np.unique(d["ref"]):
            for sgn in (-1, 1):
                m = cor & (d["ref"] == ref) & (np.sign(d["lat"]) == sgn) & lab
                if m.sum() < 500: continue
                j = np.flatnonzero(m)
                if mode == "pix":
                    pm = p[j] >= thr; st = None
                else:
                    pm, st = ext_fill(dyd[j], p[j], thr)
                pred[j] |= pm
                tn = d["cls"][j] == S2.NATIVE
                tpres = tn.sum() >= MIN_AREA; ppres = pm.sum() >= MIN_AREA
                ts = float(np.percentile(dyd[j][tn], 10)) if tpres else None
                ps = (float(np.percentile(dyd[j][pm], 10)) if ppres else None)
                sides.append(dict(course=c, ref=str(ref), side="R" if sgn > 0 else "L", truth=tpres, pred=ppres,
                                  t_start=ts, p_start=ps, t_area=int(tn.sum()), p_area=int(pm.sum()),
                                  inter=int((tn & pm).sum())))
        y = (d["cls"] == S2.NATIVE)[cor & lab]; pr = pred[cor & lab]
        tp, fp, fn = int((y & pr).sum()), int((~y & pr).sum()), int((y & ~pr).sum())
        rows[c] = dict(tp=tp, fp=fp, fn=fn, prec=tp / max(tp + fp, 1), rec=tp / max(tp + fn, 1), iou=tp / max(tp + fp + fn, 1),
                       pred_m2=tp + fp, truth_m2=tp + fn)
    TP = sum(r["tp"] for r in rows.values()); FP = sum(r["fp"] for r in rows.values()); FN = sum(r["fn"] for r in rows.values())
    pooled = dict(prec=TP / max(TP + FP, 1), rec=TP / max(TP + FN, 1), iou=TP / max(TP + FP + FN, 1),
                  fp_no_native=sum(r["fp"] for c, r in rows.items() if c not in NAT))
    st = [s for s in sides if s["truth"] and s["pred"]]
    err = [abs(s["p_start"] - s["t_start"]) for s in st]
    sd = dict(n_sides=len(sides), truth_sides=sum(s["truth"] for s in sides), pred_sides=sum(s["pred"] for s in sides),
              tp_sides=len(st), fp_sides=sum(s["pred"] and not s["truth"] for s in sides),
              fn_sides=sum(s["truth"] and not s["pred"] for s in sides),
              start_err_med_yd=float(np.median(err)) if err else None, start_err_p75_yd=float(np.percentile(err, 75)) if err else None,
              start_bias_med_yd=float(np.median([s["p_start"] - s["t_start"] for s in st])) if st else None,
              side_area_iou_tp=float(np.mean([s["inter"] / max(s["t_area"] + s["p_area"] - s["inter"], 1) for s in st])) if st else None)
    return rows, pooled, sd, sides


res = {}
for mode in ("pix", "ext"):
    for thr in thrs:
        rows, pooled, sd, sides = evaluate(mode, thr)
        res[f"{mode}_{thr}"] = dict(rows=rows, pooled=pooled, sides=sd, side_rows=sides)
        print(f"== {sys.argv[1]} {mode} thr {thr}: pooled prec {pooled['prec']:.2f} rec {pooled['rec']:.2f} iou {pooled['iou']:.2f}"
              f" | FP on no-native courses {pooled['fp_no_native']} m2 | sides truth {sd['truth_sides']} pred {sd['pred_sides']}"
              f" tp {sd['tp_sides']} fp {sd['fp_sides']} fn {sd['fn_sides']} start err med {sd['start_err_med_yd']} p75 {sd['start_err_p75_yd']}"
              f" bias {sd['start_bias_med_yd']}")
        if "-v" in sys.argv:
            for c, r in rows.items():
                print(f"   {c:22s} prec {r['prec']:.2f} rec {r['rec']:.2f} iou {r['iou']:.2f} pred {r['pred_m2']:7d} truth {r['truth_m2']:7d}")
if jout: json.dump(res, open(jout, "w"), default=float)
