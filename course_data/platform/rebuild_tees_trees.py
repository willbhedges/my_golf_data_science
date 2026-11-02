"""Rebuild only the tee layer and/or the tree layer of committed packages, offline (for the error budget).

    python3 course_data/platform/rebuild_tees_trees.py --out DIR [--layers tees,trees,fairway] [--courses a,b] [--k 1]
        [--fw-band YDS | --fw-edge fairway_edge.json --fw-theta 0.5] [--fw-lie fairway|first_cut]
    -> DIR/<slug>/package.json   (python3 course_data/platform/error_budget.py --auto-dir DIR --tag NAME)

tees   the S2 stage as platform/package.build_package runs it (place_tees_v2: tees/localize.py + the tagged-box
       rule, then sanity.guard_tees) on the package's raw/osm.geojson, card yardages and DEM (lidar + texture pads),
       written into the committed package with tees/picks_localize.retee (aim, measured length, elevation profile,
       reframe). Packages without raw/osm.geojson (library/colbert_hills) keep their tees.
trees  the vision_any/2 tree polygons re-made from the lidar canopy with buffer k m (v2_model.tree_rule, HAG and
       clump size from model_v2/model.json) + the committed vision_any.geojson's other features (water, native: as
       committed), put in with vision_any/gapfill.gapfill (every vision zone re-clipped to each hole's window).
       OB is NOT re-inferred (ob_infer does not read the tree layer). Courses without a vision_any/<slug>/raw stack
       keep their trees.
fairway  platform/fairway_band.widen_package after the tees / trees: the OSM fairway widened by a band that only
       turns rough into fairway (or first_cut). --fw-band: one width for every course (yds); --fw-edge: per course
       from the NAIP edge profile (platform/fairway_edge.py; band = extension(profile, theta) m, capped at --fw-max).
Everything else in the package (OSM zones, OB, card, greens, routing) is the committed build.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import importlib.util
import io
import json
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
def tee_positions(pkg, pkg_dir, slug):
    """S2 tee positions {ref: {tees: {set: {...}}}} as build_package makes them, or None (no raw OSM)."""
    osm = os.path.join(pkg_dir, "raw", "osm.geojson")
    if not os.path.exists(osm):
        return None
    PP = _load("rtt_platform_package", os.path.join(HERE, "package.py"))
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import sanity
    fc = json.load(open(osm))
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


def retee(pkg, pkg_dir, slug):
    try:
        pos = tee_positions(pkg, pkg_dir, slug)
    except RuntimeError as e:                 # e.g. "no hole lines": OSM has no golf=hole ways (routed build)
        return pkg, f"tees kept ({e})"
    if pos is None:
        return pkg, "tees kept (no raw/osm.geojson)"
    sys.path.insert(0, os.path.join(CD, "tees"))
    import picks_localize as PL
    out, moved = PL.retee(pkg, pos, "rebuild_tees_trees")
    return out, f"tees rebuilt: {moved} tee(s) moved"


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
        pkg.setdefault("stages", {})["rebuild_tees_trees"] = "; ".join(notes)
        d = os.path.join(a.out, slug)
        os.makedirs(d, exist_ok=True)
        json.dump(pkg, open(os.path.join(d, "package.json"), "w"))
        log(f"[{slug}] {'; '.join(notes)} ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
