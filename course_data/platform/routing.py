"""Hole routing inference: which tee -> green pair is hole 1, 2, ... 18 when OSM has no golf=hole ways.

    from routing import route, inputs_from_fc, to_hole_features
    inp = inputs_from_fc(fc, segment=seg_fc, pads=lidar_pads, boundary=course["boundary"])
    res = route(inp, card=normalised_scorecard)          # {"holes": {"1": {...}, ...}, "status", ...}
    fc2 = to_hole_features(res, fc)                      # fc + golf=hole LineStrings (+ model greens / tees)

    python course_data/platform/routing.py <osm.geojson> [--segment segment.geojson] [--card scorecard.json]
           [--hide-holes] [--out routing.json]          # offline; --hide-holes validates against the OSM ways

Inputs (`inputs_from_fc`): greens = OSM golf=green polygons + segment-model greens OSM lacks; tees = OSM golf=tee
boxes + segment-model tees + lidar flat pads (tees/lidar_pads.py) OSM lacks; fairways (OSM + model) for the
corridor term; the clubhouse (golf=clubhouse, a named club house / pro shop building, else the largest building
inside the course next to a car park, else the car park). `hide_holes=True` drops golf=hole ways and every
`ref` tag (the validation mode: nothing in the inputs names a hole).

Model. Hole n is a hypothesis (tee t, green g), or (no tee, g) / (nothing) at a fixed penalty when the
detectors missed it. Costs (all in yards):
  length    straight tee->green distance D vs the card yards Y of the closest tee set on hole n: z = (D - Y)
            / (4 % Y + 8) when D > Y; when D < Y the tolerance is 6 % Y + 10 on par 3s and 12 % Y + 15 on par
            4/5s (dog-legs: the card is measured along the line); cost min(z, 3.2)^2. Pars only: par ranges.
            No card: a 90-640 yd prior.
  walk      green(n) -> tee(n+1): ((max(0, d - 45)) / 85)^2, x0.3 at the turn (9 -> 10).
  corridor  par 4/5: 1.2 x the share of the line (25-85 % of the way) that is NOT fairway / green / tee
            (only when the course has fairway polygons); +1.5 when the line crosses another green.
  alignment an elongated tee polygon whose long axis is > 18 deg off the line: up to +1.5.
  clubhouse tee 1 (and less, tee 10, greens 9 and 18) far from the clubhouse: ((d - 150) / 160)^2.
Greens and tee boxes are used at most once. A beam search (width 3000) over the holes in card order with
dedupe on (last green, used greens) finds the cheapest routing; the final beam gives each hole a Boltzmann
marginal `p_green` (share of near-best routings that agree on its green) -> `check` when < 0.8.
Fixed anchors: holes whose OSM golf=hole way exists are pinned to it (production on partially mapped courses).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import numpy as np

YD = 0.9144
WALK_FREE, WALK_SCALE = 60.0, 110.0      # green -> next tee: free up to 60 yds, cost 1 at 170
ALIGN_FW_DEG = 35.0                      # a fairway the line runs along (else it crosses it)
CORRIDOR_BUF = 20.0                      # line points within 20 yds of a fairway count as on it (dog-legs)
COV_W = {"osm": 0.6, "segment": 0.25, "lidar": 0.15}   # reward per tee box explained by a hole
FINGERPRINT_W, FP_CAP = 1.0, 1.5         # tee-complex fingerprint vs every card set (see fingerprint)
REUSED_TEE = 2.5
CROSS_PEN = 1.5                          # per pair of hole lines that cross (rare on real courses)                         # two holes from one box (shared tee complexes exist)
COVERED_START = 2.0                      # a hole starting on a box another hole already explains
COV_PERP, COV_BACK, COV_FWD = 18.0, 40.0, 0.45         # a box is "on" a hole: <= 18 yds off the line, from
                                                       # 40 yds behind the tee to 65 % of the way to the green
BEAM = 3000
TOPK = 90
MISS_TEE = 4.0
MISS_HOLE = 8.0
PRACTICE_YD, PRACTICE_PEN = 45.0, 1.0
MODEL_GREEN_PEN = 0.6
P_CHECK = 0.8
PAR_RANGES = {3: (90, 260), 4: (240, 500), 5: (420, 660), 6: (560, 760)}


# ----------------------------------------------------------------------------- geometry
class Proj:
    """Local equirectangular projection in yards around (lon0, lat0)."""

    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = lon0, lat0
        self.kx = 111320.0 * math.cos(math.radians(lat0)) / YD
        self.ky = 110950.0 / YD

    def fwd(self, lon, lat):
        return ((np.asarray(lon, float) - self.lon0) * self.kx, (np.asarray(lat, float) - self.lat0) * self.ky)

    def inv(self, x, y):
        return (self.lon0 + np.asarray(x, float) / self.kx, self.lat0 + np.asarray(y, float) / self.ky)

    def ring(self, coords):
        a = np.asarray(coords, float)
        x, y = self.fwd(a[:, 0], a[:, 1])
        return np.c_[x, y]


def poly_centroid(xy):
    """Area centroid of a ring (n, 2) (vertex mean when degenerate)."""
    xy = np.asarray(xy, float)
    if len(xy) < 3:
        return xy.mean(0)
    x, y = xy[:, 0], xy[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    c = x * y1 - x1 * y
    a = c.sum() / 2
    if abs(a) < 1e-9:
        return xy.mean(0)
    return np.array([((x + x1) * c).sum() / (6 * a), ((y + y1) * c).sum() / (6 * a)])


def poly_area(xy):
    x, y = np.asarray(xy, float).T
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(np.roll(x, -1), y)) / 2


def long_axis(xy):
    """(axis angle in radians, elongation >= 1) of a polygon: its minimum rotated rectangle when shapely is
    available, else the vertex covariance."""
    xy = np.asarray(xy, float)
    if len(xy) < 3:
        return 0.0, 1.0
    try:
        from shapely.geometry import Polygon
        r = np.asarray(Polygon(xy).buffer(0).minimum_rotated_rectangle.exterior.coords)[:4]
        e1, e2 = r[1] - r[0], r[2] - r[1]
        l1, l2 = float(np.hypot(*e1)), float(np.hypot(*e2))
        if min(l1, l2) > 1e-6:
            e = e1 if l1 >= l2 else e2
            return math.atan2(e[1], e[0]), max(l1, l2) / min(l1, l2)
    except Exception:                                           # noqa: BLE001
        pass
    c = np.cov((xy - xy.mean(0)).T)
    w, v = np.linalg.eigh(c)
    if w[0] <= 1e-9:
        return math.atan2(v[1, 1], v[0, 1]), 10.0
    return math.atan2(v[1, 1], v[0, 1]), float(math.sqrt(w[1] / w[0]))


def _outer_rings(geom):
    t, c = geom.get("type"), geom.get("coordinates")
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [p[0] for p in c]
    return []


def _ll_of(geom):
    """Representative lon/lat of a GeoJSON geometry (polygon centroid, point, line midpoint)."""
    t, c = geom.get("type"), geom.get("coordinates")
    if t == "Point":
        return float(c[0]), float(c[1])
    rings = _outer_rings(geom)
    if rings:
        r = max(rings, key=len)
        a = np.asarray(r, float)
        lon0, lat0 = a[:, 0].mean(), a[:, 1].mean()
        p = Proj(lon0, lat0)
        cx, cy = poly_centroid(p.ring(r))
        lo, la = p.inv(cx, cy)
        return float(lo), float(la)
    if t == "LineString":
        a = np.asarray(c, float)
        return float(a[:, 0].mean()), float(a[:, 1].mean())
    return None


# ----------------------------------------------------------------------------- inputs
def _point_in_any(pt, rings):
    x, y = pt
    for r in rings:
        n, inside, j = len(r), False, len(r) - 1
        for i in range(n):
            xi, yi = r[i]
            xj, yj = r[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi:
                inside = not inside
            j = i
        if inside:
            return True
    return False


def clubhouse(fc, boundary_rings=()):
    """(lon, lat, how) of the clubhouse or None: golf=clubhouse / building=clubhouse / a building named club
    house, pro shop, clubhouse > the largest building inside the course within 120 yds of a car park > the
    car park (amenity=parking or parking aisles) nearest the course centre, inside or within 150 yds of it."""
    feats = [f for f in fc.get("features", []) if f.get("geometry")]
    allpts = [_ll_of(f["geometry"]) for f in feats if f["properties"].get("leisure") == "golf_course"]
    for f in feats:
        p = f["properties"]
        nm = str(p.get("name", "")).lower()
        if p.get("golf") == "clubhouse" or p.get("building") == "clubhouse" or p.get("club") == "golf" or \
                any(k in nm for k in ("clubhouse", "club house", "pro shop", "golf shop", "proshop")):
            ll = _ll_of(f["geometry"])
            if ll and (not boundary_rings or _near_rings(ll, boundary_rings, 200)):
                return ll[0], ll[1], "named"
    parks = []
    for f in feats:
        p = f["properties"]
        if p.get("amenity") == "parking" or p.get("service") == "parking_aisle" or p.get("parking"):
            ll = _ll_of(f["geometry"])
            if ll and (not boundary_rings or _near_rings(ll, boundary_rings, 150)):
                parks.append(ll)
    blds = []
    for f in feats:
        p = f["properties"]
        if p.get("building") and p.get("building") not in ("house", "residential", "apartments", "garage",
                                                           "detached", "shed", "roof"):
            rings = _outer_rings(f["geometry"])
            if not rings:
                continue
            ll = _ll_of(f["geometry"])
            if not ll or (boundary_rings and not _near_rings(ll, boundary_rings, 30)):
                continue
            pr = Proj(*ll)
            blds.append((poly_area(pr.ring(rings[0])), ll))
    if parks and blds:
        pr = Proj(*parks[0])
        best = None
        for a, ll in sorted(blds, reverse=True):
            bx, by = pr.fwd(*ll)
            for pl in parks:
                px, py = pr.fwd(*pl)
                if math.hypot(bx - px, by - py) < 120:
                    best = ll
                    break
            if best:
                return best[0], best[1], "building next to parking"
    if parks:
        if allpts and allpts[0]:
            c = allpts[0]
            pr = Proj(*c)
            parks.sort(key=lambda ll: math.hypot(*pr.fwd(*ll)))
        return parks[0][0], parks[0][1], "parking"
    return None


def _near_rings(ll, rings, yds):
    if _point_in_any(ll, rings):
        return True
    pr = Proj(*ll)
    for r in rings:
        a = pr.ring(r)
        if len(a) and np.hypot(a[:, 0], a[:, 1]).min() < yds:
            return True
    return False


def _feat_poly(f):
    rings = _outer_rings(f["geometry"])
    return max(rings, key=len) if rings else None


def inputs_from_fc(fc, segment=None, pads=None, boundary=None, hide_holes=False, min_p_green=0.6,
                   min_p_tee=0.5, use_segment_tees=True, osm_features=True):
    """-> dict(greens, tees, fairways, clubhouse, anchors, proj). Every green / tee is
    {id, ll (lon, lat), poly [[lon, lat]...] | None, src}. OSM features outside the course (inside_course False)
    are dropped; model / lidar features are kept when within 60 yds of the boundary. osm_features=False drops
    the OSM greens / tees / fairways (simulates an unmapped course: model + lidar only)."""
    rings = _outer_rings(boundary) if isinstance(boundary, dict) else (boundary or [])
    feats = [f for f in fc.get("features", []) if f.get("geometry")]
    inside = [f for f in feats if f["properties"].get("inside_course") is not False]
    greens, tees, fairways, anchors = [], [], [], {}
    for f in inside:
        p = f["properties"]
        g = p.get("golf")
        if not osm_features and g in ("green", "tee", "fairway"):
            continue
        if g == "green":
            poly = _feat_poly(f)
            ll = _ll_of(f["geometry"])
            if ll:
                greens.append(dict(id=f"osm:{p.get('osm_type', 'way')}/{p.get('osm_id')}", ll=ll, poly=poly, src="osm",
                                   ref=None if hide_holes else p.get("ref")))
        elif g == "tee":
            poly = _feat_poly(f)
            ll = _ll_of(f["geometry"])
            if ll:
                tees.append(dict(id=f"osm:{p.get('osm_type', 'way')}/{p.get('osm_id')}", ll=ll, poly=poly, src="osm",
                                 ref=None if hide_holes else p.get("ref")))
        elif g == "fairway":
            for r in _outer_rings(f["geometry"]):
                fairways.append(dict(poly=r, src="osm"))
        elif g == "hole" and not hide_holes and f["geometry"]["type"] == "LineString" and p.get("ref"):
            anchors[str(p["ref"])] = dict(line=f["geometry"]["coordinates"], par=p.get("par"))
    allll = [g["ll"] for g in greens + tees] or ([tuple(np.asarray(rings[0], float).mean(0))] if rings else [])
    if not allll and segment:
        allll = [_ll_of(f["geometry"]) for f in segment.get("features", []) if f.get("geometry")][:50]
    if not allll:
        return dict(greens=[], tees=[], fairways=[], clubhouse=None, anchors=anchors, proj=None)
    a = np.asarray([ll for ll in allll if ll], float)
    pr = Proj(float(a[:, 0].mean()), float(a[:, 1].mean()))

    def near_existing(ll, items, yds):
        if not items:
            return False
        x, y = pr.fwd(*ll)
        pts = np.asarray([pr.fwd(*i["ll"]) for i in items])
        return bool((np.hypot(pts[:, 0] - x, pts[:, 1] - y) < yds).any())

    def in_course(ll):
        return not rings or _near_rings(ll, rings, 60)

    if segment:
        osm_greens = list(greens)
        for i, f in enumerate(segment.get("features", [])):
            p = f.get("properties", {})
            cls = p.get("class")
            ll = _ll_of(f["geometry"]) if f.get("geometry") else None
            if not ll or not in_course(ll):
                continue
            poly = _feat_poly(f)
            if cls == "green" and float(p.get("p", 1)) >= min_p_green and 150 <= float(p.get("area_m2", 400)) <= 3000:
                if not near_existing(ll, osm_greens, 35) and not (poly and any(
                        _point_in_any(g["ll"], [g["poly"]]) for g in osm_greens if g["poly"] and
                        _point_in_any(g["ll"], [poly]))):
                    greens.append(dict(id=f"segment:{i}", ll=ll, poly=poly, src="segment", p=p.get("p")))
            elif cls == "tee" and use_segment_tees and float(p.get("p", 1)) >= min_p_tee and \
                    float(p.get("area_m2", 100)) >= 40:
                if not near_existing(ll, [t for t in tees if t["src"] == "osm"], 10):
                    tees.append(dict(id=f"segment:{i}", ll=ll, poly=poly, src="segment", p=p.get("p")))
            elif cls == "fairway" and float(p.get("p", 1)) >= 0.5 and poly:
                fairways.append(dict(poly=poly, src="segment"))
    for i, pd in enumerate(pads or []):
        c = pd.get("centroid")
        ll = (c[1], c[0]) if c else None                    # lidar_pads: (lat, lon)
        if not ll or not in_course(ll) or near_existing(ll, tees, 10):
            continue
        poly = [[q[1], q[0]] for q in pd.get("coords", [])] or None
        tees.append(dict(id=pd.get("id", f"lidar:{i}"), ll=ll, poly=poly, src="lidar"))
    # a "tee" on a green is the model confusing a collar / an apron
    tees = [t for t in tees if not any(g["poly"] and _point_in_any(t["ll"], [g["poly"]]) for g in greens)
            and not near_existing(t["ll"], greens, 8)]
    ch = clubhouse(fc, rings)
    return dict(greens=greens, tees=tees, fairways=fairways, clubhouse=ch, anchors=anchors, proj=pr)


# ----------------------------------------------------------------------------- card
def card_holes(card):
    """normalised scorecard (scorecard/1) | {"par": [...], "yards": {set: [...]}} | None ->
    (n_holes, pars [n] (None items allowed), yards [n][sets])."""
    if not card:
        return None, None, None
    pars = card.get("par")
    sets = card.get("tee_sets") or {}
    ys = card.get("yards") if isinstance(card.get("yards"), dict) else {k: v.get("yards") for k, v in sets.items()}
    ys = {k: v for k, v in (ys or {}).items() if v}
    if not pars:
        pars = next((v.get("par") for v in sets.values() if v.get("par")), None)
    n = len(pars) if pars else (max(len(v) for v in ys.values()) if ys else None)
    if not n:
        return None, None, None
    yards = []
    for i in range(n):
        row = sorted({int(v[i]) for v in ys.values() if i < len(v) and v[i] and 60 <= int(v[i]) <= 800})
        yards.append(row)
    pars = [int(p) if p and str(p).isdigit() else None for p in (pars or [None] * n)]
    return n, pars, yards


def fingerprint(DB, yards, par):
    """Mean over the card's tee sets of how well SOME box on the hole sits at that set's yardage (0..1.5 each):
    a hole whose boxes match 3 of 3 card sets beats one where a single box happens to fit."""
    tot = np.zeros(DB.shape[:2])
    for Y in yards:
        dd = DB - Y
        tol = np.where(dd >= 0, 0.04 * Y + 8, (0.06 * Y + 10) if par == 3 else (0.12 * Y + 15))
        z = np.abs(dd) / tol
        with np.errstate(all="ignore"):
            zmin = np.nanmin(np.where(np.isnan(DB), np.inf, z), axis=2)
        tot += np.minimum(zmin ** 2, FP_CAP)
    return tot / len(yards)


def length_cost(D, yards, par):
    """(cost, matched card yards or None) for straight distance(s) D (array) on a hole."""
    D = np.asarray(D, float)
    if yards:
        best = np.full(D.shape, np.inf)
        which = np.zeros(D.shape)
        for Y in yards:
            over = (D - Y) / (0.04 * Y + 8)
            short = (Y - D) / ((0.06 * Y + 10) if par == 3 else (0.12 * Y + 15))
            z = np.where(D >= Y, over, short)
            c = np.minimum(z, 3.2) ** 2
            upd = c < best
            best = np.where(upd, c, best)
            which = np.where(upd, Y, which)
        return best, which
    lo, hi = PAR_RANGES.get(par, (90, 640))
    z = np.where(D < lo, (lo - D) / 25.0, np.where(D > hi, (D - hi) / 25.0, 0.0))
    return np.minimum(z, 3.2) ** 2, np.full(D.shape, np.nan)


# ----------------------------------------------------------------------------- routing
def _fairway_shapes(polys_xy):
    """[(contains_xy(x, y) on the polygon buffered CORRIDOR_BUF, long-axis angle, elongation)] per fairway."""
    try:
        from shapely import contains_xy, prepare
        from shapely.geometry import Polygon
    except ImportError:
        return []
    out = []
    for p in polys_xy:
        if len(p) < 4:
            continue
        g = Polygon(p)
        if not g.is_valid:
            g = g.buffer(0)
        if g.is_empty or g.area < 300:
            continue
        ang, el = long_axis(np.asarray(g.minimum_rotated_rectangle.exterior.coords)[:-1])
        b = g.buffer(CORRIDOR_BUF, 6)
        prepare(b)
        out.append(((lambda x, y, b=b: contains_xy(b, x, y)), ang, el))
    return out


def _prep_union(polys_xy, buffer=0.0):
    try:
        from shapely import contains_xy, prepare
        from shapely.geometry import Polygon
        from shapely.ops import unary_union
    except ImportError:
        return None
    ps = []
    for p in polys_xy:
        if len(p) >= 3:
            g = Polygon(p)
            if not g.is_valid:
                g = g.buffer(0)
            if not g.is_empty:
                ps.append(g)
    if not ps:
        return None
    u = unary_union(ps)
    if buffer:
        u = u.buffer(buffer, 8)
    prepare(u)
    return lambda x, y: contains_xy(u, x, y)


def route(inp, card=None, n_holes=None, beam=BEAM, use_anchors=True, clubhouse_ll="auto", force=None):
    """Infer the routing. -> dict(status, n_holes, holes {ref: {...}}, cost, unused_greens, method, inputs).
    force {ref: (tee index | -1, green index | -1)}: score a given routing instead of searching (diagnostics)."""
    pr = inp.get("proj")
    G, T = inp["greens"], inp["tees"]
    if pr is None or not G:
        return dict(status="no greens", n_holes=0, holes={}, cost=None, method="routing/1")
    n, pars, yards = card_holes(card)
    if n is None:
        ng = len(G)
        n = n_holes or (18 if ng >= 13 else 9)
        pars, yards = [None] * n, [[] for _ in range(n)]
    gxy = np.asarray([pr.fwd(*g["ll"]) for g in G], float).reshape(-1, 2)
    txy = np.asarray([pr.fwd(*t["ll"]) for t in T], float).reshape(-1, 2)
    nG, nT = len(G), len(T)
    D = np.hypot(txy[:, None, 0] - gxy[None, :, 0], txy[:, None, 1] - gxy[None, :, 1]) if nT else np.zeros((0, nG))
    W = np.hypot(gxy[:, None, 0] - txy[None, :, 0], gxy[:, None, 1] - txy[None, :, 1]) if nT else np.zeros((nG, 0))
    walk = np.minimum((np.maximum(W - WALK_FREE, 0) / WALK_SCALE) ** 2, 9.0)
    # practice greens: a green with others within 45 yds (putting / chipping greens by the clubhouse)
    GG = np.hypot(gxy[:, None, 0] - gxy[None, :, 0], gxy[:, None, 1] - gxy[None, :, 1])
    gpen = np.minimum(((GG < PRACTICE_YD).sum(1) - 1) * PRACTICE_PEN, 2 * PRACTICE_PEN)
    # model greens are less certain than mapped ones (false positives on tees / approaches)
    gpen = gpen + np.array([0.0 if g["src"] == "osm" else MODEL_GREEN_PEN + 2.0 * (1.0 - float(g.get("p") or 0.8))
                            for g in G])
    wt = np.array([COV_W.get(t["src"], 0.2) for t in T])
    tee_axes = np.array([long_axis(pr.ring(t["poly"])) if t.get("poly") and len(t["poly"]) >= 4 else (0.0, 1.0)
                         for t in T]).reshape(-1, 2)
    ch = inp.get("clubhouse") if clubhouse_ll == "auto" else clubhouse_ll
    chxy = np.asarray(pr.fwd(ch[0], ch[1])) if ch else None

    def ch_cost(xy, w):
        if chxy is None or not w:
            return np.zeros(np.asarray(xy).shape[:-1])
        d = np.hypot(xy[..., 0] - chxy[0], xy[..., 1] - chxy[1])
        return w * np.minimum((np.maximum(d - 150, 0) / 160) ** 2, 6.0)

    # corridor (fairway share) and other-green crossings, per (t, g)
    fws = _fairway_shapes([pr.ring(f["poly"]) for f in inp.get("fairways", [])])
    has_fw = bool(inp.get("fairways"))
    cand = D < 760
    corr = np.zeros_like(D)
    cross = np.zeros_like(D)
    fr = np.linspace(0.25, 0.85, 9)
    ti, gi = np.nonzero(cand)
    if len(ti):
        px = txy[ti, 0][:, None] + (gxy[gi, 0] - txy[ti, 0])[:, None] * fr[None]
        py = txy[ti, 1][:, None] + (gxy[gi, 1] - txy[ti, 1])[:, None] * fr[None]
        if fws:
            bear = np.arctan2(gxy[gi, 1] - txy[ti, 1], gxy[gi, 0] - txy[ti, 0])
            on = np.zeros(px.shape, bool)
            off = np.zeros(px.shape, bool)
            for test, ang, el in fws:
                hit = test(px.ravel(), py.ravel()).reshape(px.shape)
                dang = np.abs((bear - ang + np.pi / 2) % np.pi - np.pi / 2)
                aligned = (dang < math.radians(ALIGN_FW_DEG)) | (el < 1.6)
                on |= hit & aligned[:, None]
                off |= hit & ~aligned[:, None]
            corr[ti, gi] = (1.0 - on.mean(1)) + 0.7 * (off & ~on).mean(1)
        fr2 = np.linspace(0.15, 0.92, 24)
        qx = txy[ti, 0][:, None] + (gxy[gi, 0] - txy[ti, 0])[:, None] * fr2[None]
        qy = txy[ti, 1][:, None] + (gxy[gi, 1] - txy[ti, 1])[:, None] * fr2[None]
        for k in range(nG):
            dk = np.hypot(qx - gxy[k, 0], qy - gxy[k, 1]).min(1)
            hit = (dk < 12) & (gi != k)
            cross[ti[hit], gi[hit]] = 1.5
    # tee-box alignment
    align = np.zeros_like(D)
    for i, t in enumerate(T):
        if not t.get("poly") or len(t["poly"]) < 4:
            continue
        ang, el = long_axis(pr.ring(t["poly"]))
        if el < 1.4:
            continue
        b = np.arctan2(gxy[:, 1] - txy[i, 1], gxy[:, 0] - txy[i, 0])
        d = np.abs((b - ang + np.pi / 2) % np.pi - np.pi / 2)
        align[i] = np.minimum((np.maximum(np.degrees(d) - 20, 0) / 20) ** 2, 1.6) * 0.5

    anchors = inp.get("anchors", {}) if use_anchors else {}
    # tee-complex fingerprint: distances to g of every box on the hole (t, g)
    DB = None
    if nT and nT * nT * nG <= 6_000_000:
        dv = gxy[None, :, :] - txy[:, None, :]                       # (t, g, 2)
        L = np.maximum(np.hypot(dv[..., 0], dv[..., 1]), 1e-6)
        rel = txy[None, None, :, :] - txy[:, None, None, :]          # (t, 1, b, 2)
        u = (rel[..., 0] * dv[:, :, None, 0] + rel[..., 1] * dv[:, :, None, 1]) / L[..., None]
        v = np.abs(rel[..., 0] * dv[:, :, None, 1] - rel[..., 1] * dv[:, :, None, 0]) / L[..., None]
        on = (u >= -COV_BACK) & (u <= COV_FWD * L[..., None]) & (v <= COV_PERP)
        DB = np.where(on, D.T[None, :, :], np.nan)                   # D.T[g, b] -> (t, g, b)
    # hypotheses per hole: (t, g, cost, matched yards)
    hyps = []
    for h in range(n):
        ref = str(h + 1)
        par = pars[h] if pars else None
        rows = []
        if ref in anchors:
            line = np.asarray(anchors[ref]["line"], float)
            sx, sy = pr.fwd(*line[0])
            ex, ey = pr.fwd(*line[-1])
            gk = int(np.argmin(np.hypot(gxy[:, 0] - ex, gxy[:, 1] - ey)))
            tk = int(np.argmin(np.hypot(txy[:, 0] - sx, txy[:, 1] - sy))) if nT else -1
            if tk >= 0 and math.hypot(txy[tk, 0] - sx, txy[tk, 1] - sy) > 40:
                tk = -1
            hyps.append([(tk, gk, 0.0, float("nan"))])
            continue
        if nT:
            lc, which = length_cost(D, yards[h] if yards else None, par)
            c = lc + align + (FINGERPRINT_W * fingerprint(DB, yards[h], par) if (yards and yards[h] and DB is not None)
                              else 0.0)
            if par != 3:
                c = c + (1.2 * corr if has_fw else 0) + cross
            else:
                c = c + cross
            c = c + ch_cost(txy, 1.0 if h == 0 else (0.6 if h == 9 and n >= 18 else 0.0))[:, None]
            c = c + ch_cost(gxy, 0.5 if (h == n - 1 or (h == 8 and n >= 18)) else 0.0)[None, :]
            c = c + gpen[None, :]
            ok = (lc < 9.5) & cand
            if force and ref in force:
                ok = np.zeros_like(ok)
                if force[ref][0] >= 0 and force[ref][1] >= 0:
                    ok[force[ref][0], force[ref][1]] = True
            ti, gi = np.nonzero(ok)
            cc = c[ti, gi]
            order = np.argsort(cc)[:TOPK]
            rows = [(int(ti[o]), int(gi[o]), float(cc[o]), float(which[ti[o], gi[o]])) for o in order]
        for k in range(nG):
            if force and ref in force and (force[ref][0] >= 0 or force[ref][1] != k):
                continue
            rows.append((-1, k, MISS_TEE + float(ch_cost(gxy[k], 0.5 if h == n - 1 else 0.0)), float("nan")))
        rows.append((-1, -1, MISS_HOLE, float("nan")))
        hyps.append(rows)
    covs = []
    for rows in hyps:
        cv = np.zeros((len(rows), nT))
        for j, (tk, gk, _, _) in enumerate(rows):
            if tk >= 0 and gk >= 0:
                cv[j] = _on_hole(txy, txy[tk], gxy[gk], tee_axes) * wt
        covs.append(cv)

    # crossing lines: unique (t, g) pairs over all holes, pairwise proper intersections
    pairs = sorted({(r[0], r[1]) for rows in hyps for r in rows if r[0] >= 0 and r[1] >= 0})
    pidx = {p: i for i, p in enumerate(pairs)}
    hp = [np.array([pidx.get((r[0], r[1]), -1) for r in rows]) for rows in hyps]
    X = _crossings(np.array([txy[p[0]] for p in pairs]).reshape(-1, 2),
                   np.array([gxy[p[1]] for p in pairs]).reshape(-1, 2)) if pairs else np.zeros((0, 0), bool)
    NP = len(pairs)
    # beam search
    S_x = np.zeros((1, NP + 1), np.int16)       # how many chosen lines each pair would cross
    S_cost = np.zeros(1)
    S_g = np.zeros((1, nG + 1), bool)          # last column: dummy for -1
    S_t = np.zeros((1, nT + 1), bool)
    S_c = np.zeros((1, nT), float)              # tee boxes already explained (weights)
    S_last = np.array([-1])
    S_gap = np.array([False])
    back = []
    for h in range(n):
        rows = hyps[h]
        ht = np.array([r[0] for r in rows])
        hg = np.array([r[1] for r in rows])
        hc = np.array([r[2] for r in rows])
        # transition from the state's last green to the hypothesis tee
        tr = np.zeros((len(S_cost), len(rows)))
        lastok = S_last >= 0
        teeok = ht >= 0
        if lastok.any() and teeok.any():
            sub = walk[np.ix_(S_last[lastok], ht[teeok])]
            if h == 9 and n >= 18:
                sub = sub * 0.3
            sub = sub * np.where(S_gap[lastok], 0.4, 1.0)[:, None]
            tr[np.ix_(lastok, teeok)] = sub
        cv = covs[h]
        gain = cv.sum(1)[None, :] - (S_c > 0).astype(float) @ cv.T if nT else 0.0
        tot = S_cost[:, None] + hc[None, :] + tr - gain + CROSS_PEN * S_x[:, hp[h]] * (hp[h] >= 0)[None, :]
        usedg = S_g[:, hg]                      # hg == -1 -> last column (never set)
        usedt = S_t[:, ht]
        tot = tot + COVERED_START * np.c_[S_c > 0, np.zeros((len(S_cost), 1), bool)][:, ht] * (ht >= 0)[None, :]
        bad = usedg & (hg >= 0)[None, :]
        tot = tot + REUSED_TEE * (usedt & (ht >= 0)[None, :])
        tot = np.where(bad, np.inf, tot)
        flat = tot.ravel()
        k = min(len(flat), beam * 4)
        idx = np.argpartition(flat, k - 1)[:k] if k < len(flat) else np.arange(len(flat))
        idx = idx[np.argsort(flat[idx])]
        seen, keep = set(), []
        for q in idx:
            if not np.isfinite(flat[q]):
                break
            s, r = divmod(int(q), len(rows))
            key = (int(hg[r]), S_g[s].tobytes() if hg[r] < 0 else (S_g[s] | _onehot(nG + 1, hg[r])).tobytes())
            if key in seen:
                continue
            seen.add(key)
            keep.append((s, r))
            if len(keep) >= beam:
                break
        ss = np.array([s for s, _ in keep])
        rr = np.array([r for _, r in keep])
        S_cost = flat[ss * len(rows) + rr]
        S_g = S_g[ss].copy()
        S_t = S_t[ss].copy()
        S_c = np.maximum(S_c[ss], cv[rr]) if nT else S_c[ss]
        S_x = S_x[ss].copy()
        pk = hp[h][rr]
        okp = pk >= 0
        if okp.any():
            S_x[np.nonzero(okp)[0], :NP] += X[pk[okp]]
        ok = hg[rr] >= 0
        S_g[np.nonzero(ok)[0], hg[rr][ok]] = True
        ok = ht[rr] >= 0
        S_t[np.nonzero(ok)[0], ht[rr][ok]] = True
        S_gap = hg[rr] < 0
        S_last = np.where(hg[rr] >= 0, hg[rr], S_last[ss])
        back.append((ss, rr))

    def trace(i):
        seq = []
        for h in range(n - 1, -1, -1):
            ss, rr = back[h]
            seq.append(int(rr[i]))
            i = int(ss[i])
        return seq[::-1]

    best = trace(0)
    m = min(len(S_cost), 400)
    w = np.exp(-(S_cost[:m] - S_cost[0]) / 1.0)
    seqs = [trace(i) for i in range(m)]
    holes = {}
    covered = np.zeros(nT)
    for h in range(n):
        tk, gk, c, Y = hyps[h][best[h]]
        cvb = covs[h][best[h]]
        gain_h = float((cvb * (covered <= 0)).sum()) if nT else 0.0
        covered = np.maximum(covered, cvb) if nT else covered
        agree = sum(w[i] for i in range(m) if hyps[h][seqs[i][h]][1] == gk) / w.sum()
        ent = dict(ref=str(h + 1), par=pars[h] if pars else None, card_yards=yards[h] if yards else [],
                   cost=round(c, 3), cover_gain=round(gain_h, 2), p_green=round(float(agree), 3),
                   anchored=str(h + 1) in anchors)
        if gk >= 0:
            ent.update(green_id=G[gk]["id"], green_ll=list(G[gk]["ll"]), green_src=G[gk]["src"])
        if tk >= 0:
            ent.update(tee_id=T[tk]["id"], tee_ll=list(T[tk]["ll"]), tee_src=T[tk]["src"])
        if gk >= 0 and tk >= 0:
            ent.update(straight_yd=round(float(D[tk, gk]), 1), matched_card_yd=None if math.isnan(Y) else Y)
        if h > 0:
            pg = hyps[h - 1][best[h - 1]][1]
            if pg >= 0 and tk >= 0:
                ent["walk_from_prev_green_yd"] = round(float(W[pg, tk]), 1)
                ent["walk_cost"] = round(float(walk[pg, tk]) * (0.3 if h == 9 and n >= 18 else 1), 3)
        flags = []
        if gk < 0:
            flags.append("no green found")
        if tk < 0:
            flags.append("no tee found")
        if agree < P_CHECK:
            flags.append(f"ambiguous ({agree:.0%} of near-best routings agree)")
        if ent.get("straight_yd") and yards and yards[h] and c > 4:
            flags.append("length off the card")
        ent["flags"] = flags
        ent["status"] = "ok" if not flags else "check"
        holes[str(h + 1)] = ent
    used = {hyps[h][best[h]][1] for h in range(n)}
    if force is not None:
        inp["_debug"] = dict(D=D, corr=corr, cross=cross, align=align, walk=walk, W=W)
    return dict(method="routing/1", status="ok", n_holes=n, card=bool(yards and any(yards)),
                cost=round(float(S_cost[0]), 3), holes=holes,
                n_check=sum(1 for v in holes.values() if v["status"] != "ok"),
                unused_greens=[G[k]["id"] for k in range(nG) if k not in used],
                clubhouse=list(ch) if ch else None,
                inputs=dict(greens=nG, greens_osm=sum(g["src"] == "osm" for g in G), tees=nT,
                            tees_by_src={s: sum(t["src"] == s for t in T) for s in ("osm", "segment", "lidar")},
                            fairways=len(inp.get("fairways", [])), anchors=len(anchors)))


def _crossings(a, b):
    """(P, P) int16: segment i (a[i] -> b[i]) properly crosses segment j, ignoring touches within 10 yds of
    an end (a hole's green is next to the following tee)."""
    P = len(a)
    if P == 0:
        return np.zeros((0, 0), np.int16)
    d = b - a
    L = np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-6)
    rx = a[None, :, 0] - a[:, None, 0]
    ry = a[None, :, 1] - a[:, None, 1]
    den = d[:, None, 0] * d[None, :, 1] - d[:, None, 1] * d[None, :, 0]
    with np.errstate(all="ignore"):
        ti = (rx * d[None, :, 1] - ry * d[None, :, 0]) / den
        tj = (rx * d[:, None, 1] - ry * d[:, None, 0]) / den
        mi = 10.0 / L[:, None]
        mj = 10.0 / L[None, :]
        x = (np.abs(den) > 1e-9) & (ti > mi) & (ti < 1 - mi) & (tj > mj) & (tj < 1 - mj)
    np.fill_diagonal(x, False)
    return x.astype(np.int16)


