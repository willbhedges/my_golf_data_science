"""False-native area on a no-native course: per landing corridor (1 m labelled cells, 180-320 yds +/-50) and course-wide
(10 m cells: eligible, on course, not OSM fairway). python3 fp_report.py pred.npz thr slug [slug...]"""
import sys, json, numpy as np
import s2lib as S2, common
P = np.load(sys.argv[1]); thr = float(sys.argv[2]); out = {}
for c in sys.argv[3:]:
    d = common.load(c); p = P[c + "_p"]; g = S2.load_g10(c); pg = P[c + "_g"]
    cor = (d["along"] >= 180) & (d["along"] <= 320) & (np.abs(d["lat"]) <= 50)
    per = {str(r): int(((p >= thr) & cor & (d["ref"] == r)).sum()) for r in sorted(np.unique(d["ref"]), key=lambda x: int(x))}
    el = (np.nan_to_num(g["elig"]) > 0.5) & (np.nan_to_num(g["course"]) > 0.5) & (np.nan_to_num(g["fairway"]) < 0.5)
    cw = int(((pg >= thr) & el).sum()) * 100
    out[c] = dict(corridor_m2=per, corridor_total_m2=sum(per.values()), course_wide_m2=cw, course_elig_m2=int(el.sum()) * 100)
    print(c, "thr", thr, "corridor m2 total", sum(per.values()), {k: v for k, v in per.items() if v}, "| course-wide", cw, "of", int(el.sum()) * 100)
if "--json" in sys.argv: pass
json.dump(out, open(sys.argv[1].replace(".npz", f"_fp{thr}.json"), "w"))
