"""panel.py hole a0 a1 [latmin latmax] [which] [ppy] -> panel_HH_a0_a1.jpg : RGB+outlines | CIR raw"""
import sys, os, importlib.util
import numpy as np, cv2
ROOT="/home/user/my_golf_data_science"
sys.path.insert(0, ROOT+"/course_data/imagery")
import render as R
from PIL import Image, ImageDraw
k=int(sys.argv[1]); a0=float(sys.argv[2]); a1=float(sys.argv[3])
l0=float(sys.argv[4]) if len(sys.argv)>4 else -60; l1=float(sys.argv[5]) if len(sys.argv)>5 else 60
which=sys.argv[6] if len(sys.argv)>6 else "truth"; ppy=float(sys.argv[7]) if len(sys.argv)>7 else 5.0
spec=importlib.util.spec_from_file_location("c",f"{ROOT}/course_data/courses/gateway_national/{which}/course.py");C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
img=R.Imagery(ROOT+"/course_data/packages/gateway_national/imagery")
f0=C.FRAMES[k]; hd=C.HOLES.get(k) or C.PAR3[k]
W=int((l1-l0)*ppy); H=int((a1-a0)*ppy)
tee_px=(-l0*ppy, a1*ppy)
fr=R.Frame(f0["tee_ll"], f0["aim_ll"], ppy=ppy, tee_px=tee_px, proj=f0.get("proj","enu"), size=(W,H))
rgb,_=R.render(fr,img,interp=cv2.INTER_CUBIC); rgb=rgb[...,:3]
nir,_=R.render(fr,img,nir=True,interp=cv2.INTER_CUBIC)
nir=nir[...,0] if nir.ndim==3 else nir
cir=np.dstack([nir,rgb[...,0],rgb[...,1]])
def conv(p):
    al=(f0["tee_px"][1]-p[1])/f0["ppy"]; la=(p[0]-f0["tee_px"][0])/f0["ppy"]
    return (tee_px[0]+la*ppy, tee_px[1]-al*ppy)
COL={"fairway":(0,255,0),"rough":(255,255,255),"recovery":(0,120,0),"native":(255,180,0),"water":(0,160,255),"sand":(255,90,200),"ob":(255,0,0),"green":(0,255,255)}
def deco(arr, outlines):
    im=Image.fromarray(arr.astype(np.uint8)); d=ImageDraw.Draw(im)
    if outlines:
        for name,poly in hd["zones"]:
            if len(poly)>=3 and name in COL and name!="rough":
                pts=[conv(p) for p in poly]; d.line(pts+[pts[0]],fill=COL[name],width=1)
    for a in range(int(np.ceil(a0/10)*10), int(a1)+1, 10):
        y=tee_px[1]-a*ppy; big=a%50==0
        d.line([(0,y),(8 if not big else 16,y)],fill=(255,0,255),width=1)
        if a%20==0: d.text((18,y-5),str(a),fill=(255,255,0))
    for l in range(int(np.ceil(l0/10)*10), int(l1)+1, 10):
        x=tee_px[0]+l*ppy
        d.line([(x,H-1),(x,H-(8 if l%50 else 16))],fill=(255,0,255),width=1)
        d.text((x-8,H-22),str(l),fill=(255,255,0))
    return im
MARK=[]
import json
try:
    d=json.load(open('v5.json'))[("Back" if which=="truth" else "Middle")+"_d0"]
    r=[x for x in d if x['key']==str(k)][0]
    if r['kind']=='tee':
        import re as _re
        m=_re.match(r"Aim (?:on the line|(\d+) yds (left|right)) · (\d+) total", r['topKey'])
        aim=0 if not m.group(1) else float(m.group(1))*(-1 if m.group(2)=='left' else 1)
        row=[x for x in r['rows'] if x.startswith('●')][0].split('|')
        MARK=[(float(m.group(3)), aim+r['drift'], float(row[4]), float(row[1]))]
except Exception as e: print('nomark',e)
A=deco(rgb,True)
try:
    import json as _j
    PKG=_j.load(open(ROOT+f"/course_data/courses/gateway_national/{which}/package.json"))
    hh=PKG["holes"]; hh=hh.get(str(k)) if isinstance(hh,dict) else [x for x in hh if str(x.get("number",x.get("hole")))==str(k)][0]
    gp=np.asarray(hh["green_polygon_ll"],float); px=fr.ll_to_px(gp)
    ImageDraw.Draw(A).line([tuple(p) for p in px]+[tuple(px[0])],fill=(0,255,255),width=1)
except Exception as e: print('nogreen',repr(e))
dA=ImageDraw.Draw(A)
for tot,lat,wid,car in MARK:
    x=tee_px[0]+lat*ppy; y=tee_px[1]-tot*ppy
    dA.ellipse([x-wid/2*ppy,y-wid*0.22*ppy,x+wid/2*ppy,y+wid*0.22*ppy],outline=(255,255,0))
    dA.ellipse([x-3,y-3,x+3,y+3],fill=(255,0,0))
    yc=tee_px[1]-car*ppy; dA.line([(x-20,yc),(x+20,yc)],fill=(255,255,0)); B=deco(cir,False)
import pyproj
from scipy.ndimage import map_coordinates
nd=np.load('s2/ndvi_nov26.npy'); bb=np.load('s2/n26a.npz')["bounds"]
xx,yy=np.meshgrid(np.arange(W)+.5,np.arange(H)+.5)
ll=fr.px_to_ll(np.column_stack([xx.ravel(),yy.ravel()]))
ux,uy=pyproj.Transformer.from_crs(4326,32615,always_xy=True).transform(ll[:,0],ll[:,1])
col=(np.asarray(ux)-bb[0])/10-.5; row=(bb[3]-np.asarray(uy))/10-.5
v=map_coordinates(nd,[row,col],order=int(os.environ.get("S2ORD","1")),mode="nearest").reshape(H,W)
t=np.clip((v-0.45)/(0.90-0.45),0,1)
cm=np.dstack([255*(1-t)+40*t, 120*(1-t)+200*t+0*t, 40*(1-t)+60*t]).astype(np.uint8)
# contour lines at 0.70
Cn=deco(cm,True)
if os.environ.get("NOCIR"):
    out=Image.new("RGB",(W*2+6,H),(0,0,0)); out.paste(A,(0,0)); out.paste(Cn,(W+6,0))
else:
    out=Image.new("RGB",(W*3+12,H),(0,0,0)); out.paste(A,(0,0)); out.paste(B,(W+6,0)); out.paste(Cn,(2*W+12,0))
fn=f"panel_{which}_{k:02d}_{int(a0)}_{int(a1)}.jpg"; out.save(fn,quality=90); print(fn,out.size)
