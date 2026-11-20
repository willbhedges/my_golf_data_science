"""smoke_compare.py REF.json RUN.json: the routing bench smoke's pass test - every course's per-hole result (hole_ok)
and routed lines identical between the two runs. Prints per course; exit 1 on any difference."""
import json, sys
a = {r["slug"]: r for r in json.load(open(sys.argv[1]))["courses"]}
b = {r["slug"]: r for r in json.load(open(sys.argv[2]))["courses"]}
bad = 0
for s in sorted(set(a) | set(b)):
    ra, rb = a.get(s) or {}, b.get(s) or {}
    same_ok = ra.get("hole_ok") == rb.get("hole_ok") and ra.get("hole_ok") is not None
    same_lines = ra.get("lines") == rb.get("lines")
    bad += not (same_ok and same_lines)
    print("%-34s ref %s run %s hole_ok %s lines %s %s" % (s, sum((ra.get("hole_ok") or {}).values()), sum((rb.get("hole_ok") or {}).values()),
          "same" if same_ok else "DIFF", "same" if same_lines else "DIFF", rb.get("error") or ""))
print("PASS" if not bad else "FAIL: %d courses differ" % bad)
sys.exit(1 if bad else 0)
