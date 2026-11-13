"""Compact matrix of a results json: rows = variants, columns = holes; cell = club initial + aim + margin(x1000)."""
import json, sys
SH = {"Driver": "D", "2-wood": "2w", "4-wood": "4w", "Long iron": "LI", "Mid iron": "MI", "8-iron": "8i"}
d = {}
for f in sys.argv[1:]:
    d.update(json.load(open(f)))
holes = sorted(d, key=int)
names = list(d[holes[0]])
print("%-34s" % "variant" + "".join("%-13s" % ("h" + h) for h in holes))
for n in names:
    row = "%-34s" % n[:33]
    for h in holes:
        r = d[h].get(n)
        if r is None:
            row += "%-13s" % "-"
            continue
        b = d[h]["central"] if "central" in d[h] else d[h][names[0]]
        flag = "*" if r["pick"] != b["pick"] else ("'" if abs(r["aim"] - b["aim"]) >= 2 else " ")
        row += "%-13s" % ("%s%s%+.0f %d/%s" % (flag, SH[r["pick"]], r["aim"], round(r["margin"] * 1000), SH[r["runner"]]))
    print(row)
