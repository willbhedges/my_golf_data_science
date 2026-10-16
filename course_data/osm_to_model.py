"""OSM golf features -> the tee-strategy model's hole dicts (no screenshots, no tracing).

  python course_data/osm_to_model.py course_data/spirit_hollow [--tee blue] [--lengths 1=419,2=616]

The model (mozingo/tee_strategy.py) works in a 2-D frame with `tee`, `dot270` (a point 270 yds
down the tee line), `green` and `zones = [(lie, polygon), ...]`, and gets yards from
|dot270 - tee| / 270. Here the frame is *yards, rotated so the tee line points up the
screen*, i.e. a point is (x, y) = (yds right of the line, -yds along it):

    tee = (0, 0)    dot270 = (0, -270)    px_per_yd = 1

so every polygon can be read straight off as (right, -along) and fed to the model unchanged
(it also matches the screenshot convention: screen y grows downwards).

The tee line is tee -> second node of the OSM `golf=hole` way (the hole's first aiming point;
for a par 3 that's the green). OSM lies map to the model's lies as in LIE_MAP; later zones in
ZONE_ORDER win where polygons overlap, like `lie_at` does. Anything outside the course
boundary is OB unless --no-boundary-ob (OSM boundaries are often loose, so check the preview).

Writes holes_from_osm.json and holes_preview.png next to osm.geojson.
"""
import argparse
import json
import math
import os

import numpy as np

YD = 0.9144
ZONE_ORDER = ["ob", "native", "recovery", "fairway", "water", "sand"]
ROAD_TYPES = {"motorway", "trunk", "primary", "secondary", "tertiary", "residential",
              "unclassified", "motorway_link", "trunk_link", "primary_link", "secondary_link"}
WINDOW = dict(lat=150, back=40, beyond=40)          # yds kept around each hole


def lie_of(p, geom_type):
    """OSM tags -> model lie (or None to ignore). Lines get buffered by the returned width."""
    g, nat, lu = p.get("golf"), p.get("natural"), p.get("landuse")
    if g == "fairway":
        return "fairway", 0
    if g == "bunker" or nat == "sand":
        return "sand", 0
    if g in ("water_hazard", "lateral_water_hazard") or nat in ("water", "wetland") or "water" in p:
        return "water", 0
    if "waterway" in p and geom_type == "LineString":
        return "water", 4 if p["waterway"] in ("stream", "ditch", "drain") else 10
    if nat in ("wood", "scrub") or lu == "forest":
        return "recovery", 0
    if nat == "tree_row":
        return "recovery", 8
    if nat in ("grassland", "heath") or lu in ("meadow", "farmland") or g == "native" \
            or p.get("rough") in ("deep", "native", "long"):
        return "native", 0
    if g == "out_of_bounds" or "building" in p or lu in ("residential", "commercial", "industrial"):
        return "ob", 0
    if p.get("highway") in ROAD_TYPES and geom_type == "LineString":
        return "ob", 12 if p["highway"] in ("motorway", "trunk", "primary") else 7
    if p.get("railway") and geom_type == "LineString":
        return "ob", 6
    return None


# ----------------------------------------------------------------------------- geometry
class Frame:
    """WGS84 lon/lat <-> (yds right, -yds along) for one tee and aiming point."""

    def __init__(self, tee_ll, aim_ll):
        self.lon0, self.lat0 = tee_ll
        self.k = math.cos(math.radians(self.lat0))
        e, n = self._en(np.array([aim_ll]))[0]
        self.f = np.array([e, n]) / math.hypot(e, n)          # forward, east/north
        self.r = np.array([self.f[1], -self.f[0]])             # golfer's right, east/north

    def _en(self, ll):
        ll = np.asarray(ll, float)
        return np.c_[(ll[:, 0] - self.lon0) * self.k, ll[:, 1] - self.lat0] * 111320.0 / YD

    def to_model(self, ll):
        en = self._en(ll)
        return np.c_[en @ self.r, -(en @ self.f)]

    def along_right(self, ll):
        xy = self.to_model(ll)
        return np.c_[-xy[:, 1], xy[:, 0]]


def buffer_line(xy, w):
    """Polyline -> closed polygon of half-width w (yds), mitre-free but good enough."""
    xy = np.asarray(xy, float)
    d = np.diff(xy, axis=0)
    nrm = np.c_[-d[:, 1], d[:, 0]] / (np.linalg.norm(d, axis=1)[:, None] + 1e-9)
    nv = np.vstack([nrm[:1], (nrm[:-1] + nrm[1:]) / 2, nrm[-1:]])
    nv /= np.linalg.norm(nv, axis=1)[:, None] + 1e-9
    return np.vstack([xy + w * nv, (xy - w * nv)[::-1], xy[:1] + w * nv[:1]])


