"""Build-time sanity guards for recurring pipeline errors found by the course reviews (library/*/review.md).

  clean_osm(fc)            OSM input cleanup before anything is built:
                           * practice tees: a golf=tee whose name / description mentions range, practice or
                             driving, or that lies inside a golf=driving_range area, is dropped (Ironhorse 1: the
                             Black tee sat on "Driving Range Tee Box (Turf)")
                           * hole ways of a neighbouring course: when refs are duplicated or there are more than
                             18 golf=hole ways, ways outside this course's boundary (inside_course False) or inside
                             another leisure=golf_course area are dropped (Pevely Farms took Crescent Farms' 1, 9,
                             10 and 18)
  guard_tees(tp, fc)       tee positions (tees/positions dict, in place):
                           * a walk-back more than MAX_FORWARD_YD forward of the hole-line start, made to force a
                             short card length onto a longer hole, is put back at the line start and marked CHECK
                             (Lake Shawnee page 4: a 339-yd par 4 made a 148-yd par 3)
                           * a walk-back that runs onto another hole's green, a building or a parking area is
                             capped just in front of it and marked CHECK (St Andrews 16 on the 15th green,
                             Colbert Hills 1 on the clubhouse / car park); any other non-box placement that lands
                             on one is moved forward off it
  guard_routed(res, ...)   routed holes (platform/routing.py result, in place, before to_hole_features):
                           * a green already used by another hole is swapped for an unused green that fits the
                             card, else flagged (Ironhorse 18 on hole 4's green, Dub's Dread 4 = 13)
                           * a hole wildly beyond its par's length limit, or far off every card length, is
                             rejected (not built; Ironhorse 18 at 1607 yds)
Pure functions on GeoJSON-ish dicts; shapely only.
"""
import math
import re

from shapely.geometry import Point, Polygon, shape
from shapely.ops import unary_union

YD = 0.9144
MAX_FORWARD_YD = 60.0          # a walk-back may not move the tee further than this up the hole line
OBSTACLE_MARGIN_YD = 3.0
SHIFT_MAX_YD = 80.0
SAME_GREEN_YD = 20.0
PAR_MAX_YD = {3: 290, 4: 520, 5: 700, 6: 800}
PRACTICE_RE = re.compile(r"\b(driving|range|practi[cs]e|warm[- ]?up)\b", re.I)
BOX_METHODS = ("tagged", "review", "tee_centroid")


