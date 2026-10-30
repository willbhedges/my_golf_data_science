import json,base64,math,sys,os
YD=1/0.9144
def kx(lat): return 111320*math.cos(math.radians(lat))*YD
KY=110540*YD
def ll2xy(ll,o): return ((ll[0]-o[0])*kx(o[1]),(ll[1]-o[1])*KY)
def xy2ll(x,y,o): return [o[0]+x/kx(o[1]), o[1]+y/KY]
for slug in ['colbert_hills','shoal_creek']:
    D=json.load(open(f'{slug}_pgdata.bin'))
    P=json.load(open(f'/home/user/my_golf_data_science/course_data/library/{slug}/package.json'))
    os.makedirs(f'img_{slug}',exist_ok=True)
    meta={}
    for setname,holes in [(D['base_set'],D['holes'])]+[(k,v) for k,v in D.get('alt',{}).items()]:
        for h in holes:
            if 'img' not in h: continue
            b=base64.b64decode(h['img'].split(',',1)[1])
            fn=f'img_{slug}/h{int(h["key"]):02d}_{setname}.jpg'; open(fn,'wb').write(b)
            ph=P['holes'][h['key']]
            t=ph['tees'].get(setname,{}).get('tee_ll') or ph.get('tee_ll')
            g=ph['green_ll']
            d=ll2xy(g,t); dist=math.hypot(*d); brg=math.degrees(math.atan2(d[0],d[1]))%360
            meta[f'{h["key"]}_{setname}']=dict(file=fn,set=setname,key=h['key'],tee_ll=t,bearing=h['bearing'],w=h['w'],h=h['h'],s=h['s'],x0=h['x0'],y0=h['y0'],tee=h.get("tee"),f=h.get("f"),r=h.get("r"),ppy=h.get("ppy"),kind=h.get("kind"),green=h.get("green"),green_al=h.get('green_al'))
            if setname==D['base_set'] or True:
                print(slug,setname,h['key'],h['kind'] if 'kind' in h else '', 'pkg dist',round(dist,1),'brg',round(brg,1),'page',h.get('green_al'),h['bearing'], h['w'],h['h'])
    json.dump(meta,open(f'meta_{slug}.json','w'))