def _on_hole(pts, t, g, axes=None):
    """bool per point: within COV_PERP of the tee->green line, from COV_BACK behind the tee to COV_FWD of it,
    and (elongated boxes) with the long axis within 30 deg of the line."""
    d = g - t
    L = max(float(np.hypot(*d)), 1e-6)
    u = ((pts - t) @ d) / L
    v = np.abs((pts[:, 0] - t[0]) * d[1] - (pts[:, 1] - t[1]) * d[0]) / L
    ok = (u >= -COV_BACK) & (u <= COV_FWD * L) & (v <= COV_PERP)
    if axes is not None and len(axes):
        b = math.atan2(d[1], d[0])
        da = np.abs((b - axes[:, 0] + np.pi / 2) % np.pi - np.pi / 2)
        ok &= (axes[:, 1] < 1.4) | (da < math.radians(30))
    return ok


def _onehot(n, k):
    a = np.zeros(n, bool)
    a[k] = True
    return a


# ----------------------------------------------------------------------------- outputs
def to_hole_features(res, fc, inp=None):
    """fc + one golf=hole LineString per routed hole (tee -> green, tags ref / par / source=routing) + the
    model greens / tees the routing used as golf=green / golf=tee polygons, so platform/package.py builds them."""
    out = dict(fc, features=list(fc.get("features", [])))
    have = {str(f["properties"].get("ref")) for f in out["features"]
            if f["properties"].get("golf") == "hole" and f["properties"].get("ref")}
    byid = {x["id"]: x for x in ((inp or {}).get("greens", []) + (inp or {}).get("tees", []))}
    added = set()
    for ref, h in res.get("holes", {}).items():
        for kind in ("green", "tee"):
            i = h.get(f"{kind}_id")
            if i and not i.startswith("osm:") and i not in added and i in byid and byid[i].get("poly"):
                poly = [list(p) for p in byid[i]["poly"]]
                if poly[0] != poly[-1]:
                    poly.append(poly[0])
                out["features"].append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[poly]),
                                            properties=dict(golf=kind, source=f"routing:{byid[i]['src']}",
                                                            osm_id=i, osm_type="model", inside_course=True)))
                added.add(i)
        if ref in have or not h.get("tee_ll") or not h.get("green_ll"):
            continue
        props = dict(golf="hole", ref=ref, source="routing", inside_course=True, osm_type="routing",
                     osm_id=f"routing:{ref}", routing_status=h["status"])
        if h.get("par"):
            props["par"] = str(h["par"])
        out["features"].append(dict(type="Feature", properties=props,
                                    geometry=dict(type="LineString", coordinates=[list(h["tee_ll"]), list(h["green_ll"])])))
    return out


