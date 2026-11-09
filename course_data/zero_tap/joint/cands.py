"""joint routing: one candidate structure for every detection source.

A `Course` (plain dict, local yard frame, truth.Proj around the mean green):
  pj       truth.Proj
  G        [ng, 2] green centres;  Gr [ng] equal-area radius;  Gp [ng] P(real hole green);  Gid
  T        list of tee complexes: dict(c=(x, y), pts=[nb, 2] box centres, p, id, ax=(ux, uy)|None)
  fair     list of dict(poly=shapely polygon, cl=[k, 2] centreline)
  fair_u   union of the fairway polygons (or None)
  club     (x, y) | None;  park [k, 2] car-park centres
  pnext    {(green index, tee index): perception P(next tee)} (scene source only)
  source   'scene' | 'truth' | 'osm'

Sources:
  from_scene  the blind perception scene (course_scene/1): what an unmapped course really has;
  from_truth  the true hole endpoints with their numbers hidden and shuffled (one tee point + one green per hole),
              fairways / car parks / clubhouse from the holes-hidden OSM file: isolates routing from detection;
  from_osm    OSM green and tee polygons (holes and refs hidden), tee boxes grouped into complexes.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from shapely.geometry import shape, Polygon, LineString
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ZT = os.path.dirname(HERE)
sys.path[:0] = [ZT]
import truth as TR  # noqa: E402

M2YD = 1.0 / 0.9144


def _xy(pj, ll):
    return pj.fwd(ll[0], ll[1])


def _poly(pj, ring):
    try:
        p = Polygon([_xy(pj, q) for q in ring])
        if not p.is_valid:
            p = p.buffer(0)
        return p if (not p.is_empty and p.area > 0) else None
    except Exception:
        return None


def centreline(poly, k=6):
    """Crude centreline of a fairway polygon: centroids of k slices along its major axis."""
    try:
        r = poly.minimum_rotated_rectangle
        xs, ys = r.exterior.coords.xy
    except Exception:
        c = poly.centroid
        return np.array([[c.x, c.y]])
    p0 = np.array([xs[0], ys[0]])
    e1 = np.array([xs[1] - xs[0], ys[1] - ys[0]])
    e2 = np.array([xs[3] - xs[0], ys[3] - ys[0]])
    if np.hypot(*e1) < np.hypot(*e2):
        e1, e2 = e2, e1
    L = float(np.hypot(*e1))
    if L < 60:
        c = poly.centroid
        return np.array([[c.x, c.y]])
    k = int(min(k, max(2, L // 40)))
    out = []
    for i in range(k):
        a, b = p0 + e1 * (i / k), p0 + e1 * ((i + 1) / k)
        sl = Polygon([a - e2 * 0.05, b - e2 * 0.05, b + e2 * 1.05, a + e2 * 1.05])
        try:
            part = poly.intersection(sl)
        except Exception:
            continue
        if not part.is_empty and part.area > 1:
            out.append((part.centroid.x, part.centroid.y))
    if not out:
        c = poly.centroid
        out = [(c.x, c.y)]
    return np.array(out)


def _finish(co):
    co["G"] = np.asarray(co["G"], float).reshape(-1, 2)
    co["Gr"] = np.asarray(co["Gr"], float)
    co["Gp"] = np.asarray(co["Gp"], float)
    for t in co["T"]:
        t["pts"] = np.asarray(t["pts"], float).reshape(-1, 2)
        t["c"] = np.asarray(t["c"], float)
    polys = [f["poly"] for f in co["fair"]]
    co["fair_u"] = unary_union(polys) if polys else None
    co["park"] = np.asarray(co.get("park") or [], float).reshape(-1, 2)
    co.setdefault("pnext", {})
    return co


def _osm_context(fc, pj):
    """Fairways, car parks, clubhouse from an OSM feature collection (golf holes hidden or all golf stripped)."""
    fair, park, club, bld = [], [], [], []
    for f in (fc or {}).get("features", []):
        p = f.get("properties") or {}
        gk = p.get("golf")
        is_club = gk == "clubhouse" or p.get("building") == "clubhouse" or p.get("club") == "golf" and p.get("building")
        if not (gk == "fairway" or p.get("amenity") == "parking" or is_club):
            continue
        try:
            g = shape(f["geometry"])
        except Exception:
            continue
        if g.is_empty:
            continue
        rings = TR._outer(f["geometry"])
        if gk == "fairway":
            for r in rings:
                q = _poly(pj, r)
                if q is not None and q.area > 200:
                    fair.append(dict(poly=q, cl=centreline(q)))
        elif p.get("amenity") == "parking":
            c = g.centroid
            park.append(_xy(pj, (c.x, c.y)) + (g.area,))
        elif is_club:
            c = g.centroid
            club.append(_xy(pj, (c.x, c.y)))
    return fair, park, club


def _pick_club(co, park, club):
    """Clubhouse: a tagged one, else the scene's, else the biggest car park within 400 yd of a green."""
    if club:
        co["club"] = club[0]
        co["club_src"] = "tag"
    G = np.asarray(co["G"], float).reshape(-1, 2)
    pk = []
    for x, y, a in park:
        if len(G) and np.min(np.hypot(G[:, 0] - x, G[:, 1] - y)) < 400:
            pk.append((x, y, a))
    co["park"] = [(x, y) for x, y, a in pk]
    if co.get("club") is None and pk:
        x, y, a = max(pk, key=lambda q: q[2])
        co["club"] = (x, y)
        co["club_src"] = "parking"
    if co.get("club") is None:
        co["club_src"] = "none"


