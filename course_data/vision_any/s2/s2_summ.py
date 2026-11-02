"""Summarise s2_eb outputs against the control rebuild. python3 s2_summ.py eb/eb_ctl.json,eb/eb_ctl2.json eb/eb_<v>.json..."""
import json, sys
SEV = ["blue_hills", "eagle_knoll", "gateway_national", "hot_springs_arlington", "pine_dunes", "veenker", "coldwater"]
EXTRA = ["ellis", "spirit_hollow", "annbriar", "amana_colonies"]
ctl = {}
for f in sys.argv[1].split(","):
    try: ctl.update(json.load(open(f)))
    except OSError: pass
def stat(R, s):
    if s not in R: return None
    rows = R[s]["rows"]
    return (sum(r["configs"]["auto"]["match"] for r in rows), sum(r["configs"]["auto"]["regret"] or 0 for r in rows), len(rows),
            {r["hole"]: r["configs"]["auto"]["match"] for r in rows})
out = {}
for f in ["control"] + sys.argv[2:]:
    R = ctl if f == "control" else json.load(open(f))
    tm = tr = 0; ok = True; line = []
    for s in SEV + EXTRA:
        a = stat(R, s); c = stat(ctl, s)
        if a is None: line.append(f"{s}: -"); ok = ok and s not in SEV; continue
        ch = [f"{h}{'+' if a[3][h] else '-'}" for h in a[3] if c and h in c[3] and a[3][h] != c[3][h]]
        line.append(f"{s}: {a[0]}/{a[2]} {a[1]:.3f} {' '.join(ch)}")
        if s in SEV: tm += a[0]; tr += a[1]
    print(f"== {f}: 7 courses match {tm} regret {tr:.3f}{'' if ok else ' (incomplete)'}")
    for l in line: print("   ", l)
