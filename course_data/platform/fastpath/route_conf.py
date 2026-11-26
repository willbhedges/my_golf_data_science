"""Two routings of one course -> which one to ship and a per-hole P(hole right) (NOTES_ROUTING.md 2026-11-26).

A course without mapped holes is routed twice, on the scenes of two detectors (the default U-Net and golfseg_own_v3;
the routing fits are the default's in both). The two routings move 5-18 holes on about half the courses, their accuracy
is equal (87.1 % each on the paired 594 TRAIN-BIG courses), and where they disagree on a hole's green the hole is right
29 % of the time. A gradient-boosted model on the routing's own per-hole features (route_gate's), the neighbouring
holes, course-level statistics and the distance of this hole's green / tee to the other routing's gives

    p_hole          P(this hole is numbered right), per routing
    pick            the routing with the larger sum of p_hole (the other must win by PICK_MARGIN holes)

Out of fold by course (8 folds) on the paired runs 44817755394 / 44823590755:
    holes right, default routing 87.11 % -> picked routing 88.33 % (104 of 594 courses switch)
    flagging the 10 % least certain holes catches 56 % of the wrong ones (route_gate alone 45 %), 15 % -> 66 % (54 %)

    python3 route_conf.py fit RUN_DIR [RUN_DIR...]     refit from artifact folders (pair-*/bench_{A,B}.json.gz)
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
import detector as _DET  # noqa: E402

MODEL = _DET.routing_file("route_conf.json", "ROUTE_CONF_MODEL")
ENV = "ROUTE_ENSEMBLE"          # 1 (default): second routing on the other detector + this model; 0: route_gate only
PICK_MARGIN = 0.5               # predicted holes right the second routing must lead by to replace the first
APPROX_P = 0.65                 # holes under this are marked approximate (10 % of holes, 72 % of them wrong)
SECOND_UNET = os.path.join(os.path.dirname(os.path.dirname(HERE)), "segment", "models", "golfseg_own_v3", "model.safetensors")
NAN = float("nan")


def on():
    return os.environ.get(ENV, "1") != "0" and os.path.exists(MODEL) and os.path.exists(SECOND_UNET)


def yd(a, b):
    k = math.cos(math.radians(a[1]))
    return math.hypot((a[0] - b[0]) * k, (a[1] - b[1])) * 111320 / 0.9144


def _seglen(co):
    return sum(yd(co[i], co[i + 1]) for i in range(len(co) - 1))


def _lg(p):
    if p is None:
        return NAN
    p = min(max(p, 0.01), 0.99)
    return math.log(p / (1 - p))


def _nan(f, a):
    a = np.asarray(a, float)
    return float(f(a[np.isfinite(a)])) if np.isfinite(a).any() else NAN


def record(r, card, n):
    """A route_scene result (with its golf=hole features) -> the bench's course record (route_bench.route_course)."""
    import route_bench as RB
    feats = [f for f in r.get("features") or [] if (f.get("properties") or {}).get("golf") == "hole"]
    out = dict(route={k: v for k, v in r.items() if not k.startswith("_") and k != "features"},
               lines={str(f["properties"]["ref"]): dict(co=f["geometry"]["coordinates"], tee=f["properties"].get("tee_src"),
                                                        green=f["properties"].get("green_src")) for f in feats},
               has_card=bool(card and card.get("tee_sets")))
    cf = RB.card_fit(feats, card, n) if feats else None
    if cf:
        out["card_resid"] = {str(k): round(v, 1) for k, v in cf[2].items()}
    return out


