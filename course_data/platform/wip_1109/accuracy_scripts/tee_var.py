"""Tee positions of every truth course under localizer variants vs the truth tee (scored set)."""
import sys, json, os, warnings, copy, io, contextlib
warnings.filterwarnings("ignore")
CD="/home/user/my_golf_data_science/course_data"
sys.path.insert(0, CD+"/platform")
import rebuild_tees_trees as R, error_budget as E
R._load0=R._load
VARS={"base":dict(joint=False,canopy_w=0.0),"excl":dict(joint=False,canopy_w=0.15),"canopy":dict(joint=False,canopy_w=0.3),"both":dict(joint=True,canopy_w=0.3)}
out={}
for sv in ("v1","v2"):
    for cfg in E.SETS[sv]():
        slug=cfg["slug"]
        pp = os.path.join(E.ROOT, cfg["package"]) if cfg.get("package") else os.path.join(CD, "packages", slug, "package.json")
        pkg=json.load(open(pp)); pd=os.path.dirname(pp)
        try: truth=E.truth_holes(cfg)
        except Exception as ex: print(slug,"truth err",ex); continue
        S=next((k for k in pkg.get("tee_sets",{}) if k.lower()==cfg["tees"].lower()),None)
        res={}
        for name,par in VARS.items():
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    R.tee_positions(pkg,pd,slug,[]) if False else None
                    import importlib
                    PPm=R._load("rtt_platform_package", os.path.join(R.HERE,"package.py"))
                    lz=PPm.load(os.path.join(CD,"tees","localize.py"),"cdp_tee_localize")
                    lz.PARAMS.update(par)
                    R._load=lambda n,p,_m=PPm:_m if n=="rtt_platform_package" else R.__dict__["_load0"](n,p)
                    pos=R.tee_positions(pkg,pd,slug,[])
                    if pos is not None: pos,_=R.guard_positions(pkg,pos)
            except RuntimeError as ex:
                pos=None
            res[name]=pos
        if res["base"] is None: print(slug,"no positions"); continue
        rows={}
        for ref,td in truth.items():
            if not td.get("tee_ll"): continue
            row={}
            for name,pos in res.items():
                r=((pos.get(ref) or {}).get("tees") or {}).get(S) if S else None
                if r is None:
                    t=(pkg["holes"].get(ref,{}).get("tees") or {}).get(S) or {}
                    ll=t.get("tee_ll") or pkg["holes"].get(ref,{}).get("tee_ll")
                    row[name]=dict(err=round(R.hav_yd(ll,td["tee_ll"]),1) if ll else None,kept=True)
                else:
                    row[name]=dict(err=round(R.hav_yd([r["lon"],r["lat"]],td["tee_ll"]),1),tee_id=r.get("tee_id"),p=r.get("p_assign"),method=r.get("method"),blocked=r.get("canopy_blocked_yd"),ll=[r["lon"],r["lat"]])
            row["par"]=td.get("par"); rows[ref]=row
        out[slug]=dict(set=S,rows=rows,
            allsets={name:{ref:{s:(r.get("tee_id"),round(r["lat"],6),round(r["lon"],6)) for s,r in hp["tees"].items()} for ref,hp in pos.items()} for name,pos in res.items() if pos},
            joint={ref:hp.get("joint") for ref,hp in (res["both"] or {}).items() if hp.get("joint")})
        print(slug, {n:sum(1 for r in rows.values() if r[n]["err"] is not None and r[n]["err"]>10) for n in VARS}, len(rows), flush=True)
json.dump(out,open(sys.argv[1],"w"))
