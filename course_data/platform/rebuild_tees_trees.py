"""Rebuild only the tee layer and/or the tree layer of committed packages, offline (for the error budget).

    python3 course_data/platform/rebuild_tees_trees.py --out DIR [--layers tees,trees,fairway,water] [--courses a,b] [--k 1]
        [--fw-band YDS | --fw-edge fairway_edge.json --fw-theta 0.5] [--fw-lie fairway|first_cut]
    -> DIR/<slug>/package.json   (python3 course_data/platform/error_budget.py --auto-dir DIR --tag NAME)

tees   the S2 stage as platform/package.build_package runs it (place_tees_v2: tees/localize.py + the tagged-box
       rule, then sanity.guard_tees) on the package's raw/osm.geojson, card yardages and DEM (lidar + texture pads),
       written into the committed package with tees/picks_localize.retee (aim, measured length, elevation profile,
       reframe). Packages without raw/osm.geojson (library/colbert_hills) keep their tees. The raw OSM is cleaned as
       the build cleans it (sanity.clean_osm) and its hole ways are matched to the package's hole lines (prepare_osm:
       a neighbouring course's ways with the same refs once moved pevely_farms 1/9/10/18 by 1,100-1,700 yds). Guard
       (guard_positions): a re-made tee > 150 yds from the package's, or off the card by > 15 % (and worse than the
       package tee), keeps the package tee; the reason is logged and listed in stages.retee_guard.
trees  the vision_any/2 tree polygons re-made from the lidar canopy with buffer k m (v2_model.tree_rule, HAG and
       clump size from model_v2/model.json) + the committed vision_any.geojson's other features (water, native: as
       committed), put in with vision_any/gapfill.gapfill (every vision zone re-clipped to each hole's window).
       OB is NOT re-inferred (ob_infer does not read the tree layer). Courses without a vision_any/<slug>/raw stack
       keep their trees.
fairway  platform/fairway_band.widen_package after the tees / trees: the OSM fairway widened by a band that only
       turns rough into fairway (or first_cut). --fw-band: one width for every course (yds); --fw-edge: per course
       from the NAIP edge profile (platform/fairway_edge.py; band = extension(profile, theta) m, capped at --fw-max).
water  vision_any/water_filter.filter_package (as gapfill now runs it): false vision water (OSM roads / paths, thin paved strips, raised bare
       ground) removed from the committed water zones (+ --piped: OSM stream pieces over turf tagged tunnel or with no
       DTM channel), then the yard frame refreshed. Run it on its own
       (--layers water) to score the water rule alone.
Everything else in the package (OSM zones, OB, card, greens, routing) is the committed build.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import io
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ----------------------------------------------------------------------------- tees
MAX_MOVE_YD = 150.0     # guard: a re-made tee more than this from the package's tee keeps the package tee
MAX_CARD_DEV = 0.15     # guard: ... and one whose measured length is off the card by more (and worse than the package's)
MATCH_START_YD = 60.0   # an OSM golf=hole way is a package hole's line when its start is this close to the package's
MATCH_END_YD = 120.0    # ... and its end this close (a green override can move the end a little)


def hav_yd(a_ll, b_ll):
    """great-circle yards between two [lon, lat] points"""
    lo1, la1, lo2, la2 = map(math.radians, (a_ll[0], a_ll[1], b_ll[0], b_ll[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(min(1.0, math.sqrt(h))) / 0.9144


def prepare_osm(fc, pkg, course_name=None):
    """raw/osm.geojson -> (fc, [notes]) with the golf=hole ways the committed build used, keyed by the PACKAGE's
    hole numbers. build_package cleans the raw OSM (sanity.clean_osm: practice tees, neighbouring courses' hole
    ways, osm_supplement), renumbers, routes and applies review overrides before place_tees_v2; retee used to pass
    the raw OSM, so on a multi-course site a neighbour's way with the same ref won (pevely_farms 1, 9, 10, 18: tees
    1,100-1,700 yds away). Here: clean_osm as the build runs it, then every hole way is matched to a package hole
    by its hole_line_ll ends (start <= MATCH_START_YD, end <= MATCH_END_YD, one to one, closest first) and takes
    that hole's ref and par; unmatched ways are dropped, so a hole with no matching way (routed, review-redrawn)
    gets no S2 position and keeps its tees."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import sanity
    names = [n for n in ((pkg.get("request") or {}).get("course"), course_name) if n]
    with contextlib.redirect_stdout(io.StringIO()):
        fc, notes = sanity.clean_osm(fc, names=names, near=(pkg.get("request") or {}).get("near"))
    fc = copy.deepcopy(fc)
    notes = list(notes)
    lines = {k: h["hole_line_ll"] for k, h in pkg["holes"].items() if len(h.get("hole_line_ll") or []) >= 2}
    ways = [f for f in fc["features"] if f["properties"].get("golf") == "hole"
            and (f.get("geometry") or {}).get("type") == "LineString"]
    cand = []
    for i, f in enumerate(ways):
        c = f["geometry"]["coordinates"]
        for k, L in lines.items():
            ds, de = hav_yd(c[0], L[0]), hav_yd(c[-1], L[-1])
            if ds <= MATCH_START_YD and de <= MATCH_END_YD:
                cand.append((ds + de, i, k))
    used, got = set(), {}
    for _, i, k in sorted(cand):
        if i in used or k in got:
            continue
        used.add(i)
        got[k] = i
    for k, i in got.items():
        p = ways[i]["properties"]
        if str(p.get("ref")) != k:
            p["osm_ref"] = p.get("ref")
        p["ref"] = k
        if pkg["holes"][k].get("par"):
            p["par"] = str(pkg["holes"][k]["par"])
    drop = {id(ways[i]) for i in range(len(ways)) if i not in used}
    if drop:
        notes.append(f"ignored {len(drop)} golf=hole way(s) that match no package hole line: OSM "
                     + ", ".join(str(f["properties"].get("osm_id")) for f in ways if id(f) in drop)[:200])
        fc["features"] = [f for f in fc["features"] if id(f) not in drop]
    miss = sorted(set(lines) - set(got), key=lambda r: r.zfill(3))
    if miss:
        notes.append(f"no OSM hole way matches the package line of hole(s) {', '.join(miss)}: tees kept there")
    return fc, notes


