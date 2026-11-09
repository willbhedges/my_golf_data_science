"""joint routing: choose the solver weights on DEV only (local-model scores are out-of-fold), greedy coordinate search.

    python course_data/zero_tap/joint/tune.py --cache CACHE --source scene --card 1 [--rounds 1]

Objective: holes numbered right + 0.5 * courses fully right (quick label check). Writes joint/params.json.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import run as R  # noqa: E402

GRID = [("w_c", [0.5, 1.0, 1.5, 2.5]), ("w_w", [0.5, 1.0, 1.5]), ("w_h", [0.5, 1.0, 1.5]), ("w_s", [0.5, 1.0, 2.0]),
        ("w_x", [0.0, 1.5, 3.0]), ("c_vt", [4.0, 5.5, 7.5]), ("c_miss", [8.0, 11.0, 15.0]),
        ("w_dg", [0.0, 0.5, 1.0]), ("w_dt", [0.0, 0.25, 0.6]), ("card_s", [6.0, 9.0, 14.0]),
        ("set_slack", [0.0, 12.0, 30.0]), ("c_nowalk", [6.0, 9.0, 12.0])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--source", default="scene")
    ap.add_argument("--card", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    dev, _ = R.get_scored(a.cache, a.source)
    ds = [d for d in dev if d["card"]] if a.card else dev
    key = "%s_%s" % (a.source, "card" if a.card else "nocard")
    allp = json.load(open(R.PARAMS)) if os.path.exists(R.PARAMS) else {}
    P = dict(allp.get(key, {}))

    def obj(p):
        q = R.quick(R.run_all(ds, 3, use_card=bool(a.card), params=p, want_margins=False))
        return q["holes_right"] + 0.5 * q["all_right"], q
    best, q = obj(P)
    print("start", P, q, flush=True)
    for _ in range(a.rounds):
        for k, vals in GRID:
            if a.only and k not in a.only.split(","):
                continue
            if not a.card and k in ("w_c", "card_s", "set_slack"):
                continue
            if a.source == "truth" and k in ("c_vt", "c_miss", "w_dg", "w_dt"):
                continue
            cur = P.get(k, R.S.DEF[k])
            for v in vals:
                if v == cur:
                    continue
                s, q2 = obj(dict(P, **{k: v}))
                if s > best + 1e-9:
                    best, q, P[k] = s, q2, v
            print(k, P.get(k, cur), q, flush=True)
    allp = json.load(open(R.PARAMS)) if os.path.exists(R.PARAMS) else {}
    allp[key] = P
    json.dump(allp, open(R.PARAMS, "w"), indent=1, sort_keys=True)
    print("final", key, P, q)


if __name__ == "__main__":
    main()
