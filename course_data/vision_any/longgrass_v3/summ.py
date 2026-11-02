import json, sys, os
SEV = ["blue_hills","eagle_knoll","gateway_national","hot_springs_arlington","pine_dunes","veenker","coldwater"]
ctl = json.load(open(os.path.join(os.environ["WT"], "course_data/platform/error_budget_longgrass_variants.json")))["variants"]["control"]
for f in sys.argv[1:]:
    R = json.load(open(f)); tm = tr = cm = cr = 0
    print("==", f)
    for s in SEV + ["ellis", "spirit_hollow"]:
        if s not in R: continue
        rows = R[s]["rows"]
        m = sum(r["configs"]["auto"]["match"] for r in rows); g = sum(r["configs"]["auto"]["regret"] or 0 for r in rows)
        c = ctl.get(s)
        cs = f"control {c['auto_match']} / {c['auto_regret']:.3f}" if c else ""
        lg = [(r["hole"], r["configs"]["auto"]["match"], c["holes"][str(r["hole"])]["match"] if c else None) for r in rows]
        ch = [f"{h}:{'+' if a else '-'}" for h, a, b in lg if b is not None and a != b]
        print(f"  {s:22s} match {m}/{len(rows)} regret {g:.3f}   {cs}  changed {ch}")
        if s in SEV: tm += m; tr += g; cm += c["auto_match"]; cr += c["auto_regret"]
    print(f"  7 courses: match {tm} regret {tr:.3f}   control {cm} / {cr:.3f}")