def course_rows(r):
    """[(ref, {feature: value})] of one course record, the routing's own features only"""
    import route_gate
    rt = r["route"]
    hf = rt.get("hole_features") or []
    n = len(hf)
    if not n:
        return []
    _, ph = route_gate.p_all(rt)
    lines = r.get("lines") or {}
    resid = r.get("card_resid") or {}
    refs = [h["ref"] for h in hf]
    co = {k: v["co"] for k, v in lines.items() if v.get("co") and len(v["co"]) >= 2}
    tee = {k: c[0] for k, c in co.items()}
    grn = {k: c[-1] for k, c in co.items()}
    ph = np.array(ph)
    marg = np.array([min(h.get("margin") or 0, 40) for h in hf])
    cr = np.array([h["card_rel"] if h.get("card_rel") is not None else NAN for h in hf])
    walks = {}
    for i, ref in enumerate(refs):
        nx = refs[(i + 1) % n]
        if ref in grn and nx in tee:
            walks[ref] = yd(grn[ref], tee[nx])
    wv = list(walks.values()) or [NAN]
    gaps = [a[0] for a in rt.get("alts") or [] if isinstance(a, (list, tuple)) and a]
    cl = dict(c_n=n, c_pmean=ph.mean(), c_pmin=ph.min(), c_plo=(ph < 0.7).mean(), c_p2=np.sort(ph)[min(1, n - 1)],
              c_mmin=marg.min(), c_mmed=np.median(marg), c_mlo=(marg < 2).mean(),
              c_crmed=_nan(np.median, cr), c_crbad=_nan(np.mean, np.where(np.isfinite(cr), cr > 0.15, NAN)),
              c_virt=(rt.get("n_virtual") or 0) / n, c_greens=(rt.get("greens") or 0) / n,
              c_tees=(rt.get("tee_complexes") or 0) / n, c_cost=(rt.get("cost") or 0) / n,
              c_wmed=_nan(np.median, wv), c_wmax=_nan(np.max, wv), c_wbig=_nan(np.mean, np.where(np.isfinite(wv), np.asarray(wv) > 300, NAN)),
              c_alt0=min(gaps) if gaps else NAN, c_altmed=float(np.median(gaps)) if gaps else NAN,
              c_altz=float(np.mean(np.array(gaps) < 0.01)) if gaps else NAN,
              c_rr=len((rt.get("rerank") or {}).get("changed") or []) / n, c_fb=float(bool(rt.get("shared_fallback"))),
              c_hascard=float(bool(r.get("has_card"))))
    rows = []
    for i, h in enumerate(hf):
        ref = h["ref"]
        pv = refs[(i - 1) % n]
        f = dict(p0=ph[i], margin=marg[i], kind=h.get("kind", 0), card_rel=cr[i], ob=h.get("ob") or 0, phl=_lg(h.get("ph")),
                 cross=h.get("cross") or 0, pwl=_lg(h.get("pw")), gpl=_lg(h.get("gp")), garea=h.get("garea") or NAN,
                 gmap=h.get("gmap") or 0, tpl=_lg(h.get("tp")), tbox=h.get("tbox") or 0, rr=h.get("rr") or 0,
                 fb=float(bool(h.get("fallback"))), resid=resid.get(ref, NAN), idx=i / n,
                 w_in=walks.get(pv, NAN), w_out=walks.get(ref, NAN),
                 p_prev=ph[(i - 1) % n], p_next=ph[(i + 1) % n], m_prev=marg[(i - 1) % n], m_next=marg[(i + 1) % n],
                 cr_prev=cr[(i - 1) % n], cr_next=cr[(i + 1) % n], p_rel=ph[i] - ph.mean())
        if ref in co:
            L = _seglen(co[ref])
            og = [yd(tee[ref], g) for k, g in grn.items() if k != ref]
            ot = [yd(grn[ref], t) for k, t in tee.items() if k != ref]
            gg = [yd(grn[ref], g) for k, g in grn.items() if k != ref]
            tt = [yd(tee[ref], t) for k, t in tee.items() if k != ref]
            f.update(len=L, straight=yd(co[ref][0], co[ref][-1]) / max(L, 1), npts=len(co[ref]),
                     tee_ng=min(og) if og else NAN, grn_nt=min(ot) if ot else NAN,
                     grn_ng=min(gg) if gg else NAN, tee_nt=min(tt) if tt else NAN,
                     tsrc=float(lines[ref].get("tee") == "scene"), gsrc=float(lines[ref].get("green") == "scene"))
            f["w_in_x"] = f["w_in"] - f["tee_ng"] if og and np.isfinite(f["w_in"]) else NAN
            f["w_out_x"] = f["w_out"] - f["grn_nt"] if ot and np.isfinite(f["w_out"]) else NAN
        f.update(cl)
        rows.append((ref, f))
    return rows


