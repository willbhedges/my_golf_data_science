"""Train the S2 model on <train> courses, predict <test> courses; merged with an existing LOCO pred file.
python3 s2_apply.py <train,> <test,> <base_pred.npz> <out.npz>"""
import sys, numpy as np
tr, te, base, out = sys.argv[1].split(","), sys.argv[2].split(","), sys.argv[3], sys.argv[4]
sys.argv = [sys.argv[0], "s2", ",".join(tr + te)]
src = open("s2_loco.py").read().split("out = {}")[0]
exec(src)
clf = train_10(tr); res = dict(np.load(base))
for c in te:
    d = course(c); pg = clf.predict_proba(d["G"])[:, 1].astype(np.float32)
    res[c + "_g"] = pg.reshape(int(d["g"]["H"]), int(d["g"]["W"])); res[c + "_p"] = pg[d["cell"]]
np.savez_compressed(out, **res); print("saved", out)