# ----------------------------------------------------------------------------- projection
class _P:
    def __init__(self, lon0, lat0):
        self.lon0, self.lat0 = lon0, lat0
        self.kx = math.cos(math.radians(lat0)) * 111320 / YD
        self.ky = 111320 / YD

    def fwd(self, lon, lat):
        return ((lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky)

    def inv(self, x, y):
        return (self.lon0 + x / self.kx, self.lat0 + y / self.ky)

    def geom(self, g):
        from shapely.ops import transform
        return transform(lambda x, y, z=None: self.fwd(x, y), g)


def _proj_for(fc):
    for f in fc.get("features", []):
        g = f.get("geometry") or {}
        if g.get("type") in ("Polygon", "LineString", "Point", "MultiPolygon"):
            c = shape(g).centroid
            return _P(c.x, c.y)
    return _P(0.0, 0.0)


def _shp(f):
    try:
        g = shape(f["geometry"])
        return g if g.is_valid else g.buffer(0)
    except Exception:                                            # noqa: BLE001
        return None


# ----------------------------------------------------------------------------- 1. OSM cleanup
def practice_tee(props):
    """A tee box named / described as a range, practice or driving tee."""
    txt = " ".join(str(props.get(k, "")) for k in ("name", "description", "note", "tee", "golf:tee", "ref"))
    return bool(PRACTICE_RE.search(txt))


def drop_practice_tees(fc):
    """-> (fc copy, [dropped osm ids]). Tees named range/practice/driving or inside a golf=driving_range area."""
    feats = fc.get("features", [])
    ranges = [g for g in (_shp(f) for f in feats if (f["properties"].get("golf") == "driving_range"
                                                       or f["properties"].get("leisure") == "driving_range")
                          and f["geometry"]["type"] in ("Polygon", "MultiPolygon")) if g is not None]
    rng = unary_union(ranges) if ranges else None
    keep, dropped = [], []
    for f in feats:
        p = f["properties"]
        if p.get("golf") == "tee" and f.get("geometry"):
            g = _shp(f)
            inside = rng is not None and g is not None and rng.contains(g.representative_point())
            if practice_tee(p) or inside:
                dropped.append(p.get("osm_id"))
                continue
        keep.append(f)
    return (dict(fc, features=keep) if dropped else fc), dropped


def select_hole_ways(fc, max_holes=18):
    """-> (fc copy, [dropped osm ids]). When golf=hole refs repeat or there are more than max_holes ways, the
    ways of a neighbouring course go: outside this course (inside_course False) or inside another
    leisure=golf_course polygon (one that does not hold most of this course's ways)."""
    feats = fc.get("features", [])
    holes = [f for f in feats if f["properties"].get("golf") == "hole" and f.get("geometry")
             and f["geometry"]["type"] == "LineString"]
    refs = [str(f["properties"].get("ref")) for f in holes if f["properties"].get("ref")]
    if len(refs) == len(set(refs)) and len(holes) <= max_holes:
        return fc, []
    courses = [(f, _shp(f)) for f in feats if f["properties"].get("leisure") == "golf_course"
               and f["geometry"]["type"] in ("Polygon", "MultiPolygon")]
    own = [f for f in holes if f["properties"].get("inside_course") is not False]
    others = []
    for cf, g in courses:
        if g is None or sum(g.contains(shape(f["geometry"]).interpolate(0.5, normalized=True))
                            for f in own) > len(own) / 2:
            continue                                         # this course's own polygon
        n_in = sum(g.contains(shape(f["geometry"]).interpolate(0.5, normalized=True)) for f in holes)
        if n_in and n_in < len(holes):
            others.append(g)
    drop = set()
    for f in holes:
        mid = shape(f["geometry"]).interpolate(0.5, normalized=True)
        if f["properties"].get("inside_course") is False or any(g.contains(mid) for g in others):
            drop.add(id(f))
    kept_refs = [str(f["properties"].get("ref")) for f in holes if id(f) not in drop and f["properties"].get("ref")]
    if not kept_refs:                                        # never drop every hole
        return fc, []
    dropped = [f["properties"].get("osm_id") for f in holes if id(f) in drop]
    return (dict(fc, features=[f for f in feats if id(f) not in drop]) if drop else fc), dropped


def clean_osm(fc):
    """-> (fc, [notes]): drop_practice_tees + select_hole_ways."""
    notes = []
    fc, t = drop_practice_tees(fc)
    if t:
        notes.append(f"ignored {len(t)} practice / driving-range tee box(es): OSM {', '.join(map(str, t[:6]))}")
    fc, h = select_hole_ways(fc)
    if h:
        notes.append(f"ignored {len(h)} golf=hole way(s) of a neighbouring course (outside this course's boundary): "
                     f"OSM {', '.join(map(str, h[:8]))}")
    return fc, notes


# ----------------------------------------------------------------------------- 2. tee positions
ROADS = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street",
         "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "road"}
ROAD_HALF_WIDTH_YD = 5.0


def obstacles(fc, pr):
    """[(kind, shapely polygon in yards, id)] tees must not sit on: greens, buildings, parking, public roads
    (highway=residential etc., buffered; cart paths and service roads are not), residential land."""
    out = []
    for f in fc.get("features", []):
        p, g = f["properties"], f.get("geometry") or {}
        if g.get("type") in ("LineString", "MultiLineString") and p.get("highway") in ROADS and not p.get("golf"):
            s = _shp(f)
            if s is not None and not s.is_empty:
                out.append(("road", pr.geom(s).buffer(ROAD_HALF_WIDTH_YD), p.get("osm_id")))
            continue
        if g.get("type") not in ("Polygon", "MultiPolygon"):
            continue
        kind = "green" if p.get("golf") == "green" else "building" if p.get("building") not in (None, "", "no") \
            else "parking" if p.get("amenity") == "parking" or p.get("parking") in ("surface",) \
            else "residential" if p.get("landuse") == "residential" and not p.get("golf") else None
        if kind:
            s = _shp(f)
            if s is not None and not s.is_empty:
                out.append((kind, pr.geom(s), p.get("osm_id")))
    return out


def _hole_lines(fc):
    return {str(f["properties"]["ref"]): f["geometry"]["coordinates"] for f in fc.get("features", [])
            if f["properties"].get("golf") == "hole" and (f.get("geometry") or {}).get("type") == "LineString"
            and f["properties"].get("ref")}


def _hit(pt, obs, skip):
    for kind, g, oid in obs:
        if g in skip:
            continue
        if g.contains(pt):
            return kind, oid
    return None


def guard_tees(tp, fc, max_forward=MAX_FORWARD_YD):
    """tp = tees/positions dict {holes: {ref: {tees: {set: {lat, lon, method, ...}}}}}; edited in place.
    -> [notes]. Moved entries get method '<old>_capped' and check='<reason>'."""
    if not tp or not tp.get("holes"):
        return []
    pr = _proj_for(fc)
    lines = _hole_lines(fc)
    obs = obstacles(fc, pr)
    notes = []
    for ref, hp in tp["holes"].items():
        line = lines.get(str(ref))
        if not line or len(line) < 2:
            continue
        S = pr.fwd(*line[0][:2])
        P1 = pr.fwd(*line[1][:2])
        E = Point(pr.fwd(*line[-1][:2]))
        L = math.hypot(P1[0] - S[0], P1[1] - S[1]) or 1.0
        u = ((P1[0] - S[0]) / L, (P1[1] - S[1]) / L)
        own = [g for k, g, _ in obs if (k == "green" and g.buffer(10).contains(E))
               or (k == "residential" and g.contains(Point(S)))]      # land the hole itself is mapped in
        # forward sets legitimately sit far up the line; only the hole's BACK tee (the one furthest from the
        # green) being walked forward means the card hole does not fit this OSM hole
        pos = {s: (r["lon"], r["lat"]) for s, r in (hp.get("tees") or {}).items()
               if isinstance(r, dict) and r.get("lat") is not None}
        alongs = {s: (pr.fwd(*ll)[0] - S[0]) * u[0] + (pr.fwd(*ll)[1] - S[1]) * u[1] for s, ll in pos.items()}
        back = min(alongs, key=alongs.get) if alongs else None
        hard = [o for o in obs if o[0] != "residential"]
        for s, r in (hp.get("tees") or {}).items():
            if not isinstance(r, dict) or r.get("lat") is None or str(r.get("method", "")).startswith(BOX_METHODS) \
                    or r.get("check"):
                continue
            T = pr.fwd(r["lon"], r["lat"])
            along = (T[0] - S[0]) * u[0] + (T[1] - S[1]) * u[1]
            new, why = None, None
            if r.get("method") == "walkback" and along > max_forward and s == back:
                new = S
                why = (f"walk-back moved the back tee {along:.0f} yds up the hole line to fit the card: kept at the "
                       "line start (card hole may not be this OSM hole)")
            elif r.get("method") == "walkback" and back is not None and alongs[back] > max_forward:
                why = "the hole's back tee was walked up the hole line: card hole may not be this OSM hole"
            elif r.get("method") == "walkback" and along < 0:
                # walk from the line start back to the tee; stop in front of the first obstacle
                n = int(-along // 2) + 1
                for i in range(1, n + 1):
                    d = min(i * 2.0, -along)
                    q = (S[0] - u[0] * d, S[1] - u[1] * d)
                    h = _hit(Point(q), obs, own)
                    if h:
                        back = max(0.0, d - OBSTACLE_MARGIN_YD)
                        new = (S[0] - u[0] * back, S[1] - u[1] * back)
                        why = (f"walk-back ran onto a {h[0]} (OSM {h[1]}) {d:.0f} yds behind the line start: "
                               f"capped there ({-along - back:.0f} yds short of the card)")
                        break
            elif _hit(Point(T), hard, own):            # a box-based point: residential land is not proof
                h = _hit(Point(T), hard, own)
                for i in range(1, int(SHIFT_MAX_YD // 2) + 1):
                    q = (T[0] + u[0] * i * 2.0, T[1] + u[1] * i * 2.0)
                    if not _hit(Point(q), hard, own):
                        q = (q[0] + u[0] * OBSTACLE_MARGIN_YD, q[1] + u[1] * OBSTACLE_MARGIN_YD)
                        new = q
                        why = f"tee was on a {h[0]} (OSM {h[1]}): moved {i * 2 + OBSTACLE_MARGIN_YD:.0f} yds forward off it"
                        break
                else:
                    why = f"tee is on a {h[0]} (OSM {h[1]})"
            if why:
                if new is not None:
                    lon, lat = pr.inv(*new)
                    r.update(lon=lon, lat=lat, method=f"{r.get('method')}_capped", confidence="low")
                r["check"] = why
                notes.append(f"hole {ref} {s}: CHECK, {why}")
    return notes


# ----------------------------------------------------------------------------- 3. routed holes
def _fit_card(d, card_yards, par):
    """Smallest |d - card| (yd), or the distance outside the par's range without a card."""
    if card_yards:
        return min(abs(d - y) for y in card_yards)
    lo, hi = {3: (90, 260), 4: (240, 500), 5: (420, 660)}.get(par, (90, 660))
    return max(0.0, lo - d, d - hi)


def length_reason(d, par, card_yards):
    """Why a hole of straight length d (yd) cannot be this card hole, or None."""
    lim = PAR_MAX_YD.get(par)
    if lim and d > lim:
        return f"{d:.0f} yds is beyond any par {par} (max {lim})"
    if card_yards:
        y = max(card_yards)
        if d > y + max(150.0, 0.4 * y) or d < min(card_yards) - max(150.0, 0.5 * min(card_yards)):
            return f"{d:.0f} yds is far from the card ({', '.join(str(int(v)) for v in card_yards)})"
    return None


def guard_routed(res, fc, missing, greens=()):
    """res = routing result {holes: {ref: {tee_ll, back_tee_ll, green_ll, green_id, par, card_yards, flags,
    status}}} (lon, lat); missing = refs routing placed (the others are OSM ways); greens = candidate greens
    [{id, ll}] (routing inputs). Edited in place. -> [notes]."""
    holes = res.get("holes") or {}
    pr = _proj_for(fc)
    xy = lambda ll: pr.fwd(float(ll[0]), float(ll[1]))          # noqa: E731
    dist = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])     # noqa: E731
    fixed = {r: xy(c[-1]) for r, c in _hole_lines(fc).items() if r not in missing}
    routed = [r for r in missing if (holes.get(r) or {}).get("green_ll") and holes[r].get("tee_ll")]
    notes = []

    def flag(h, msg):
        h.setdefault("flags", []).append(msg)
        h["status"] = "check"

    def used_except(ref):
        u = dict((k, v) for k, v in fixed.items() if k != ref)
        u.update({k: xy(holes[k]["green_ll"]) for k in routed if k != ref and holes[k].get("green_ll")})
        return u

    # shared greens: the routed hole that fits its card worse gives its green up
    def fit_of(r):
        h = holes[r]
        t = xy(h.get("back_tee_ll") or h["tee_ll"])
        return _fit_card(dist(t, xy(h["green_ll"])), h.get("card_yards") or [], h.get("par"))

    conceded = set()
    for r in sorted(routed, key=lambda k: -fit_of(k)):
        h = holes[r]
        if not h.get("green_ll"):
            continue
        g = xy(h["green_ll"])
        others = used_except(r)
        share = [k for k, v in others.items() if dist(v, g) <= SAME_GREEN_YD]
        if not share or all(k in conceded for k in share):
            continue                                     # the worse-fitting partner already took the flag
        t = xy(h.get("back_tee_ll") or h["tee_ll"])
        best = None
        for c in greens or ():
            cxy = xy(c["ll"])
            if any(dist(cxy, v) <= SAME_GREEN_YD for v in others.values()):
                continue
            d = dist(t, cxy)
            e = _fit_card(d, h.get("card_yards") or [], h.get("par"))
            tol = max(25.0, 0.1 * max(h.get("card_yards") or [d]))
            if e <= tol and not length_reason(d, h.get("par"), h.get("card_yards")) and (best is None or e < best[0]):
                best = (e, c, d)
        if best:
            old = h.get("green_id")
            h.update(green_ll=list(best[1]["ll"]), green_id=best[1].get("id"), green_src=best[1].get("src"),
                     straight_yd=round(best[2], 1))
            flag(h, f"green reassigned: {old} is hole {', '.join(share)}'s green; unused green {best[1].get('id')} "
                    f"fits the card ({best[2]:.0f} yds)")
            notes.append(f"hole {r}: green shared with hole {', '.join(share)} -> unused green {best[1].get('id')}")
        else:
            conceded.add(r)
            flag(h, f"shares hole {', '.join(share)}'s green and no unused green fits")
            notes.append(f"hole {r}: CHECK, shares hole {', '.join(share)}'s green")
    for r in routed:
        h = holes[r]
        t = xy(h.get("back_tee_ll") or h["tee_ll"])
        d = dist(t, xy(h["green_ll"]))
        why = length_reason(d, h.get("par"), h.get("card_yards") or [])
        if why:
            h["rejected"] = why
            h["status"] = "rejected"
            h.setdefault("flags", []).append(f"rejected: {why}")
            h.pop("green_ll", None)                            # to_hole_features skips it; the hole is not built
            notes.append(f"hole {r}: routed hole rejected ({why})")
    return notes


# ----------------------------------------------------------------------------- 4. OSM hole numbering vs the card
def _card_rows(card):
    sets = (card or {}).get("tee_sets") or {}
    pars = list((card or {}).get("par") or next((v.get("par") for v in sets.values() if v.get("par")), []) or [])
    n = max([len(pars)] + [len(v.get("yards") or []) for v in sets.values()])
    ys = [max([v["yards"][i] for v in sets.values() if i < len(v.get("yards") or []) and v["yards"][i]] or [0])
          for i in range(n)]
    pars = [int(p) if str(p or "").isdigit() else None for p in pars] + [None] * (n - len(pars))
    return pars, ys


def _way_len(coords):
    pr = _P(coords[0][0], coords[0][1])
    xy = [pr.fwd(c[0], c[1]) for c in coords]
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(xy, xy[1:]))


def _bad(L, osm_par, par, y):
    if not y:
        return osm_par is not None and par is not None and osm_par != par
    return abs(L - y) > max(50.0, 0.16 * y) or (osm_par is not None and par is not None and osm_par != par)


def renumber_holes(fc, card, prior=1.0):
    """OSM numbers some courses' holes in a different order from the card (Swope Memorial: card 3-9 = OSM ways
    8, 9, 6, 7, 3, 4, 5; Tournament Club of Iowa: swapped nines). When matching by ref leaves >= 2 holes whose
    par or length is far off the card, the OSM ways are assigned to card holes by a min-cost assignment on
    (length vs the card's longest yardage, par) with the ref as a weak prior, and the refs are rewritten when that
    fixes at least 2 more holes. -> (fc, {old ref: new ref} | {})."""
    pars, ys = _card_rows(card)
    if not ys or not any(ys):
        return fc, {}
    ways = {}
    for f in fc.get("features", []):
        p = f["properties"]
        if p.get("golf") == "hole" and (f.get("geometry") or {}).get("type") == "LineString" \
                and str(p.get("ref", "")).isdigit() and 1 <= int(p["ref"]) <= len(ys):
            if str(p["ref"]) in ways:
                return fc, {}                                 # duplicated refs: select_hole_ways' job
            op = p.get("par")
            ways[str(p["ref"])] = (f, _way_len(f["geometry"]["coordinates"]), int(op) if str(op or "").isdigit() else None)
    refs = sorted(ways, key=int)
    if len(refs) < 4:
        return fc, {}
    idx = [int(r) - 1 for r in refs]

    def cost(i, r):
        _, L, op = ways[r]
        y, par = ys[i], pars[i]
        c = min(abs(L - y) / max(25.0, 0.08 * y), 6.0) if y else 0.0
        if op is not None and par is not None and op != par:
            c += 3.0
        lim = PAR_MAX_YD.get(par)
        if lim and L > lim + 30:
            c += 3.0
        return c + (0.0 if int(r) - 1 == i else prior)

    import numpy as np
    from scipy.optimize import linear_sum_assignment
    C = np.array([[cost(i, r) for r in refs] for i in idx])
    rows, cols = linear_sum_assignment(C)
    ident = float(np.trace(C))
    new = float(C[rows, cols].sum())
    bad_id = sum(_bad(ways[r][1], ways[r][2], pars[int(r) - 1], ys[int(r) - 1]) for r in refs)
    mapping = {refs[c]: str(idx[r] + 1) for r, c in zip(rows, cols) if refs[c] != str(idx[r] + 1)}
    bad_new = sum(_bad(ways[old][1], ways[old][2], pars[int(nw) - 1], ys[int(nw) - 1])
                  for old, nw in ((r, mapping.get(r, r)) for r in refs))
    if bad_id < 2 or bad_new > bad_id - 2 or new > ident - 4.0 or not mapping:
        return fc, {}
    feats = []
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") == "hole" and str(p.get("ref")) in mapping and ways.get(str(p.get("ref")), (None,))[0] is f:
            f = dict(f, properties=dict(p, ref=mapping[str(p["ref"])], osm_ref=p["ref"]))
        feats.append(f)
    return dict(fc, features=feats), mapping
