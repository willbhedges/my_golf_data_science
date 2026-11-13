import json, numpy as np, pyproj
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import contains_xy
HZ=json.load(open('/home/user/my_golf_data_science/course_data/truth/gateway_national/hand_zones_ll.json'))
tr=pyproj.Transformer.from_crs(4326,32615,always_xy=True)
def P(ll):
    x,y=tr.transform([p[0] for p in ll],[p[1] for p in ll]); pg=Polygon(list(zip(x,y)))
    return pg if pg.is_valid else pg.buffer(0)
Z={}
for ref,h in HZ["holes"].items():
    for i,z in enumerate(h["zones"]):
        if len(z["poly_ll"])>=3: Z.setdefault(z["lie"],[]).append((ref,i,P(z["poly_ll"]),z.get("note","")))
print({k:len(v) for k,v in Z.items()})
def load(tag):
    d=np.load(f's2/{tag}.npz'); b=d["bounds"]; H,W=d["B04"].shape
    xs=b[0]+10*(np.arange(W)+.5); ys=b[3]-10*(np.arange(H)+.5)
    X,Y=np.meshgrid(xs,ys)
    r=d["B04"].astype(float); n=d["B08"].astype(float); g=d["B03"].astype(float); bl=d["B02"].astype(float)
    off=1000.0
    r,n,g,bl=[np.clip(a-off,1,None) for a in (r,n,g,bl)]
    return X,Y,(n-r)/(n+r),r,g,bl,n
fw=unary_union([p for _,_,p,_ in Z["fairway"]]); wat=unary_union([p for _,_,p,_ in Z.get("water",[])]); nat=unary_union([p for _,_,p,_ in Z["native"]])
tre=unary_union([p for _,_,p,_ in Z.get("recovery",[])]); sand=unary_union([p for _,_,p,_ in Z.get("sand",[])])
if __name__=="__main__":
    import sys
    for tag in sys.argv[1:]:
        X,Y,nd,r,g,bl,n=load(tag)
        mfw=contains_xy(fw.buffer(-8),X,Y); mnat=contains_xy(nat.buffer(-7),X,Y)&~contains_xy(fw.buffer(5),X,Y)&~contains_xy(tre.buffer(5),X,Y)&~contains_xy(wat.buffer(8),X,Y)
        allz=unary_union([fw,wat,nat,tre,sand])
        # rough: within 25 m of fairway, outside everything by 7 m
        mro=contains_xy(fw.buffer(22),X,Y)&~contains_xy(allz.buffer(7),X,Y)
        print(tag,"n px fw/rough/native",mfw.sum(),mro.sum(),mnat.sum(), "NDVI fw %.3f rough %.3f native %.3f | sd %.3f %.3f %.3f"%(nd[mfw].mean(),nd[mro].mean(),nd[mnat].mean(),nd[mfw].std(),nd[mro].std(),nd[mnat].std()),
              "| red fw %.0f ro %.0f nat %.0f"%(r[mfw].mean(),r[mro].mean(),r[mnat].mean()))