def from_scene(scene, fc=None):
    gs = scene.get("greens") or []
    if not gs:
        raise ValueError("no greens")
    lon0 = float(np.mean([g["centroid"][0] for g in gs]))
    lat0 = float(np.mean([g["centroid"][1] for g in gs]))
    pj = TR.Proj(lon0, lat0)
    co = dict(pj=pj, source="scene", G=[], Gr=[], Gp=[], Gid=[], T=[], fair=[], club=None)
    gi = {}
    for g in gs:
        gi[g["id"]] = len(co["G"])
        co["G"].append(_xy(pj, g["centroid"]))
        co["Gr"].append(math.sqrt(max(float(g.get("area_m2") or 300.0), 30.0) / math.pi) * M2YD)
        ph = float(g.get("p_hole", g.get("p", 1.0)))
        co["Gp"].append(min(ph, float(g.get("p", 1.0))) if g.get("kind") == "practice" else ph)
        co["Gid"].append(g["id"])
    ti = {}
    for t in scene.get("tee_complexes") or []:
        if t.get("virtual"):
            continue
        pts = [b["centroid"] for b in t.get("boxes", []) if b.get("centroid")] or [t["centroid"]]
        ax = None
        if t.get("axis_deg") is not None and float(t.get("length_m") or 0) > 12:
            a = math.radians(float(t["axis_deg"]))            # compass bearing -> (east, north)
            ax = (math.sin(a), math.cos(a))
        ti[t["id"]] = len(co["T"])
        co["T"].append(dict(c=_xy(pj, t["centroid"]), pts=[_xy(pj, q) for q in pts], id=t["id"], ax=ax,
                            p=float(t.get("p", 1.0)) * (1.0 - float(t.get("p_range_tee") or 0.0))))
    for f in scene.get("fairways") or []:
        q = _poly(pj, f["polygon"])
        if q is None:
            continue
        cl = np.array([_xy(pj, c) for c in (f.get("centerline") or [])]) if f.get("centerline") else centreline(q)
        co["fair"].append(dict(poly=q, cl=cl))
    ch = scene.get("clubhouse") or {}
    if ch.get("ll"):
        co["club"] = _xy(pj, ch["ll"])
        co["club_src"] = "scene"
        co["club_p"] = float(ch.get("p") or 0.0)
    park = [_xy(pj, p["centroid"]) + (float(p.get("area_m2") or 0),) for p in scene.get("parking") or []]
    _, opark, oclub = _osm_context(fc, pj)
    _pick_club(co, park + opark, [] if co["club"] is not None else oclub)
    co["pnext"] = {}
    for r in (scene.get("relations") or {}).get("green_to_tee") or []:
        if r["green"] in gi and r["tee"] in ti:
            co["pnext"][(gi[r["green"]], ti[r["tee"]])] = float(r.get("p_next") or 0.0)
    return _finish(co)


