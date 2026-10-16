"""Any-course package builder (offline): request + fetched raw data -> course_data/packages/<slug>/.

  python course_data/platform/package.py build course_data/requests/package_mozingo_lake.json [--render]
  python course_data/platform/package.py run   course_data/requests/package_*.json    # fetch (Actions) + build

Pipeline (ARCHITECTURE.md stages; every stage is the existing team module, imported, not rewritten):
  S0/S1   raw/course.json, raw/osm.geojson         resolve.py, fetch_package.py (Actions)
  S1 card scorecard.py: request yardages > request["scorecard"] file (tees/ format) > golfify > club site;
          no card -> the OSM tee nearest each hole-line start (usually the back tee) + a warning
  S2 tees tees/place_tee.py (box matched to the card yardage, walkback if none); an OSM tee box tagged with
          the set's colour wins ("tagged")
  S3      geometry/build_holes.py: yard frame (package) + fitted pixel frame (images / the book)
  S4      course_data/vision_any/gapfill.py:gapfill(package, imagery_dir) if present (trees, long grass)
  S6      confidence per hole (pipeline.confidence), coverage stats, elevation (3DEP DEM + elevation/adjust.py)
Outputs in packages/<slug>/:
  package.json    the self-contained course package (schema course_package/1, below)
  course_auto.py  HOLES / PAR3 / ORDER / LABELS / NOTES / AIM_AT (spirit_hollow/course.py API, pixel frame)
  qa.md           per-hole confidence + flags, coverage, warnings
  screenshots/    holeNN.png in each hole's pixel frame (--render; needs the imagery)

package.json (course_package/1):
  course     {name, slug, osm{type,id}, center[lon,lat], bbox[w,s,e,n], boundary (GeoJSON), town, state,
              website, holes_mapped, candidates}
  request    the request file as given
  tee_set    {requested, chosen, how, source, warning}
  tee_sets   {Name: {colour, aliases, yards[], par[], total, rating, slope, source}} (all sets on the card)
  scorecard  {source, url, kind, confidence, tried}
  frame      "yard": x = yds right of the tee line, y = -yds along it, tee (0,0), dot270 (0,-270)
  holes      {ref: {ref, par, length (card), measured_length, handicap, tee_ll, aim_ll, green_ll [lon,lat],
              bearing_deg (true, tee->aim), green_bearing_deg, tee, dot270, green, hole_line, green_polygon,
              zones [[lie, [[x,y],...]], ...] (later wins), zone_src [...], par3 {...} (par 3s),
              pixel {ppy, tee_px, size}, tee_choice, tee_options, elevation {...},
              provenance {tee|green|par|length|zones|bearing: {source, confidence}},
              confidence {score, band, osm, imagery, inferred, flags}, landing_lies {lie: share}, image}}
  imagery    {dir, source, year, acquired, resolution_m, crs, files} | null
  elevation  {file, source, resolution_m} | null
  coverage   osm_coverage.coverage(...)
  stages, warnings, built, attribution
"""
import argparse
import copy
import datetime as dt
import glob
import importlib.util
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE, CD]
import osm_coverage  # noqa: E402
import platform_common as pc  # noqa: E402
import scorecard as scm  # noqa: E402

SCHEMA = "course_package/1"
W, H = 920, 2000
_MODS = {}


def load(path, name):
    """Import a team module by path (cached); None if it is absent or fails to import."""
    if name in _MODS:
        return _MODS[name]
    mod = None
    if os.path.exists(path):
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        except Exception as e:                                   # noqa: BLE001
            pc.log(f"! could not import {path}: {type(e).__name__}: {e}")
            mod = None
    _MODS[name] = mod
    return mod


def geometry():
    return load(os.path.join(CD, "geometry", "build_holes.py"), "cdp_build_holes")


def pipeline():
    return load(os.path.join(CD, "pipeline.py"), "cdp_pipeline")


def place_tee_mod():
    return load(os.path.join(CD, "tees", "place_tee.py"), "cdp_place_tee")


# ----------------------------------------------------------------------------- scorecard
def card_confidence(kind):
    return dict(request=1.0, file=0.95, golfify=0.9, club_site=0.85).get(kind, 0.0)


def pick_scorecard(req, raw_dir):
    """-> (card | None, info dict). Order: request yardages > request scorecard file > golfify > club site."""
    tried = []
    if req.get("yardages"):
        card = scm.card_from_yardages(req["yardages"], req.get("pars"), name=req.get("tee_set") or "request")
        return card, dict(kind="request", source="request file yardages", url=None, tried=tried)
    if req.get("scorecard"):
        p = req["scorecard"] if os.path.isabs(req["scorecard"]) else os.path.join(pc.ROOT, req["scorecard"])
        card = pc.read_json(p)
        if card:
            card = scm.normalise(card)
            url = card.get("source") if isinstance(card.get("source"), str) else None
            return card, dict(kind="file", source=os.path.relpath(p, pc.ROOT), url=url, tried=tried)
        tried.append(dict(source=req["scorecard"], ok=False, info="file missing or unreadable"))
    web = pc.read_json(os.path.join(raw_dir, "scorecard_web.json"), {}) or {}
    tried += web.get("tried", [])
    for want in ("golfify", "club_site"):
        for c in web.get("cards", []):
            if c["source"] == want and c.get("card"):
                return scm.normalise(c["card"]), dict(kind=want, source=want, url=c.get("url"), tried=tried)
    return None, dict(kind=None, source=None, url=None, tried=tried)


# ----------------------------------------------------------------------------- tees (S2)
def _tee_tags(props):
    return " ".join(str(props.get(k, "")) for k in ("tee", "golf:tee", "colour", "color", "name")).lower().split()


