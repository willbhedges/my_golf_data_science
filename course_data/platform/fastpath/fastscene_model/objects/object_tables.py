"""Out-of-fold perception object tables for the fastscene object models: model dir + course dirs -> tables/<slug>/"""
import json, os, sys, time, numpy as np
sys.path.insert(0, '/home/user/my_golf_data_science/course_data/platform/fastpath')
import fastscene as FS
FS._perc()
import perceive as PV, evaluate as EV, truth as TR, scene as SC
out = sys.argv[2]
m = FS.load_model(sys.argv[1])
os.environ['FASTSCENE_OBJECT_MODELS'] = '0'
for d in sys.argv[3:]:
    s = os.path.basename(d.rstrip('/'))
    if os.path.exists(os.path.join(out, s, 'objects.json')):
        continue
    t = time.time()
    try:
        fc = json.load(open(d + '/raw/osm.geojson'))
        sc, info = FS.build(d, m, out=False, labels=fc)
        st, D = info['stack'], info['D']
        D['relations'] = sc['relations']['green_to_tee']
        T = TR.Truth(st)
        T.cart_length_m = lambda inside=True: 0.0
        ev = EV.evaluate(st, None, D, T)
        rows = PV.tables(st, D['_layers'], D, T, os.path.join(out, s))
        print(s, {k: len(v) for k, v in rows.items() if isinstance(v, list)}, round(time.time() - t, 1), flush=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(s, 'failed', repr(e)[:200], flush=True)