def tee_positions(pkg, pkg_dir, slug, notes=None):
    """S2 tee positions {ref: {tees: {set: {...}}}} as build_package makes them, or None (no raw OSM)."""
    osm = os.path.join(pkg_dir, "raw", "osm.geojson")
    if not os.path.exists(osm):
        return None
    PP = _load("rtt_platform_package", os.path.join(HERE, "package.py"))
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import sanity
    try:
        course_name = (json.load(open(os.path.join(pkg_dir, "raw", "course.json"))) or {}).get("name")
    except (OSError, ValueError):
        course_name = None
    fc, n = prepare_osm(json.load(open(osm)), pkg, course_name)
    if notes is not None:
        notes += n
    sets = list(pkg.get("tee_sets") or {})
    per = {s: {} for s in sets}
    for k, h in pkg["holes"].items():
        for s in sets:
            y = (h.get("yards") or {}).get(s)
            if y:
                per[s][k] = dict(yards=y, par=h.get("par"))
    card_sets = {s: (v if isinstance(v, dict) else {}) for s, v in (pkg.get("tee_sets") or {}).items()}
    img = os.path.join(pkg_dir, "imagery")
    dem = os.path.join(img, "dem.tif")
    pads, _ = PP.lidar_pads(fc, dem if os.path.exists(dem) else None)
    j = PP.place_tees_v2(fc, per, card_sets, pads, img_dir=img if os.path.exists(dem) else None, slug=slug, req={})
    sanity.guard_tees(j, fc)
    return j["holes"]


def _measure(h, lat, lon):
    sys.path.insert(0, os.path.join(CD, "tees"))
    import eval_tees as ET
    line = [(c[1], c[0]) for c in h["hole_line_ll"]]
    return float(ET.measure(line, (h["green_ll"][1], h["green_ll"][0]), lat, lon))


def guard_positions(pkg, pos, max_move=MAX_MOVE_YD, max_dev=MAX_CARD_DEV):
    """-> (positions copy, [why]): drop (keep the package tee for) every re-made tee more than max_move yds from
    the package's tee, or whose measured length is off the card by more than max_dev AND by more than the package
    tee's (a move that brings a stale tee closer to the card is allowed)."""
    out = copy.deepcopy(pos)
    kept = []
    for k, h in pkg["holes"].items():
        hp = (out.get(k) or {}).get("tees") or {}
        for s in list(hp):
            t, r = (h.get("tees") or {}).get(s), hp[s]
            if not t or not t.get("tee_ll"):
                continue
            d = hav_yd(t["tee_ll"], [r["lon"], r["lat"]])
            why = None
            if d > max_move:
                why = f"moved {d:.0f} yds (> {max_move:.0f})"
            elif t.get("card_yards") and h.get("hole_line_ll") and h.get("green_ll"):
                c = float(t["card_yards"])
                m = _measure(h, r["lat"], r["lon"])
                dev = abs(m - c) / c
                old = abs(float(t["measured_yards"]) - c) / c if t.get("measured_yards") else 0.0
                if dev > max_dev and dev > old + 1e-9:
                    why = f"measured {m:.0f} vs card {c:.0f} ({dev:.0%} > {max_dev:.0%}; package {old:.0%})"
            if why:
                del hp[s]
                kept.append(f"{k} {s}: {why}")
    return out, kept


