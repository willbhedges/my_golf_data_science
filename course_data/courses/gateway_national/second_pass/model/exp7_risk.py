"""Mean and spread of the tee-shot outcome (expected strokes to go, per swing) for each club at its best aim:
how much variance is there to trade?  python3 exp7_risk.py out.json"""
import json, sys
from harness import *

res = {}
tot = dict(mu=0.0, var=0.0, mu_alt=0.0, var_alt=0.0)
for h in HOLES:
    r = solve(h, keep=True)
    raw = r["raw"]
    row = {}
    for c in r["order"][:4]:
        s = raw[c]["s"]
        lie = raw[c]["lie"]
        pen = float(np.mean(np.isin(lie, [M.CODE["water"], M.CODE["ob"]])) + 0.0)
        row[c] = dict(aim=raw[c]["aim"], mean=float(s.mean()), sd=float(s.std()), p_pen=pen,
                      p_native=float(np.mean(lie == M.CODE["native"])), p_bad=float(np.mean(s > s.mean() + 0.5)))
    res[h] = row
    best = r["order"][0]
    low = min(row, key=lambda c: row[c]["sd"])
    tot["mu"] += row[best]["mean"]; tot["var"] += row[best]["sd"] ** 2
    tot["mu_alt"] += row[low]["mean"]; tot["var_alt"] += row[low]["sd"] ** 2
    print(h, " | ".join("%s %+.1f mean %.3f sd %.3f pen %.3f" % (c, v["aim"], v["mean"], v["sd"], v["p_pen"]) for c, v in row.items()), flush=True)
print("13 tee shots, best club each: mean %.3f, sd of the tee-shot part %.3f | lowest-sd club each: mean %.3f (+%.3f), sd %.3f" % (
    tot["mu"], tot["var"] ** 0.5, tot["mu_alt"], tot["mu_alt"] - tot["mu"], tot["var_alt"] ** 0.5))
json.dump(dict(holes={str(k): v for k, v in res.items()}, total=tot), open(sys.argv[1], "w"), indent=0)
