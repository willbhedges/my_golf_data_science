"""Place a named tee set's tee box on a hole, from OSM geometry + the scorecard yardage.

Inputs
  line      hole centre-line, [(lat, lon), ...] from the tee end to the green (OSM golf=hole).
            The last vertex is taken as the green centre unless `green` is given.
  tees      candidate tee boxes near the start of the hole: [{"id": ..., "coords": [(lat, lon), ...]}]
            (polygon ring, or a single point for golf=tee nodes / marker points).
  yardage   scorecard yardage of the chosen tee set.

How scorecard yardage is measured (USGA Course Rating System Manual, "Measuring the course"):
  horizontally, from the permanent yardage marker (normally the middle of the tee box) along the
  line of play to the centre of the green; on a dogleg the line of play goes through the turning
  point(s). So the distance from a point P on the tee to the green is
      |P - V_k| + (line length from V_k to the green)
  where V_k is the first line vertex in front of P (the next turning point). A point behind the
  start of the line is measured straight to V_1, i.e. the first leg is extended backwards.

Algorithm (place_tee)
  1. Project everything to a local flat frame in yards (equirectangular about the hole; error
     < 0.1 % over a hole).
  2. For each candidate tee: keep it if it is near the line of play (perpendicular offset
     <= max_offset_yd from the first leg, extended backwards; not more than max_behind_yd behind
     the line start, nor past half the hole -- that drops other holes' boxes) and roughly the right distance
     out (within max_err_yd of the yardage at its nearest end). Compute the along-the-line
     distance to the green of its centroid ("middle of the tee") and of its front-most and
     back-most points (the tee's usable extent; markers move up and back day to day).
  3. Error for a tee = 0 if the yardage falls inside [front, back] extent, else the gap to the
     nearer end. The best tee is the smallest error, ties broken by |centroid distance - yardage|
     (the scorecard is measured from the middle).
  4. The returned point is the centroid if the yardage is within `centre_tol_yd` of the
     centroid's distance; otherwise the point on the tee's axis (the line through the centroid
     parallel to the first leg) at exactly the yardage, clamped to the tee's extent.
  Confidence: high if the yardage is within 5 yds of a box's extent, medium within 15, else low.
  5. No acceptable tee polygon -> walk back from the green along the line by the yardage
     (extending the first leg backwards if the yardage is longer than the line). method="walkback".

place_tee_sets() does this for several tee sets on one hole and reports when two sets share
a box (common: one long tee with two marker colours).
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

YD_PER_M = 1.0 / 0.9144
R_EARTH_M = 6371008.8


# --------------------------------------------------------------------------- local frame
class Frame:
    """Equirectangular projection about (lat0, lon0); x east, y north, in yards."""

    def __init__(self, lat0: float, lon0: float):
        self.lat0, self.lon0 = lat0, lon0
        self.kx = math.radians(1) * R_EARTH_M * math.cos(math.radians(lat0)) * YD_PER_M
        self.ky = math.radians(1) * R_EARTH_M * YD_PER_M

    def fwd(self, lat: float, lon: float) -> tuple[float, float]:
        return ((lon - self.lon0) * self.kx, (lat - self.lat0) * self.ky)

    def inv(self, x: float, y: float) -> tuple[float, float]:
        return (self.lat0 + y / self.ky, self.lon0 + x / self.kx)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _norm(a):
    return math.hypot(a[0], a[1])


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def polygon_centroid(pts: Sequence[tuple[float, float]]) -> tuple[float, float]:
    """Area centroid of a ring (closed or not); falls back to the vertex mean when degenerate."""
    pts = list(pts)
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if len(pts) < 3:
        n = len(pts)
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    a = cx = cy = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    if abs(a) < 1e-9:
        n = len(pts)
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    return (cx / (3 * a), cy / (3 * a))


# --------------------------------------------------------------------------- line geometry
class LineOfPlay:
    """A hole centre-line in yards. dist_to_green(P) follows the USGA measuring convention."""

    def __init__(self, pts: Sequence[tuple[float, float]]):
        if len(pts) < 2:
            raise ValueError("hole line needs at least 2 points")
        self.pts = [tuple(p) for p in pts]
        seg = [_norm(_sub(self.pts[i + 1], self.pts[i])) for i in range(len(self.pts) - 1)]
        # remaining[k] = line length from vertex k to the green
        self.remaining = [0.0] * len(self.pts)
        for k in range(len(self.pts) - 2, -1, -1):
            self.remaining[k] = self.remaining[k + 1] + seg[k]
        self.length = self.remaining[0]
        d = _sub(self.pts[1], self.pts[0])
        self.u0 = (d[0] / seg[0], d[1] / seg[0])            # unit vector of the first leg

    def first_leg_coords(self, p) -> tuple[float, float]:
        """(along, offset) of p relative to the first leg: along from the line start (negative
        behind it), offset to the right (+) / left (-) of the direction of play."""
        r = _sub(p, self.pts[0])
        return _dot(r, self.u0), _cross(r, self.u0)

    def _next_vertex(self, p) -> int:
        """Index of the first vertex in front of p (the next turning point, or the green)."""
        best_k, best_d = 1, float("inf")
        for i in range(len(self.pts) - 1):
            a, b = self.pts[i], self.pts[i + 1]
            ab = _sub(b, a)
            t = max(0.0, min(1.0, _dot(_sub(p, a), ab) / max(_dot(ab, ab), 1e-12)))
            q = (a[0] + t * ab[0], a[1] + t * ab[1])
            d = _norm(_sub(p, q))
            if d < best_d - 1e-9:
                best_d, best_k = d, i + 1
        return best_k

    def dist_to_green(self, p) -> float:
        k = self._next_vertex(p)
        return _norm(_sub(self.pts[k], p)) + self.remaining[k]

    def point_at_distance(self, yards: float) -> tuple[float, float]:
        """Point on the line `yards` from the green (along the line); beyond the start the first
        leg is extended backwards."""
        if yards >= self.length:
            back = yards - self.length
            return (self.pts[0][0] - back * self.u0[0], self.pts[0][1] - back * self.u0[1])
        for k in range(len(self.pts) - 1):
            if self.remaining[k + 1] <= yards <= self.remaining[k]:
                a, b = self.pts[k], self.pts[k + 1]
                seg = self.remaining[k] - self.remaining[k + 1]
                t = (self.remaining[k] - yards) / seg if seg > 0 else 0.0
                return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        return self.pts[-1]


# --------------------------------------------------------------------------- placement
def _tee_metrics(lop: LineOfPlay, ring_xy, centroid):
    dists = [lop.dist_to_green(p) for p in ring_xy] or [lop.dist_to_green(centroid)]
    return dict(d_centroid=lop.dist_to_green(centroid), d_front=min(dists), d_back=max(dists))


def _point_on_axis(lop: LineOfPlay, centroid, yards, d_front, d_back):
    """Point on the line through the tee centroid parallel to the first leg at `yards` from the
    green, clamped to the tee's extent. Solved by bisection (dist is monotone along the axis)."""
    target = min(max(yards, d_front), d_back)
    lo, hi = -150.0, 150.0                       # offset along -u0 (backwards = longer)

    def at(s):
        return (centroid[0] - s * lop.u0[0], centroid[1] - s * lop.u0[1])

    f = lambda s: lop.dist_to_green(at(s)) - target  # noqa: E731
    if f(lo) > 0 or f(hi) < 0:
        return centroid
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return at(0.5 * (lo + hi))


