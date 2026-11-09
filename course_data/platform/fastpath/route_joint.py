"""Hole lines for a course OSM maps without them (greens + tee boxes, no golf=hole ways): zero_tap/joint (card-aware
joint routing, 0.5 s) on the OSM polygons, written as golf=hole ways the package build reads like OSM's own.

  python3 route_joint.py fit CACHE            fit the four evidence models on the bench DEV split (prep.py --source osm
                                              cache) -> zero_tap/joint/model_osm.pkl (offline, once)
  route(fc, card, n_holes) -> dict(features [golf=hole LineStrings, ref / par], min_margin, margins, n_virtual, ...)

Gate (MIN_MARGIN): the solver's min-marginal. Bench with hole lines hidden, web card, tee_reuse (BLIND_LOOP.md):
min margin >= 4 -> dev 19 shown / 16 with every green numbered right, test 28 / 27. Below it the course is not shown.
"""
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(os.path.dirname(HERE))
J = os.path.join(CD, "zero_tap", "joint")
MODEL = os.path.join(J, "model_osm.pkl")
MIN_MARGIN = 4.0
PARAMS = dict(K=18, beam=4000, tee_reuse=1)
_MS = [None]


def _mods():
    for p in (J, os.path.dirname(J)):
        if p not in sys.path:
            sys.path.insert(0, p)
    import cands as C
    import feats as F
    import models as M
    import solve as S
    return C, F, M, S


def fit(cache):
    C, F, M, S = _mods()
    import prep
    dev = prep.load(cache, "osm", "dev")
    ms = M.fit(dev)
    pickle.dump(ms, open(MODEL, "wb"))
    print("fitted on", len(dev), "dev courses ->", MODEL, round(os.path.getsize(MODEL) / 1e6, 2), "MB")


def _line(F, co, p, q):
    """tee -> green as the hole is played: through the centreline of the fairway that leads to the green (the same
    path feats.play_length measures), simplified to the dog-leg corners; straight when no fairway fits."""
    from shapely.geometry import LineString
    p, q = np.asarray(p, float), np.asarray(q, float)
    S = float(np.hypot(*(q - p)))
    try:
        _, fi = F.play_length(co, p, q)
    except Exception:                                                # noqa: BLE001
        fi = -1
    if fi < 0 or S < 150:
        return [tuple(p), tuple(q)]
    cl = co["fair"][fi]["cl"]
    u = (q - p) / S
    s = (cl - p) @ u / S
    keep = (s > 0.12) & (s < 0.93)
    pts = cl[keep][np.argsort(s[keep])]
    ln = LineString(np.vstack([p, pts, q])).simplify(10.0)
    return [tuple(c) for c in ln.coords]


def route(fc, card, n_holes):
    C, F, M, S = _mods()
    if _MS[0] is None:
        _MS[0] = pickle.load(open(MODEL, "rb"))
    co = C.from_osm(fc)
    geo = F.geometry(co)
    hp, hx = F.hole_features(co, geo)
    wp, wx, W = F.walk_features(co, geo)
    d = dict(row=dict(slug="x"), co=co, geo=geo, hp=hp, hx=hx, wp=wp, wx=wx, W=W, card=card, kind=int(n_holes))
    d["sc"] = M.predict(_MS[0], d)
    sol = S.solve(d, card, PARAMS, None)
    if not sol["seq"]:
        return dict(features=[], min_margin=0.0, why="no routing found")
    mg = S.margins(sol, None)
    pars = (card or {}).get("par") or []
    feats, nv = [], 0
    for i, (t, g) in enumerate(sol["holes"]):
        if t < 0 or g < 0:
            nv += 1
            continue
        tc = co["T"][t]
        far = int(np.argmax(np.hypot(*(np.asarray(tc["pts"]) - np.asarray(co["G"][g])).T)))
        path = _line(F, co, tc["pts"][far], co["G"][g])
        line = [[round(v, 7) for v in co["pj"].inv(*q)] for q in path]
        L = float(geo["P"][t, g])
        par = pars[i % len(pars)] if pars else (3 if L < 245 else 4 if L < 470 else 5)
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": line},
                      "properties": {"golf": "hole", "ref": str(i + 1), "par": str(par), "src": "joint",
                                     "margin": round(float(mg[i]), 2)}})
    return dict(features=feats, min_margin=float(min(mg)) if len(mg) else 0.0, margins=[round(float(m), 2) for m in mg],
                n_virtual=nv, n_holes=int(n_holes), greens=len(co["G"]), tee_complexes=len(co["T"]))


