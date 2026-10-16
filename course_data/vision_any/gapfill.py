"""S4 gap-fill for any course: add vision `recovery` (trees), `native` (long grass) and `water` (creek
corridors, open water) zones to a course package (ARCHITECTURE.md 9.3).

    from gapfill import gapfill
    pkg2 = gapfill(package_dict, imagery_dir)          # new dict; the input is not mutated

    python3 course_data/vision_any/gapfill.py --package course_data/packages/<slug>/package.json [--out ...]
    python3 course_data/vision_any/gapfill.py --holes course_data/spirit_hollow/holes.json --out ...   # v1 model

Where the layers come from (in order):
  1. course_data/vision_any/<slug>/vision_any.geojson, built by run_any.py from the free rasters fetched by
     .github/workflows/vision_any.yml (lidar canopy, NAIP native classifier, NDWI + DTM creek corridors);
  2. otherwise run_any.build() on the fly from course_data/vision_any/<slug>/raw/ (or imagery_dir's
     NAIP + DEM when raw/ is missing: trees then come from NAIP alone, flagged in sources.vision).
Nothing here is trained on a hand-traced map (the product path).

Per hole, every vision polygon is clipped to the hole window (+/-160 yds of the tee line, 40 yds behind the
back-most tee to 40 past the green), minus the OSM fairway / green / tee / bunker polygons already in the
hole, split into hole-free parts, and appended to `zones_ll` as {lie, poly [[lon, lat]...], src, p}.
Water is only added where the hole has no OSM water already covering it. Then the yard-frame `zones` are
refreshed with platform.package.reframe() if it exists, else here (same frame: UTM yards, tee (0,0), y =
-yds along tee -> aim), sorted by the model's ZONE_ORDER. `exposure` = share of the landing-zone edges
(+/-35 yds, 220-340 yds) under tree canopy.

For a v1 holes.json (course_model/1, pixel frame) gapfill_holes() does the same in each hole's fitted pixel
frame (tee_ll, aim_ll, px_per_yd, tee px).
"""
import argparse
import copy
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
YD = 0.9144
MODEL_ID = "vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised)"
ZONE_ORDER = ["ob_boundary", "native", "recovery", "ob", "first_cut", "fairway", "green", "water", "sand"]
PENAL_ADD = ("recovery", "native", "water")
WINDOW = dict(lat=160, back=40, beyond=40)


