import json, os, sys
W, S = sys.argv[1], sys.argv[2]
E = os.path.join(W, "course_data", "courses", "eagle_knoll")
def put(which, hole, rec, note):
    p = os.path.join(E, which, "v2", "v2_decisions.json")
    d = json.load(open(p))
    old = d.get(hole, {})
    for k in ("ladder", "sens", "width_sweep", "width_flips"):     # old-engine extras: not valid for the new pick
        rec.pop(k, None)
    rec["replaced"] = note + f" (was {old.get('pick')} {old.get('aim')})"
    d[hole] = rec
    json.dump(d, open(p, "w"), indent=1, default=float)
    print(which, hole, old.get("pick"), old.get("aim"), "->", rec["pick"], rec["aim"], "m=%.4f se=%.4f" % (rec["margin"], rec["margin_se"]))
for which, hole, f in [("truth", "14", "qd_truth_14.json"), ("truth", "9", "qd_truth_9.json"),
                       ("truth_eagle", "9", "qd_truth_eagle_9.json"), ("truth_middle", "9", "qd_truth_middle_9.json")]:
    fp = os.path.join(S, f)
    if os.path.exists(fp):
        rec = json.load(open(fp))[hole]
        put(which, hole, rec, "2026-11-06 local re-solve (OPTIMIZE.md 12)")
        if which == "truth" and hole == "14":
            put("truth_eagle", "14", json.loads(json.dumps(rec)), "2026-11-06: Back 14 result, the same box (OPTIMIZE.md 12)")