def unnumbered_lines(fc, n_holes):
    """OSM golf=hole ways when the course has (nearly) all of them but (nearly) none carries a usable ref: the pairs
    are known, only the numbering is not (Brookhaven CC, blind loop 2026-11-09). -> [coords] or None"""
    lines, numbered = [], 0
    for f in (fc or {}).get("features", []):
        pr, g = f.get("properties") or {}, f.get("geometry") or {}
        if pr.get("golf") == "hole" and g.get("type") == "LineString" and len(g["coordinates"]) >= 2 \
                and pr.get("inside_course") is not False:
            lines.append(g["coordinates"])
            numbered += str(pr.get("ref") or "").strip().isdigit()
    if len(lines) < 0.8 * n_holes or len(lines) > 1.3 * n_holes or numbered > 0.3 * len(lines):
        return None
    return lines


def route_lines(fc, lines, card, n_holes):
    """Number unnumbered hole lines: the joint solve with every (tee, green) pair fixed to a line, so only the order
    is solved (card yardage per position + green -> next tee walks + clubhouse start / end)."""
    C, F, M, S = _mods()
    from shapely.geometry import LineString
    if _MS[0] is None:
        _MS[0] = pickle.load(open(MODEL, "rb"))
    lon0 = float(np.mean([ln[-1][0] for ln in lines]))
    lat0 = float(np.mean([ln[-1][1] for ln in lines]))
    pj = C.TR.Proj(lon0, lat0)
    co = dict(pj=pj, source="lines", G=[], Gr=[], Gp=[], Gid=[], T=[], fair=[], club=None)
    L = []
    for j, ln in enumerate(lines):
        xy = [pj.fwd(*q[:2]) for q in ln]
        L.append(LineString(xy).length)
        co["G"].append(xy[-1])
        co["Gr"].append(12.0)
        co["Gp"].append(0.98)
        co["Gid"].append("g%d" % j)
        co["T"].append(dict(c=xy[0], pts=[xy[0]], id="t%d" % j, ax=None, p=0.98))
    fair, park, club = C._osm_context(fc, pj)
    co["fair"] = fair
    C._pick_club(co, park, club)
    co = C._finish(co)
    geo = F.geometry(co)
    for j in range(len(lines)):                       # the hole's length is its line's, not the straight distance
        geo["P"][j, j] = L[j]
        try:
            geo["Pbox"][j][j] = np.array([L[j]])
        except Exception:                             # noqa: BLE001
            pass
    hp, hx = F.hole_features(co, geo)
    wp, wx, W = F.walk_features(co, geo)
    d = dict(row=dict(slug="x"), co=co, geo=geo, hp=hp, hx=hx, wp=wp, wx=wx, W=W, card=card, kind=int(n_holes))
    d["sc"] = M.predict(_MS[0], d)
    d["sc"]["ph"] = np.array([0.98 if int(t) == int(g) else 1e-6 for t, g in hp], float)
    sol = S.solve(d, card, dict(PARAMS, tee_reuse=0, ph_min=0.5), None)
    if not sol["seq"]:
        return dict(features=[], min_margin=0.0, why="no ordering found")
    mg = S.margins(sol, None)
    pars = (card or {}).get("par") or []
    feats, nv = [], 0
    for i, (t, g) in enumerate(sol["holes"]):
        if t < 0 or g < 0 or t != g:
            nv += 1
            continue
        par = pars[i % len(pars)] if pars else (3 if L[t] < 245 else 4 if L[t] < 470 else 5)
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": lines[t]},
                      "properties": {"golf": "hole", "ref": str(i + 1), "par": str(par), "src": "joint:lines",
                                     "margin": round(float(mg[i]), 2)}})
    return dict(features=feats, min_margin=float(min(mg)) if len(mg) else 0.0, margins=[round(float(m), 2) for m in mg],
                n_virtual=nv, n_holes=int(n_holes), mode="unnumbered OSM hole lines ordered", lines=len(lines))


if __name__ == "__main__":
    if sys.argv[1] == "fit":
        fit(sys.argv[2])
