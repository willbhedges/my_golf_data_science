import json,sys,math
from PIL import Image,ImageDraw,ImageFont
from geo import *
slug=sys.argv[1]; extra=json.load(open(sys.argv[2])) if len(sys.argv)>2 else {}
P=json.load(open(f'/home/user/my_golf_data_science/course_data/library/{slug}/package.json'))
M=json.load(open(f'meta_{slug}.json')); D=json.load(open(f'{slug}_pgdata.bin'))
base=D['base_set']
COL={'Black/Blue':(0,0,0),'Web':(120,120,120),'Silver':(200,200,200),'Purple':(150,60,200),'White':(255,255,255),'Gold':(230,180,20),'Blue':(40,90,255),'Black':(0,0,0)}
OSMC={'tee':(255,0,255),'green':(0,255,0),'fairway':(0,200,255),'water':(0,0,255),'hole':(255,255,0),'bunker':(255,220,150)}
out=[]
for ref in map(str,range(1,19)):
    m=M.get(f'{ref}_{base}')
    if not m or m['kind']!='tee': continue
    G=Img(m); im=Image.open(m['file']).convert('RGB'); d=ImageDraw.Draw(im)
    h=P['holes'][ref]
    def poly(pts,c,w=2):
        q=[G.ll2px(p) for p in pts]; d.line(q+[q[0]],fill=c,width=w)
    for f in extra.get('features',[]):
        if f['kind'] in OSMC and f.get('near',{}).get(ref,True):
            q=[G.ll2px(p) for p in f['ll']]
            if f['kind']=='hole': d.line(q,fill=OSMC['hole'],width=2); 
            else: d.line(q+([q[0]] if len(q)>2 else []),fill=OSMC[f['kind']],width=2)
            if f['kind'] in('tee','green') and q: d.text((max(q)[0]+3,q[0][1]),f['id'],fill=OSMC[f['kind']])
    ln=[G.ll2px(p) for p in h['hole_line_ll']]; d.line(ln,fill=(255,128,0),width=1)
    for s,t in h['tees'].items():
        if s=='Web': continue
        u,v=G.ll2px(t['tee_ll']); c=COL.get(s,(255,0,0)); d.rectangle([u-5,v-5,u+5,v+5],outline=c,width=2); d.text((u+8,v-6),f"{s[:2]}{t['card_yards']}",fill=c)
    for T in extra.get('truth',{}).get(ref,{}).items():
        s,ll=T; u,v=G.ll2px(ll); c=COL.get(s,(255,0,0)); d.line([u-7,v-7,u+7,v+7],fill=(255,0,0),width=2); d.line([u-7,v+7,u+7,v-7],fill=(255,0,0),width=2); d.text((u-40,v-6),s[:2],fill=(255,0,0))
    # yard ticks every 50 along frame
    for al in range(0,500,50):
        pass
    d.text((5,5),f"{slug} {ref} par{h['par']} {h['yards']}",fill=(255,255,0))
    out.append((ref,im))
# sheets: crop bottom part (tee area) scaled
import os; os.makedirs(f'sheet_{slug}',exist_ok=True)
for ref,im in out: im.save(f'sheet_{slug}/ov{int(ref):02d}.jpg',quality=85)
print(len(out))