def place_tees(fc, card_holes, set_name, colour):
    """tees/place_tee.py for every hole -> tee_positions-shaped dict {holes: {ref: {tees: {set: {...}}}}}."""
    pt = place_tee_mod()
    lines, tees = {}, []
    for f in fc["features"]:
        p, g = f["properties"], f["geometry"]
        if p.get("golf") == "hole" and g["type"] == "LineString" and p.get("ref"):
            lines[str(p["ref"])] = [(c[1], c[0]) for c in g["coordinates"]]
        elif p.get("golf") == "tee" and g["type"] in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in cs], tags=p))
    if pt is None or not lines:
        return None
    by_hole = pt.assign_tees_to_holes(lines, tees)
    out = {}
    want = {str(set_name).lower(), str(colour or "").lower()} - {""}
    for ref, line in lines.items():
        yards = (card_holes.get(ref) or {}).get("yards")
        tagged = [t for t in by_hole.get(ref, []) if want & set(_tee_tags(t["tags"]))]
        if tagged:
            ring = tagged[0]["coords"]
            lat = sum(c[0] for c in ring) / len(ring)
            lon = sum(c[1] for c in ring) / len(ring)
            r = dict(lat=lat, lon=lon, method="tagged", tee_id=tagged[0]["id"], confidence="high", error_yd=0.0)
        elif yards:
            r = pt.place_tee(line, by_hole.get(ref, []), float(yards))
            if r["error_yd"] is None or r["error_yd"] > 10 or r["method"] == "walkback":
                alt = pt.place_tee(line, tees, float(yards))          # borrow a neighbour's box (place_course rule)
                if alt["method"] != "walkback" and alt["error_yd"] is not None and alt["error_yd"] <= 10:
                    alt["borrowed"] = True
                    r = alt
            r = {k: v for k, v in r.items() if k != "candidates"}
        else:
            continue
        out[ref] = dict(tees={set_name: r})
    return dict(schema="tees/positions", holes=out)


# ----------------------------------------------------------------------------- geo helpers
def bearing(a_ll, b_ll):
    from pyproj import Geod
    az, _, _ = Geod(ellps="WGS84").inv(a_ll[0], a_ll[1], b_ll[0], b_ll[1])
    return round(az % 360.0, 1)


def hole_frame(h):
    """imagery/render.Frame for a package hole (UTM, matching geometry's planar frame)."""
    rd = load(os.path.join(CD, "imagery", "render.py"), "cdp_render")
    return rd.Frame(h["tee_ll"], h["aim_ll"], ppy=h["pixel"]["ppy"], tee_px=h["pixel"]["tee_px"], proj="utm")


def dem_sampler(path):
    """lonlat (N,2) -> metres, bilinear on a DEM GeoTIFF (rasterio) ; None if unreadable."""
    try:
        import rasterio
        from pyproj import Transformer
        with rasterio.open(path) as src:
            z = src.read(1).astype(np.float64)
            tr = src.transform
            crs = src.crs.to_string()
            nd = src.nodata
        if nd is not None and not np.isnan(nd):
            z[z == nd] = np.nan
    except Exception as e:                                       # noqa: BLE001
        pc.log("dem unreadable", path, e)
        return None
    to = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    inv = ~tr

    def f(ll):
        ll = np.atleast_2d(np.asarray(ll, float))
        x, y = to.transform(ll[:, 0], ll[:, 1])
        x, y = np.asarray(x), np.asarray(y)
        c, r = inv.a * x + inv.b * y + inv.c, inv.d * x + inv.e * y + inv.f
        c, r = np.asarray(c) - 0.5, np.asarray(r) - 0.5
        c0, r0 = np.floor(c).astype(int), np.floor(r).astype(int)
        fc, fr = c - c0, r - r0
        hh, ww = z.shape
        ok = (c0 >= 0) & (r0 >= 0) & (c0 + 1 < ww) & (r0 + 1 < hh)
        c0, r0 = np.clip(c0, 0, ww - 2), np.clip(r0, 0, hh - 2)
        v = (z[r0, c0] * (1 - fc) * (1 - fr) + z[r0, c0 + 1] * fc * (1 - fr)
             + z[r0 + 1, c0] * (1 - fc) * fr + z[r0 + 1, c0 + 1] * fc * fr)
        return np.where(ok, v, np.nan)
    return f


def elevation_for_hole(h, sample, yds_to_ll):
    """Tee-line profile, landing plane and green drop from a DEM sampler (lonlat -> m), in the format
    elevation/adjust.py reads; + elevation/adjust.adjustments() per club when that module is present."""
    FT = 0.3048
    L = float(h.get("measured_length") or h["length"])
    tee_z = float(sample(yds_to_ll(np.array([[0.0, 0.0]])))[0])
    if not np.isfinite(tee_z):
        return None
    prof = []
    for a in np.arange(0, min(L + 20, 440) + 1, 10):
        pts = np.array([[x, -a] for x in (-10, -5, 0, 5, 10)])
        z = sample(yds_to_ll(pts))
        if np.isfinite(z).any():
            prof.append(dict(yd=float(a), band_ft_rel_tee=round(float(np.nanmean(z) - tee_z) / FT, 2)))
    gx, gy = h["green"]
    gz = float(sample(yds_to_ll(np.array([[gx, gy]])))[0])
    out = dict(par=h["par"], bearing_deg_true=h["bearing_deg"], tee_ft=round(tee_z / FT, 1), profile=prof,
               green=dict(delta_ft=round((gz - tee_z) / FT, 1) if np.isfinite(gz) else None, along_yd=round(-gy, 1)))
    if h["par"] >= 4:
        A, R = np.meshgrid(np.arange(240, 321, 8.0), np.arange(-20, 21, 8.0))
        A, R = A.ravel(), R.ravel()
        z = sample(yds_to_ll(np.c_[R, -A]))
        ok = np.isfinite(z)
        if ok.sum() >= 10:
            M = np.c_[np.ones(ok.sum()), A[ok], R[ok]]
            coef, *_ = np.linalg.lstsq(M, z[ok] / 0.9144, rcond=None)      # z in yards
            b, c = coef[1] * 100, coef[2] * 100
            out["landing_slope"] = dict(along_pct=round(float(b), 2), cross_pct=round(float(c), 2),
                                        magnitude_pct=round(float(math.hypot(b, c)), 2),
                                        fall_line_deg_cw_from_line=round(math.degrees(math.atan2(-c, -b)), 1))
        z270 = sample(yds_to_ll(np.array([[x, -270.0] for x in (-10, -5, 0, 5, 10)])))
        if np.isfinite(z270).any():
            out["landing"] = {"270": dict(delta_ft=round(float(np.nanmean(z270) - tee_z) / FT, 1))}
    adj = load(os.path.join(CD, "elevation", "adjust.py"), "cdp_elev_adjust")
    if adj is not None and out["green"]["delta_ft"] is not None and (h["par"] == 3 or "landing_slope" in out):
        try:
            out["adjustments"] = adj.adjustments(h["ref"], holes={h["ref"]: dict(out, green_slope=None)})
        except Exception as e:                                   # noqa: BLE001
            out["adjustments_error"] = f"{type(e).__name__}: {e}"[:200]
    return out


