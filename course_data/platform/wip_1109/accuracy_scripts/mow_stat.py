import pickle, sys, os, numpy as np, glob
D=sys.argv[1]
for f in sorted(glob.glob(D+"/*.pkl")):
    c=pickle.load(open(f,"rb")); ds=[]; nside=0
    for ref,g in c["holes"].items():
        if "foot" not in g: continue
        sh=g["shape"]; X=np.tile(np.arange(-75,75.01,1.0),(sh[0],1)).ravel(); A=np.repeat(np.arange(130,400.01,1.0),sh[1])
        for s in (-1,1):
            sm=(X*s>0)&g["foot"]&(g["d"]>0)
            tn=sm&g["t_native"]
            if tn.sum()<300: continue
            nside+=1
            for a0 in range(150,345,5):
                m=tn&(A>=a0)&(A<a0+5)
                if m.sum()>=10: ds.append(np.percentile(g["d"][m],5))
    ds=np.array(ds)
    if len(ds): print(f"{c['slug']:20s} sides {nside:2d} slices {len(ds):4d} truth native inner edge d beyond auto mown: p10 {np.percentile(ds,10):5.1f} p25 {np.percentile(ds,25):5.1f} med {np.median(ds):5.1f} p75 {np.percentile(ds,75):5.1f} p90 {np.percentile(ds,90):5.1f}  |d-10|>8: {np.mean(np.abs(ds-10)>8):.2f}")
