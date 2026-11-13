import requests, json, sys, numpy as np, rasterio, planetary_computer as pc
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
bbox=[-90.158,38.6495,-90.131,38.6685]
def search(dt, cc=10):
    q={"collections":["sentinel-2-l2a"],"bbox":bbox,"datetime":dt,"limit":100,"query":{"eo:cloud_cover":{"lt":cc}}}
    return requests.post("https://planetarycomputer.microsoft.com/api/stac/v1/search",json=q,timeout=60).json()["features"]
def grab(f, tag):
    out={}
    for b in ["B02","B03","B04","B08","B11","SCL"]:
        href=pc.sign(f["assets"][b]["href"])
        with rasterio.open(href) as ds:
            bb=transform_bounds("EPSG:4326",ds.crs,*bbox)
            # snap to 20 m grid
            bb=[np.floor(bb[0]/20)*20,np.floor(bb[1]/20)*20,np.ceil(bb[2]/20)*20,np.ceil(bb[3]/20)*20]
            w=from_bounds(*bb,ds.transform)
            a=ds.read(1,window=w); out[b]=a
            if b=="B02": out["bounds"]=np.array(bb); out["crs"]=str(ds.crs)
    np.savez_compressed(f"s2/{tag}.npz",**out); print(tag,f["id"],out["B02"].shape,out["crs"],(out["SCL"]>=8).mean())
for dt,tag in [(sys.argv[i],sys.argv[i+1]) for i in range(1,len(sys.argv),2)]:
    fs=[f for f in search(dt) if "T15SYC" in f["id"]]
    fs.sort(key=lambda f:f["properties"]["eo:cloud_cover"])
    print(dt,[ (f["id"][11:19],f["properties"]["eo:cloud_cover"]) for f in fs][:12])
    if fs: grab(fs[0],tag)
