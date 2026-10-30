import json,sys,glob
from PIL import Image,ImageDraw
from geo import *
slug=sys.argv[1]
P=json.load(open(f'/home/user/my_golf_data_science/course_data/library/{slug}/package.json'))
M=json.load(open(f'meta_{slug}.json')); D=json.load(open(f'{slug}_pgdata.bin')); base=D['base_set']
tiles=[]
for ref in map(str,range(1,19)):
    m=M.get(f'{ref}_{base}')
    if m['kind']!='tee': continue
    G=Img(m); im=Image.open(f'sheet_{slug}/ov{int(ref):02d}.jpg')
    vs=[G.ll2px(t['tee_ll'])[1] for t in P['holes'][ref]['tees'].values()]
    top=max(0,int(min(vs))-180); bot=min(im.size[1],int(max(vs))+60)
    c=im.crop((0,top,im.size[0],bot)); d=ImageDraw.Draw(c); d.text((5,5),f'H{ref} top={top}',fill=(255,255,0))
    sc=min(1.0,760/c.size[1]); c=c.resize((int(c.size[0]*sc),int(c.size[1]*sc)))
    tiles.append((ref,top,sc,c))
for i in range(0,len(tiles),4):
    grp=tiles[i:i+4]; W=sum(t[3].size[0] for t in grp)+10*len(grp); H=max(t[3].size[1] for t in grp)
    S=Image.new('RGB',(W,H),(40,40,40)); x=0
    for ref,top,sc,c in grp: S.paste(c,(x,0)); x+=c.size[0]+10
    S.save(f'sheet_{slug}/tees_{i//4}.jpg',quality=85); print(f'tees_{i//4}',[(r,t,round(s,2)) for r,t,s,_ in grp])