def cross_rows(a, b):
    """course_rows(a) + the distance of each hole's green / tee to routing b's hole of the same number (x_dg, x_dt),
    to b's nearest hole of any number (x_any) and the course's share of agreeing greens (c_xg)"""
    rows = course_rows(a)
    la, lb = a.get("lines") or {}, b.get("lines") or {}
    for ref, f in rows:
        x, y = la.get(ref), lb.get(ref)
        if x and y and x.get("co") and y.get("co"):
            f["x_dg"] = min(yd(x["co"][-1], y["co"][-1]), 400)
            f["x_dt"] = min(yd(x["co"][0], y["co"][0]), 400)
        else:
            f["x_dg"] = f["x_dt"] = NAN
        if x and x.get("co"):
            d = [max(yd(x["co"][-1], v["co"][-1]), yd(x["co"][0], v["co"][0]) / 2) for v in lb.values() if v.get("co")]
            f["x_any"] = min(min(d), 400) if d else NAN
        else:
            f["x_any"] = NAN
    ga = _nan(np.mean, [NAN if not np.isfinite(f["x_dg"]) else float(f["x_dg"] <= 20) for _, f in rows])
    for _, f in rows:
        f["c_xg"] = ga
    return rows


_M = {}


def _load(path=MODEL):
    if path not in _M:
        import lightgbm as lgb
        d = json.load(open(path))
        _M[path] = {k: (v["cols"], [lgb.Booster(model_str=s) for s in v["boosters"]]) for k, v in d["models"].items()}
    return _M[path]


def _predict(rows, kind):
    cols, bs = _load()[kind]
    X = np.array([[float(f.get(c, NAN)) for c in cols] for _, f in rows], float)
    return np.mean([b.predict(X) for b in bs], axis=0)


def score(a, b=None):
    """-> {ref: p_hole} of routing a: with the second routing b the 'pair' model, alone the 'single' model"""
    rows = cross_rows(a, b) if b is not None else course_rows(a)
    if not rows:
        return {}
    p = _predict(rows, "pair" if b is not None else "single")
    return {ref: round(float(v), 4) for (ref, _), v in zip(rows, p)}


def pick(a, b):
    """-> dict(use 'a' | 'b', p {ref: p_hole} of the routing used, sum_a, sum_b, agree = share of holes whose green
    the two routings put in the same place)"""
    pa, pb = score(a, b), score(b, a)
    sa, sb = sum(pa.values()), sum(pb.values())
    use = "b" if pb and sb > sa + PICK_MARGIN else "a"
    ag = [f["x_dg"] <= 20 for _, f in cross_rows(a, b) if np.isfinite(f["x_dg"])]
    out = dict(use=use, p=pb if use == "b" else pa, sum_a=round(sa, 2), sum_b=round(sb, 2),
               agree=round(float(np.mean(ag)), 3) if ag else None)
    if "pair_id" in _load():
        rows = cross_rows(b, a) if use == "b" else cross_rows(a, b)
        out["p_id"] = {ref: round(float(v), 4) for (ref, _), v in zip(rows, _predict(rows, "pair_id"))}
    return out


# ------------------------------------------------------------------------------------------------- verified holes
# A hole is VERIFIED (shown as right with no human check) when the 'pair_id' model gives it P(the green is this hole's
# and the tee stands on this hole) >= VERIFY_P and a second scorecard source agrees with the card the routing used.
# Out of fold by course on the 594 paired TRAIN-BIG courses (NOTES_ROUTING.md 2026-11-26, verified holes): 31.7 % of
# holes verified, 99.1 % of them right (never-used split: 29.7 %, 99.2 %); green and number right 99.65 %.
VERIFY_P = 0.98
CORROBORATE_YD = 12.0          # two cards agree on a hole within this
CORROBORATE_SHARE = 0.8        # ... on this share of the holes, in their best pair of tee sets


def _sets(card):
    return [list(v.get("yards") or []) for v in ((card or {}).get("tee_sets") or {}).values()]