def place_tee(line: Sequence[tuple[float, float]], tees: Iterable[dict], yardage: float, *,
              green: tuple[float, float] | None = None, max_offset_yd: float = 45.0,
              max_behind_yd: float = 150.0, max_err_yd: float = 25.0,
              centre_tol_yd: float = 3.0) -> dict:
    """Pick the tee box for `yardage` (see module docstring). Returns
    {lat, lon, method, tee_id, error_yd, dist_yd, d_centroid, d_front, d_back, candidates}."""
    line = [tuple(p) for p in line]
    if green is not None:
        line = line[:-1] + [tuple(green)]
    lat0 = sum(p[0] for p in line) / len(line)
    lon0 = sum(p[1] for p in line) / len(line)
    fr = Frame(lat0, lon0)
    lop = LineOfPlay([fr.fwd(*p) for p in line])

    cands = []
    for t in tees:
        ring = [fr.fwd(*p) for p in t["coords"]]
        if len(ring) > 1 and ring[0] == ring[-1]:
            ring = ring[:-1]
        c = polygon_centroid(ring)
        along, off = lop.first_leg_coords(c)
        m = _tee_metrics(lop, ring, c)
        # only boxes beside the first leg (or behind its start), not ones serving a later leg
        if abs(off) > max_offset_yd or along > 0.5 * lop.length or along < -max_behind_yd:
            continue
        err = 0.0 if m["d_front"] <= yardage <= m["d_back"] else min(
            abs(yardage - m["d_front"]), abs(yardage - m["d_back"]))
        cands.append(dict(tee_id=t.get("id"), centroid_xy=c, offset_yd=off, error_yd=err,
                          centre_err_yd=abs(m["d_centroid"] - yardage), **m))
    cands.sort(key=lambda c: (round(c["error_yd"], 6), c["centre_err_yd"]))

    summary = [dict(tee_id=c["tee_id"], d_centroid=round(c["d_centroid"], 1),
                    d_front=round(c["d_front"], 1), d_back=round(c["d_back"], 1),
                    offset_yd=round(c["offset_yd"], 1), error_yd=round(c["error_yd"], 1))
               for c in cands]
    if cands and cands[0]["error_yd"] <= max_err_yd:
        b = cands[0]
        if b["centre_err_yd"] <= centre_tol_yd:
            p, method = b["centroid_xy"], "tee_centroid"
        else:
            p = _point_on_axis(lop, b["centroid_xy"], yardage, b["d_front"], b["d_back"])
            method = "tee_axis"
        lat, lon = fr.inv(*p)
        conf = "high" if b["error_yd"] <= 5 else "medium" if b["error_yd"] <= 15 else "low"
        return dict(lat=lat, lon=lon, method=method, tee_id=b["tee_id"], confidence=conf,
                    error_yd=round(b["error_yd"], 1), dist_yd=round(lop.dist_to_green(p), 1),
                    d_centroid=round(b["d_centroid"], 1), d_front=round(b["d_front"], 1),
                    d_back=round(b["d_back"], 1), candidates=summary)
    p = lop.point_at_distance(yardage)
    lat, lon = fr.inv(*p)
    return dict(lat=lat, lon=lon, method="walkback", tee_id=None, confidence="low",
                error_yd=None if not cands else round(cands[0]["error_yd"], 1),
                dist_yd=round(yardage, 1), d_centroid=None, d_front=None, d_back=None,
                line_length_yd=round(lop.length, 1), candidates=summary)