def retee(pkg, pkg_dir, slug):
    notes = []
    try:
        pos = tee_positions(pkg, pkg_dir, slug, notes)
    except RuntimeError as e:                 # e.g. "no hole lines": OSM has no golf=hole ways (routed build)
        return pkg, f"tees kept ({e})"
    if pos is None:
        return pkg, "tees kept (no raw/osm.geojson)"
    pos, kept = guard_positions(pkg, pos)
    for w in kept:
        log(f"[{slug}] retee guard: kept the package tee on {w}")
    sys.path.insert(0, os.path.join(CD, "tees"))
    import picks_localize as PL
    out, moved = PL.retee(pkg, pos, "rebuild_tees_trees")
    msg = f"tees rebuilt: {moved} tee(s) moved"
    if kept:
        msg += f"; guard kept {len(kept)} package tee(s): " + "; ".join(kept[:6]) + (" ..." if len(kept) > 6 else "")
        out.setdefault("stages", {})["retee_guard"] = kept
    if any("match no package" in n or "neighbour" in n for n in notes):
        msg += f" (osm: {sum('match no package' in n or 'neighbour' in n for n in notes)} hole-way note(s))"
    return out, msg


# ----------------------------------------------------------------------------- trees
def tree_fc(vslug, k):
    """vision_any/2 FeatureCollection: trees re-made with buffer k m + the committed non-tree features."""
    vd = os.path.join(CD, "vision_any")
    if vd not in sys.path:
        sys.path.insert(0, vd)
    import layers as L
    import run_any as RA
    import v2_model as VM
    from shapely.geometry import mapping
    from shapely.ops import transform
    cp = os.path.join(vd, vslug, "vision_any.geojson")      # absent when the build had no raw stack (no vision layer)
    cur = json.load(open(cp)) if os.path.exists(cp) else dict(type="FeatureCollection", features=[], properties={})
    tb = json.load(open(os.path.join(vd, "model_v2", "model.json")))["settings"]["trees"]
    cdir = RA.course_dir_for(vslug)
    S = L.Stack.load(vslug, cdir)
    M, _ = L.osm_masks(S, json.load(open(os.path.join(cdir, "osm.geojson"))))
    canopy = L.tree_mask(S, M, hag_min=tb["hag"], min_area_m2=10.0)[0]
    trees = VM.tree_rule(canopy, k, tb["min_area_m2"], S.res)
    p = next((f["properties"].get("p") for f in cur["features"] if f["properties"].get("lie") == "recovery"), 0.646)
    S.ll_to_rc([[0, 0]])
    feats = []
    for g in L.mask_to_polys(S, trees, min_yd2=150, simplify_yd=2.0):
        gm = transform(lambda x, y: S._fwd.transform(x, y), g)
        feats.append(dict(type="Feature", geometry=mapping(g), properties=dict(
            lie="recovery", src=f"vision2:lidar_canopy_hag>{tb['hag']}m_buffer{int(k):+d}m", p=p,
            area_yd2=round(gm.area / 0.9144 ** 2), model="vision_any/2")))
    feats += [f for f in cur["features"] if f["properties"].get("lie") != "recovery"]
    props = dict(cur.get("properties") or {})
    props["trees_how"] = str(props.get("trees_how", "")).replace(f"buffered {tb['k_m']:+d} m", f"buffered {int(k):+d} m")
    return dict(type="FeatureCollection", features=feats, properties=props)


def retree(pkg, slug, k):
    vslug = "mozingo" if slug == "mozingo_lake" else slug
    if not os.path.exists(os.path.join(CD, "vision_any", vslug, "raw")):
        return pkg, "trees kept (no vision_any raw stack)"
    fc = tree_fc(vslug, k)
    G = _load("rtt_gapfill", os.path.join(CD, "vision_any", "gapfill.py"))
    G.load_layers = lambda s, imagery_dir=None, course_dir=None: (fc, fc.get("properties", {}))
    with contextlib.redirect_stdout(io.StringIO()):
        out = G.gapfill(pkg, slug=vslug)
    n = sum(1 for h in out["holes"].values() for z in h.get("zones_ll") or [] if z.get("lie") == "recovery")
    return out, f"trees rebuilt: buffer {int(k):+d} m, {n} tree zones"


