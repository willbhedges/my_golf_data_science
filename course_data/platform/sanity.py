"""Build-time sanity guards for recurring pipeline errors found by the course reviews (library/*/review.md).

  clean_osm(fc, names)     OSM input cleanup before anything is built:
                           * hole refs: a multi-course site's qualified refs ("Black - 13", "1 - #2", "L4",
                             "Practice 1") are reduced to the named course's holes, renumbered 1..18 (Bethpage,
                             Pinehurst, Neshanic Valley, Old Works: v2 hole_number crashed on int("Black - 13"))
                           * practice tees: a golf=tee whose name / description mentions range, practice or
                             driving, or that lies inside a golf=driving_range area, is dropped (Ironhorse 1: the
                             Black tee sat on "Driving Range Tee Box (Turf)")
                           * hole ways of a neighbouring course: when refs are duplicated or there are more than
                             18 golf=hole ways, ways outside this course's boundary (inside_course False) or inside
                             another leisure=golf_course area are dropped (Pevely Farms took Crescent Farms' 1, 9,
                             10 and 18), but a repeated ref keeps its best way (inside-length share, connected to
                             this course's green / tee) instead of losing both (Hodge Park 10); osm_supplement
                             (src=hand) hole ways first replace the OSM ways with the same ref and are never
                             dropped (Creekmoor 10)
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
import itertools
import math
import re
import statistics

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


def _hand(f):
    return (f.get("properties") or {}).get("src") == "hand"


def supplement_hole_ways(fc):
    """-> (fc copy, [dropped OSM ids]). A hand-mapped (osm_supplement, src=hand) golf=hole way replaces every OSM
    golf=hole way with the same ref, so a supplement that re-maps the course's holes does not duplicate the refs
    (Creekmoor: live OSM and the supplement both carried 1-18, and the duplicate refs set off select_hole_ways)."""
    feats = fc.get("features", [])
    is_hole = lambda f: (f.get("properties") or {}).get("golf") == "hole"           # noqa: E731
    hand = {str(f["properties"].get("ref")) for f in feats if is_hole(f) and _hand(f) and f["properties"].get("ref")}
    if not hand:
        return fc, []
    drop = [f for f in feats if is_hole(f) and not _hand(f) and str(f["properties"].get("ref")) in hand]
    if not drop:
        return fc, []
    ids = {id(f) for f in drop}
    return dict(fc, features=[f for f in feats if id(f) not in ids]), [f["properties"].get("osm_id") for f in drop]


CONNECT_GREEN_YD = 25.0       # a hole line's last point this close to one of this course's greens ...
CONNECT_TEE_YD = 35.0         # ... and its first point this close to one of its tees: "connected"


def _inside_frac(f):
    """Share of a hole line's length inside the course boundary (fetch_course.line_inside, stored by summarise);
    older osm.geojson files carry only the flag."""
    p = f["properties"]
    v = p.get("inside_frac")
    if isinstance(v, (int, float)):
        return float(v)
    return 0.0 if p.get("inside_course") is False else 1.0


def select_hole_ways(fc, max_holes=18):
    """-> (fc copy, [dropped osm ids]). When golf=hole refs repeat or there are more than max_holes ways, the
    ways of a neighbouring course go. A way is "foreign" when it is outside this course (inside_course False) or
    its midpoint is inside another leisure=golf_course polygon (one that does not hold most of this course's ways).
    Per ref:
      * a hand-mapped (src=hand, osm_supplement) way wins and is never dropped (a reviewer put it there on purpose);
      * else, when the ref repeats, ONE way is kept: the best by (not foreign, connected to this course's greens /
        tees, share of length inside the boundary, has a par tag); a foreign best is kept (and re-flagged
        inside_course True) only when it is connected to this course's green or tee, so a ref never vanishes just
        because both copies looked doubtful (Hodge Park 10: this course's dogleg and a neighbour's 10 were both
        dropped, and the router redrew 10 through the woods);
      * a lone foreign way is dropped unless both ends connect to this course's tee and green.
    "Connected": last point within CONNECT_GREEN_YD of a golf=green, first point within CONNECT_TEE_YD of a
    golf=tee, both inside this course and not inside the other course."""
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

    P = _proj_for(fc)

    def own_features(kind):
        out = []
        for f in feats:
            if f["properties"].get("golf") != kind or f["properties"].get("inside_course") is False:
                continue
            g = _shp(f)
            if g is None or g.is_empty or any(o.contains(g.representative_point()) for o in others):
                continue
            out.append(P.geom(g))
        return unary_union(out) if out else None
    greens, tees = own_features("green"), own_features("tee")

    def connected(f):
        c = f["geometry"]["coordinates"]
        t = tees is not None and Point(P.fwd(*c[0][:2])).distance(tees) <= CONNECT_TEE_YD
        g = greens is not None and Point(P.fwd(*c[-1][:2])).distance(greens) <= CONNECT_GREEN_YD
        return int(t) + int(g)

    info = {}
    for f in holes:
        mid = shape(f["geometry"]).interpolate(0.5, normalized=True)
        foreign = f["properties"].get("inside_course") is False or any(g.contains(mid) for g in others)
        info[id(f)] = dict(foreign=foreign, conn=connected(f), frac=_inside_frac(f),
                           par=str(f["properties"].get("par", "")).isdigit())
    groups = {}
    for f in holes:
        groups.setdefault(str(f["properties"].get("ref")) if f["properties"].get("ref") else None, []).append(f)
    drop, rescue = set(), set()
    for ref, fs in groups.items():
        hand = [f for f in fs if _hand(f)]
        if hand:
            drop |= {id(f) for f in fs if not _hand(f)}
            continue
        if ref is None or len(fs) == 1:
            for f in fs:
                i = info[id(f)]
                if i["foreign"]:
                    (drop if i["conn"] < 2 else rescue).add(id(f))
            continue
        best = max(fs, key=lambda f: (not info[id(f)]["foreign"], info[id(f)]["conn"], info[id(f)]["frac"],
                                      info[id(f)]["par"]))
        drop |= {id(f) for f in fs if f is not best}
        bi = info[id(best)]
        if bi["foreign"]:
            if bi["conn"] >= 1:
                rescue.add(id(best))
            else:
                drop.add(id(best))                           # every copy is a neighbour's
    kept_refs = [str(f["properties"].get("ref")) for f in holes if id(f) not in drop and f["properties"].get("ref")]
    if not kept_refs:                                        # never drop every hole
        return fc, []
    dropped = [f["properties"].get("osm_id") for f in holes if id(f) in drop]
    if not drop and not rescue:
        return fc, []
    out = []
    for f in feats:
        if id(f) in drop:
            continue
        if id(f) in rescue:
            f = dict(f, properties=dict(f["properties"], inside_course=True, inside_course_rescued=True))
        out.append(f)
    return dict(fc, features=out), dropped


# ----------------------------------------------------------------------------- hole refs
REF_STOP = {"no", "course", "the", "nine", "golf", "hole", "holes", "club", "links", "at", "of"}
REF_PRACTICE = {"practice", "academy", "range", "warmup", "warm", "pitch", "putt", "learning"}


def _ref_tokens(text):
    return tuple(t for t in re.findall(r"[a-z]+|\d+", str(text).lower()) if t not in REF_STOP)


def parse_hole_ref(ref):
    """OSM golf=hole ref -> (qualifier tokens, hole number) | None. "7" -> ((), 7); "Black - 13" -> (("black",), 13);
    "1 - #2" -> (("2",), 1); "L4" -> (("l",), 4); "Practice 1" -> (("practice",), 1); "Hole 5" -> ((), 5);
    "tee_boxes" -> None."""
    r = str(ref).strip()
    m = re.fullmatch(r"(\d{1,2})", r)
    if m:
        return (), int(m.group(1))
    m = (re.fullmatch(r"(\d{1,2})\s*[-\u2013\u2014:/|,]\s*(.*\D.*|\d+)", r))
    if m:
        return _ref_tokens(m.group(2)), int(m.group(1))
    m = re.fullmatch(r"(.*?\D)\s*[-\u2013\u2014:/|,#]?\s*(\d{1,2})", r)
    if m:
        return _ref_tokens(m.group(1)), int(m.group(2))
    return None


def normalize_hole_refs(fc, names=()):
    """-> (fc copy, [notes]). OSM hole refs the model cannot number (v2 hole_number: int(ref)) are made plain numbers:
    a multi-course site maps its holes "Black - 13" (Bethpage), "1 - #2" (Pinehurst), "L4" / "M4" / "R4" (Neshanic
    Valley's nines), "Practice 1" (Old Works) or "tee_boxes". The ref group whose qualifier is named in `names` (the
    request / OSM course name: "Bethpage Black", "Pinehurst No. 2") is kept, else the plain-number group, else the
    largest group; practice / academy groups and unparseable refs go. Plain refs only: unchanged."""
    feats = fc.get("features", [])
    holes = [f for f in feats if f["properties"].get("golf") == "hole" and f["properties"].get("ref") not in (None, "")]
    parsed = {id(f): parse_hole_ref(f["properties"]["ref"]) for f in holes}
    if all(re.fullmatch(r"\d+", str(f["properties"]["ref"]).strip()) for f in holes):
        return fc, []
    groups = {}
    for f in holes:
        p = parsed[id(f)]
        if p is not None and not (set(p[0]) & REF_PRACTICE):
            groups.setdefault(p[0], []).append(f)
    want = set()
    for n in names or ():
        want |= set(_ref_tokens(n))
    named = [k for k in groups if k and set(k) <= want]
    if named:
        keep = max(named, key=lambda k: len(groups[k]))
        why = f"the '{' '.join(keep)}' holes (named in the request)"
    elif () in groups:
        keep, why = (), "the plain-numbered holes"
    elif groups:
        keep = max(groups, key=lambda k: len(groups[k]))
        why = f"the largest ref group '{' '.join(keep)}'"
    else:
        return fc, []
    kept = {id(f) for f in groups[keep]}
    drop = {id(f) for f in holes if id(f) not in kept}
    out = []
    for f in feats:
        if id(f) in drop:
            continue
        if id(f) in kept and str(f["properties"]["ref"]) != str(parsed[id(f)][1]):
            p = dict(f["properties"], ref=str(parsed[id(f)][1]), ref_osm=f["properties"]["ref"])
            f = dict(f, properties=p)
        out.append(f)
    notes = [f"hole refs: kept {why} ({len(kept)} ways, refs as plain numbers)"]
    if drop:
        gone = sorted({str(f["properties"]["ref"]) for f in holes if id(f) in drop})
        notes.append(f"ignored {len(drop)} golf=hole way(s) of another course / practice area by ref: "
                     + ", ".join(gone[:12]) + (" ..." if len(gone) > 12 else ""))
    return dict(fc, features=out), notes


# ----------------------------------------------------------------------------- 36-hole facilities
SPLIT_MIN_DUP_REFS = 6        # this many repeated plain refs = two courses' holes, not a neighbour's stray way
SUB_COURSE_MIN_HOLES = 6
NAME_STOP = REF_STOP | {"course", "courses", "gc", "cc", "country", "resort", "par", "north", "south", "east",
                         "west"}


def _hole_no(f):
    """A hole way's number: its plain ref, else the number in its name when the ref is missing ("#7 - par 4",
    "River # 9 - par 4": Queenstown Harbor maps five River holes so), else None."""
    p = f["properties"]
    r = str(p.get("ref") or "").strip()
    if re.fullmatch(r"\d{1,2}", r):
        return int(r)
    if r:
        return None
    nm = str(p.get("name") or "")
    m = re.search(r"#\s*(\d{1,2})\b", nm) or re.match(r"\s*(?:hole\s*)?(\d{1,2})\b", nm, re.I)
    return int(m.group(1)) if m else None


def _plain_holes(fc):
    """This course's numbered golf=hole lines (inside_course not False; a neighbour's stray ways stay
    select_hole_ways' job)."""
    return [f for f in fc.get("features", []) if f["properties"].get("golf") == "hole" and f.get("geometry")
            and f["geometry"]["type"] == "LineString" and f["properties"].get("inside_course") is not False
            and _hole_no(f) is not None]


