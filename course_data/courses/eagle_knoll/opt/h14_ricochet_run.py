"""Back 14 ricochet / escape re-score: central + sensitivities, 40,000 common swings. Writes results/h14_ricochet.json."""
import sys, time, json, copy, numpy as np
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h14_ricochet as H
N=40000; z=H.M.draws_z(N,123)
T0=time.time()
AIMS={'4-wood':np.arange(-6,10.5,1.0),'Mid iron':np.arange(3,12.5,1.0),'8-iron':np.arange(0,10.5,1.0)}
TREES=('trees left','trees right','trees behind','trees short')
def run(ph,esc,k=None,aims=AIMS,full=False):
    k0=H.O['k_per_yd']
    if k is not None: H.O['k_per_yd']=k; ph=dict(ph,k=k)
    eg,_=H.escape_grid(esc)
    res={}
    for c,A in aims.items():
        tot,cls,st=H.score_club(c,z,A,ph,eg)
        j=int(np.argmin(tot.mean(0)))
        res[c]=dict(aims=A,ev=tot.mean(0),j=j,tot=tot[:,j],cls=cls[:,j],eng=1+st['eng_s'].mean(0),
                    eng_j=1+st['eng_s'][:,j],eng_lie=st['eng_lie'][:,j],stop=st['stop'][:,j],
                    summ=H.summarize(tot,cls,j))
    H.O['k_per_yd']=k0
    return res
def margins(res):
    w=res['4-wood']; out={}
    for c in ('Mid iron','8-iron'):
        d=res[c]['tot']-w['tot']
        tw=np.isin(w['cls'],TREES).mean(); tc=np.isin(res[c]['cls'],TREES).mean()
        out[c]=dict(margin=round(float(d.mean()),4),se=round(float(d.std()/np.sqrt(N)),4),
                    breakeven_extra_per_tree_ball=round(float(d.mean()/(tw-tc)),3) if tw>tc else None)
    return out
def brief(res):
    return {c:dict(best_aim=float(r['aims'][r['j']]),avg=round(float(r['tot'].mean()),4),
                   engine_avg_same_aim=round(float(r['eng'][r['j']]),4),
                   tree_share=round(float(np.isin(r['cls'],TREES).mean()),4),
                   tree_avg=round(float(r['tot'][np.isin(r['cls'],TREES)].mean()),3) if np.isin(r['cls'],TREES).any() else None,
                   crown_stop_share=round(float(r['stop'].mean()),4),
                   pond_ricochet_share=round(float((r['cls']=='pond by ricochet').mean()),4),
                   curve={f"{a:+.0f}":round(float(e),4) for a,e in zip(r['aims'],r['ev'])},
                   outcomes=r['summ']) for c,r in res.items()}
out={}
res=run(H.PHYS,H.ESC)
w=res['4-wood']
# ricochet fates of crown-stopped 4-wood balls, and engine-at-same-aim comparison
st=w['stop']
fates={k:round(float((w['cls'][st]==k).mean()),3) for k in np.unique(w['cls'][st])}
# engine (no ricochet, generic punch-out) margin on the same swings
eng_m={c:round(float((res[c]['eng_j']-w['eng_j']).mean()),4) for c in ('Mid iron','8-iron')}
out['central']=dict(clubs=brief(res),margins=margins(res),crown_stopped_4wood_fates=fates,engine_margin_same_aims=eng_m)
print(json.dumps(out['central']['margins']),json.dumps({c:(v['best_aim'],v['avg']) for c,v in out['central']['clubs'].items()}),time.time()-T0,flush=True)
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results','h14_ricochet.json'),'w'),indent=1,default=float)
# break-even: extra cost on every tree finish until lay-up wins
best={c:np.array([res[c]['aims'][res[c]['j']]]) for c in res}
ph0,es0=H.PHYS,H.ESC
SC={
 'retention low (e_n .2, e_t .5)':(dict(ph0,e_n=0.2,e_t=0.5),es0,None),
 'retention high (e_n .6, e_t .85)':(dict(ph0,e_n=0.6,e_t=0.85),es0,None),
 'scatter low (glancing)':(dict(ph0,scatter='low'),es0,None),
 'scatter high (head-on)':(dict(ph0,scatter='high'),es0,None),
 'bank roll: rough mu .2, trees .3':(dict(ph0,mu=dict(ph0['mu'],rough=0.2,trees=0.3)),es0,None),
 'unplayable 0, lost 0':(ph0,dict(es0,p_unp=0.0,p_lost=0.0),None),
 'unplayable .08, lost .05':(ph0,dict(es0,p_unp=0.08,p_lost=0.05),None),
 'escape easy':(ph0,dict(es0,delta=0.0,trunk=0.005,under=0.05,sd_rel=0.15),None),
 'escape hard':(ph0,dict(es0,delta=0.25,trunk=0.04,under=0.2,sd_rel=0.30),None),
 'crown k 0.05':(ph0,es0,0.05),
 'crown k 0.20 (leaf-on)':(ph0,es0,0.20),
 'worst: hard escape + high retention + high scatter + unp .08 / lost .05 + k .2':(dict(ph0,e_n=0.6,e_t=0.85,scatter='high'),dict(es0,delta=0.25,trunk=0.04,under=0.2,sd_rel=0.30,p_unp=0.08,p_lost=0.05),0.20),
}
out['sensitivity']={}
for name,(ph,es,k) in SC.items():
    r=run(ph,es,k)
    out['sensitivity'][name]=dict(margins=margins(r),**{c:dict(aim=float(v['aims'][v['j']]),avg=round(float(v['tot'].mean()),4),
        tree_share=round(float(np.isin(v['cls'],TREES).mean()),4),
        tree_avg=round(float(v['tot'][np.isin(v['cls'],TREES)].mean()),3) if np.isin(v['cls'],TREES).any() else None,
        pond_ricochet=round(float((v['cls']=='pond by ricochet').mean()),4)) for c,v in r.items()})
    print(name,json.dumps(out['sensitivity'][name]),round(time.time()-T0),flush=True)
    json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results','h14_ricochet.json'),'w'),indent=1,default=float)