# ----------------------------------------------------------------------------- fairway
def fairway_band_yd(slug, a):
    """The band (yds) for a course from the CLI options (fixed, or the NAIP edge extension)."""
    if a.fw_edge:
        import fairway_edge as FE
        prof = (json.load(open(a.fw_edge)).get(slug) or {}).get("course")
        if not prof:
            return 0.0
        e = FE.extension(prof, a.fw_theta) or 0.0
        b = round(min(max(e - a.fw_offset, 0.0), a.fw_max) / 0.9144, 1)
        return b if b >= a.fw_min else 0.0
    return float(a.fw_band or 0.0)


def refairway(pkg, slug, a):
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import fairway_band as FB
    b = fairway_band_yd(slug, a)
    if b <= 0:
        return pkg, "fairway kept (band 0)"
    G = _load("rtt_gapfill_fw", os.path.join(CD, "vision_any", "gapfill.py"))
    rf = G._reframe()
    with contextlib.redirect_stdout(io.StringIO()):
        out, n = FB.widen_package(pkg, b, a.fw_lie, reframe=rf)
    return out, f"fairway band {b:g} yd {a.fw_lie} ({n} zones)"


# ----------------------------------------------------------------------------- water
def rewater(pkg, slug, piped=False):
    vd = os.path.join(CD, "vision_any")
    if vd not in sys.path:
        sys.path.insert(0, vd)
    import water_filter as WF
    vslug = "mozingo" if slug == "mozingo_lake" else slug
    with contextlib.redirect_stdout(io.StringIO()):
        rep = WF.filter_package(pkg, slug=slug, piped=piped)
    G = _load("rtt_gapfill_water", os.path.join(CD, "vision_any", "gapfill.py"))
    rf = G._reframe()
    if rf is not None:
        r = rf(pkg)
        pkg = r if isinstance(r, dict) else pkg
    pp = rep.get("piped") or {}
    v = rep.get("vision")
    vs = (f"vision -{v['removed_m2']:.0f} of {v['water_m2']:.0f} m2 {v['reasons']}" if isinstance(v, dict) else str(v))
    return pkg, (f"water filtered ({vslug}): piped {pp.get('tagged', 0)} tagged + {pp.get('crossing_m', 0)} m crossing, "
                 f"{pp.get('zones_cut', 0)} zones cut; {vs}")


# ----------------------------------------------------------------------------- main
def main():
    sys.path.insert(0, HERE)
    import error_budget as E
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--layers", default="tees,trees")
    ap.add_argument("--courses")
    ap.add_argument("--set", default="v1", choices=sorted(E.SETS), help="course list (error_budget.py --set)")
    ap.add_argument("--k", type=int, default=None, help="tree buffer m (default model_v2/model.json trees.k_m)")
    ap.add_argument("--fw-band", type=float, help="fairway band yds (every course)")
    ap.add_argument("--fw-edge", help="fairway_edge.json: band per course from the NAIP edge profile")
    ap.add_argument("--fw-theta", type=float, default=0.5)
    ap.add_argument("--fw-offset", type=float, default=0.0, help="m subtracted from the edge extension")
    ap.add_argument("--fw-max", type=float, default=15.0, help="m cap on the band")
    ap.add_argument("--fw-min", type=float, default=2.0, help="yds: a smaller edge band is grid noise (1 m), none")
    ap.add_argument("--piped", action="store_true", help="water: also cut piped OSM stream crossings")
    ap.add_argument("--fw-lie", default="fairway", choices=("fairway", "first_cut"))
    a = ap.parse_args()
    layers = set(a.layers.split(","))
    k = a.k if a.k is not None else json.load(open(os.path.join(CD, "vision_any", "model_v2", "model.json")))["settings"]["trees"]["k_m"]
    want = set(a.courses.split(",")) if a.courses else None
    for cfg in E.SETS[a.set]():
        slug = cfg["slug"]
        if want and slug not in want:
            continue
        t0 = time.time()
        pp = os.path.join(ROOT, cfg["package"]) if cfg.get("package") else os.path.join(CD, "packages", slug, "package.json")
        pkg = json.load(open(pp))
        notes = []
        if "tees" in layers:
            pkg, n = retee(pkg, os.path.dirname(pp), slug)
            notes.append(n)
        if "trees" in layers:
            pkg, n = retree(pkg, slug, k)
            notes.append(n)
        if "fairway" in layers:
            pkg, n = refairway(pkg, slug, a)
            notes.append(n)
        if "water" in layers:
            pkg, n = rewater(pkg, slug, piped=a.piped)
            notes.append(n)
        pkg.setdefault("stages", {})["rebuild_tees_trees"] = "; ".join(notes)
        d = os.path.join(a.out, slug)
        os.makedirs(d, exist_ok=True)
        json.dump(pkg, open(os.path.join(d, "package.json"), "w"))
        log(f"[{slug}] {'; '.join(notes)} ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
