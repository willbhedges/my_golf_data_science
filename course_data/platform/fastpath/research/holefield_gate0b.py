"""Gate 0b: does the learned hole field (holefield_gate0.py's weights) fix the tees the scene router gets wrong?

On the gate-0 test fold, for every hole the router (pair_keeposm2 arm A: OSM greens / tees given) routed to a mapped
hole's green: owner of the router's tee (the hole whose line, first 60 %, is nearest within 40 m) against the owner
of the field's best tee for that green among every mapped tee polygon and hole start.
Usage: python3 holefield_gate0b.py OUT_DIR [WEIGHTS.pt]   (default $PREV_DIR/holefield_gate0.pt)"""
import glob
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import holefield_gate0 as G0  # noqa: E402

ART = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "research", "artifacts", "pair_keeposm2")


def router_lines():
    out = {}
    for f in glob.glob(os.path.join(ART, "*", "pair-*", "bench_A.json.gz")):
        for c in json.load(gzip.open(f, "rt"))["courses"]:
            if c.get("lines"):
                out[c["slug"]] = c
    return out


def main():
    import torch
    out = sys.argv[1]
    w = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ["PREV_DIR"], "holefield_gate0.pt")
    os.makedirs(out, exist_ok=True)
    net = G0.build_net()
    net.load_state_dict(torch.load(w, map_location="cpu"))
    net.eval()
    RL = router_lines()
    slugs = [s for s in sorted(os.listdir(G0.BD)) if G0.is_test(s) and s in RL]
    tab = np.zeros((2, 2), int)                                # [router right?][field right?]
    margin = []
    n_c = 0
    for s in slugs:
        c = G0.load(s)
        if c is None:
            continue
        n_c += 1
        lon0, lat0, kx, ky = c["origin"]

        def px(ll, lon0=lon0, lat0=lat0, kx=kx, ky=ky):
            return np.array([(ll[0] - lon0) * kx / G0.RES + G0.SIZE / 2, G0.SIZE / 2 - (ll[1] - lat0) * ky / G0.RES])
        with torch.no_grad():
            o = net(torch.from_numpy(c["x"][None]))[0].numpy()
        F = o[:2] * (1 / (1 + np.exp(-o[2])))[None]
        st = np.array([h[1] for h in c["holes"]])
        gr = np.array([h[2] for h in c["holes"]])
        cand = list(st) + list(c["tees"])

        def owner(t):
            d = [G0._pt_line(t, h[3]) for h in c["holes"]]
            return int(np.argmin(d)) if min(d) * G0.RES <= 40 else -1
        own = np.array([owner(t) for t in cand])
        for ref, ln in RL[s]["lines"].items():
            if not ln.get("co"):
                continue
            g = px(ln["co"][-1])
            d = np.hypot(*(gr - g).T) * G0.RES
            k = int(d.argmin())
            if d[k] > 23:                                      # not a mapped hole's green
                continue
            r_ok = owner(px(ln["co"][0])) == k
            sc = np.array([G0.line_score(F, t, gr[k]) for t in cand])
            f_ok = own[int(sc.argmax())] == k
            tab[int(r_ok), int(f_ok)] += 1
            if not r_ok:
                tr = sc[own == k].max() if (own == k).any() else -1.0
                margin.append(float(tr - G0.line_score(F, px(ln["co"][0]), gr[k])))
    m = np.array(margin)
    res = dict(courses=n_c, holes=int(tab.sum()), router_right=int(tab[1].sum()), field_right=int(tab[:, 1].sum()),
               both_right=int(tab[1, 1]), router_wrong_field_right=int(tab[0, 1]), router_right_field_wrong=int(tab[1, 0]),
               both_wrong=int(tab[0, 0]),
               router_wrong_true_tee_scores_higher_than_routed=round(float((m > 0).mean()), 4) if len(m) else None,
               n_router_wrong=len(m))
    json.dump(res, open(os.path.join(out, "holefield_gate0b.json"), "w"), indent=1)
    print("RESULT", json.dumps(res))


if __name__ == "__main__":
    main()
