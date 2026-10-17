import sys, json; sys.path[:0]=["mozingo","spirit_hollow"]
import numpy as np, course, tee_strategy as t, wind_grid as W, yardage_book as yb
from matplotlib.path import Path
W.set_prior_means()
G=json.load(open("spirit_hollow/output/wind_grid.json"))["holes"]
PEN={"recovery","native","water","ob","sand"}
def lie_at(hd, pts):
    lie=np.array(["rough"]*len(pts),dtype=object)
    for n,p in hd["zones"]: lie[Path(p).contains_points(pts)]=n
    return lie
bad=0
for h,hd in course.HOLES.items():
    tee,f,r,ppy=t.hole_frame(hd)
    for c,v in G[str(h)]["0_0"]["clubs"].items():
        _,lie,_,_=t.simulate(h,c,v["aim"]); mp=np.mean([l in PEN for l in lie])
        cl=yb.shot_cloud(h,c,v["aim"])
        E=[]
        for q in np.sqrt(np.linspace(0,1,30)):
            for a in np.linspace(0,2*np.pi,120):
                al,la=yb.cloud_point(dict(cl,axes=(cl["axes"][0]*q,cl["axes"][1]*q)),a); E.append(tee+(al*f+la*r)*ppy)
        dp=np.mean([l in PEN for l in lie_at(hd,np.array(E))])
        fl=abs(mp-dp)>0.08
        bad+=fl
        if fl or h in (17,): print(h,c,v["aim"],"model",round(mp,3),"drawn",round(dp,3),"<==" if fl else "")
print("flagged",bad)
