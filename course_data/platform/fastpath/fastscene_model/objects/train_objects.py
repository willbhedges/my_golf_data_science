import sys, os, json, pickle, numpy as np
sys.path.insert(0, '/home/user/my_golf_data_science/course_data/perception')
import train as TRN
val = set(open('/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/perc/val.txt').read().split())
tabs = TRN.load_tables('/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/perc/tables')
for t in tabs: t['meta']['slug'] = os.path.basename(t['dir'])
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
allin = len(sys.argv) > 2
trt = [t for t in tabs if allin or t['meta']['slug'] not in val]; tet = [t for t in tabs if not allin and t['meta']['slug'] in val]
res = {}
for name in ('green', 'tee_box', 'tee_complex'):
    tr = [r for t in trt for r in t.get(name, [])]; te = [r for t in tet for r in t.get(name, [])]
    feats = sorted({k for r in tr for k in r if k not in ('y', 'g')})
    X, y = TRN._xy(tr, feats)
    keep = [j for j in range(len(feats)) if len(np.unique(X[:, j][np.isfinite(X[:, j])])) >= 2]
    feats = [feats[j] for j in keep]
    X, y = TRN._xy(tr, feats)
    clf = TRN.fit(X, y, balanced=False)
    thr = TRN.oof_threshold(trt, name, feats, beta=1.5) if name.startswith('tee') else None
    r = dict(features=feats, n_train=len(tr), n_test=len(te), thr=thr, train_courses=len(trt))
    if te:
        Xt, yt = TRN._xy(te, feats); r['test'] = TRN._metrics(clf, Xt, yt, thr)
    res[name] = r
    pickle.dump(dict(clf=clf, features=feats, thr=thr), open(os.path.join(out, name + '.pkl'), 'wb'))
    print(name, json.dumps({k: r.get(k) for k in ('n_train', 'n_test', 'thr', 'test')})[:500])
json.dump(res, open(os.path.join(out, 'objects.json'), 'w'), indent=1, default=str)
