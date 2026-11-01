"""pathroute v2 on a live course (platform/stage_select.py method "pathroute_v2"): OSM fc + course -> holes 1..N
with a calibrated per-hole pair confidence, no scorecard.

    import live2
    res = live2.route(fc, course, n_holes=18)          # routing-compatible {"holes": {ref: {...}}, ...}
    res = live2.route(fc, course, n_holes=18, fix=f)   # f: golfer facts by OSM id (resolve2.Session.to_ids)

OSM golf=hole ways the file already has are fixed as confirmed pairs ("hole <ref> is this tee + green") before the
decode, so pathroute only fills the holes OSM lacks and the numbering around them is consistent. Models load from
model_v2.pkl.gz next to this file (fit by sim2.py on the zero-tap dev split, see PATHROUTE.md "confirm-and-resolve").
"""
from __future__ import annotations

import math
import os
import pickle
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
# pathroute's modules have plain names that other course_data dirs also use (structure/scene.py,
# perception/features.py, zero_tap/sequence/bench.py, ...): import them with our dirs first on sys.path and our own
# sys.modules entries, then put the caller's entries back.
_NAMES = ("truth", "bench", "scene", "features", "decode", "model", "run", "prep", "features2", "prep2",
          "complexes", "confidence", "decode2", "run2", "resolve2")
_MODS = {}

MODEL = os.path.join(HERE, "model_v2.pkl.gz")
CONF_OK = 0.95             # status "ok" at or above this pair confidence (test: 0.95-0.98 -> 96.8 % right), else "check"
SNAP_YD = 40.0             # an OSM hole way's end / start -> the scene green / tee within this many yds
_M = {}


def _read(path):
    import gzip
    with (gzip.open if path.endswith(".gz") else open)(path, "rb") as fh:
        return pickle.load(fh)


def _mods():
    if _MODS:
        return _MODS
    saved = {k: sys.modules.pop(k) for k in _NAMES if k in sys.modules}
    path0 = list(sys.path)
    sys.path[:0] = [HERE, os.path.join(ZT, "pathroute"), ZT]
    try:
        import importlib
        for k in _NAMES:
            _MODS[k] = importlib.import_module(k)
        _MODS["_model"] = _read(MODEL) if os.path.exists(MODEL) else None
    finally:
        for k in _NAMES:
            sys.modules.pop(k, None)
        sys.modules.update(saved)
        sys.path[:] = path0
    return _MODS


def load_model(path=MODEL):
    if path == MODEL:
        m = _mods()["_model"]
        if m is None:
            raise RuntimeError(f"pathroute_v2: {MODEL} missing (fit it: PATHROUTE.md confirm-and-resolve)")
        return m
    if path not in _M:
        M = _mods()
        saved = {k: sys.modules.get(k) for k in _NAMES}
        sys.modules.update({k: M[k] for k in _NAMES})
        try:
            _M[path] = _read(path)
        finally:
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
    return _M[path]


def features(fc, course=None, kind=18):
    """The pathroute v1 + v2 feature dict of one course (as pathroute/prep.py + pathroute_v2/prep2.py build it)."""
    M = _mods()
    TR, S, F, F2, prep2 = M["truth"], M["scene"], M["features"], M["features2"], M["prep2"]
    fh = TR.hide(fc)
    sc = S.Scene(fh, course or {})
    if len(sc.tees) < 1 or len(sc.greens) < 2:
        raise RuntimeError(f"pathroute_v2: {len(sc.greens)} greens / {len(sc.tees)} tees in OSM")
    hp, hX = F.hole_feats(sc)
    tp, tX = F.trans_feats(sc)
    cT, cG = F.club_feats(sc)
    d = dict(slug=(course or {}).get("slug", "live"), split="live", kind=kind, hp=hp, hX=hX, tp=tp, tX=tX, cT=cT,
             cG=cG, lab=None, club_src=sc.club_src,
             greens=[dict(id=g["id"], ll=sc.pj.inv(*g["c"]), r=g["r"]) for g in sc.greens],
             tees=[dict(id=tt["id"], ll=sc.pj.inv(*tt["c"]), c=tt["c"], ax=tt["ax"], L=tt["L"]) for tt in sc.tees],
             gc=sc.gc, tc=sc.tc, club=sc.club)
    pr = prep2._props(fh, sc)
    d["hX"] = np.c_[hX, F2.hole2_feats(sc, hp, pr)]
    d["tpp"], d["tpX"] = F2.tee_pairs(sc, pr)
    return d, sc


