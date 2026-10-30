import json,math,os,sys
from geo import *
from build import *
W=sys.argv[1]
OV={
 'colbert_hills':{
   ('1','Black/Blue'):([-96.64015989743766,39.21254938780645],'hand: back edge of the back pad (photo); no box further back (cart path / clubhouse). Pad measures ~557 vs card 590: card not reachable on the ground, estimated'),
   ('1','Silver'):([-96.64013790371551,39.21250884088767],'hand: centre of the back pad (photo); measures ~552 vs card 578, estimated (package tee 13 yds behind the pad, in the rough)'),
 },
 'shoal_creek':{}}
EST={'shoal_creek':{('2','Gold'):'walk-back tee, no pad visible behind the Blue box on 2018 NAIP: estimated',
  ('2','White'):'lidar pad on the cart path area: estimated',('2','Blue'):'at the cart-path junction, pad edge: estimated',
  ('4','Gold'):'walk-back tee, pad not distinct on 2018 NAIP: estimated',
  ('5','*'):'par 3, all sets walk-back along the hole line (no OSM pads; photo is green-only): estimated',
  ('6','*'):'no NAIP 2018 coverage on the tee half of 6 (black in the page photo): estimated',
  ('10','Black'):'lidar pad: estimated',('18','White'):'lidar pad, visible small box: kept'},
 'colbert_hills':{('17','Black/Blue'):'lidar pad 19 yds behind the back OSM box (fits card 237; par-3 photo shows the green only): estimated'}}
LINE_FIX={'colbert_hills':{},'shoal_creek':{('6','Blue'):'package tagged tee measured 278 vs card 333 (wrong box): placed on the hole line at card length, estimated',
                         ('12','Black'):'lidar tee measured 177 vs card 166: placed on the hole line at card length, estimated'}}
for slug in ['colbert_hills','shoal_creek']:
    P=json.load(open(f'/home/user/my_golf_data_science/course_data/library/{slug}/package.json'))
    sets=[s for s in P['tee_sets'] if s!='Web']
    out=dict(schema='holes_truth/1',course=P['course']['name'],slug=slug,likely_set=sets[0],key_sets=sets[:2],sets=sets,
        card_source=P['sources']['scorecard'].get('url'),
        source=f'course_data/zero_tap/truth_sets/{slug}/ (truth5 agent, 2026-10-30)',
        imagery=P['imagery'].get('naip_date'),
        method=open(f'method_{slug}.txt').read() if os.path.exists(f'method_{slug}.txt') else '',
        holes={})
    rows=[]
    for ref in map(str,range(1,19)):
        h=P['holes'][ref]; line=h['hole_line_ll']; gp=h.get('green_polygon_ll')
        g=centroid(gp) if gp else h['green_ll']
        tees={};how={};meas_={};conf={}
        for s in sets:
            t=h['tees'][s]; ll=t['tee_ll']; why=f"package tee ({t['method']}/{t.get('tee_source')}) checked on a visible pad in the photo"
            c='pad'
            k=(ref,s)
            if k in OV[slug]: ll,why=OV[slug][k]; c='estimated'
            elif k in LINE_FIX[slug]: ll=on_line_at(h['yards'][s],line,g); why=LINE_FIX[slug][k]; c='estimated'
            else:
                e=EST[slug].get(k) or EST[slug].get((ref,'*'))
                if e: why=e; c='estimated'
                elif h['par']==3: why=f"package tee ({t['method']}/{t.get('tee_source')}) on an OSM pad; par-3 photo shows only the green: pad not seen"; c='osm_pad'
            tees[s]=[round(ll[0],7),round(ll[1],7)]; how[s]=why; conf[s]=c; meas_[s]=round(meas(ll,line,g))
        zones={lie:[z['poly'] for z in h['zones_ll'] if z['lie']==lie and z.get('src')=='osm'] for lie in ['fairway','water','sand']}
        out['holes'][ref]=dict(par=h['par'],card={s:h['yards'][s] for s in sets},tees=tees,tee_how=how,tee_conf=conf,
            green_ll=[round(g[0],7),round(g[1],7)],green_poly_ll=gp,hole_line_ll=line,measured=meas_,
            fairway_ll=zones['fairway'],water_ll=zones['water'],bunker_ll=zones['sand'],
            note='' if gp else 'no OSM green polygon: green centre = OSM hole-line end (estimated)')
        rows.append((ref,h['par'],{s:(h['yards'][s],meas_[s],conf[s]) for s in sets}))
    os.makedirs(f'{W}/course_data/zero_tap/truth_sets/{slug}',exist_ok=True)
    json.dump(out,open(f'{W}/course_data/zero_tap/truth_sets/{slug}/holes_truth.json','w'),indent=1)
    print(slug)
    for r in rows: print(r[0],r[1],' '.join(f"{s[:5]}:{a}/{b}{'*' if c=='estimated' else ''}" for s,(a,b,c) in r[2].items()))