def _course_label(f):
    """The course a hole way says it belongs to: golf:course:name (Troon North: 'Monument Course'), else its
    name's words ('River # 9 - par 4' -> 'river')."""
    p = f["properties"]
    return p.get("golf:course:name") or " ".join(sorted(_name_tokens(re.sub(r"\d+", " ", str(p.get("name") or "")))))


def _name_tokens(text):
    return {t for t in re.findall(r"[a-z]+", str(text or "").lower()) if t not in NAME_STOP and len(t) > 1}


def _chains(holes, P):
    """Group hole ways into k courses (k = the most copies of one ref) by walking the round: each copy of ref n+1
    joins the course whose hole n green (line end) is nearest its tee (line start); refs below the seed walk back."""
    by = {}
    for f in holes:
        by.setdefault(_hole_no(f), []).append(f)
    k = max(len(v) for v in by.values())
    if k < 2 or k > 4:
        return None
    seed = min(r for r, v in by.items() if len(v) == k)
    ends = lambda f: (P.fwd(*f["geometry"]["coordinates"][0][:2]), P.fwd(*f["geometry"]["coordinates"][-1][:2]))  # noqa: E731
    d = lambda a, b: math.hypot(a[0] - b[0], a[1] - b[1])                                                        # noqa: E731
    chains = [[f] for f in by[seed]]

    def place(fs, key):
        best = None
        for perm in itertools.permutations(range(k), len(fs)):
            c = sum(key(chains[ci], f) for ci, f in zip(perm, fs))
            if best is None or c < best[0]:
                best = (c, perm)
        return best[1]
    for r in sorted(x for x in by if x > seed):
        fs = by[r]
        if len(fs) > k:
            return None
        for ci, f in zip(place(fs, lambda ch, f: d(ends(ch[-1])[1], ends(f)[0])), fs):
            chains[ci].append(f)
    for r in sorted((x for x in by if x < seed), reverse=True):
        fs = by[r]
        if len(fs) > k:
            return None
        for ci, f in zip(place(fs, lambda ch, f: d(ends(f)[1], ends(ch[0])[0])), fs):
            chains[ci].insert(0, f)
    return chains