def osm_fix(fc, d, sc, kind):
    """Golf=hole ways with a numeric ref -> confirmed pairs [(number, tee, green)] (number None on 27 / 36)."""
    n = 9 if kind in (9, 27) else 18
    gc, tc = np.asarray(d["gc"], float), np.asarray(d["tc"], float)
    pairs, used_t, used_g = [], set(), set()
    for f in fc.get("features", []):
        p = f.get("properties") or {}
        if p.get("golf") != "hole" or f.get("geometry", {}).get("type") != "LineString":
            continue
        ref = str(p.get("ref", ""))
        if not ref.isdigit() or not 1 <= int(ref) <= kind:
            continue
        co = f["geometry"]["coordinates"]
        a, b = sc.pj.fwd(*co[0][:2]), sc.pj.fwd(*co[-1][:2])
        dg = np.hypot(gc[:, 0] - b[0], gc[:, 1] - b[1])
        dt = np.hypot(tc[:, 0] - a[0], tc[:, 1] - a[1])
        g, t = int(np.argmin(dg)), int(np.argmin(dt))
        if dg[g] > SNAP_YD or dt[t] > SNAP_YD or g in used_g or t in used_t:
            continue
        used_g.add(g)
        used_t.add(t)
        pairs.append((int(ref) if kind == n else None, t, g))
    return pairs


def route(fc, course=None, n_holes=18, fix=None, model=None, use_osm_holes=True):
    """-> routing-compatible result: {method, status, n_holes, holes {ref: {ref, par, tee_ll, back_tee_ll,
    green_ll, straight_yd, p_hole, confidence, status, flags, tee_id, green_id, tee_boxes_ll, fixed}}, confirm}."""
    DC, RS = _mods()["decode"], _mods()["resolve2"]
    kind = int(n_holes or 18)
    if kind not in (9, 18, 27, 36):
        kind = 18 if kind > 9 else 9
    m = model or load_model()
    d, sc = features(fc, course, kind)
    pr = m["models"].predict(d)
    s = RS.Session(d, pr, m["calib"], cfg=m.get("cfg"))
    osm_pairs = osm_fix(fc, d, sc, kind) if use_osm_holes else []
    for num, t, g in osm_pairs:
        s.confirm_pair(num, t, g)
    if fix:
        f = RS.Session.from_ids(d, fix)
        for num, t, g in f["pairs"]:
            s.confirm_pair(num, t, g)
        for g in f["not_green"]:
            s.not_a_hole(g)
        if f.get("first_tee") is not None:
            s.hole_one(f["first_tee"])
    holes, conf = s.solve()
    if not holes:
        raise RuntimeError("pathroute_v2: decode failed")
    n = 9 if kind in (9, 27) else 18
    fixed = s.fixed_pairs()
    osm_set = {(t, g) for _, t, g in osm_pairs}
    out = {}
    for h, c in zip(holes, conf):
        ref = str(h["loop"] * n + h["number"])
        boxes = [h["t"]] + list(h["boxes"])
        back = max(boxes, key=lambda b: math.hypot(*(np.asarray(d["gc"][h["g"]]) - np.asarray(d["tc"][b]))))
        ok = c >= CONF_OK
        src = "osm hole way" if (h["t"], h["g"]) in osm_set else ("golfer" if (h["t"], h["g"]) in fixed else None)
        out[ref] = dict(ref=ref, par=DC.par_from_len(h["L"]), tee_ll=list(d["tees"][h["t"]]["ll"]),
                        back_tee_ll=list(d["tees"][back]["ll"]), green_ll=list(d["greens"][h["g"]]["ll"]),
                        tee_boxes_ll=[list(d["tees"][b]["ll"]) for b in h["boxes"]],
                        straight_yd=round(h["L"], 1), p_hole=round(float(c), 4), confidence=round(float(c), 4),
                        status="ok" if ok else "check",
                        flags=[] if ok else [f"pathroute_v2 pair confidence {c:.2f}: ask the golfer"],
                        tee_id=d["tees"][h["t"]]["id"], green_id=d["greens"][h["g"]]["id"],
                        tee_src="osm", green_src="osm", fixed=src)
    order = sorted(range(len(holes)), key=lambda i: conf[i])
    ask = [str(holes[i]["loop"] * n + holes[i]["number"]) for i in order
           if conf[i] < CONF_OK and (holes[i]["t"], holes[i]["g"]) not in fixed]
    return dict(method="pathroute_v2", status="ok", n_holes=len(out), holes=out,
                n_check=sum(h["status"] != "ok" for h in out.values()), certain=False,
                confidence=round(float(s.route_conf), 4),
                confirm=dict(schema="pathroute_confirm/1", conf_ok=CONF_OK, ask_order=ask,
                             facts=s.to_ids(), osm_fixed=len(osm_pairs),
                             doc="zero_tap/PATHROUTE.md confirm-and-resolve: ask the lowest-confidence hole, add the "
                                 "answer to facts, call live2.route(..., fix=facts) again"))
