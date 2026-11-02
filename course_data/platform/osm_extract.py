"""OSM from a Geofabrik state extract + osmium instead of the public Overpass mirrors (which time out under load:
Kapalua, Queenstown Harbor, TPC Louisiana, Troon North, World Woods and Tournament Club of Iowa failed their package
stage on Overpass ReadTimeouts, 2026-11-02). The same idea as the national index (library/national_index.py).

What it answers, in the exact shapes the Overpass path produces, so everything downstream is unchanged:
  features_data(state, snwe)   the `fetch_course.features_query` response (`out body geom`): `osmium extract` cuts the
                               bbox + EXTRACT_MARGIN_M from the state .osm.pbf (smart strategy: complete ways and
                               multipolygon / boundary relations), then the query's own filters (parsed from
                               features_query, so the two cannot drift) and Overpass's bbox semantics (a way / relation
                               is in when one of its segments or member nodes touches the box) pick the elements;
                               -> osm_guard judges it like any mirror answer and fetch_course.to_geojson converts it
  StateIndex(state)            resolve.py's name search / element / around / enclosing-area / hole-count / boundary
                               queries over the state's leisure=golf_course objects + golf=hole ways
                               (`osmium tags-filter`, once per state)

Mode (environment, set by course_page_one.yml from the request's "osm_source"):
  OSM_SOURCE   "overpass" (never the extract), "auto" (default: Overpass first, one pass; the extract when Overpass
               fails, and from then on for the rest of the run), "geofabrik" (the extract only)
  OSM_PBF_DIR  where <ST>.osm.pbf lives (downloaded on first use; the workflow caches the folder per state + day)
"""
import math
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import platform_common as pc  # noqa: E402

GEOFABRIK = "https://download.geofabrik.de/north-america/us/{}-latest.osm.pbf"
EXTRACT_MARGIN_M = 1000.0      # osmium cuts this much more than the query bbox: a way whose only nodes near the box
                               # are outside it (a long segment crossing it) is still in the cut
SMART_TYPES = "multipolygon,boundary"
GOLF_FILTER = ["nwr/leisure=golf_course", "w/golf=hole"]
_failed_overpass = [False]     # auto mode: Overpass failed once in this process -> extract from then on


# ----------------------------------------------------------------------------- mode
def mode():
    m = str(os.environ.get("OSM_SOURCE") or "auto").strip().lower()
    return m if m in ("overpass", "auto", "geofabrik") else "auto"


def forced():
    """True when the extract answers instead of Overpass (OSM_SOURCE=geofabrik, or auto after an Overpass failure)."""
    return mode() == "geofabrik" or (allowed() and _failed_overpass[0])


def allowed():
    """The extract may be used: OSM_SOURCE=geofabrik, or auto with OSM_PBF_DIR set (the Actions package job; never a
    surprise state download in a local / test run)."""
    return mode() == "geofabrik" or (mode() == "auto" and bool(os.environ.get("OSM_PBF_DIR")))


def overpass_failed(why=""):
    if mode() == "auto" and not _failed_overpass[0]:
        pc.log("osm_extract: Overpass failed, Geofabrik extract from now on:", str(why)[:300])
    _failed_overpass[0] = True


# ----------------------------------------------------------------------------- the state file
def geofabrik_url(state):
    return GEOFABRIK.format(pc.STATES[pc.state_code(state)].lower().replace(" ", "-"))


def pbf_dir():
    return os.environ.get("OSM_PBF_DIR") or os.path.join(os.path.expanduser("~"), "geofabrik")


def pbf_path(state):
    return os.path.join(pbf_dir(), pc.state_code(state) + ".osm.pbf")


