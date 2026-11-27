"""Gate 1 for the learned hole field: the same network and evaluation as holefield_gate0.py, but its input is what a
photo-only course gives: the U-Net's P(green) and P(tee) (cache big/probs/<slug>/d0+yall.npz, 1 m, the scene's UTM
grid) and the corridor maps route_learn reads (big/maps/<slug>.npz: fair, bunker, water, tree, turf), block-averaged
to RES m.
Labels: the mapped hole lines (benchdata). Test fold: crc32(slug) % 5 == FOLD.

Evaluation on the test fold, tee candidates = every mapped hole start + every tee complex the scene detected:
  top1 / assign as gate 0; then per hole against the scene router on photos alone (pair_v3 arm A): the owner of the
  router's tee against the owner of the field's best tee for the green the router chose (as gate 0b).
Usage: python3 holefield_gate1.py OUT_DIR [epochs] [fold]     (inputs under $FASTPATH_CACHE or cache/v2root)
       python3 holefield_gate1.py --selftest ROOT             (no torch; ROOT holds big/probs, big/scenes, big/maps)
"""
import glob
import gzip
import json
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import holefield_gate0 as G0  # noqa: E402

FP = os.path.dirname(HERE)
ART = os.path.join(os.path.dirname(os.path.dirname(FP)), "research", "artifacts", "pair_v3")
MAPS = ["fair", "bunker", "water", "tree", "turf"]
G0.KINDS = ["green", "tee"] + MAPS                                       # the network's input channels here