# ----------------------------------------------------------------------------- validation
def truth_from_fc(fc):
    """{ref: {tee_ll, green_ll, line, length_yd, par}} from the OSM golf=hole ways (numeric refs only)."""
    out = {}
    for f in fc.get("features", []):
        p = f["properties"]
        if p.get("golf") == "hole" and f["geometry"]["type"] == "LineString" and str(p.get("ref", "")).isdigit():
            c = f["geometry"]["coordinates"]
            pr = Proj(*c[0])
            xy = pr.ring(c)
            out[str(int(p["ref"]))] = dict(tee_ll=tuple(c[0]), green_ll=tuple(c[-1]), line=c,
                                           length_yd=float(np.hypot(*np.diff(xy, axis=0).T).sum()),
                                           par=int(p["par"]) if str(p.get("par", "")).isdigit() else None)
    return out


def _seg_dist(p, line_xy):
    """Distance (yds) from p to a polyline."""
    best = np.inf
    for a, b in zip(line_xy[:-1], line_xy[1:]):
        ab = b - a
        t = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-9), 0, 1)
        best = min(best, float(np.hypot(*(a + t * ab - p))))
    return best


def score(res, truth, green_tol=20.0, tee_tol=40.0):
    """Routing vs the OSM ways. Per hole: green_ok (routed green within green_tol yds of the true line's end),
    hole_ok (green_ok and the routed tee within tee_tol yds of the first 60 % of the true line), length error
    (routed straight tee->green vs the true line's straight start->end). Physical holes: true holes whose
    green + tee appear in the routing under any number."""
    per = {}
    found = 0
    pairs = [(h.get("tee_ll"), h.get("green_ll")) for h in res.get("holes", {}).values()]
    for ref, t in truth.items():
        pr = Proj(*t["green_ll"])
        line = pr.ring(t["line"])
        cum = np.r_[0, np.cumsum(np.hypot(*np.diff(line, axis=0).T))]
        first = line[: max(2, int(np.searchsorted(cum, 0.6 * cum[-1])) + 1)]
        h = res.get("holes", {}).get(ref, {})

        def g_ok(gll):
            return gll is not None and math.hypot(*pr.fwd(*gll)) <= green_tol

        def t_ok(tll):
            return tll is not None and _seg_dist(np.asarray(pr.fwd(*tll)), first) <= tee_tol
        gok = g_ok(h.get("green_ll"))
        hok = gok and t_ok(h.get("tee_ll"))
        e = dict(green_ok=bool(gok), hole_ok=bool(hok))
        if h.get("tee_ll") and h.get("green_ll"):
            sx, sy = pr.fwd(*t["tee_ll"])
            # true length from the routed tee: along the true line from the routed tee's projection on it
            p = np.asarray(pr.fwd(*h["tee_ll"]))
            best, along = np.inf, 0.0
            for i, (a, b) in enumerate(zip(line[:-1], line[1:])):
                ab = b - a
                u = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-9), 0, 1)
                dd = float(np.hypot(*(a + u * ab - p)))
                if dd < best:
                    best, along = dd, cum[-1] - (cum[i] + u * float(np.hypot(*ab)))
            e["length_err_yd"] = round(abs(h["straight_yd"] - along), 1) if hok else None
            e["tee_err_yd"] = round(math.hypot(*np.subtract(p, (sx, sy))), 1)
        per[ref] = e
        if any(gl is not None and tl is not None and g_ok(gl) and t_ok(tl) for tl, gl in pairs):
            found += 1
    n = max(len(truth), 1)
    le = [e["length_err_yd"] for e in per.values() if e.get("length_err_yd") is not None]
    flagged = {r for r, h in res.get("holes", {}).items() if h.get("status") != "ok"}
    wrong = {r for r, e in per.items() if not e["hole_ok"]}
    return dict(n_true=len(truth), hole_number_acc=round(sum(e["hole_ok"] for e in per.values()) / n, 3),
                green_assign_acc=round(sum(e["green_ok"] for e in per.values()) / n, 3),
                physical_holes_found=round(found / n, 3),
                median_length_err_yd=round(float(np.median(le)), 1) if le else None,
                p90_length_err_yd=round(float(np.percentile(le, 90)), 1) if le else None,
                all_correct=len(wrong) == 0 and len(truth) > 0,
                flagged=len(flagged), wrong=len(wrong), wrong_unflagged=len(wrong - flagged),
                flag_precision=round(len(wrong & flagged) / len(flagged), 3) if flagged else None,
                per_hole=per)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("osm")
    ap.add_argument("--segment")
    ap.add_argument("--pads")
    ap.add_argument("--card", help="scorecard/1 json (or scorecard_web.json: the first card)")
    ap.add_argument("--course", help="raw/course.json (boundary)")
    ap.add_argument("--hide-holes", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    rd = lambda p: json.load(open(p)) if p and os.path.exists(p) else None      # noqa: E731
    fc = rd(a.osm)
    card = rd(a.card)
    if card and "cards" in card:
        card = card["cards"][0]["card"] if card["cards"] else None
    course = rd(a.course) or {}
    inp = inputs_from_fc(fc, segment=rd(a.segment), pads=rd(a.pads), boundary=course.get("boundary"),
                         hide_holes=a.hide_holes)
    res = route(inp, card)
    if a.hide_holes:
        res["validation"] = score(res, truth_from_fc(fc))
        print(json.dumps({k: v for k, v in res["validation"].items() if k != "per_hole"}))
    for r, h in res["holes"].items():
        print(r, h.get("par"), h.get("card_yards"), h.get("straight_yd"), h.get("green_src"), h.get("tee_src"),
              h["p_green"], h["flags"])
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
