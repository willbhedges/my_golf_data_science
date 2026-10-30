import json,sys,statistics as st
from geo import *
W=sys.argv[1]
for slug in ['colbert_hills','shoal_creek']:
    T=json.load(open(f'{W}/course_data/zero_tap/truth_sets/{slug}/holes_truth.json'))
    res={}
    for label,fn in [('current','package.json'),('v0_no_vision','package_v0_no_vision.json')]:
        A=json.load(open(f'/home/user/my_golf_data_science/course_data/library/{slug}/{fn}'))
        rows=[];allerr=[];bigs=[]
        for ref,t in T['holes'].items():
            a=A['holes'].get(ref)
            if not a: rows.append(dict(ref=ref,missing=True)); continue
            ge=dist(a['green_ll'],t['green_ll'])
            # routing: nearest truth green to auto green
            near=min(T['holes'],key=lambda r:dist(a['green_ll'],T['holes'][r]['green_ll']))
            te={}
            for s,ll in t['tees'].items():
                at=(a['tees'].get(s) or {}).get('tee_ll')
                te[s]=None if at is None else round(dist(at,ll),1)
                if te[s] is not None:
                    allerr.append(te[s])
                    if te[s]>10: bigs.append(f"{ref} {s} {te[s]:.0f}")
            rows.append(dict(ref=ref,routing_ok=(near==ref and ge<=25),green_err=round(ge,1),par_ok=a['par']==t['par'],auto_par=a['par'],tee_err=te))
        res[label]=dict(rows=rows,n_routing_ok=sum(r.get('routing_ok',0) for r in rows),n_par_ok=sum(r.get('par_ok',0) for r in rows),
            tee_err_median=round(st.median(allerr),1),tee_err_mean=round(st.mean(allerr),1),tee_err_max=max(allerr),n_tee=len(allerr),
            tee_over10=bigs,green_err_max=max(r['green_err'] for r in rows),green_err_median=round(st.median(r['green_err'] for r in rows),1),
            tee_err_by_set={s:round(st.mean([r['tee_err'][s] for r in rows if r['tee_err'].get(s) is not None]),1) for s in T['sets']})
        r=res[label]; print(slug,label,{k:v for k,v in r.items() if k!='rows'})
    json.dump(res,open(f'{W}/course_data/zero_tap/truth_sets/{slug}/eval.json','w'),indent=1)