# ----------------------------------------------------------------------------- landing / par 3 helpers
def landing_lies(h):
    pl = pipeline()
    a, l = pl.landing_grid()
    lie, _ = pl.lie_with_index(h, pl.to_px(h, a, l))
    vals, counts = np.unique(lie.astype(str), return_counts=True)
    return {str(v): round(float(c) / len(lie), 3) for v, c in zip(vals, counts)}


def par3_haz(h):
    """Worst lie 2-14 yds off each green edge (same rule as geometry.par3_entry) from the current zones."""
    from matplotlib.path import Path
    p3 = h["par3"]
    tee, flag = np.array(p3["tee"], float), np.array(p3["flag"], float)
    v = flag - tee
    fwd = v / np.linalg.norm(v)
    right = np.array([-fwd[1], fwd[0]])
    gl = np.array(p3["green"], float)
    sev = dict(water=4, ob=4, recovery=3, native=3, sand=2, fairway=0, rough=0)
    nm = dict(water="water", ob="ob", recovery="trees", native="native", sand="bunker", fairway="rough", rough="rough")
    paths = [(n, Path(np.array(p, float))) for n, p in h["zones"]]
    haz = {}
    for side, (ax, sign) in dict(left=(0, -1), right=(0, 1), short=(1, -1), long=(1, 1)).items():
        edge = gl[:, ax].max() if sign > 0 else gl[:, ax].min()
        probes = []
        for dd in np.arange(2, 15, 2):
            for o in np.linspace(-6, 6, 5):
                q = np.zeros(2)
                q[ax], q[1 - ax] = edge + sign * dd, o
                probes.append(flag + q[0] * right + q[1] * fwd)
        lies = np.array(["rough"] * len(probes), dtype=object)
        for n, pth in paths:
            lies[pth.contains_points(np.array(probes))] = n
        lst = list(lies)
        haz[side] = nm[max(set(lst), key=lambda n: (sev[n], lst.count(n)))]
    return haz


# ----------------------------------------------------------------------------- build
LIE_ORDER = ["ob_boundary", "native", "recovery", "ob", "first_cut", "fairway", "green", "water", "sand"]
MODEL_LIE = {"green": "fairway", "ob_boundary": "ob"}
WINDOW_LAT, WINDOW_BEHIND, WINDOW_PAST, WINDOW_MIN = 150.0, 40.0, 40.0, 330.0


def find_imagery(req, pkg_dir, slug=None):
    """NAIP (+ DEM) directory with georef.json: request > packages/<slug>/imagery > imagery/<slug>."""
    for d in [req.get("imagery_dir"), os.path.join(pkg_dir, "imagery"),
              os.path.join(CD, "imagery", slug or os.path.basename(os.path.normpath(pkg_dir)))]:
        if not d:
            continue
        d = d if os.path.isabs(d) else os.path.join(pc.ROOT, d)
        if os.path.exists(os.path.join(d, "georef.json")):
            return d
    return None


def vision_raw_dirs(slug, course):
    """vision_any/<slug>/raw folders that look like this course (lidar HAG etc.), for gapfill."""
    out = []
    for d in sorted(glob.glob(os.path.join(CD, "vision_any", "*", "raw", "meta.json"))):
        name = os.path.basename(os.path.dirname(os.path.dirname(d)))
        if name == slug or slug.startswith(name + "_") or name.startswith(slug):
            out.append(os.path.relpath(os.path.dirname(d), pc.ROOT))
    return out


def imagery_ref(img_dir):
    if not img_dir:
        return None, None
    g = pc.read_json(os.path.join(img_dir, "georef.json"), {}) or {}
    im = g.get("imagery") or {}
    rel = os.path.relpath(img_dir, pc.ROOT)
    imagery = dict(dir=rel, source=im.get("source"), year=im.get("year"), acquired=im.get("acquired"),
                   naip_date=(im.get("acquired") or [None])[0], items=im.get("items"),
                   resolution_m=im.get("resolution_m"), crs=im.get("crs"), bands=im.get("bands"),
                   files=im.get("files"),
                   present=all(os.path.exists(os.path.join(img_dir, f)) for f in (im.get("files") or {}).values())) \
        if im else None
    dem = g.get("dem")
    dem_path = os.path.join(img_dir, (dem or {}).get("file", "dem.tif"))
    elevation = dict(file=os.path.relpath(dem_path, pc.ROOT), source=(dem or {}).get("source"),
                     resolution_m=(dem or {}).get("resolution_m"), crs=(dem or {}).get("crs")) \
        if os.path.exists(dem_path) else None
    return imagery, elevation


