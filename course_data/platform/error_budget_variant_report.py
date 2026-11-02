"""Summary of error_budget_variant.py runs: card-course match / regret and long-grass corridor precision."""
import json, sys, os, statistics as st
L = sys.argv.pop(1)
NO_CARD = {"national_kc"}
out = {}
for v in sys.argv[1:]:
    p = os.path.join(L, f"eb_{v}.json")
    if not os.path.exists(p): continue
    R = json.load(open(p))
    rows = [(s, r) for s, c in R.items() if s not in NO_CARD for r in c["rows"]]
    def agg(name):
        return dict(match=sum(r["configs"][name]["match"] for _, r in rows),
                    club=sum(r["configs"][name]["club"] for _, r in rows),
                    regret=round(sum(r["configs"][name]["regret"] or 0 for _, r in rows), 3))
    o = dict(courses=sorted(R), holes=len(rows), auto=agg("auto"), plus_lg=agg("+long_grass"))
    # corridor precision (all 11 incl. national_kc: geometry only)
    cor = []
    for s, c in R.items():
        for r in c["rows"]:
            lg = (r.get("geo") or {}).get("layers", {}).get("long_grass")
            if lg: cor.append((s, r["hole"], lg))
    def stats(sel):
        T = sum(x["truth"] for _, _, x in sel); A = sum(x["auto"] for _, _, x in sel)
        I = sum(x["truth"] - x["missing"] for _, _, x in sel)
        ious = [ (x["truth"]-x["missing"]) / max(x["truth"]+x["extra"],1) for _,_,x in sel]
        return dict(n=len(sel), truth_yd2=T, auto_yd2=A, inter=I, iou=round(I/max(T+A-I,1),3),
                    prec=round(I/max(A,1),3), rec=round(I/max(T,1),3),
                    median_corridor_iou=round(st.median(ious),3) if ious else None,
                    median_abs_area_err=round(st.median([abs(x["auto"]-x["truth"]) for _,_,x in sel])) if sel else None)
    held = [x for x in cor if x[0] != "spirit_hollow"]
    o["corr_native"] = stats([x for x in held if x[2]["truth"] > 300])
    o["corr_none"] = stats([x for x in held if x[2]["truth"] <= 300])
    o["corr_all_heldout"] = stats(held)
    o["corr_sh_insample"] = stats([x for x in cor if x[0] == "spirit_hollow"])
    o["per_course"] = {s: stats([x for x in cor if x[0] == s]) | dict(
        match=sum(r["configs"]["auto"]["match"] for r in R[s]["rows"]), n=len(R[s]["rows"]),
        regret=round(sum(r["configs"]["auto"]["regret"] or 0 for r in R[s]["rows"]), 3)) for s in R}
    o["truth_picks"] = {f"{s}:{r['hole']}": r["truth"]["pick"] for s, r in rows}
    out[v] = o
json.dump(out, open(os.path.join(L, "analysis.json"), "w"), indent=1)
for v, o in out.items():
    print(v, o["holes"], "auto", o["auto"], "+lg", o["plus_lg"])
    for k in ("corr_native", "corr_none", "corr_sh_insample"): print("   ", k, o[k])