# --------------------------------------------------------------------------- joint assignment (Q2)
SOURCE_COST = {"osm": 0.0, "borrowed": 4.0, "lidar": 6.0}


def _hole_frame(line, green=None):
    line = [tuple(p) for p in line]
    if green is not None:
        line = line[:-1] + [tuple(green)]
    lat0 = sum(p[0] for p in line) / len(line)
    lon0 = sum(p[1] for p in line) / len(line)
    fr = Frame(lat0, lon0)
    return fr, LineOfPlay([fr.fwd(*p) for p in line])


def _candidates(fr, lop, tees, source, max_offset_yd, max_behind_yd):
    out = []
    for t in tees:
        ring = [fr.fwd(*p) for p in t["coords"]]
        if len(ring) > 1 and ring[0] == ring[-1]:
            ring = ring[:-1]
        c = polygon_centroid(ring)
        along, off = lop.first_leg_coords(c)
        if abs(off) > max_offset_yd or along > 0.5 * lop.length or along < -max_behind_yd:
            continue
        m = _tee_metrics(lop, ring, c)
        out.append(dict(tee_id=t.get("id"), centroid_xy=c, offset_yd=off,
                        source=t.get("source") or source, **m))
    return out


def assign_tee_sets(line, tees, yardages: dict, *, green=None, borrow=(), max_offset_yd: float = 45.0,
                    max_behind_yd: float = 150.0, max_err_yd: float = 25.0, borrow_err_yd: float = 10.0,
                    centre_tol_yd: float = 3.0, walkback_cost: float = 30.0, gap_weight: float = 0.25, gap_cap_yd: float = 10.0,
                    order_tol_yd: float = 2.0, order_penalty: float = 100.0, source_cost=None,
                    offset_free_yd: float = 45.0, offset_cost: float = 0.1) -> dict:
    """Ordered joint assignment of every tee set on one hole (auto_course_lookup.md 4.2-1).

    Sets are taken back to front by card yards (Gold >= Black >= White >= Rust); each picks one candidate
    box (sharing allowed) or a walk-back, so that the placed points keep that order along the line of play
    (a longer set never sits in front of a shorter one, `order_tol_yd` slack). Distances are measured to
    `green` (the green polygon centroid; else the line's last vertex) along the hole line, through its
    turning points (LineOfPlay). Cost, minimised exactly by dynamic programming over the sets:

        sum_s [ err_s + source_cost(box) + 0.05 * |centroid - card| ]
          + gap_weight * sum min(|e_s - e_s+1|, gap_cap_yd)      (consecutive sets, both on boxes)
        err_s = gap from the card yardage to the box's front..back extent (0 inside it); e_s = signed error
        walk-back (no box within max_err_yd) costs `walkback_cost`; an order violation `order_penalty`;
        a box more than offset_free_yd off the first leg costs offset_cost per extra yard (only reachable
        when max_offset_yd > offset_free_yd: dog-legged back tees set off to the side, e.g. SH 2 Gold).

    The gap term is the 'difference' trick: matched gaps between sets are cheap even when the green centre
    is a few yards off, so one green error cannot shuffle the sets. `tees` = the hole's own candidates
    ({id, coords, source: osm|lidar}); `borrow` = other holes' boxes, used only within `borrow_err_yd`
    (shared tee complexes). Returns {set: place_tee-shaped dict + source, borrowed, order_ok, shared_with}.
    """
    sc = dict(SOURCE_COST, **(source_cost or {}))
    fr, lop = _hole_frame(line, green)
    cands = _candidates(fr, lop, tees, "osm", max_offset_yd, max_behind_yd)
    for c in _candidates(fr, lop, borrow, "osm", max_offset_yd, max_behind_yd):
        c["borrowed"] = True
        cands.append(c)
    names = sorted((n for n, y in yardages.items() if y), key=lambda n: -float(yardages[n]))
    options = []
    for n in names:
        y = float(yardages[n])
        opts = []
        for i, c in enumerate(cands):
            p = min(max(y, c["d_front"]), c["d_back"])
            err = abs(y - p)
            lim = borrow_err_yd if c.get("borrowed") else max_err_yd
            if err > lim:
                continue
            cost = err + 0.05 * abs(c["d_centroid"] - y) + sc.get("borrowed" if c.get("borrowed") else c["source"], 0.0) \
                + offset_cost * max(0.0, abs(c["offset_yd"]) - offset_free_yd)
            opts.append(dict(cand=i, p=p, e=p - y, err=err, cost=cost))
        opts.append(dict(cand=None, p=y, e=0.0, err=None, cost=walkback_cost))
        options.append(opts)
    # DP over sets (back to front)
    best = [dict() for _ in names]
    for j, o in enumerate(options[0] if options else []):
        best[0][j] = (o["cost"], None)
    for i in range(1, len(names)):
        for j, o in enumerate(options[i]):
            cand = []
            for jp, (cp, _) in best[i - 1].items():
                op = options[i - 1][jp]
                pen = 0.0 if op["p"] + order_tol_yd >= o["p"] else order_penalty
                gap = 0.0 if op["cand"] is None or o["cand"] is None else min(abs(op["e"] - o["e"]), gap_cap_yd)
                cand.append((cp + o["cost"] + gap_weight * gap + pen, jp))
            best[i][j] = min(cand)
    pick = [None] * len(names)
    if names:
        j = min(best[-1], key=lambda k: best[-1][k][0])
        for i in range(len(names) - 1, -1, -1):
            pick[i] = j
            j = best[i][j][1]
    out = {}
    for i, n in enumerate(names):
        o = options[i][pick[i]]
        y = float(yardages[n])
        if o["cand"] is None:
            q = lop.point_at_distance(y)
            lat, lon = fr.inv(*q)
            near = min((abs(y - min(max(y, c["d_front"]), c["d_back"])) for c in cands), default=None)
            r = dict(lat=lat, lon=lon, method="walkback", tee_id=None, confidence="low",
                     error_yd=None if near is None else round(near, 1), dist_yd=round(y, 1), d_centroid=None,
                     d_front=None, d_back=None, line_length_yd=round(lop.length, 1), source="hole_line")
        else:
            c = cands[o["cand"]]
            if abs(c["d_centroid"] - y) <= centre_tol_yd:
                q, method = c["centroid_xy"], "tee_centroid"
            else:
                q = _point_on_axis(lop, c["centroid_xy"], y, c["d_front"], c["d_back"])
                method = "tee_axis"
            if c["source"] == "lidar":
                method = "lidar_pad"
            lat, lon = fr.inv(*q)
            conf = "high" if o["err"] <= 5 else "medium" if o["err"] <= 15 else "low"
            if c["source"] == "lidar" and conf == "high":
                conf = "medium"
            r = dict(lat=lat, lon=lon, method=method, tee_id=c["tee_id"], confidence=conf,
                     error_yd=round(o["err"], 1), dist_yd=round(lop.dist_to_green(q), 1),
                     d_centroid=round(c["d_centroid"], 1), d_front=round(c["d_front"], 1),
                     d_back=round(c["d_back"], 1), source=c["source"])
            if c.get("borrowed"):
                r["borrowed"] = True
        out[n] = r
    for i, n in enumerate(names):                     # order check on the result
        r = out[n]
        r["order_ok"] = all(out[m]["dist_yd"] + order_tol_yd >= r["dist_yd"] for m in names[:i]) and \
            all(r["dist_yd"] + order_tol_yd >= out[m]["dist_yd"] for m in names[i + 1:])
        r["shared_with"] = sorted(m for m, o in out.items()
                                  if m != n and r["tee_id"] is not None and o["tee_id"] == r["tee_id"])
    return out