def load(slug, root):
    """gate 0's course dict with x from the detector's maps; + tees += the scene's tee complexes; None when the
    course has no cached inputs or does not fit the canvas"""
    from pyproj import Transformer
    pp = os.path.join(root, "big", "probs", slug, "d0+yall.npz")
    sp = os.path.join(root, "big", "scenes", slug + ".json.gz")
    if not (os.path.exists(pp) and os.path.exists(sp)):
        return None
    keep = G0.KINDS
    G0.KINDS = ["green", "tee", "fairway", "bunker", "water"]            # gate 0's rasteriser: labels + truth layout
    try:
        c = G0.load(slug)
    finally:
        G0.KINDS = keep
    if c is None:
        return None
    sc = json.load(gzip.open(sp, "rt"))
    g = sc["grid"]
    P = np.load(pp)["p"].astype(np.float32)[1:3] / 255.0                  # P(green), P(tee): the cached classes
    mp = os.path.join(root, "big", "maps", slug + ".npz")
    if not os.path.exists(mp):
        return None
    z = np.load(mp)
    M = []
    for name in MAPS:                                                    # the corridor maps route_learn reads
        a = z[name].astype(np.float32)
        if a.shape != P.shape[1:]:
            return None
        M.append(a / (255.0 if a.max() > 1 else 1.0))
    P = np.concatenate([P, np.stack(M)])
    k = max(1, int(round(G0.RES / float(g["res_m"]))))
    H, W = (P.shape[1] // k) * k, (P.shape[2] // k) * k
    B = P[:, :H, :W].reshape(P.shape[0], H // k, k, W // k, k).mean((2, 4))
    lon0, lat0, kx, ky = c["origin"]
    S = G0.SIZE
    cc, rr = np.meshgrid(np.arange(S) + 0.5, np.arange(S) + 0.5)
    lon = lon0 + (cc - S / 2) * G0.RES / kx
    lat = lat0 + (S / 2 - rr) * G0.RES / ky
    X, Y = Transformer.from_crs("EPSG:4326", g["crs"], always_xy=True).transform(lon, lat)
    t = g["transform"]
    ci = np.floor((X - t[2]) / (t[0] * k)).astype(int)
    ri = np.floor((Y - t[5]) / (t[4] * k)).astype(int)
    ok = (ci >= 0) & (ci < B.shape[2]) & (ri >= 0) & (ri < B.shape[1])
    x = np.zeros((B.shape[0], S, S), np.float32)
    x[:, ok] = B[:, ri[ok], ci[ok]]
    c["x_truth"] = c["x"]
    c["x"] = x
    c["cover"] = float(ok.mean())

    def px(ll):
        return np.array([(ll[0] - lon0) * kx / G0.RES + S / 2, S / 2 - (ll[1] - lat0) * ky / G0.RES])
    c["px"] = px
    det = [px(tc["centroid"]) for tc in sc.get("tee_complexes") or [] if tc.get("centroid")]
    c["tees_truth"] = c["tees"]
    c["tees"] = [q for q in det if 0 <= q[0] < S and 0 <= q[1] < S]
    return c


def router_lines():
    out = {}
    for f in sorted(glob.glob(os.path.join(ART, "*", "pair-*", "bench_A.json.gz"))):
        for c in json.load(gzip.open(f, "rt"))["courses"]:
            if c.get("lines") and c["slug"] not in out:
                out[c["slug"]] = c
    return out


def against_router(courses, fields):
    RL = router_lines()
    tab = np.zeros((2, 2), int)
    margin = []
    for c, F in zip(courses, fields):
        if c["slug"] not in RL:
            continue
        st = np.array([h[1] for h in c["holes"]])
        gr = np.array([h[2] for h in c["holes"]])
        cand = list(st) + list(c["tees"])

        def owner(t):
            d = [G0._pt_line(t, h[3]) for h in c["holes"]]
            return int(np.argmin(d)) if min(d) * G0.RES <= 40 else -1
        own = np.array([owner(t) for t in cand])
        for ln in RL[c["slug"]]["lines"].values():
            if not ln.get("co"):
                continue
            d = np.hypot(*(gr - c["px"](ln["co"][-1])).T) * G0.RES
            k = int(d.argmin())
            if d[k] > 23:
                continue
            r_ok = owner(c["px"](ln["co"][0])) == k
            sc = np.array([G0.line_score(F, t, gr[k]) for t in cand])
            f_ok = own[int(sc.argmax())] == k
            tab[int(r_ok), int(f_ok)] += 1
            if not r_ok:
                tr = sc[own == k].max() if (own == k).any() else -1.0
                margin.append(float(tr - G0.line_score(F, c["px"](ln["co"][0]), gr[k])))
    m = np.array(margin)
    return dict(holes=int(tab.sum()), router_right=int(tab[1].sum()), field_right=int(tab[:, 1].sum()),
                both_right=int(tab[1, 1]), router_wrong_field_right=int(tab[0, 1]),
                router_right_field_wrong=int(tab[1, 0]), both_wrong=int(tab[0, 0]), n_router_wrong=len(m),
                router_wrong_true_tee_scores_higher=round(float((m > 0).mean()), 4) if len(m) else None)


def main():
    if sys.argv[1] == "--selftest":
        root = sys.argv[2]
        cs = [c for c in (load(s, root) for s in sorted(os.listdir(os.path.join(root, "big", "probs")))) if c]
        for c in cs:
            a, b = c["x"], c["x_truth"]
            iou = [round(float(((a[i] > 0.5) & (b[j] > 0)).sum() / max(((a[i] > 0.5) | (b[j] > 0)).sum(), 1)), 2) for i, j in ((0, 0), (2, 2))]
            print(c["slug"], "cover", round(c["cover"], 2), "x mean", c["x"].mean((1, 2)).round(4).tolist(),
                  "IoU green / fairway vs the mapped layout", iou, "tees detected", len(c["tees"]), "holes", len(c["holes"]))
        print("truth field", G0.evaluate(cs, [c["field"] for c in cs])[0], "router", against_router(cs, [c["field"] for c in cs]))
        return
    out = sys.argv[1]
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    fold = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    root = os.environ.get("FASTPATH_CACHE") or os.path.join(FP, "cache", "v2root")
    os.makedirs(out, exist_ok=True)
    slugs = sorted(os.listdir(G0.BD))
    cs = [c for c in (load(s, root) for s in slugs) if c]
    te = [c for c in cs if zlib.crc32(c["slug"].encode()) % 5 == fold]
    tr = [c for c in cs if zlib.crc32(c["slug"].encode()) % 5 != fold]
    print("courses", len(cs), "of", len(slugs), "train", len(tr), "test", len(te), "fold", fold,
          "cover", round(float(np.mean([c["cover"] for c in cs])), 3), flush=True)
    res = dict(n_train=len(tr), n_test=len(te), fold=fold, truth_field=G0.evaluate(te, [c["field"] for c in te])[0])
    print(json.dumps(res), flush=True)
    F, log = G0.train(tr, te, epochs, out)
    ev, per = G0.evaluate(te, F)
    res.update(learned=ev, router=against_router(te, F), log=log, per_course=per)
    np.savez_compressed(os.path.join(out, "fields_fold%d.npz" % fold),
                        **{c["slug"]: f.astype(np.float16) for c, f in zip(te, F)})
    json.dump(res, open(os.path.join(out, "holefield_gate1.json"), "w"), indent=1)
    print("RESULT", json.dumps({k: res[k] for k in ("n_train", "n_test", "truth_field", "learned", "router")}))


if __name__ == "__main__":
    main()