def course_groups(fc):
    """The hole ways of a multi-course facility, one group per course: [{holes, name, how}] or [] when the hole
    ways are one course. Sub-course leisure=golf_course polygons first (each holding >= SUB_COURSE_MIN_HOLES hole
    midpoints but not most of them: Troon North's Monument / Pinnacle inside the club outline), else the hole
    ways' own names ("River 3" / "Lakes 3"), else chains walked green -> next tee (_chains)."""
    holes = _plain_holes(fc)
    refs = [_hole_no(f) for f in holes]
    dup = sum(1 for r in set(refs) if refs.count(r) > 1)
    if dup < SPLIT_MIN_DUP_REFS or any(_hand(f) for f in holes):
        return []
    mids = [shape(f["geometry"]).interpolate(0.5, normalized=True) for f in holes]
    subs = []
    for f in fc.get("features", []):
        if f["properties"].get("leisure") != "golf_course" or (f.get("geometry") or {}).get("type") not in (
                "Polygon", "MultiPolygon"):
            continue
        g = _shp(f)
        if g is None:
            continue
        idx = [i for i, m in enumerate(mids) if g.contains(m)]
        if SUB_COURSE_MIN_HOLES <= len(idx) <= 0.75 * len(holes):
            subs.append((g.area, f["properties"].get("name"), idx))
    if len(subs) >= 2:
        taken, groups = set(), []
        for _, nm, idx in sorted(subs, key=lambda t: t[0]):            # smallest polygon first
            mine = [i for i in idx if i not in taken]
            if len(mine) >= SUB_COURSE_MIN_HOLES:
                taken |= set(mine)
                groups.append(dict(holes=[holes[i] for i in mine], name=nm, how="sub-course outline"))
        if len(groups) >= 2 and len(taken) >= 0.8 * len(holes):
            return groups
    named = {}
    for f in holes:
        named.setdefault(_course_label(f), []).append(f)
    big = {k: v for k, v in named.items() if k and len(v) >= SUB_COURSE_MIN_HOLES}
    if len(big) >= 2 and sum(len(v) for v in big.values()) >= 0.8 * len(holes):
        return [dict(holes=v, name=k, how="hole way names") for k, v in big.items()]
    ch = _chains(holes, _proj_for(fc))
    if not ch:
        return []
    out = []
    for c in ch:                                     # a chain is named by the words its hole ways carry
        words = sorted({w for f in c for w in _name_tokens(_course_label(f))})
        out.append(dict(holes=c, name=" ".join(words) or None, how="hole chains (green -> next tee)"))
    return out