def place_tee_sets(line, tees, yardages: dict, **kw) -> dict:
    """place_tee for each {tee_set_name: yardage}; adds `shared_with` for sets on the same box."""
    tees = list(tees)
    out = {name: place_tee(line, tees, y, **kw) for name, y in yardages.items()}
    for name, r in out.items():
        r["shared_with"] = sorted(n for n, o in out.items()
                                  if n != name and r["tee_id"] is not None and o["tee_id"] == r["tee_id"])
    return out


def haversine_yd(a, b) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_EARTH_M * math.asin(math.sqrt(h)) * YD_PER_M


def assign_tees_to_holes(lines: dict, tees: Iterable[dict], *, max_offset_yd: float = 45.0,
                         max_behind_yd: float = 150.0) -> dict:
    """Give each tee box to exactly one hole: the hole whose first leg it sits closest to
    (smallest |perpendicular offset|), among holes where it lies between max_behind_yd behind the
    line start and half-way down the hole. Boxes that fit no hole are dropped.
    `lines` maps hole ref -> [(lat, lon), ...]. Returns ref -> [tee, ...]."""
    tees = list(tees)
    out = {ref: [] for ref in lines}
    if not lines:
        return out
    lat0 = sum(p[0] for ln in lines.values() for p in ln) / sum(len(ln) for ln in lines.values())
    lon0 = sum(p[1] for ln in lines.values() for p in ln) / sum(len(ln) for ln in lines.values())
    fr = Frame(lat0, lon0)
    lops = {ref: LineOfPlay([fr.fwd(*p) for p in ln]) for ref, ln in lines.items()}
    for t in tees:
        ring = [fr.fwd(*p) for p in t["coords"]]
        if len(ring) > 1 and ring[0] == ring[-1]:
            ring = ring[:-1]
        c = polygon_centroid(ring)
        best = None
        for ref, lop in lops.items():
            along, off = lop.first_leg_coords(c)
            if abs(off) > max_offset_yd or along > 0.5 * lop.length or along < -max_behind_yd:
                continue
            score = abs(off) + 0.1 * max(0.0, -along)      # prefer boxes level with the line start
            if best is None or score < best[0]:
                best = (score, ref)
        if best is not None:
            out[best[1]].append(t)
    return out


