"""summ3.py OOF.json [TEST.json]: holes right / all-right on train+big, choice (not never-used), never-used, test"""
import json, os, sys
new = set(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "never_used.txt")).read().strip().split(","))  # the 200 never-used courses
def agg(rs):
    H = sum(r["n_true"] for r in rs); ok = sum(sum(r.get("hole_ok", {}).values()) for r in rs)
    al = sum(bool((r.get("score") or {}).get("all_correct")) for r in rs)
    return f"{len(rs)}: {100*ok/max(H,1):.2f} % / {al}"
rs = json.load(open(sys.argv[1]))["courses"]
print("train+big", agg(rs), "| choice", agg([r for r in rs if r["slug"] not in new]), "| never-used", agg([r for r in rs if r["slug"] in new]))
if len(sys.argv) > 2:
    print("test", agg(json.load(open(sys.argv[2]))["courses"]))
