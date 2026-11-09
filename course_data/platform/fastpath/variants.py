"""Cheaper builds of the truth courses, made from the committed full packages by removing what a stage adds
(for the time-vs-accuracy table: what does skipping or cheapening a stage cost in regret?).

  python3 variants.py NAME [--courses a,b]   -> cache/variants/NAME/<slug>/package.json
  NAME: full | no_native (S4n held out anyway: the committed band is the shipped model's, trained on these courses)
        no_lidar_trees | meta_trees | no_ob_evidence | no_vision_water | no_elevation | osm_only (all of them)
"""
import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAT = os.path.dirname(HERE)
CD = os.path.dirname(PLAT)
ROOT = os.path.dirname(CD)
CACHE = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
sys.path[:0] = [HERE, PLAT]
import platform_common as pc  # noqa: E402
import package as pk  # noqa: E402

LIDAR_TREES = ("vision2:lidar_canopy", "vision:lidar_hag")
RULES = {
    "full": (),
    "no_native": ("auto:native_side",),
    "no_lidar_trees": ("auto:native_side",) + LIDAR_TREES,
    "meta_trees": ("auto:native_side",) + LIDAR_TREES,          # + Meta canopy trees (canopy.py)
    "no_ob_evidence": ("auto:native_side", "ob:property_line"),
    "no_vision_water": ("auto:native_side", "vision:naip_ndwi"),
    "no_elevation": ("auto:native_side",),
    "osm_only": ("auto:native_side", "ob:property_line", "vision", "segment:") + LIDAR_TREES,
}


def truth_courses():
    sys.path.insert(0, PLAT)
    out = []
    import importlib.util
    spec = importlib.util.spec_from_file_location("eb_list", os.path.join(PLAT, "error_budget.py"))
    src = open(os.path.join(PLAT, "error_budget.py")).read()
    import re
    v1 = re.findall(r'dict\(slug="(\w+)", tees="([^"]+)", kind="(\w+)"(?:,\s*package="([^"]+)")?', src)
    for s, t, k, p in v1:
        out.append(dict(slug=s, package=p or f"course_data/packages/{s}/package.json"))
    idx = pc.read_json(os.path.join(CD, "truth_sets_v2", "index.json"), {}).get("courses", {})
    for s in idx:
        if os.path.exists(os.path.join(CD, "truth_sets_v2", s, "holes_truth.json")) and \
                os.path.exists(os.path.join(CD, "truth_sets_v2", s, "hand_zones_ll.json")):
            out.append(dict(slug=s, package=f"course_data/packages/{s}/package.json"))
    return out


def make(name, slugs=None, log=print):
    drop = RULES[name]
    out_root = os.path.join(CACHE, "variants", name)
    n = 0
    for c in truth_courses():
        if slugs and c["slug"] not in slugs:
            continue
        p = pc.read_json(os.path.join(ROOT, c["package"]))
        if not p:
            continue
        p = copy.deepcopy(p)
        removed = 0
        for h in p["holes"].values():
            zl = h.get("zones_ll") or []
            keep = [z for z in zl if not str(z.get("src", "")).startswith(drop)]
            removed += len(zl) - len(keep)
            h["zones_ll"] = keep
            if name in ("no_elevation", "osm_only"):
                h.pop("elevation", None)
                for t in (h.get("tees") or {}).values():
                    t.pop("elevation", None)
        if name == "meta_trees":
            import canopy
            added = canopy.add_trees(p, CACHE)
            log(f"  {c['slug']}: Meta canopy trees {added}")
        try:
            q = pk.reframe(p)
        except Exception as e:                                       # noqa: BLE001
            log(f"  {c['slug']}: reframe failed {type(e).__name__}: {e}")
            continue
        d = os.path.join(out_root, c["slug"])
        os.makedirs(d, exist_ok=True)
        json.dump(q, open(os.path.join(d, "package.json"), "w"))
        n += 1
        log(f"{name} {c['slug']}: {removed} zones removed")
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--courses")
    a = ap.parse_args()
    make(a.name, a.courses.split(",") if a.courses else None)
