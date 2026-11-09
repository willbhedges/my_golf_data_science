"""Reproduce the scoreboard's SH full-mode same-club metric on an arbitrary package file.
usage: run_full.py PACKAGE.json OUT.json [holes,comma]"""
import sys, json, os, time
ROOT = "/home/user/my_golf_data_science"
sys.path.insert(0, os.path.join(ROOT, "course_data", "qa"))
import scoreboard as SB
pkg, out = sys.argv[1], sys.argv[2]
only = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
cfg = dict(SB.COURSES[0]); cfg["package"] = os.path.abspath(pkg)
sets = SB.sh_truth_sets(); final = SB.final_truth()
res = {}
for st in sorted({sets[str(k)] for k in SB.sh_course().HOLES}):
    ks = {str(k).rstrip("BF") for k in SB.sh_course().HOLES if sets[str(k)] == st}
    if only: ks &= only
    if not ks: continue
    t0 = time.time()
    rf, _, sf = SB.product_plan(cfg, st, keys=ks, mode="full", S=64, N=3000)
    print(st, len(rf), "holes", round(time.time() - t0), "s", flush=True)
    res[st] = rf
rows = {}
same = 0; n = 0
for key in SB.sh_course().HOLES:
    key = str(key); st = sets[key]; ref = key.rstrip("BF")
    fr = res.get(st, {}).get(ref)
    if not fr or key not in final: continue
    s, t = SB.agree(fr, final[key]); n += 1; same += s
    rows[key] = dict(pick=fr["pick"], aim=fr["aim"], tie=fr.get("tie"), runner=fr.get("runner"), margin=fr.get("margin"),
                     truth=final[key]["pick"], same=s, regret=SB.regret(fr, final[key]),
                     ev={c: r.get("ev") for c, r in (fr.get("clubs") or {}).items()})
    print(key, st, fr["pick"], round(float(fr["aim"]), 1), "truth", final[key]["pick"], "same" if s else "NO", flush=True)
print("SAME", same, "/", n)
json.dump(dict(same=same, n=n, rows=rows), open(out, "w"), indent=1, default=str)
