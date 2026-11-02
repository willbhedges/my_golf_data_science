"""Export what the browser needs to re-solve pathroute v2 routing (course_data/app/pathroute_engine.js): the decoder
inputs of one course (pathroute_decoder/1) and Python reference decodes for the JS parity test.

    import export_js as XJ
    R = XJ.record(d, pr, model)              # d: v1+v2 features (live2.features / R2.load), pr = model["models"].predict(d)
    python course_data/zero_tap/pathroute_v2/export_js.py --c1 C1 --c2 C2 --n 24 \
        --out course_data/app/fixtures/pathroute     # parity fixtures: R + reference decodes with / without facts

pathroute_decoder/1: kind, tees [{id, ll}], greens [{id, ll}], tc / gc (scene yds), H (sparse [tee, green, nats];
others H_default), T (sparse [green, tee, nats], walk weight applied; others T_default), S / E (start / end nats, club
weight applied), comp (tee complex per tee), BIG, cfg (K, beam, mm_beam, cross, reuse), calib (confidence.Calib2 /
Calib coefficients), par_cuts, conf_ok. Floats are written as Python repr (exact round trip), so the JS decode sees
the same doubles as decode2.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import pickle
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
for _p in (HERE, os.path.join(ZT, "pathroute"), ZT):
    if _p not in sys.path:
        sys.path.append(_p)
import decode as DC  # noqa: E402
import complexes as CX  # noqa: E402
import confidence as CF  # noqa: E402
import run2 as R2  # noqa: E402
import resolve2 as RS  # noqa: E402

CONF_OK = 0.95


def calib_export(cal):
    if isinstance(cal, CF.Calib2) or hasattr(cal, "export"):
        return cal.export()
    m = cal.m
    return dict(schema="pathroute_calib/1", features=CF.CONF_F, coef=[float(c) for c in m.coef_[0]],
                intercept=float(m.intercept_[0]),
                transform="[x0..x5, log1p(max(minmarg,0)), minmarg_c, L/300]")


def record(d, pr, model, comp=None, cfg=None, conf_ok=CONF_OK):
    cfg = cfg or model.get("cfg") or R2.CFG
    if comp is None:
        comp = CX.cluster(len(d["tees"]), d["tpp"], pr["tpair"], thr=cfg["comp_thr"])
    H, T, S, E = DC.cost_mats(d, pr, R2.W)
    seen, Hs = set(), []
    for t, g in d["hp"]:
        if (int(t), int(g)) not in seen:
            seen.add((int(t), int(g)))
            Hs.append([int(t), int(g), float(H[t, g])])
    seen, Ts = set(), []
    for g, t in d["tp"]:
        if (int(g), int(t)) not in seen:
            seen.add((int(g), int(t)))
            Ts.append([int(g), int(t), float(T[g, t])])
    tdef = float(R2.W["trans"] * DC.BIG)
    assert np.all((T == tdef) | np.isin(np.arange(T.size).reshape(T.shape), [g * T.shape[1] + t for g, t, _ in Ts]))
    return dict(schema="pathroute_decoder/1", kind=int(d["kind"]),
                tees=[dict(id=t["id"], ll=[float(t["ll"][0]), float(t["ll"][1])]) for t in d["tees"]],
                greens=[dict(id=g["id"], ll=[float(g["ll"][0]), float(g["ll"][1])]) for g in d["greens"]],
                tc=[[float(x), float(y)] for x, y in np.asarray(d["tc"], float)],
                gc=[[float(x), float(y)] for x, y in np.asarray(d["gc"], float)],
                H=Hs, H_default=float(DC.BIG), T=Ts, T_default=tdef, S=[float(x) for x in S], E=[float(x) for x in E],
                comp=[int(c) for c in comp], BIG=float(DC.BIG),
                cfg=dict(K=int(cfg["K"]), beam=int(cfg["beam"]), mm_beam=int(cfg["mm_beam"]), cross=float(cfg["cross"]),
                         reuse=float(cfg["reuse"])),
                calib=calib_export(model["calib"]),
                calib_fix=calib_export(model["calib_fix"]) if model.get("calib_fix") is not None else None, par_cuts=[225.0, 450.0], conf_ok=conf_ok,
                sticky=dict(RS.STICKY) if RS.STICKY else None)


def ref_solve(d, pr, model, comp, fix, free=None):
    """Python reference (resolve2.Session.solve without the hole-1 fallback): holes + calibrated confidence."""
    holes, rc, X = R2.decode_course(d, pr, model.get("cfg") or R2.CFG, fix=fix, comp=comp, free=free)
    has = bool(fix and (fix.get("pairs") or fix.get("not_green") or fix.get("reject") or fix.get("first_tee") is not None))
    cal = model["calib_fix"] if has and model.get("calib_fix") is not None else model["calib"]
    c = cal.predict(X) if len(holes) else np.zeros(0)
    fp = {(int(t), int(g)) for _, t, g in (fix or {}).get("pairs") or ()}
    c = [1.0 if (h["t"], h["g"]) in fp else float(x) for h, x in zip(holes, c)]
    return dict(fix=fix, route_conf=float(rc),
                holes=[[h["number"], h["loop"], h["t"], h["g"], h["boxes"], float(h["L"])] for h in holes],
                conf=c, X=[[float(v) for v in row] for row in np.asarray(X)])


def cases(d, pr, model, comp, rng):
    """Free decode + three fact sets: two confirmed pairs (lowest-confidence holes, one re-numbered), a reject of a
    decoded pair + a practice green, and a hole-1 tee (the decoded hole 5's tee)."""
    out = [ref_solve(d, pr, model, comp, None)]
    holes = out[0]["holes"]
    if not holes:
        return out
    free = {(h[2], h[3]) for h in holes}
    order = np.argsort(out[0]["conf"], kind="stable")
    single = d["kind"] in (9, 18)
    a, b = holes[int(order[0])], holes[int(order[min(1, len(order) - 1)])]
    # a "golfer" confirmation: hole a's green with its decoded tee at a's number; hole b's green with the second-best
    # tee for it (a correction), numbered like b
    H = DC.cost_mats(d, pr, R2.W)[0]
    col = H[:, b[3]].copy()
    col[[b[2]] + b[4]] = np.inf
    t2 = int(np.argmin(col)) if np.isfinite(col.min()) else b[2]
    f1 = dict(pairs=[(a[0] if single else None, a[2], a[3])], not_green=[], first_tee=None)
    if t2 != a[2] and b[3] != a[3]:
        f1["pairs"].append((b[0] if single else None, t2, b[3]))
    out.append(ref_solve(d, pr, model, comp, f1, free))
    c = holes[int(order[min(2, len(order) - 1)])]
    ng = len(d["greens"])
    used = {h[3] for h in holes}
    spare = [g for g in range(ng) if g not in used]
    f2 = dict(pairs=[], not_green=spare[:1], first_tee=None, reject=[(c[2], c[3])])
    out.append(ref_solve(d, pr, model, comp, f2, free))
    if single:
        h5 = holes[min(4, len(holes) - 1)]
        f3 = dict(pairs=[(a[0], a[2], a[3])] if a is not h5 else [], not_green=[], first_tee=h5[2])
        out.append(ref_solve(d, pr, model, comp, f3, free))
    return out


def session_case(d, pr, model, comp):
    """resolve2.Session (default sticky re-solve) over a golfer sequence: free solve; "yes" to the lowest-confidence
    hole (confirm_yes, no re-solve); a correction of the next one (its second-best tee, sticky re-solve); "not a hole"
    without a re-solve (drop_hole); another correction; "not a hole" + re-solve for the next -> holes + conf per solve."""
    s = RS.Session(d, pr, model["calib"], cfg=model.get("cfg"), calib_fix=model.get("calib_fix"))
    s.comp = comp
    single = d["kind"] in (9, 18)
    H = DC.cost_mats(d, pr, R2.W)[0]
    steps = []

    def rec(act):
        steps.append(dict(act=act, holes=[[h["number"], h["loop"], h["t"], h["g"], h["boxes"]] for h in s.holes],
                          conf=[float(c) for c in s.conf]))
    s.solve()
    rec(None)
    for kind in ("yes", "fix", "drop", "fix", "not"):
        i = s.ask()
        if i is None:
            break
        h = s.holes[i]
        num = h["number"] if single else None
        if kind == "yes":
            act = ["yes", i, num]
        elif kind == "fix":
            col = H[:, h["g"]].copy()
            col[[h["t"]] + list(h["boxes"]) + [p[1] for p in s.fix["pairs"]]] = np.inf
            t2 = int(np.argmin(col)) if np.isfinite(col.min()) else h["t"]
            act = ["confirm", num, t2, h["g"]]
        elif kind == "drop":
            act = ["drop", i]
        else:
            act = ["not", h["g"]]
        if act[0] in ("yes", "drop"):       # the shipped flow: no re-solve after a "yes" / "not a hole"
            s.confirm_yes(i, num) if act[0] == "yes" else s.drop_hole(i)
            rec(act)
            continue
        if act[0] == "confirm":
            s.confirm_pair(*act[1:])
        else:
            s.not_a_hole(act[1])
        s.solve()
        rec(act)
        if not s.holes:
            break
    return steps


def _read(p):
    with (gzip.open if p.endswith(".gz") else open)(p, "rb") as fh:
        return pickle.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--c1", required=True)
    ap.add_argument("--c2", required=True)
    ap.add_argument("--model", default=os.path.join(HERE, "model_v2.pkl.gz"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--split", default="test")
    a = ap.parse_args()
    m = _read(a.model)
    ds = [d for d in R2.load(a.c1, a.c2, a.split) if not d.get("error") and len(d["tees"]) >= 2]
    # a spread of sizes: every 27 / 36 course first (few), then 9s and 18s, by slug
    ds.sort(key=lambda d: (d["kind"] not in (27, 36), d["kind"] != 9, d["slug"]))
    multi = [d for d in ds if d["kind"] in (27, 36)][:3]
    nines = [d for d in ds if d["kind"] == 9][:5]
    eights = [d for d in ds if d["kind"] == 18][: max(0, a.n - len(multi) - len(nines))]
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(0)
    t0 = time.time()
    for d in multi + nines + eights:
        pr = m["models"].predict(d)
        comp = CX.cluster(len(d["tees"]), d["tpp"], pr["tpair"], thr=(m.get("cfg") or R2.CFG)["comp_thr"])
        R = record(d, pr, m, comp)
        doc = dict(schema="pathroute_parity/1", slug=d["slug"], route=R, cases=cases(d, pr, m, comp, rng),
                   session=session_case(d, pr, m, comp))
        with gzip.open(os.path.join(a.out, d["slug"] + ".json.gz"), "wt") as fh:
            json.dump(doc, fh)
        print(d["slug"], d["kind"], len(doc["cases"]), f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