def from_truth(t, fc=None, seed=0):
    """True hole endpoints, shuffled, numbers hidden. -> Course (+ `_ref`: the hidden numbers, for tests only)."""
    hs = list(t["holes"])
    rng = np.random.default_rng(seed)
    og, ot = rng.permutation(len(hs)), rng.permutation(len(hs))
    lon0 = float(np.mean([h["green_ll"][0] for h in hs]))
    lat0 = float(np.mean([h["green_ll"][1] for h in hs]))
    pj = TR.Proj(lon0, lat0)
    co = dict(pj=pj, source="truth", G=[], Gr=[], Gp=[], Gid=[], T=[], fair=[], club=None)
    for j in og:
        h = hs[j]
        co["G"].append(_xy(pj, h["green_ll"]))
        co["Gr"].append(float(h.get("green_r_yd") or 12.0))
        co["Gp"].append(0.98)
        co["Gid"].append("g%d" % len(co["Gid"]))
    for j in ot:
        h = hs[j]
        q = _xy(pj, h["line"][0])
        co["T"].append(dict(c=q, pts=[q], id="t%d" % len(co["T"]), ax=None, p=0.98))
    fair, park, club = _osm_context(fc, pj)
    co["fair"] = fair
    _pick_club(co, park, club)
    return _finish(co)


def from_osm(fc, link=28.0):
    """OSM greens / tee boxes (holes hidden). Tee boxes within `link` yd of each other (edge to edge) = a complex."""
    feats = (fc or {}).get("features", [])
    gl = []
    for f in feats:
        if (f.get("properties") or {}).get("golf") == "green":
            rs = TR._outer(f["geometry"])
            if rs:
                gl.append(TR._centroid(rs[0]))
    if not gl:
        raise ValueError("no greens")
    pj = TR.Proj(float(np.mean([q[0] for q in gl])), float(np.mean([q[1] for q in gl])))
    co = dict(pj=pj, source="osm", G=[], Gr=[], Gp=[], Gid=[], T=[], fair=[], club=None)
    boxes = []
    for f in feats:
        p = f.get("properties") or {}
        gk = p.get("golf")
        if gk not in ("green", "tee"):
            continue
        fid = "%s/%s" % (p.get("osm_type", "x"), p.get("osm_id", "?"))
        if gk == "tee" and f["geometry"]["type"] == "Point":
            x, y = _xy(pj, f["geometry"]["coordinates"])
            boxes.append((Polygon([(x - 3, y - 3), (x + 3, y - 3), (x + 3, y + 3), (x - 3, y + 3)]), fid))
            continue
        for r in TR._outer(f["geometry"]):
            q = _poly(pj, r)
            if q is None:
                continue
            if gk == "green" and q.area > 30:
                co["G"].append((q.centroid.x, q.centroid.y))
                co["Gr"].append(math.sqrt(q.area / math.pi))
                co["Gp"].append(0.9)
                co["Gid"].append(fid)
            elif gk == "tee":
                boxes.append((q, fid))
    if not boxes:
        raise ValueError("no tees")
    par = list(range(len(boxes)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i][0].distance(boxes[j][0]) <= link:
                par[find(i)] = find(j)
    grp = {}
    for i in range(len(boxes)):
        grp.setdefault(find(i), []).append(i)
    for k, mem in grp.items():
        pts = [(boxes[i][0].centroid.x, boxes[i][0].centroid.y) for i in mem]
        c = tuple(np.mean(pts, 0))
        ax = None
        if len(pts) >= 2:
            d = np.asarray(pts) - np.asarray(c)
            w, v = np.linalg.eigh(d.T @ d)
            if w[1] > 15 ** 2:
                ax = (float(v[0, 1]), float(v[1, 1]))
        co["T"].append(dict(c=c, pts=pts, id=boxes[mem[0]][1], ax=ax, p=0.9))
    fair, park, club = _osm_context(fc, pj)
    co["fair"] = fair
    _pick_club(co, park, club)
    return _finish(co)


def label(co, t):
    """Truth labels for a Course (training / evaluation only): g2h[green] = true hole index or -1,
    t2h[tee] = set of true hole indices the complex is a tee of (bench tolerances)."""
    import bench as B
    M = B.Matcher(t)
    g2h, t2h = [], []
    for g in co["G"]:
        ll = co["pj"].inv(*g)
        p = M.pj.fwd(*ll)
        js = [j for j in range(len(M.holes)) if M.green_ok(j, p)]
        g2h.append(js[0] if js else -1)
    for tc in co["T"]:
        pts = [M.pj.fwd(*co["pj"].inv(*q)) for q in list(tc["pts"]) + [tc["c"]]]
        t2h.append({j for j in range(len(M.holes)) if M.tee_ok(j, pts)})
    refs = [(h["ref"], h.get("course")) for h in t["holes"]]
    return dict(g2h=g2h, t2h=t2h, refs=refs)