def call_gapfill(package, img_dir, warnings):
    mod = load(os.path.join(CD, "vision_any", "gapfill.py"), "cdp_vision_gapfill")
    st = package["stages"]
    if mod is None or not callable(getattr(mod, "gapfill", None)):
        st["vision"] = "missing (course_data/vision_any/gapfill.py not present)"
        return package
    if not img_dir and not package["sources"].get("vision_raw"):
        st["vision"] = "skipped: no imagery for this course"
        warnings.append("no imagery: trees / long grass come from OSM only")
        return package
    try:
        out = mod.gapfill(copy.deepcopy(package), img_dir)
        if not isinstance(out, dict):
            raise TypeError(f"gapfill returned {type(out).__name__}")
        if not str(out.get("stages", {}).get("vision", "")).startswith("ok"):
            out.setdefault("stages", {})["vision"] = "ok: vision_any/gapfill.py"
        return out
    except Exception as e:                                       # noqa: BLE001
        st["vision"] = f"failed: {type(e).__name__}: {e}"[:300]
        warnings.append("vision gap-fill failed; trees / long grass come from OSM only")
        return package


def find_local_card(course):
    """A card already in the repo for this OSM course (tees/scorecard.json for Spirit Hollow)."""
    for p in glob.glob(os.path.join(CD, "tees", "*scorecard*.json")) + glob.glob(os.path.join(CD, "tees", "*", "scorecard.json")):
        c = pc.read_json(p, {}) or {}
        meta = c.get("course") if isinstance(c.get("course"), dict) else {}
        oid = meta.get("osm_relation") or meta.get("osm_id") or (meta.get("osm") or {}).get("id")
        if oid and course.get("osm") and int(oid) == int(course["osm"]["id"]) and c.get("tee_sets"):
            return os.path.relpath(p, pc.ROOT)
    return None


def osm_lines(fc):
    return {str(f["properties"]["ref"]): f["geometry"]["coordinates"] for f in fc["features"]
            if f["properties"].get("golf") == "hole" and f["geometry"]["type"] == "LineString"
            and f["properties"].get("ref")}


def _frame(tee_ll, aim_ll):
    rd = load(os.path.join(CD, "imagery", "render.py"), "cdp_render")
    return rd.Frame(tee_ll, aim_ll, proj="utm")


def _ring_ll(fr, poly):
    return [[round(float(a), 7), round(float(b), 7)] for a, b in fr.yds_to_ll(np.asarray(poly, float))]