def _point_in_ring(pt, ring) -> bool:
    x, y = pt
    inside = False
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0 + 1e-15):
            inside = not inside
    return inside


def green_for_line(line, greens, max_yd: float = 40.0):
    """Centroid (lat, lon) of the OSM green at the end of a hole line: the green polygon containing the
    line's last vertex, else the nearest one whose centroid is within max_yd; None if neither (the
    geometry stage's find_green rule). greens = [{"coords": [(lat, lon), ...]}]."""
    end = tuple(line[-1])
    fr = Frame(*end)
    best = None
    for g in greens:
        ring = [fr.fwd(*p) for p in g["coords"]]
        if len(ring) > 1 and ring[0] == ring[-1]:
            ring = ring[:-1]
        if len(ring) < 3:
            continue
        c = polygon_centroid(ring)
        if _point_in_ring((0.0, 0.0), ring):
            return fr.inv(*c)
        d = min(_norm(p) for p in ring)
        if d <= max_yd and (best is None or d < best[0]):
            best = (d, c)
    return fr.inv(*best[1]) if best else None


def place_course_sets(lines: dict, tees, yardages: dict, *, greens=(), pads=(), borrow: bool = True,
                      relaxed_offset_yd: float = 130.0, **kw) -> dict:
    """Every hole x every tee set with assign_tee_sets. lines = {ref: [(lat, lon), ...]}, tees = OSM
    boxes [{id, coords}], yardages = {ref: {set: yards}}, greens = OSM green rings (the measuring point
    is the green centroid), pads = extra candidates (lidar_pads.detect_pads: {id, coords, source: 'lidar'}),
    given to a hole only when one of its sets has no OSM box within 10 yds. Such a hole is also re-solved
    with boxes up to relaxed_offset_yd off the first leg (any hole's, with the offset cost): new back tees
    on dog-legs are often set well off the old line (SH 2's 607 Gold shares hole 18's complex). Returns
    {ref: {green: {lat, lon} | None, sets_without_box: [...], tees: {set: {...}}}}."""
    tees = list(tees)
    pads = list(pads)
    by_hole = assign_tees_to_holes(lines, tees)
    pads_by_hole = assign_tees_to_holes(lines, pads) if pads else {}
    out = {}
    for ref, line in lines.items():
        yds = {n: y for n, y in (yardages.get(ref) or {}).items() if y}
        if not yds:
            continue
        g = green_for_line(line, list(greens)) if greens else None
        own = [dict(t, source=t.get("source", "osm")) for t in by_hole.get(ref, [])]
        others = [t for r, ts in by_hole.items() if r != ref for t in ts] if borrow else []
        res = assign_tee_sets(line, own, yds, green=g, borrow=others, **kw)
        missing = [n for n, r in res.items() if r["method"] == "walkback" or (r["error_yd"] or 0) > 10]
        if missing:
            near_pads = [dict(p, source="lidar") for p in pads_by_hole.get(ref, [])]
            kw2 = dict(kw, max_offset_yd=max(relaxed_offset_yd, kw.get("max_offset_yd", 45.0)))
            res = assign_tee_sets(line, own + near_pads, yds, green=g, borrow=others if borrow else (), **kw2)
            for r in res.values():
                r["relaxed"] = True
        out[ref] = dict(green=dict(lat=g[0], lon=g[1]) if g else None, sets_without_box=missing,
                        lidar_candidates=len(pads_by_hole.get(ref, [])), tees=res)
    return out


def centroid_ll(coords):
    """Area centroid (lat, lon) of a ring given in (lat, lon), computed in a local frame (a raw lat/lon
    shoelace loses precision to cancellation at these magnitudes)."""
    coords = [tuple(p) for p in coords]
    fr = Frame(*coords[0])
    return fr.inv(*polygon_centroid([fr.fwd(*p) for p in coords]))
