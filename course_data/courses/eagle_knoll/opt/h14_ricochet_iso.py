import sys, json, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h14_ricochet as H
N=40000; z=H.M.draws_z(N,123)
TREES=('trees left','trees right','trees behind','trees short')
eg_none=np.full(H.AA.shape,np.nan)
eg,_=H.escape_grid(H.ESC)
out={}
A=np.arange(-6,10.5,1.0)
for name,g in (('ricochet + engine generic punch-out',eg_none),('ricochet + lidar escape (central)',eg)):
    tot,cls,st=H.score_club('4-wood',z,A,H.PHYS,g)
    ev=tot.mean(0); j=int(np.argmin(ev))
    tm,cm,_=H.score_club('Mid iron',z,np.array([8.0]),H.PHYS,g)
    d0=tm[:,0]-tot[:,j]; i5=list(A).index(0.0); i1=list(A).index(1.0)
    dp=tm[:,0]-0.5*(tot[:,i5]+tot[:,i1])
    out[name]=dict(best_aim=float(A[j]),avg=round(float(ev[j]),4),curve={f"{a:+.0f}":round(float(e),4) for a,e in zip(A,ev)},
       margin_vs_mid8=round(float(d0.mean()),4),se=round(float(d0.std()/np.sqrt(N)),4),
       margin_at_aim_0to1=round(float(dp.mean()),4),
       eng_curve={f"{a:+.0f}":round(float(e),4) for a,e in zip(A,1+st['eng_s'].mean(0))},
       outcomes=H.summarize(tot,cls,j), outcomes_aim0=H.summarize(tot,cls,i5))
    print(name,json.dumps(out[name]),flush=True)
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'results','h14_ricochet_iso.json'),'w'),indent=1)