def build_package(req, pkg_dir, render=False, gapfill=True):
    """Offline: raw/ (+ imagery/) -> package dict. Raises SystemExit when raw data is missing."""
    raw = os.path.join(pkg_dir, "raw")
    slug = os.path.basename(os.path.normpath(pkg_dir))
    course = pc.read_json(os.path.join(raw, "course.json"))
    if not course:
        raise SystemExit(f"{raw}/course.json missing: run fetch_package.py (GitHub Actions)")
    if course.get("status") != "ok":
        raise SystemExit(f"course not resolved ({course.get('status')}): candidates "
                         + json.dumps(course.get("candidates", [])[:8]))
    fc = pc.read_json(os.path.join(raw, "osm.geojson"))
    if not fc:
        raise SystemExit(f"{raw}/osm.geojson missing")
    summ = pc.read_json(os.path.join(raw, "summary.json"), {}) or {}
    stages, warnings = {}, []
    stages["resolve"] = (f"ok: {course['osm']['type']}/{course['osm']['id']} {course['name']} "
                         f"({course.get('town')}, {course.get('state')})")
    stages["osm"] = f"ok: {len(fc['features'])} features"

    # S1 scorecard + tee set
    req = dict(req)
    if not req.get("scorecard") and not req.get("yardages") and req.get("local_scorecard", True):
        local = find_local_card(course)
        if local:
            req["scorecard"] = local
    card, cinfo = pick_scorecard(req, raw)
    wanted = req.get("tee_set") or req.get("tees")
    chosen, how = scm.choose_tee_set(card, wanted) if card else (None, "no scorecard")
    if card and chosen is None:
        chosen, _ = scm.choose_tee_set(card, "back")
        warnings.append(f"{how}; using the longest set '{chosen}' instead")
        how = f"fallback: longest set ({how})"
    refs = sorted(osm_lines(fc), key=lambda r: r.zfill(3))
    stages["scorecard"] = f"ok: {cinfo['kind']} ({cinfo['source']})" if card else "missing"
    if not card:
        warnings.append("no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM "
                        "tee box nearest each hole-line start (usually the back tee); lengths are measured")
    card_sets = (card or {}).get("tee_sets") or {}
    per_hole_card = {s: scm.per_hole(card, s, refs) for s in card_sets}
    main_card = per_hole_card.get(chosen, {})

    # card pars into the OSM hole tags so geometry builds par-3 entries for card par 3s
    fc = copy.deepcopy(fc)
    par_src = {}
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") == "hole" and p.get("ref"):
            r = str(p["ref"])
            ch = main_card.get(r) or next((v.get(r) for v in per_hole_card.values() if v.get(r, {}).get("par")), {}) or {}
            if ch.get("par"):
                par_src[r] = "card" if str(p.get("par", "")) in ("", str(ch["par"])) else f"card (OSM says {p['par']})"
                p["par"] = str(ch["par"])
            elif str(p.get("par", "")).isdigit():
                par_src[r] = "osm"

    # S2 + S3 for every tee set on the card (zones come from the longest set's window)
    bh = geometry()
    world = bh.World(fc)
    built, tee_pos = {}, {}
    for s in (card_sets or {None: None}):
        hc = per_hole_card.get(s, {})
        tp = place_tees(fc, hc, s, card_sets[s].get("colour")) if (s and hc) else None
        lengths = {r: float(c["yards"]) for r, c in hc.items() if c.get("yards")}
        built[s], _ = bh.build(fc, s, lengths or None, world=world, tees=tp, frame="yard")
        tee_pos[s] = tp
    stages["tees"] = (f"ok: tees/place_tee.py for {len(card_sets)} sets on the card yardages" if card_sets else
                      "fallback: OSM tee nearest the hole-line start (no yardages)")
    if not built or not any(built.values()):
        raise SystemExit("no holes built (no golf=hole ways and no tee/green pairs)")
    back = max(built, key=lambda s: sum(h["length"] for h in built[s].values()))
    chosen_key = chosen if chosen in built else back
    base = built[back]
    stages["geometry"] = f"ok: geometry/build_holes.py ({len(base)} holes, {len(built)} tee set(s))"

    lines = osm_lines(fc)
    holes = {}
    for k in sorted(base, key=lambda r: str(r).zfill(3)):
        b = base[k]
        frb = _frame(b["tee_ll"], b["aim_ll"])
        zones_ll = []
        for lie, poly in b["zones"]:
            ring = _ring_ll(frb, poly)
            src = "osm"
            if lie == "ob" and world.course is not None:
                from shapely.geometry import Polygon as SPoly
                rp = world.proj(SPoly(ring)).representative_point()
                if not world.course.contains(rp):
                    src = "osm:course_boundary"
            zones_ll.append(dict(lie=lie, poly=ring, src=src, p=1.0))
        tees = {}
        for s, hs in built.items():
            y = hs.get(k)
            if not y:
                continue
            ch = per_hole_card.get(s, {}).get(k, {})
            meth = y["tee_choice"]
            tees[s or "osm_back"] = dict(
                tee_ll=y["tee_ll"], aim_ll=y["aim_ll"], bearing_deg=bearing(y["tee_ll"], y["aim_ll"]),
                method=meth.replace("tee stage: ", "").replace(f"{s} ", "") if s else meth,
                tee_choice=meth, confidence=next((v for kk, v in pipeline().TEE_TRUST if kk in meth), 0.4),
                measured_yards=y["length"], card_yards=ch.get("yards"),
                tee_id=((tee_pos.get(s) or {}).get("holes", {}).get(k, {}).get("tees", {}).get(s, {}) or {}).get("tee_id"))
            if ch.get("yards") and abs(y["length"] - ch["yards"]) > 15 and s == chosen_key:
                warnings.append(f"hole {k}: measured {y['length']} vs card {ch['yards']} yds for {s} "
                                "(no OSM tee box at that yardage?)")
        hcp = main_card.get(k, {}).get("hcp") or b.get("handicap")
        h = dict(ref=k, par=int(b["par"]), hcp=int(hcp) if str(hcp or "").isdigit() else hcp,
                 yards={s: per_hole_card[s].get(k, {}).get("yards") for s in per_hole_card},
                 hole_line_ll=[[round(x, 7), round(y_, 7)] for x, y_ in lines[k]] if k in lines else
                 _ring_ll(frb, b["hole_line"]),
                 green_ll=b["green_ll"],
                 green_polygon_ll=_ring_ll(frb, b["green_polygon"]) if b.get("green_polygon") else None,
                 tees=tees, zones_ll=zones_ll, inferred=b.get("inferred", False), tee_options=b["tee_options"],
                 provenance=dict(green="osm_green" if b["provenance"]["green"] == "osm_green" else "hole_line_end",
                                 par=par_src.get(k, "length rule")))
        h["green_polygon"] = h["green_polygon_ll"]
        holes[k] = h

    img_dir = find_imagery(req, pkg_dir, slug)
    imagery, elevation = imagery_ref(img_dir)
    stages["imagery"] = f"ok: {imagery['dir']} ({imagery['source']}, {imagery['year']})" if imagery else "missing"
    tee_sets = {}
    for name, s in card_sets.items():
        r = s.get("ratings") or []
        tee_sets[name] = dict(colour=s.get("colour"), aliases=s.get("aliases", []), yards=s.get("yards"),
                              par=s.get("par") or card.get("par"), total=s.get("total"),
                              rating=s.get("rating") or (r[0].get("rating") if r else None),
                              slope=s.get("slope") or (r[0].get("slope") if r else None),
                              source=s.get("source") or cinfo["source"])
    if not tee_sets:
        tee_sets["osm_back"] = dict(colour=None, aliases=["back"], yards=None, par=None, total=None, rating=None,
                                    slope=None, source="OSM tee nearest each hole-line start (no scorecard)")
    bnd = course.get("boundary")
    ring = None
    if bnd:
        rings = [bnd["coordinates"][0]] if bnd["type"] == "Polygon" else [p[0] for p in bnd["coordinates"]]
        ring = max(rings, key=len)
    package = dict(
        schema=SCHEMA, slug=slug, built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        request=req,
        course=dict({k: course.get(k) for k in ("name", "osm", "center", "bbox", "town", "state", "address",
                                                "website", "holes_mapped", "candidates")},
                    slug=slug, city=course.get("town"), boundary=ring, boundary_geojson=bnd),
        sources=dict(osm=dict(fetched=summ.get("fetched_utc"), file=os.path.relpath(os.path.join(raw, "osm.geojson"), pc.ROOT),
                              attribution="(c) OpenStreetMap contributors, ODbL 1.0"),
                     scorecard=dict(kind=cinfo["kind"], source=cinfo["source"], url=cinfo.get("url"),
                                    confidence=card_confidence(cinfo["kind"]), tried=cinfo["tried"]),
                     imagery=imagery, dem=elevation, vision_raw=vision_raw_dirs(slug, course)),
        tee_set=chosen_key if chosen_key else "osm_back",
        tee_set_info=dict(requested=wanted, chosen=chosen, how=how,
                          colour=card_sets.get(chosen, {}).get("colour") if chosen else None,
                          warning=None if card else "no scorecard: back tee (OSM tee nearest each hole-line start)"),
        tee_sets=tee_sets, scorecard=dict(kind=cinfo["kind"], source=cinfo["source"], url=cinfo.get("url"),
                                          confidence=card_confidence(cinfo["kind"])),
        imagery=imagery, elevation=elevation,
        frame="yard",
        frame_doc="zones_ll / *_ll are WGS84 [lon, lat] and frame-free. zones, tee, dot270, green, hole_line are "
                  "the yard frame of tee_set (x = yds right of the tee line, y = -yds along it; tee (0,0), "
                  "dot270 (0,-270)), derived by platform/package.py reframe(). Pixel frame per hole: "
                  "px = pixel.tee_px + pixel.ppy * (x, y) (920 x 2000, the image / book frame).",
        holes=holes, stages=stages, warnings=warnings,
        attribution=["(c) OpenStreetMap contributors, ODbL 1.0", "USDA NAIP (public domain)", "USGS 3DEP (public domain)"])
    if package["tee_set"] == "osm_back":
        for h in holes.values():
            if None in h["tees"]:
                h["tees"]["osm_back"] = h["tees"].pop(None)

    # elevation for every tee set
    sample = dem_sampler(os.path.join(pc.ROOT, elevation["file"])) if elevation else None
    if sample is not None:
        n_ok = 0
        for k, h in holes.items():
            for s, t in h["tees"].items():
                fr = _frame(t["tee_ll"], t["aim_ll"])
                g = fr.ll_to_yds(np.array([h["green_ll"]]))[0]
                hh = dict(ref=k, par=h["par"], length=t["card_yards"] or t["measured_yards"],
                          measured_length=t["measured_yards"], green=[float(g[0]), float(g[1])],
                          bearing_deg=t["bearing_deg"])
                try:
                    t["elevation"] = elevation_for_hole(hh, sample, fr.yds_to_ll)
                    n_ok += t["elevation"] is not None and s == package["tee_set"]
                except Exception as e:                           # noqa: BLE001
                    t["elevation"] = None
                    warnings.append(f"hole {k} {s}: elevation failed ({type(e).__name__}: {e})")
        stages["elevation"] = f"ok: {elevation['file']} ({n_ok}/{len(holes)} holes)"
    else:
        stages["elevation"] = "missing (no DEM)"

    package = reframe(package)
    if gapfill:
        package = call_gapfill(package, img_dir, warnings)
        package["warnings"] = warnings if package.get("warnings") is None else package["warnings"]
        package = reframe(package)
    else:
        stages["vision"] = "not run (gapfill=False)"
    package["coverage"] = osm_coverage.coverage(fc, package["holes"])
    if render:
        package["stages"]["images"] = render_images(package, pkg_dir, img_dir)
    return package