def _download(url, path):
    import requests
    with requests.get(url, headers=pc.UA, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(path + ".part", "wb") as fh:
            for b in r.iter_content(1 << 20):
                fh.write(b)
    os.replace(path + ".part", path)


def ensure_pbf(state, download=_download, sleep=time.sleep):
    """-> path of the state's .osm.pbf, downloading it when it is not on disk (cache miss)."""
    p = pbf_path(state)
    if os.path.exists(p) and os.path.getsize(p) > 0:
        return p
    os.makedirs(os.path.dirname(p), exist_ok=True)
    url = geofabrik_url(state)
    for k in range(3):
        try:
            t0 = time.time()
            download(url, p)
            pc.log(f"osm_extract: {url} -> {p} ({os.path.getsize(p) / 1e6:.0f} MB, {time.time() - t0:.0f}s)")
            return p
        except Exception as e:                                  # noqa: BLE001
            pc.log(f"osm_extract: download try {k + 1} failed: {e!r}"[:300])
            if k == 2:
                raise
            sleep(30 * (k + 1))


def osm_base(pbf):
    """The extract's replication timestamp ('2026-11-01T20:21:02Z'), or None."""
    try:
        r = subprocess.run(["osmium", "fileinfo", "-g", "header.option.osmosis_replication_timestamp", pbf],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or None
    except Exception:                                           # noqa: BLE001
        return None


def pad_snwe(snwe, m):
    s, w, n, e = snwe
    dlat = m / 111320.0
    dlon = dlat / max(0.05, math.cos(math.radians((s + n) / 2)))
    return (s - dlat, w - dlon, n + dlat, e + dlon)


def extract(pbf, snwe, out, margin_m=EXTRACT_MARGIN_M):
    """`osmium extract` of the bbox (+ margin) to OSM XML `out`."""
    s, w, n, e = pad_snwe(snwe, margin_m)
    cmd = ["osmium", "extract", "-b", f"{w:.7f},{s:.7f},{e:.7f},{n:.7f}", "--strategy", "smart",
           "-S", f"types={SMART_TYPES}", "-f", "osm", "-o", out, "--overwrite", pbf]
    subprocess.run(cmd, check=True, capture_output=True, timeout=1800)
    return out


# ----------------------------------------------------------------------------- OSM XML -> Overpass elements
def read_osm(path):
    """OSM XML -> dict(nodes={id: (lat, lon, tags)}, ways={id: (node ids, tags)}, rels={id: (members, tags)})."""
    nodes, ways, rels = {}, {}, {}
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag not in ("node", "way", "relation"):
            continue
        tags = {t.get("k"): t.get("v") for t in el.findall("tag")}
        oid = int(el.get("id"))
        if el.tag == "node":
            nodes[oid] = (float(el.get("lat")), float(el.get("lon")), tags)
        elif el.tag == "way":
            ways[oid] = ([int(n.get("ref")) for n in el.findall("nd")], tags)
        else:
            rels[oid] = ([(m.get("type"), int(m.get("ref")), m.get("role") or "") for m in el.findall("member")], tags)
        el.clear()
    return dict(nodes=nodes, ways=ways, rels=rels)


def _way_geom(osm, wid):
    w = osm["ways"].get(wid)
    if not w:
        return []
    return [dict(lat=osm["nodes"][n][0], lon=osm["nodes"][n][1]) for n in w[0] if n in osm["nodes"]]


def _bounds(pts):
    if not pts:
        return None
    return dict(minlat=min(p["lat"] for p in pts), minlon=min(p["lon"] for p in pts),
                maxlat=max(p["lat"] for p in pts), maxlon=max(p["lon"] for p in pts))


def element(osm, typ, oid, geom=True):
    """One object as Overpass prints it with `out body geom` (geom=True) or `out tags center bb` (geom=False)."""
    if typ == "node":
        lat, lon, tags = osm["nodes"][oid]
        el = dict(type="node", id=oid, lat=lat, lon=lon)
        if tags:
            el["tags"] = dict(tags)
        return el
    if typ == "way":
        nds, tags = osm["ways"][oid]
        g = _way_geom(osm, oid)
        el = dict(type="way", id=oid, bounds=_bounds(g))
        if geom:
            el.update(nodes=list(nds), geometry=g)
    else:
        mem, tags = osm["rels"][oid]
        members, pts = [], []
        for t, ref, role in mem:
            m = dict(type=t, ref=ref, role=role)
            if t == "way":
                g = _way_geom(osm, ref)
                m["geometry"] = g
                pts += g
            elif t == "node" and ref in osm["nodes"]:
                m.update(lat=osm["nodes"][ref][0], lon=osm["nodes"][ref][1])
                pts.append(dict(lat=m["lat"], lon=m["lon"]))
            members.append(m)
        el = dict(type="relation", id=oid, bounds=_bounds(pts))
        if geom:
            el["members"] = members
    if el.get("bounds") is None:
        el.pop("bounds", None)
    elif not geom:
        b = el["bounds"]
        el["center"] = dict(lat=(b["minlat"] + b["maxlat"]) / 2, lon=(b["minlon"] + b["maxlon"]) / 2)
    if tags:
        el["tags"] = dict(tags)
    return el


# ----------------------------------------------------------------------------- the features query, mirrored
_FILTER_RX = re.compile(r'^\s*(node|way|relation|nwr)\["([^"]+)"(?:(=|~)"([^"]*)")?\]\([^)]*\);', re.M)


def query_filters(query=None):
    """The (types, key, op, value) filters of an Overpass bbox union query (default fetch_course.features_query),
    parsed from its text: the extract path keeps exactly what the Overpass query asks for."""
    if query is None:
        import fetch_course as fcm
        query = fcm.features_query((0, 0, 0, 0))
    out = []
    for typ, k, op, v in _FILTER_RX.findall(query):
        types = ("node", "way", "relation") if typ == "nwr" else (typ,)
        out.append((types, k, op or None, v if op else None))
    if not out:
        raise ValueError("no filters parsed from the features query")
    return out


def tags_match(typ, tags, filters):
    for types, k, op, v in filters:
        if typ not in types or k not in tags:
            continue
        if op is None or (op == "=" and tags[k] == v) or (op == "~" and re.search(v, tags[k])):
            return True
    return False


def _in_box(lat, lon, box):
    s, w, n, e = box
    return s <= lat <= n and w <= lon <= e


def _seg_hits_box(a, b, box):
    """Segment a-b ((lat, lon)) touches the box (Liang-Barsky clip)."""
    s, w, n, e = box
    x0, y0, x1, y1 = a[1], a[0], b[1], b[0]
    t0, t1, dx, dy = 0.0, 1.0, x1 - x0, y1 - y0
    for p, q in ((-dx, x0 - w), (dx, e - x0), (-dy, y0 - s), (dy, n - y0)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def _line_hits_box(pts, box):
    if any(_in_box(p[0], p[1], box) for p in pts):
        return True
    return any(_seg_hits_box(a, b, box) for a, b in zip(pts, pts[1:]))


def _way_pts(osm, wid):
    w = osm["ways"].get(wid)
    return [osm["nodes"][n][:2] for n in w[0] if n in osm["nodes"]] if w else []


def select(osm, snwe, filters=None):
    """Overpass `(<filters>(bbox);); out body geom;` over parsed OSM: the elements, sorted like Overpass prints
    them (nodes, ways, relations; by id)."""
    filters = filters or query_filters()
    out = []
    for oid in sorted(osm["nodes"]):
        lat, lon, tags = osm["nodes"][oid]
        if tags and tags_match("node", tags, filters) and _in_box(lat, lon, snwe):
            out.append(element(osm, "node", oid))
    for oid in sorted(osm["ways"]):
        tags = osm["ways"][oid][1]
        if tags and tags_match("way", tags, filters) and _line_hits_box(_way_pts(osm, oid), snwe):
            out.append(element(osm, "way", oid))
    for oid in sorted(osm["rels"]):
        mem, tags = osm["rels"][oid]
        if not (tags and tags_match("relation", tags, filters)):
            continue
        hit = False
        for t, ref, _ in mem:
            if t == "node" and ref in osm["nodes"] and _in_box(*osm["nodes"][ref][:2], snwe):
                hit = True
            elif t == "way" and _line_hits_box(_way_pts(osm, ref), snwe):
                hit = True
            if hit:
                break
        if hit:
            out.append(element(osm, "relation", oid))
    return out


def overpass_shape(elements, base=None, generator="geofabrik+osmium (course_data/platform/osm_extract.py)"):
    return dict(version=0.6, generator=generator,
                osm3s=dict(timestamp_osm_base=base, copyright="The data included in this document is from "
                           "www.openstreetmap.org. The data is made available under ODbL."),
                elements=elements)


def features_from_osm_file(path, snwe, base=None, query=None):
    return overpass_shape(select(read_osm(path), snwe, query_filters(query)), base)


def features_data(state, snwe, work=None, query=None):
    """The answer to `query` (default fetch_course.features_query: `(nwr[..](bbox); ...); out body geom;`) for bbox
    snwe (S, W, N, E) from the state's Geofabrik extract."""
    pbf = ensure_pbf(state)
    work = work or pbf_dir()
    out = os.path.join(work, f"cut_{os.getpid()}_{int(time.time() * 1000)}.osm")
    t0 = time.time()
    try:
        extract(pbf, snwe, out)
        data = features_from_osm_file(out, snwe, osm_base(pbf), query)
    finally:
        if os.path.exists(out):
            os.remove(out)
    pc.log(f"osm_extract: {len(data['elements'])} elements for {snwe} from {os.path.basename(pbf)} "
           f"({time.time() - t0:.0f}s, data as of {data['osm3s']['timestamp_osm_base']})")
    return data


# ----------------------------------------------------------------------------- resolve over the state's courses
def _dist_m(lat, lon, a, b):
    """Distance (m) from (lat, lon) to the segment a-b ((lat, lon)), equirectangular."""
    k = math.cos(math.radians(lat)) * 111320.0
    ax, ay, bx, by = (a[1] - lon) * k, (a[0] - lat) * 111320.0, (b[1] - lon) * k, (b[0] - lat) * 111320.0
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L))
    return math.hypot(ax + t * dx, ay + t * dy)


class StateIndex:
    """The state's leisure=golf_course objects + golf=hole ways (from an OSM XML: `osmium tags-filter` output)."""

    def __init__(self, osm):
        self.osm = osm
        self.courses = [("node", i) for i, v in sorted(osm["nodes"].items()) if v[2].get("leisure") == "golf_course"]
        self.courses += [("way", i) for i, v in sorted(osm["ways"].items()) if v[1].get("leisure") == "golf_course"]
        self.courses += [("relation", i) for i, v in sorted(osm["rels"].items())
                         if v[1].get("leisure") == "golf_course"]
        self.holes = [_way_pts(osm, i) for i, v in sorted(osm["ways"].items()) if v[1].get("golf") == "hole"]
        self._rings = {}

    @classmethod
    def from_file(cls, path):
        return cls(read_osm(path))

    @classmethod
    def for_state(cls, state):
        st = pc.state_code(state)
        if st in _INDEX:
            return _INDEX[st]
        pbf = ensure_pbf(st)
        out = os.path.join(pbf_dir(), st + ".golf.osm")
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(pbf):
            t0 = time.time()
            subprocess.run(["osmium", "tags-filter", pbf, *GOLF_FILTER, "-o", out, "-f", "osm", "--overwrite"],
                           check=True, capture_output=True, timeout=1800)
            pc.log(f"osm_extract: {st} golf index {os.path.getsize(out) / 1e6:.1f} MB ({time.time() - t0:.0f}s)")
        _INDEX[st] = idx = cls.from_file(out)
        return idx

    def has(self, typ, oid):
        return oid in self.osm[{"node": "nodes", "way": "ways", "relation": "rels"}[typ]]

    def tags(self, typ, oid):
        v = self.osm[{"node": "nodes", "way": "ways", "relation": "rels"}[typ]][oid]
        return v[2] if typ == "node" else v[1]

    def bb(self, typ, oid):
        """`out tags center bb` element."""
        return element(self.osm, typ, oid, geom=False)

    def body_geom(self, typ, oid):
        """`out body geom` element."""
        return element(self.osm, typ, oid, geom=True)

    # --- resolve.py's queries
    def by_name(self, *regexes):
        """nwr[leisure=golf_course][name~rx1,i][name~rx2,i]... -> `out tags center bb` elements."""
        rxs = [re.compile(r, re.I) for r in regexes]
        return [self.bb(t, i) for t, i in self.courses
                if self.tags(t, i).get("name") and all(r.search(self.tags(t, i)["name"]) for r in rxs)]

    def by_id(self, typ, oid):
        return [self.bb(typ, oid)] if self.has(typ, oid) else []

    def _pts(self, typ, oid):
        if typ == "node":
            return [[self.osm["nodes"][oid][:2]]]
        if typ == "way":
            return [_way_pts(self.osm, oid)]
        return [_way_pts(self.osm, r) if t == "way" else [self.osm["nodes"][r][:2]]
                for t, r, _ in self.osm["rels"][oid][0] if (t == "way" or r in self.osm["nodes"])]

    def rings(self, typ, oid):
        """Outer rings ([[lon, lat], ...]) of an area course (way / multipolygon relation), via to_geojson."""
        import fetch_course as fcm
        if typ == "node":
            return []
        if (typ, oid) in self._rings:
            return self._rings[(typ, oid)]
        self._rings[(typ, oid)] = self._rings_of(typ, oid)
        return self._rings[(typ, oid)]

    def _rings_of(self, typ, oid):
        import fetch_course as fcm
        feats = fcm.to_geojson([self.body_geom(typ, oid)])["features"]
        if not feats:
            return []
        g = feats[0]["geometry"]
        if g["type"] == "LineString":
            c = g["coordinates"]
            return [c + [c[0]]] if len(c) >= 3 else []
        return fcm.outer_rings(g)

    def around(self, lat, lon, radius=4000):
        """nwr[leisure=golf_course](around:r,lat,lon): a node / segment within r m, or the point inside the area."""
        import fetch_course as fcm
        out = []
        dlat = radius / 111320.0
        dlon = dlat / max(0.05, math.cos(math.radians(lat)))
        for t, i in self.courses:
            b = self.bb(t, i)
            if "lat" in b:
                b = dict(bounds=dict(minlat=b["lat"], maxlat=b["lat"], minlon=b["lon"], maxlon=b["lon"]))
            bd = b.get("bounds")
            if not bd or not (bd["minlat"] - dlat <= lat <= bd["maxlat"] + dlat and
                              bd["minlon"] - dlon <= lon <= bd["maxlon"] + dlon):
                continue
            near = False
            for line in self._pts(t, i):
                if len(line) == 1:
                    near = _dist_m(lat, lon, line[0], line[0]) <= radius
                else:
                    near = any(_dist_m(lat, lon, a, b) <= radius for a, b in zip(line, line[1:]))
                if near:
                    break
            if not near:
                near = any(fcm.point_in_ring([lon, lat], r) for r in self.rings(t, i))
            if near:
                out.append(self.bb(t, i))
        return out

    def enclosing(self, lat, lon):
        """is_in(lat, lon) -> way / relation leisure=golf_course areas -> `out tags center bb` elements."""
        import fetch_course as fcm
        out = []
        for t, i in self.courses:
            b = self.bb(t, i).get("bounds") if t != "node" else None
            if b and b["minlat"] <= lat <= b["maxlat"] and b["minlon"] <= lon <= b["maxlon"] and \
                    any(fcm.point_in_ring([lon, lat], r) for r in self.rings(t, i)):
                out.append(self.bb(t, i))
        return out

    def hole_count(self, typ, oid):
        """way[golf=hole](area of the course): golf=hole ways with a node inside the course's outer rings."""
        import fetch_course as fcm
        rings = self.rings(typ, oid)
        if not rings:
            return 0
        boxes = [(min(q[0] for q in r), min(q[1] for q in r), max(q[0] for q in r), max(q[1] for q in r))
                 for r in rings]                                    # rings are [lon, lat]: (W, S, E, N)
        n = 0
        for pts in self.holes:
            if any(bs <= p[0] <= bn and bw <= p[1] <= be and fcm.point_in_ring([p[1], p[0]], r)
                   for p in pts for (bw, bs, be, bn), r in zip(boxes, rings)):
                n += 1
        return n


_INDEX = {}
