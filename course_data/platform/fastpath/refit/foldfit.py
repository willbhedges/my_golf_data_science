"""route_learn fold models (same folds as route_learn cv): foldfit.py OUT_DIR -> fold_<i>.pkl + folds.json {slug: i}"""
import os, sys, pickle, json
FP = os.environ["FP"]; sys.path[:0] = [FP, os.path.dirname(FP)]
import route_learn as RL
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
ts = RL.load_tables(RL.TRAIN)
states = sorted({t["state"] for t in ts}); fold = {s: i % 5 for i, s in enumerate(states)}
json.dump({t["slug"]: fold[t["state"]] for t in ts}, open(os.path.join(out, "folds.json"), "w"))
for i in range(5):
    tr = [t for t in ts if fold[t["state"]] != i]
    ms = {kind: RL._fit(tr, kind) for kind in RL.KINDS}
    pickle.dump(dict(models=ms, XF=RL.XF, WXF=RL.WXF, n_train=len(tr), x3=RL.X3,
                     **(dict(XF3=RL.XF3, WXF3=RL.WXF3, LXF3=RL.LXF3) if RL.X3 else {})), open(os.path.join(out, "fold_%d.pkl" % i), "wb"))
    print("fold", i, len(tr), flush=True)