def _yard_poly(fr, ring):
    from shapely.geometry import Polygon as SPoly
    p = SPoly(fr.ll_to_yds(np.asarray(ring, float)))
    return p if p.is_valid else p.buffer(0)


def reframe(package, tee_set=None):
    """Yard-frame view of every hole for `tee_set` (default package["tee_set"]) from the WGS84 data
    (tees[set].tee_ll / aim_ll, green_ll, green_polygon_ll, hole_line_ll, zones_ll): zones clipped to the
    hole window, sorted by the lie order (later wins), par-3 entries, pixel frame (geometry.frame_for 'fit'),
    then confidence, landing lies, exposure and notes. Returns a new dict; the input is not modified."""
    from shapely.geometry import LineString, Point, box
    from shapely.geometry import Polygon as SPoly
    bh = geometry()
    p = copy.deepcopy(package)
    s = tee_set or p.get("tee_set")
    p["tee_set"] = s
    for k, h in p["holes"].items():
        t = h["tees"].get(s)
        if t is None:                                            # set not on this hole: nearest by length
            t = next(iter(h["tees"].values()))
            h.setdefault("flags", []).append(f"tee set {s} missing on this hole")
        fr = _frame(t["tee_ll"], t["aim_ll"])
        Y = lambda ll: fr.ll_to_yds(np.asarray(ll, float))      # noqa: E731
        green = Y([h["green_ll"]])[0]
        gpoly = _yard_poly(fr, h["green_polygon_ll"]) if h.get("green_polygon_ll") else None
        line = Y(h["hole_line_ll"])
        W_ = lambda xy: np.c_[np.asarray(xy)[:, 0], -np.asarray(xy)[:, 1]]   # noqa: E731  yard -> (right, along)
        path, L, _, _, _ = bh._tee_path(np.zeros(2), W_(line), W_([green])[0])
        far = max([-green[1]] + ([-y for _, y in gpoly.exterior.coords] if gpoly is not None else []))
        reach = max(WINDOW_MIN, far + WINDOW_PAST)
        win = box(-WINDOW_LAT, -reach, WINDOW_LAT, WINDOW_BEHIND)
        order = []
        for i, z in enumerate(h.get("zones_ll") or []):
            lie = z.get("lie")
            key = "ob_boundary" if (lie == "ob" and str(z.get("src", "")).endswith("course_boundary")) else lie
            order.append((LIE_ORDER.index(key) if key in LIE_ORDER else 0, i, z))
        order.sort(key=lambda o: (o[0], o[1]))
        zones, zsrc = [], []
        for _, _, z in order:
            try:
                g = _yard_poly(fr, z["poly"]).intersection(win)
            except Exception:                                    # noqa: BLE001
                continue
            if g.is_empty:
                continue
            for piece in bh._holefree(g):
                if piece.area < 1.5:
                    continue
                zones.append([MODEL_LIE.get(z["lie"], z["lie"]),
                              [[round(x, 1), round(y, 1)] for x, y in piece.exterior.coords[:-1]]])
                zsrc.append(z.get("src", "osm"))
        card_y = t.get("card_yards")
        h.update(tee_ll=t["tee_ll"], aim_ll=t["aim_ll"], bearing_deg=t["bearing_deg"],
                 green_bearing_deg=bearing(t["tee_ll"], h["green_ll"]),
                 length=int(card_y) if card_y else int(round(t["measured_yards"])),
                 measured_length=t["measured_yards"], tee_choice=t["tee_choice"],
                 tee=[0.0, 0.0], dot270=[0.0, -270.0], green=[round(float(green[0]), 1), round(float(green[1]), 1)],
                 hole_line=[[round(float(x), 1), round(float(-a), 1)] for x, a in path],
                 green_polygon_yd=[[round(x, 1), round(y, 1)] for x, y in gpoly.exterior.coords[:-1]] if gpoly is not None else None,
                 zones=zones, zone_src=zsrc, elevation=t.get("elevation"))
        h["provenance"].update(tee=f"tees:{t['method']}", length=f"card:{s}" if card_y else "measured",
                               bearing="geodesic tee -> aim_ll, degrees true")
        # pixel frame: geometry.frame_for 'fit' in (right, along) coordinates
        gW = SPoly(W_(np.array(gpoly.exterior.coords))) if gpoly is not None else None
        _, ppy, tee_px, _, _, _ = bh.frame_for(np.zeros(2), np.array([0.0, 1.0]), gW, W_([green])[0],
                                               h["par"], h["length"], "fit")
        h["pixel"] = dict(ppy=round(float(ppy), 4), tee_px=[round(float(tee_px[0]), 1), round(float(tee_px[1]), 1)],
                          size=[W, H], proj="utm")
        h.pop("par3", None)
        if h["par"] == 3 and gpoly is not None:
            h["par3"] = par3_entry(h, gpoly)
    finish(p)
    return p