def keyhole(box, rings):
    """Polygon = box minus rings, as one vertex list (box, then for each ring: bridge in,
    ring traversed against the box's winding, bridge out). matplotlib's contains_points
    (nonzero winding) then treats every ring as a hole."""
    out = [box, box[:1]]
    for ring in rings:
        ring = np.asarray(ring, float)
        if ring[0].tolist() != ring[-1].tolist():
            ring = np.vstack([ring, ring[:1]])
        if _signed_area(ring) * _signed_area(np.vstack([box, box[:1]])) > 0:
            ring = ring[::-1]
        i = int(np.argmin(np.linalg.norm(ring - box[0], axis=1)))
        out += [np.vstack([ring[i:], ring[1:i + 1]]), box[:1]]
    return np.vstack(out)


def _signed_area(p):
    p = np.asarray(p, float)
    return 0.5 * np.sum(p[:-1, 0] * p[1:, 1] - p[1:, 0] * p[:-1, 1])


def _rings(geom):
    t, c = geom["type"], geom["coordinates"]
    if t == "Polygon":
        return [c[0]]
    if t == "MultiPolygon":
        return [p[0] for p in c]
    return []


def _overlaps(xy, box):
    (x0, y0), (x1, y1) = box.min(0), box.max(0)
    return xy[:, 0].max() >= x0 and xy[:, 0].min() <= x1 and xy[:, 1].max() >= y0 and xy[:, 1].min() <= y1


# ----------------------------------------------------------------------------- holes
def pick_tee(hole_ll, tees, colour=None, length=None):
    """Tee point for a hole: a golf=tee feature near the hole's first node, chosen by
    colour tag, else by best match of the playing length to `length`, else the first node."""
    start = np.array(hole_ll[0])
    k = math.cos(math.radians(start[1]))

    def yd(a, b):
        return math.hypot((a[0] - b[0]) * k, a[1] - b[1]) * 111320 / YD
    near = [t for t in tees if yd(t["pt"], start) < 120]
    if colour:
        tagged = [t for t in near if colour.lower() in {str(t["props"].get(x, "")).lower()
                                                        for x in ("tee", "colour", "color", "ref", "name")}]
        if tagged:
            return tagged[0]["pt"], "tee tagged " + colour
    if length and near:
        rest = sum(yd(a, b) for a, b in zip(hole_ll[1:], hole_ll[2:]))
        best = min(near, key=lambda t: abs(yd(t["pt"], hole_ll[1]) + rest - length))
        return best["pt"], f"tee nearest scorecard {length} yds"
    return list(start), "hole line start"


def convert(fc, colour=None, lengths=None, boundary_ob=True):
    feats = fc["features"]
    tees = [dict(pt=_centroid(f["geometry"]), props=f["properties"]) for f in feats
            if f["properties"].get("golf") == "tee"]
    greens = [dict(pt=_centroid(f["geometry"]), props=f["properties"]) for f in feats
              if f["properties"].get("golf") == "green"]
    course = [f for f in feats if f["properties"].get("leisure") == "golf_course" and _rings(f["geometry"])]
    course_rings = [r for f in course for r in _rings(f["geometry"])]
    holes_out, notes = {}, {}
    for f in feats:
        p = f["properties"]
        if p.get("golf") != "hole" or f["geometry"]["type"] != "LineString":
            continue
        ref = p.get("ref") or str(p["osm_id"])
        line = f["geometry"]["coordinates"]
        L = (lengths or {}).get(str(ref))
        tee_ll, how = pick_tee(line, tees, colour, L)
        fr = Frame(tee_ll, line[1])
        green_ll = min(greens, key=lambda g: np.hypot(*(np.subtract(g["pt"], line[-1]))))["pt"] \
            if greens else line[-1]
        green = fr.to_model([green_ll])[0]
        path = np.vstack([fr.to_model([tee_ll]), fr.to_model(line[1:])])
        length = float(np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1)))
        reach = max(330.0, min(length, 450.0))
        box = np.array([[-WINDOW["lat"], WINDOW["back"]], [WINDOW["lat"], WINDOW["back"]],
                        [WINDOW["lat"], -reach - WINDOW["beyond"]], [-WINDOW["lat"], -reach - WINDOW["beyond"]]])
        zones = []
        if boundary_ob and course_rings:
            inner = [xy for xy in (fr.to_model(r) for r in course_rings) if _overlaps(xy, box)]
            if inner:
                zones.append(("ob", keyhole(box, inner)))
        for g in feats:
            gp = g["properties"]
            if gp is p:
                continue
            lie = lie_of(gp, g["geometry"]["type"])
            if lie is None:
                continue
            name, w = lie
            if g["geometry"]["type"] == "LineString" and w:
                polys = [buffer_line(fr.to_model(g["geometry"]["coordinates"]), w)]
            else:
                polys = [fr.to_model(r) for r in _rings(g["geometry"])]
            zones += [(name, xy) for xy in polys if len(xy) >= 4 and _overlaps(xy, box)]
        zones.sort(key=lambda z: ZONE_ORDER.index(z[0]))
        key = int(ref) if str(ref).isdigit() else ref
        holes_out[key] = dict(
            par=int(p["par"]) if str(p.get("par", "")).isdigit() else None,
            length=round(length), tee=(0.0, 0.0), dot270=(0.0, -270.0),
            green=(round(float(green[0]), 1), round(float(green[1]), 1)),
            image=None, source="osm", tee_choice=how, hole_line=path.round(1).tolist(),
            zones=[(n, xy.round(1).tolist()) for n, xy in zones])
        notes[key] = how
    return holes_out