def _parse_near(near):
    if not near:
        return None
    try:
        if isinstance(near, str):
            a, b = (float(x) for x in near.split(",")[:2])
        else:
            a, b = float(near[0]), float(near[1])
        return a, b                                                  # (lat, lon)
    except Exception:                                                # noqa: BLE001
        return None


def split_courses(fc, names=(), near=None):
    """-> (fc copy, [notes]). A 36-hole facility mapped as one OSM outline (Queenstown Harbor River + Lakes,
    unnamed; Troon North Monument + Pinnacle) carries refs 1-18 twice, and the per-ref pick of select_hole_ways
    mixed the two courses. Here the hole ways are grouped by course (course_groups) and ONE course is kept:
    the group whose name (sub-course outline / hole way names, words the groups share ignored) is named in
    `names` (request / OSM course name), else the group whose hole lines are nearest the request's `near` point
    (lat, lon), else the largest (CHECK). Only golf=hole ways are dropped."""
    groups = course_groups(fc)
    if len(groups) < 2:
        return fc, []
    want = set()
    for n in names or ():
        want |= _name_tokens(n)
    toks = [_name_tokens(g["name"]) for g in groups]
    common = set.intersection(*toks) if toks else set()
    score = [len((t - common) & want) for t in toks]
    pick, why = None, None
    if max(score) > 0 and score.count(max(score)) == 1:
        pick = score.index(max(score))
        why = f"'{groups[pick]['name']}' (named in the request)"
    nr = _parse_near(near)
    if pick is None and nr is not None:
        P = _proj_for(fc)
        q = P.fwd(nr[1], nr[0])

        def dist(g):
            ds = sorted(Point(q).distance(P.geom(shape(f["geometry"]))) for f in g["holes"])
            return float(statistics.median(ds[: max(3, len(ds) // 3)]))      # the hole lines nearest the point
        ds = [dist(g) for g in groups]
        pick = min(range(len(ds)), key=ds.__getitem__)
        why = f"the course nearest the request's near point ({ds[pick]:.0f} yds vs " + \
              ", ".join(f"{x:.0f}" for i, x in enumerate(ds) if i != pick) + ")"
    if pick is None:
        pick = max(range(len(groups)), key=lambda i: len(groups[i]["holes"]))
        why = "the largest group (no name or near point decides: CHECK the course)"
    keep = {id(f) for f in groups[pick]["holes"]}
    drop = {id(f) for g in groups for f in g["holes"] if id(f) not in keep}
    out = []
    for f in fc["features"]:
        if id(f) in drop:
            continue
        if id(f) in keep and not str(f["properties"].get("ref") or "").strip():
            f = dict(f, properties=dict(f["properties"], ref=str(_hole_no(f)), ref_from="name"))
        out.append(f)
    note = (f"multi-course facility: {len(groups)} courses' hole ways in one outline (by {groups[pick]['how']}: "
            + ", ".join(f"{g['name'] or '#' + str(i + 1)} {len(g['holes'])}" for i, g in enumerate(groups))
            + f"); kept {why}, {len(keep)} ways; ignored {len(drop)}")
    return dict(fc, features=out), [note]


def clean_osm(fc, names=(), near=None):
    """-> (fc, [notes]): drop_practice_tees + normalize_hole_refs + select_hole_ways. names = the request's and OSM's
    course names (pick the right course's holes on a multi-course site)."""
    notes = []
    fc, rn = normalize_hole_refs(fc, names)
    notes += rn
    fc, sc = split_courses(fc, names, near)
    notes += sc
    fc, t = drop_practice_tees(fc)
    if t:
        notes.append(f"ignored {len(t)} practice / driving-range tee box(es): OSM {', '.join(map(str, t[:6]))}")
    fc, sup = supplement_hole_ways(fc)
    if sup:
        notes.append(f"osm_supplement hole ways replace {len(sup)} OSM golf=hole way(s) with the same ref: "
                     f"OSM {', '.join(map(str, sup[:8]))}")
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
                        cap = max(0.0, d - OBSTACLE_MARGIN_YD)
                        new = (S[0] - u[0] * cap, S[1] - u[1] * cap)
                        why = (f"walk-back ran onto a {h[0]} (OSM {h[1]}) {d:.0f} yds behind the line start: "
                               f"capped there ({-along - cap:.0f} yds short of the card)")
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