def card_agreement(a, b):
    """share of holes on which two cards' yardages agree, in their best-matching pair of tee sets (0 when none pairs)"""
    best = 0.0
    for ya in _sets(a):
        for yb in _sets(b):
            if ya and len(ya) == len(yb):
                best = max(best, float(np.mean([bool(x and z and abs(x - z) <= CORROBORATE_YD) for x, z in zip(ya, yb)])))
    return best


def card_corroboration(card, web_cards):
    """number of web scorecards from another source that agree with `card` (the one the routing used). web_cards:
    scorecard_web.json's [{source, url, card}]. The first web card with the same tee sets is `card` itself; a
    second site carrying the very same numbers does count (the rule was measured that way)."""
    mine = _sets(card)
    if not mine:
        return 0
    cards = [c for c in web_cards or [] if c.get("card")]
    own = next((c for c in cards if _sets(c["card"]) == mine), None)
    src = own.get("source") if own else None
    return sum(1 for c in cards if c is not own and (src is None or c.get("source") != src)
               and card_agreement(card, c["card"]) >= CORROBORATE_SHARE)


def verified(pk, card, web_cards):
    """-> (sorted refs verified, number of corroborating cards) for a pick() result"""
    n = card_corroboration(card, web_cards)
    pid = pk.get("p_id") or {}
    v = [r for r, p in pid.items() if p >= VERIFY_P] if n else []
    return sorted(v, key=lambda r: (not str(r).isdigit(), int(r) if str(r).isdigit() else 0)), n


JOINT_VERIFY_MARGIN = 4.0


def verified_joint(features, routed, card, web_cards):
    """-> (sorted refs verified, corroborating cards) for a route_joint routing of OSM's own unnumbered hole lines
    (routed["mode"] set; features: its golf=hole ways with `margin`). Verified: the numbering margin >= 4, no hole
    without a tee or green, and a second scorecard source agrees. route_bench joint, train+big 631 courses, lines
    mode: 56 % of holes, 99.6 % numbered right (23 wrong); without the second card 98.7 %. With greens and tees only
    (no lines) no rule passes 96 %, so nothing is verified there."""
    n = card_corroboration(card, web_cards)
    if not n or not (routed or {}).get("mode") or (routed or {}).get("n_virtual"):
        return [], n
    v = [str(f["properties"]["ref"]) for f in features or []
         if (f.get("properties") or {}).get("golf") == "hole" and f["properties"].get("ref") is not None
         and float(f["properties"].get("margin") or 0.0) >= JOINT_VERIFY_MARGIN]
    return sorted(v, key=lambda r: (not r.isdigit(), int(r) if r.isdigit() else 0)), n


# ---------------------------------------------------------------------------------------------------------- fit

def _runs(dirs):
    """{slug: {arm: record}} of detector_pair artifact folders; a later folder's arm B becomes arm C, D, ..."""
    import glob
    import gzip
    out = {}
    for i, d in enumerate(dirs):
        for arm in "AB":
            name = arm if i == 0 else ("A%d" % i if arm == "A" else chr(ord("B") + i))
            for f in glob.glob(os.path.join(d, "pair-*", "bench_%s.json.gz" % arm)):
                for c in json.load(gzip.open(f, "rt"))["courses"]:
                    if "hole_ok" in c and c["route"].get("hole_features"):
                        out.setdefault(c["slug"], {})[name] = c
    return out