def par3_entry(h, gpoly):
    """course.PAR3 fields in the yard frame: flag = green centre; green outline as (yds right, yds past the flag)."""
    tee = np.zeros(2)
    flag = np.array(h["green"], float)
    v = flag - tee
    center = float(np.linalg.norm(v))
    fwd = v / center
    right = np.array([-fwd[1], fwd[0]])
    rel = np.array(gpoly.simplify(0.3).exterior.coords[:-1]) - flag
    green = [[round(float(q @ right), 1), round(float(q @ fwd), 1)] for q in rel]
    past = [g[1] for g in green]
    return dict(tee=[0.0, 0.0], flag=[round(float(flag[0]), 1), round(float(flag[1]), 1)], center=round(center),
                front=round(center + min(past)), back=round(center + max(past)), green=green, source="package")


def exposure(h):
    """Share of the landing zone's lateral edges (40-60 yds off the line, 220-340 along) that is trees."""
    from matplotlib.path import Path
    a = np.arange(220, 341, 10.0)
    pts = np.array([[sgn * d, -al] for al in a for d in (40.0, 50.0, 60.0) for sgn in (-1, 1)])
    hit = np.zeros(len(pts), bool)
    for n, poly in h["zones"]:
        if n == "recovery":
            hit |= Path(np.array(poly, float)).contains_points(pts)
    return round(float(hit.mean()), 3)


def finish(package):
    """Confidence, landing lies, par-3 hazards, exposure and notes from the current yard-frame zones."""
    pl = pipeline()
    for k, h in package["holes"].items():
        src = h.get("zone_src") or ["osm"] * len(h["zones"])
        h_osm = dict(h, zones=[z for z, s_ in zip(h["zones"], src) if str(s_).startswith("osm")])
        hh = dict(h, has_green_polygon=h["provenance"]["green"] == "osm_green")
        if not hh["has_green_polygon"]:
            hh["green_from"] = "hole_line_end"
        card = dict(par=h["par"] if str(h["provenance"]["par"]).startswith("card") else None,
                    yards=h["length"] if str(h["provenance"]["length"]).startswith("card") else None)
        c = pl.confidence(hh, h_osm, {"par": h["par"]} if h["provenance"]["par"] == "osm" else {}, card, k)
        c["flags"] = c["flags"] + h.pop("flags", [])
        h["confidence"] = c
        lies = {}
        for z, s_ in zip(h["zones"], src):
            lies.setdefault(z[0], set()).add(str(s_).split(":")[0])
        h["provenance"]["zones"] = {lie: "+".join(sorted(v)) for lie, v in sorted(lies.items())}
        h["landing_lies"] = landing_lies(h) if h["par"] >= 4 else {}
        if not h.get("exposure_src", "").startswith("vision"):
            h["exposure"] = exposure(h) if h["par"] >= 4 else 0.0
            h["exposure_src"] = "zones"
        if h.get("par3"):
            h["par3"]["haz"] = par3_haz(h)
            bad = [f"{v} {s_}" for s_, v in h["par3"]["haz"].items() if v != "rough"]
            h["par3"]["short"] = ", ".join(bad) + "." if bad else "No mapped trouble near the green."
            h["par3"]["note"] = f"Auto-built ({'+'.join(sorted({str(x).split(':')[0] for x in src})) or 'osm'}). {h['par3']['short']}"
        src_txt = "OSM" + (" + imagery" if c["imagery"] > 0 else "")
        h["note"] = (f"Auto-built ({src_txt}; confidence {c['score']:.2f}, {c['band']}). Tee: {h['tee_choice']}."
                     + (" Check: " + "; ".join(c["flags"][:3]) + "." if c["flags"] else ""))