def _centroid(geom):
    if geom["type"] == "Point":
        return geom["coordinates"]
    pts = np.array(geom["coordinates"] if geom["type"] == "LineString" else _rings(geom)[0][:-1])
    return pts.mean(0).tolist()


# ----------------------------------------------------------------------------- preview
COL = dict(ob="#d9d9d9", native="#d8c37a", recovery="#2f6b3a", fairway="#7ccf6a",
           water="#4a90d9", sand="#f1e3b0")


def preview(holes, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    keys = sorted(holes, key=lambda k: (not isinstance(k, int), str(k).zfill(3)))
    n = max(1, len(keys))
    cols = min(6, n)
    rows = math.ceil(n / cols)
    fig, axs = plt.subplots(rows, cols, figsize=(2.6 * cols, 4.6 * rows), squeeze=False)
    for ax in axs.flat:
        ax.axis("off")
    for ax, k in zip(axs.flat, keys):
        h = holes[k]
        ax.add_patch(Polygon([[-150, 40], [150, 40], [150, -500], [-150, -500]], color="#a7d39b", lw=0))
        for name, xy in h["zones"]:
            ax.add_patch(Polygon(xy, closed=True, color=COL[name], lw=0, alpha=0.95))
        hl = np.array(h["hole_line"])
        ax.plot(hl[:, 0], hl[:, 1], "r-", lw=0.8)
        ax.plot(0, 0, "ks", ms=4)
        ax.plot(*h["green"], "wo", mec="k", ms=5)
        for d in (240, 270, 300):
            ax.plot(0, -d, "r.", ms=3)
        ax.set_xlim(-150, 150)
        ax.set_ylim(-max(330, h["length"]) - 40, 40)
        ax.set_aspect("equal")
        ax.set_title(f"{k}  par {h['par']}  {h['length']} yd", fontsize=8)
    fig.suptitle("OSM -> model frame (yds right, yds along up). grey=OB tan=native dkgreen=trees "
                 "green=fairway blue=water sand=bunker", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("course_dir")
    ap.add_argument("--tee", help="tee colour to prefer, if OSM tees are tagged")
    ap.add_argument("--lengths", help="scorecard yardages, e.g. 1=419,2=616 (picks the tee box)")
    ap.add_argument("--no-boundary-ob", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(a.course_dir, "osm.geojson")) as fh:
        fc = json.load(fh)
    lengths = dict(kv.split("=") for kv in a.lengths.split(",")) if a.lengths else None
    lengths = {k: float(v) for k, v in lengths.items()} if lengths else None
    holes = convert(fc, a.tee, lengths, not a.no_boundary_ob)
    with open(os.path.join(a.course_dir, "holes_from_osm.json"), "w") as fh:
        json.dump({str(k): v for k, v in holes.items()}, fh)
    print(f"{len(holes)} holes converted:",
          {k: (h["par"], h["length"], len(h["zones"])) for k, h in holes.items()})
    if holes:
        preview(holes, os.path.join(a.course_dir, "holes_preview.png"))


if __name__ == "__main__":
    main()