def fit(dirs, out=MODEL, seeds=5):
    import lightgbm as lgb
    R = _runs(dirs)
    arms = sorted({k for v in R.values() for k in v if not k.startswith("A") or k == "A"})
    pairs = [(x, y) for x in arms for y in arms if x != y]
    data = {"pair": [], "single": []}
    for s, v in sorted(R.items()):
        for x, y in pairs:
            if x in v and y in v:
                data["pair"] += [(s, v[x]["hole_ok"].get(ref, False), f) for ref, f in cross_rows(v[x], v[y])]
        for x in arms:
            if x in v:
                data["single"] += [(s, v[x]["hole_ok"].get(ref, False), f) for ref, f in course_rows(v[x])]
    prm = dict(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1,
               colsample_bytree=0.7, reg_lambda=5, verbose=-1)
    models = {}
    for kind, rows in data.items():
        cols = sorted({k for r in rows for k in r[2]})
        X = np.array([[float(r[2].get(c, NAN)) for c in cols] for r in rows], float)
        y = np.array([r[1] for r in rows])
        bs = [lgb.LGBMClassifier(random_state=sd, **prm).fit(X, y).booster_.model_to_string() for sd in range(seeds)]
        models[kind] = dict(cols=cols, boosters=bs, rows=len(y), courses=len({r[0] for r in rows}), right=round(float(y.mean()), 4))
        print(kind, X.shape, "right", round(float(y.mean()), 4))
    json.dump(dict(schema="route_conf/1", arms=arms, source=[os.path.basename(os.path.normpath(d)) for d in dirs],
                   params=prm, models=models), open(out, "w"))
    print("wrote", out, round(os.path.getsize(out) / 1e6, 2), "MB")


def identity_ok(truth, line):
    """The verified-hole label: the routed green within 20 yd of the mapped hole's end, and the routed tee within 90 yd
    of the first 60 % of its mapped line with no other hole's line nearer. (routing.score's 40 yd tee tolerance calls a
    forward box beside the centre line wrong: 61 of the 110 wrong holes at P >= 0.97 were such tees.)"""
    from routing import Proj, _seg_dist

    def one(ref):
        ln, t = line.get(ref), truth.get(ref)
        if not t or not ln or not ln.get("co"):
            return False
        pr = Proj(*t["green_ll"])
        if math.hypot(*pr.fwd(*ln["co"][-1])) > 20:
            return False
        p = np.asarray(pr.fwd(*ln["co"][0]))

        def dist(tt, frac):
            xy = pr.ring(tt["line"])
            cum = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
            return _seg_dist(p, xy[: max(2, int(np.searchsorted(cum, frac * cum[-1])) + 1)])
        own = dist(t, 0.6)
        return own <= 90 and all(dist(tt, 1.0) >= own for k, tt in truth.items() if k != ref)
    return one


def fit_id(dirs, out=MODEL, seeds=5):
    """Add the 'pair_id' model (the verified-hole label, identity_ok or the bench's forward-tee hole_ok_fwd) to the
    fitted file; the other models are left as they are. Needs the bench courses' OSM truth (route_bench.course_files)."""
    import sys
    import lightgbm as lgb
    sys.path.insert(0, os.path.dirname(HERE))
    import route_bench as RB
    import routing as R
    Rn = _runs(dirs)
    arms = sorted({k for v in Rn.values() for k in v if not k.startswith("A") or k == "A"})
    rows = []
    for s, v in sorted(Rn.items()):
        truth = {k: t for k, t in R.truth_from_fc(RB.course_files(s)[0]).items() if int(k) <= 18}
        for x in arms:
            if x not in v:
                continue
            ok = identity_ok(truth, v[x].get("lines") or {})
            fwd = v[x].get("hole_ok_fwd") or v[x]["hole_ok"]
            for y in arms:
                if y != x and y in v:
                    rows += [(s, bool(fwd.get(ref, False)) or ok(ref), f) for ref, f in cross_rows(v[x], v[y])]
    d = json.load(open(out))
    prm = d["params"]
    cols = sorted({k for r in rows for k in r[2]})
    X = np.array([[float(r[2].get(c, NAN)) for c in cols] for r in rows], float)
    y = np.array([r[1] for r in rows])
    bs = [lgb.LGBMClassifier(random_state=sd, **prm).fit(X, y).booster_.model_to_string() for sd in range(seeds)]
    d["models"]["pair_id"] = dict(cols=cols, boosters=bs, rows=len(y), courses=len({r[0] for r in rows}), right=round(float(y.mean()), 4))
    json.dump(d, open(out, "w"))
    print("pair_id", X.shape, "right", round(float(y.mean()), 4), "wrote", out, round(os.path.getsize(out) / 1e6, 2), "MB")


if __name__ == "__main__":
    import sys
    if sys.argv[1] == "fit":
        fit(sys.argv[2:])
    elif sys.argv[1] == "fit_id":
        fit_id(sys.argv[2:])