# ----------------------------------------------------------------------------- outputs
COURSE_MODULE = '''"""Course module for {name} ({tee_set} tees), generated from package.json by
course_data/platform/package.py on {built}. Do not edit; rebuild with

  python course_data/platform/package.py build course_data/requests/package_{slug}.json

Same API as spirit_hollow/course.py (HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS, APP, GREEN_SIDE) in each
hole's 920 x 2000 pixel frame (px = tee_px + ppy * yard-frame point), so mozingo/tee_strategy.py and
mozingo/yardage_book.use_course() take it unchanged:

  yb.use_course(NAME, DIR, PREFIX, HOLES, PAR3, NOTES, AIM_AT, ORDER, LABELS)
"""
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(DIR, "package.json")) as _fh:
    PACKAGE = json.load(_fh)
NAME = PACKAGE["course"]["name"]
PREFIX = "{prefix}"
TEE_SET = PACKAGE["tee_set"]


def _key(k):
    return int(k) if str(k).isdigit() else k


def _px(h, p):
    ppy, (tx, ty) = h["pixel"]["ppy"], h["pixel"]["tee_px"]
    return (round(tx + ppy * p[0], 1), round(ty + ppy * p[1], 1))


HOLES, PAR3, NOTES, AIM_AT = {{}}, {{}}, {{}}, {{}}
for _k, _h in PACKAGE["holes"].items():
    _z = [(n, [_px(_h, p) for p in poly]) for n, poly in _h["zones"]]
    _hole = dict(par=_h["par"], image=_h.get("image"), length=_h["length"], tee=_px(_h, (0, 0)),
                 dot270=_px(_h, (0, -270)), green=_px(_h, _h["green"]), zones=_z, aim_min=-60, aim_max=60,
                 px_per_yd=_h["pixel"]["ppy"], hole_line=[_px(_h, p) for p in _h["hole_line"]],
                 tee_ll=_h["tee_ll"], aim_ll=_h["aim_ll"], green_ll=_h["green_ll"], bearing_deg=_h["bearing_deg"],
                 auto=_h["confidence"], elevation=_h.get("elevation"))
    NOTES[_key(_k)] = _h.get("note", "Auto-built.")
    _p3 = _h.get("par3")
    if _p3:
        PAR3[_key(_k)] = dict(_p3, image=_h.get("image"), tee=_px(_h, _p3["tee"]), flag=_px(_h, _p3["flag"]),
                              green=[tuple(q) for q in _p3["green"]], zones=_z, auto=_h["confidence"])
    else:
        HOLES[_key(_k)] = _hole
        AIM_AT[_key(_k)] = "Centre of the fairway"

ORDER = sorted(set(HOLES) | set(PAR3), key=lambda k: (str(k).rstrip("BF").zfill(3), str(k)))
LABELS = {{}}
APP, GREEN_SIDE = {{}}, {{}}
'''


def qa_md(p):
    c = p["course"]
    s = p["coverage"]["summary"]
    lines = [f"# {c['name']} ({c.get('town')}, {c.get('state')}) - {p['tee_set']} tees",
             "", f"Built {p['built']}. OSM {c['osm']['type']}/{c['osm']['id']}. Scorecard: {p['scorecard']['kind']} "
             f"({p['scorecard']['source']}). Tee set: {p['tee_set_info']['how']}.", "",
             "## Coverage", "", "| | |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in s.items()]
    lines += ["", "OSM features inside the course: " + ", ".join(f"{k} {v}" for k, v in p["coverage"]["features"].items()), "",
              "## Holes", "", "| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, h in p["holes"].items():
        cf = h["confidence"]
        lines.append(f"| {k} | {h['par']} | {h['length']} / {h['measured_length']} | {h['bearing_deg']:.0f} | {cf['score']:.2f} | "
                     f"{cf['band']} | {cf['osm']:.0%} | {cf['imagery']:.0%} | {cf['inferred']:.0%} | {h['tee_choice']} | "
                     f"{'; '.join(cf['flags'])} |")
    lines += ["", "## Stages", ""] + [f"- **{k}**: {v}" for k, v in p["stages"].items()]
    if p["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in p["warnings"]]
    return "\n".join(lines) + "\n"


def render_images(package, pkg_dir, img_dir):
    if not img_dir:
        return "missing (no imagery)"
    rd = load(os.path.join(CD, "imagery", "render.py"), "cdp_render")
    try:
        img = rd.Imagery(img_dir)
    except Exception as e:                                       # noqa: BLE001
        return f"failed: {type(e).__name__}: {e}"[:200]
    n = 0
    for k, h in package["holes"].items():
        name = f"hole{int(k):02d}.png" if str(k).isdigit() else f"hole{k}.png"
        try:
            rd.render_hole(pkg_dir, h, os.path.join(pkg_dir, "screenshots", name),
                           frame=dict(tee_ll=h["tee_ll"], aim_ll=h["aim_ll"], ppy=h["pixel"]["ppy"],
                                      tee_px=h["pixel"]["tee_px"], proj="utm"), imagery=img)
            h["image"] = name
            n += 1
        except Exception as e:                                   # noqa: BLE001
            pc.log("render", k, e)
    return f"ok: {n}/{len(package['holes'])} rendered from {os.path.relpath(img_dir, pc.ROOT)}"


def write(package, pkg_dir):
    pc.write_json(os.path.join(pkg_dir, "package.json"), package, indent=None)
    slug = package["slug"]
    with open(os.path.join(pkg_dir, "course_auto.py"), "w") as fh:
        fh.write(COURSE_MODULE.format(name=package["course"]["name"], tee_set=package["tee_set"],
                                      built=package["built"], slug=slug,
                                      prefix="".join(w.title() for w in slug.split("_")) + "_Auto"))
    with open(os.path.join(pkg_dir, "qa.md"), "w") as fh:
        fh.write(qa_md(package))
    pc.write_json(os.path.join(pkg_dir, "coverage.json"), package["coverage"])


def build_request(req_path, render=False):
    import fetch_package as fp
    req = pc.read_json(req_path)
    slug = fp.request_slug(req, req_path)
    pkg_dir = os.path.join(pc.PACKAGES, slug)
    package = build_package(req, pkg_dir, render=render)
    write(package, pkg_dir)
    s = package["coverage"]["summary"]
    print(f"{slug}: {package['course']['name']} | tee set {package['tee_set']} ({package['tee_set_info']['how']}) | "
          f"{len(package['holes'])} holes | {json.dumps(s)}")
    return package


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build", "run"])
    ap.add_argument("requests", nargs="+")
    ap.add_argument("--render", action="store_true", help="render holeNN.png from the imagery")
    a = ap.parse_args()
    paths = [p for r in a.requests for p in sorted(glob.glob(r))]
    failed = []
    for p in paths:
        try:
            if a.cmd == "run":
                import fetch_package as fp
                slug, status = fp.fetch(p)
                if status != "ok":
                    print(f"{slug}: {status}; see packages/{slug}/raw/course.json for the candidates")
                    failed.append(p)
                    continue
            req = pc.read_json(p)
            build_request(p, render=a.render or bool(req.get("render")))
        except SystemExit as e:
            print(f"{p}: {e}")
            failed.append(p)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