def log(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------- frames
class YardFrame:
    """UTM-yards frame of a tee line (geometry/build_holes.py frame='yard')."""

    def __init__(self, tee_ll, aim_ll):
        from pyproj import Transformer
        lon0, lat0 = tee_ll
        epsg = (32600 if lat0 >= 0 else 32700) + int((lon0 + 180) // 6) + 1
        self.fw = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
        self.inv = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
        self.t0 = self._yd([tee_ll])[0]
        d = self._yd([aim_ll])[0] - self.t0
        self.f = d / np.linalg.norm(d)
        self.r = np.array([self.f[1], -self.f[0]])

    def _yd(self, ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        x, y = self.fw.transform(ll[:, 0], ll[:, 1])
        return np.c_[x, y] / YD

    def ll_to_xy(self, ll):
        d = self._yd(ll) - self.t0
        return np.c_[d @ self.r, -(d @ self.f)]

    def xy_to_ll(self, xy):
        xy = np.atleast_2d(np.asarray(xy, float))
        en = (self.t0 + xy[:, :1] * self.r - xy[:, 1:2] * self.f) * YD
        lon, lat = self.inv.transform(en[:, 0], en[:, 1])
        return np.c_[lon, lat]


def holefree(g):
    """Polygon(s) -> hole-free Polygons (cut through each interior ring), as geometry._holefree."""
    from shapely.geometry import LineString, Polygon
    from shapely.ops import split
    todo, out = list(getattr(g, "geoms", [g])), []
    while todo:
        p = todo.pop()
        if p.geom_type in ("MultiPolygon", "GeometryCollection"):
            todo += list(p.geoms)
            continue
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        if not p.interiors:
            out.append(p)
            continue
        c = Polygon(p.interiors[0]).representative_point()
        x0, y0, x1, y1 = p.bounds
        parts = list(split(p, LineString([(c.x, y0 - 1), (c.x, y1 + 1)])).geoms)
        if len(parts) < 2:
            out.append(Polygon(p.exterior))
        else:
            todo += parts
    return out


# --------------------------------------------------------------------------- layers
def resolve_slug(slug, center=None):
    """The vision_any course dir for a package: same slug, else the one whose grid contains the centre
    (package slugs and vision_any slugs can differ, e.g. mozingo_lake vs mozingo)."""
    if slug and os.path.isdir(os.path.join(HERE, slug, "raw")):
        return slug
    if center is not None:
        for d in sorted(os.listdir(HERE)):
            mp = os.path.join(HERE, d, "raw", "meta.json")
            if os.path.exists(mp):
                w, s, e, n = json.load(open(mp))["grid"]["ll_bbox_wsen"]
                if w <= center[0] <= e and s <= center[1] <= n:
                    return d
    return slug


def load_layers(slug, imagery_dir=None, course_dir=None):
    """-> (FeatureCollection of WGS84 vision polygons, meta). Builds them if the geojson is missing."""
    p = os.path.join(HERE, slug, "vision_any.geojson")
    if os.path.exists(p):
        fc = json.load(open(p))
        return fc, fc.get("properties", {})
    if not os.path.exists(os.path.join(HERE, slug, "raw", "meta.json")):
        raise FileNotFoundError(f"course_data/vision_any/{slug}/raw (not fetched)")
    sys.path.insert(0, HERE)
    import run_any
    fc = run_any.build(slug, course_dir=course_dir, imagery_dir=imagery_dir, write=False)
    return fc, fc.get("properties", {})


def _shapes(fc):
    from shapely.geometry import shape
    out = {k: [] for k in PENAL_ADD}
    for f in fc.get("features", []):
        lie = f["properties"].get("lie")
        if lie in out and f.get("geometry"):
            g = shape(f["geometry"])
            if not g.is_valid:
                g = g.buffer(0)
            out[lie].append((g, f["properties"]))
    return out


def _to_m(fr, g):
    """WGS84 shapely geometry -> hole yard frame (x, y) shapely geometry."""
    from shapely.ops import transform
    return transform(lambda x, y: tuple(fr.ll_to_xy(np.c_[x, y]).T), g)


def _window(h, fr, length):
    from shapely.geometry import box
    back = WINDOW["back"]
    for t in (h.get("tees") or {}).values():                   # back-most tee of any set
        if t.get("tee_ll"):
            y = fr.ll_to_xy([t["tee_ll"]])[0, 1]
            back = max(back, y + WINDOW["back"])
    return box(-WINDOW["lat"], -(length + WINDOW["beyond"]), WINDOW["lat"], back)


def _hole_zones_ll(h, fr, shapes, min_yd2=150.0):
    """-> list of zones_ll entries for one hole."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    length = float(h.get("length") or h.get("measured_length") or 450)
    win = _window(h, fr, length)
    # OSM polygons already in the hole (zones_ll if present, else yard zones)
    osm = {}
    if h.get("zones_ll"):
        for z in h["zones_ll"]:
            if str(z.get("src", "")).startswith("vision"):
                continue
            try:
                osm.setdefault(z["lie"], []).append(Polygon(fr.ll_to_xy(z["poly"])).buffer(0))
            except Exception:                                  # noqa: BLE001
                pass
    else:
        for z in h.get("zones", []):
            try:
                osm.setdefault(z[0], []).append(Polygon(z[1]).buffer(0))
            except Exception:                                  # noqa: BLE001
                pass
    protect = unary_union([g for k in ("fairway", "green", "tee", "sand") for g in osm.get(k, [])] or [Polygon()])
    osm_water = unary_union(osm.get("water", []) or [Polygon()])
    out = []
    for lie in PENAL_ADD:
        for g, props in shapes[lie]:
            gy = _to_m(fr, g)
            if not gy.intersects(win):
                continue
            gy = gy.intersection(win).difference(protect)
            if lie == "water":
                gy = gy.difference(osm_water)
            if lie in osm and lie != "water" and osm[lie]:
                gy = gy.difference(unary_union(osm[lie]))      # OSM has this class here: keep OSM's
            for p in holefree(gy.buffer(0)):
                if p.area < min_yd2:
                    continue
                p = p.simplify(1.0)
                ll = fr.xy_to_ll(np.asarray(p.exterior.coords)[:-1])
                out.append(dict(lie=lie, poly=[[round(float(a), 7), round(float(b), 7)] for a, b in ll],
                                src=props.get("src", "vision"), p=props.get("p", 0.8),
                                area_yd2=round(float(p.area))))
    return out


def exposure(fr, tree_shapes, a0=220, a1=340, half=35):
    """Share of the landing-zone side edges (+/-half yds, a0-a1 yds) under tree canopy."""
    from shapely.geometry import Point
    from shapely.ops import unary_union
    if not tree_shapes:
        return 0.0
    al = np.arange(a0, a1 + 1, 5.0)
    pts = np.r_[np.c_[-np.full_like(al, half), -al], np.c_[np.full_like(al, half), -al]]
    ll = fr.xy_to_ll(pts)
    U = unary_union([g for g, _ in tree_shapes])
    from shapely import prepared
    P = prepared.prep(U)
    return round(float(np.mean([P.contains(Point(x, y)) for x, y in ll])), 3)


def _reframe():
    p = os.path.join(ROOT, "course_data", "platform", "package.py")
    if not os.path.exists(p):
        return None
    try:
        spec = importlib.util.spec_from_file_location("vision_any_platform_package", p)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["vision_any_platform_package"] = mod
        spec.loader.exec_module(mod)
        return getattr(mod, "reframe", None)
    except Exception as e:                                     # noqa: BLE001
        log("  (platform.package not importable:", type(e).__name__, str(e)[:120], ")")
        return None


def _sort_zones(zones, src):
    rank = {n: i for i, n in enumerate(ZONE_ORDER)}
    idx = sorted(range(len(zones)), key=lambda i: rank.get(zones[i][0], 4.5))
    return [zones[i] for i in idx], [src[i] for i in idx]


# --------------------------------------------------------------------------- package/1
def gapfill(package, imagery_dir=None, slug=None, use_reframe=True):
    """course_package/1 dict -> new dict with vision zones (ARCHITECTURE.md 9.3)."""
    out = copy.deepcopy(package)
    course = out.get("course") or {}
    slug = resolve_slug(slug or course.get("slug"), course.get("center"))
    try:
        fc, meta = load_layers(slug, imagery_dir)
    except Exception as e:                                     # noqa: BLE001
        out.setdefault("stages", {})["vision"] = (
            f"missing: no vision_any layers for '{slug}' ({type(e).__name__}: {str(e)[:120]}); add the course to "
            "course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them")
        return out
    shapes = _shapes(fc)
    n_add = {k: 0 for k in PENAL_ADD}
    for ref, h in out["holes"].items():
        if not h.get("tee_ll") or not h.get("aim_ll"):
            continue
        fr = YardFrame(h["tee_ll"], h["aim_ll"])
        add = _hole_zones_ll(h, fr, shapes)
        zl = list(h.get("zones_ll") or [])
        zl = [z for z in zl if not str(z.get("src", "")).startswith("vision")]   # idempotent re-runs
        h["zones_ll"] = zl + add
        for z in add:
            n_add[z["lie"]] += 1
        h["exposure"] = exposure(fr, shapes["recovery"])
        prov = h.setdefault("provenance", {})
        pz = prov.get("zones") if isinstance(prov.get("zones"), dict) else {}
        for lie in PENAL_ADD:
            if any(z["lie"] == lie for z in add):
                pz[lie] = "vision:" + ("lidar_hag" if lie == "recovery" and "lidar" in meta.get("trees_how", "").lower()
                                       else "naip")
        prov["zones"] = pz if pz else prov.get("zones")
    reframe = _reframe() if use_reframe else None
    done = False
    if reframe is not None:
        try:
            r = reframe(out)
            out = r if isinstance(r, dict) else out
            done = True
        except Exception as e:                                 # noqa: BLE001
            log("  reframe failed, refreshing zones here:", type(e).__name__, str(e)[:160])
    if not done:
        for ref, h in out["holes"].items():
            if not h.get("tee_ll") or not h.get("aim_ll"):
                continue
            fr = YardFrame(h["tee_ll"], h["aim_ll"])
            zones = [z for z, s in zip(h.get("zones", []), h.get("zone_src") or [""] * len(h.get("zones", [])))
                     if not str(s).startswith("vision")]
            src = [s for s in (h.get("zone_src") or [""] * len(h.get("zones", []))) if not str(s).startswith("vision")]
            src = (src + ["osm"] * len(zones))[:len(zones)]
            for z in h["zones_ll"]:
                if str(z.get("src", "")).startswith("vision"):
                    xy = fr.ll_to_xy(z["poly"])
                    zones.append([z["lie"], [[round(float(x), 1), round(float(y), 1)] for x, y in xy]])
                    src.append(z["src"])
            h["zones"], h["zone_src"] = _sort_zones(zones, src)
    out.setdefault("stages", {})["vision"] = f"ok: {MODEL_ID}"
    out.setdefault("sources", {})["vision"] = dict(
        model=MODEL_ID, trained_on="OSM labels of this course only (no hand-traced maps)",
        trees=meta.get("trees_how"), native=meta.get("native_how"), water=meta.get("water_how"),
        imagery_date=meta.get("naip_dates"), lidar=meta.get("lidar"), layers=f"course_data/vision_any/{slug}/vision_any.geojson",
        added=n_add)
    return out


# --------------------------------------------------------------------------- v1 holes.json
def gapfill_holes(model, imagery_dir=None, slug=None):
    """v1 course_model/1 (pixel frame per hole) -> new dict with vision zones in each hole's pixel frame."""
    sys.path.insert(0, os.path.join(ROOT, "course_data", "imagery"))
    import render as R
    from shapely.geometry import Polygon
    out = copy.deepcopy(model)
    c = out.get("course") or {}
    ctr = c.get("center")
    ctr = [ctr["lon"], ctr["lat"]] if isinstance(ctr, dict) else ctr
    slug = resolve_slug(slug or out.get("slug") or c.get("slug"), ctr)
    fc, meta = load_layers(slug, imagery_dir)
    shapes = _shapes(fc)
    for ref, h in out["holes"].items():
        if "tee_ll" not in h or "aim_ll" not in h:
            continue
        fr = YardFrame(h["tee_ll"], h["aim_ll"])
        pf = R.Frame(h["tee_ll"], h["aim_ll"], ppy=h["px_per_yd"], tee_px=h["tee"], proj="utm")
        # OSM zones of the hole in yard coords (for protection / no-duplicate rules)
        yz = []
        for nm, poly in h["zones"]:
            ll = pf.px_to_ll(np.asarray(poly, float))
            yz.append([nm, fr.ll_to_xy(ll).tolist()])
        hh = dict(h, zones=yz, zones_ll=None, length=h.get("length"))
        add = _hole_zones_ll(hh, fr, shapes)
        zones = [z for z, s in zip(h["zones"], h.get("zone_src") or [""] * len(h["zones"])) if not str(s).startswith("vision")]
        src = [s for s in (h.get("zone_src") or ["osm"] * len(h["zones"])) if not str(s).startswith("vision")]
        src = (src + ["osm"] * len(zones))[:len(zones)]
        for z in add:
            px = pf.ll_to_px(z["poly"])
            zones.append([z["lie"], [[round(float(x), 1), round(float(y), 1)] for x, y in px]])
            src.append(z["src"])
        h["zones"], h["zone_src"] = _sort_zones(zones, src)
        h["exposure"] = exposure(fr, shapes["recovery"])
    out.setdefault("stages", {})["vision"] = f"ok: {MODEL_ID}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package")
    ap.add_argument("--holes")
    ap.add_argument("--imagery")
    ap.add_argument("--slug")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.package:
        pkg = json.load(open(a.package))
        res = gapfill(pkg, a.imagery, slug=a.slug)
    else:
        res = gapfill_holes(json.load(open(a.holes)), a.imagery, slug=a.slug)
    out = a.out or (a.package or a.holes).replace(".json", "_vision.json")
    json.dump(res, open(out, "w"), separators=(",", ":"), default=float)
    n = {}
    for h in res["holes"].values():
        for z in h.get("zones_ll") or []:
            if str(z.get("src", "")).startswith("vision"):
                n[z["lie"]] = n.get(z["lie"], 0) + 1
    log("wrote", out, n or "")


if __name__ == "__main__":
    main()
