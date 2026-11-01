"""Truth set v2: hand-checked routing / tees / greens / landing-corridor hazards for reviewed library courses.

  python3 course_data/truth_sets_v2/truth_sets.py list
  python3 course_data/truth_sets_v2/truth_sets.py build <slug> [<slug> ...]   # -> <slug>/package.json

Per course, course_data/truth_sets_v2/<slug>/ holds
  holes_spec.json   hand routing spec (OSM green / pad ids or [lon, lat]; explicit tee per set where decided by eye)
  holes_truth.json  hole number, par, card per set, tee per set, green centre + outline, line of play
                    (course_data/truth/build_holes_truth.py; same format as course_data/truth/<slug>/holes_truth.json)
  trace.py          the hand corridor trace (course_data/truth/corridor.py helpers)
  hand_zones_ll.json landing corridors of the corridor set's par-4/5 tee shots in WGS84 (corridor.py build; same schema
                    as course_data/truth/<slug>/hand_zones_ll.json): fairway, recovery (trees), water, sand, native
                    (long grass), ob; later zones win; unzoned inside footprint_ll = rough
  package.json      the committed auto package (course_data/packages/<slug>) with the truth applied (truth_package):
                    the same shape as course_data/courses/<slug>/truth/package.json, ready for decide / scoreboards
  CHECK.md          per-course confidence and the items that are still uncertain
Renders / routing maps used for the check live in course_data/truth/<slug>/{render,map}/ (tourn_truth.yml).

For an eval: `truth_package(slug, auto_pkg, tees)` returns the auto package with every truth layer swapped in (the same
rule as course_data/courses/score_auto.py), so the error-budget harness can swap layer by layer from these files.
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)


def available():
    """{slug: meta} of every course with holes_truth.json (+ hand_zones_ll.json when traced)."""
    reg = json.load(open(os.path.join(HERE, "index.json")))["courses"]
    return {s: m for s, m in reg.items() if os.path.exists(os.path.join(HERE, s, "holes_truth.json"))}


def load(slug):
    T = json.load(open(os.path.join(HERE, slug, "holes_truth.json")))
    p = os.path.join(HERE, slug, "hand_zones_ll.json")
    HZ = json.load(open(p))["holes"] if os.path.exists(p) else {}
    return T, HZ


def truth_package(slug, auto_pkg, tees=None, layers=None):
    """auto_pkg with the truth swapped in. layers (default all): any of "routing" (par, card, green, green outline,
    hole line), "tees" (every set's tee), "zones" (hand corridor zones over the auto zones inside the footprint)."""
    layers = set(layers or ("routing", "tees", "zones"))
    T, HZ = load(slug)
    pkg = copy.deepcopy(auto_pkg)
    for ref, th in T["holes"].items():
        h = pkg["holes"].get(ref)
        if h is None:
            continue
        if "routing" in layers:
            h["par"] = th["par"]
            if th.get("card"):
                h["yards"] = dict(th["card"])
            h["green_ll"] = th["green_ll"]
            if th.get("green_poly_ll"):
                h["green_polygon_ll"] = th["green_poly_ll"]
            if th.get("hole_line_ll"):
                h["hole_line_ll"] = th["hole_line_ll"]
        if "tees" in layers:
            tees_ = h.setdefault("tees", {})
            for s, ll in (th.get("tees") or {}).items():
                e = tees_.setdefault(s, {})
                e["tee_ll"] = ll
                e.pop("aim_ll", None)
                e["method"], e["confidence"] = "hand", 1.0
            st = tees if tees in (th.get("tees") or {}) else None
            if st:
                h["tee_ll"] = th["tees"][st]
                h.pop("aim_ll", None)
        m = HZ.get(ref)
        if m and "zones" in layers:
            zs = list(h.get("zones_ll") or [])
            zs.append(dict(lie="rough", poly=m["footprint_ll"], src="hand:footprint"))
            zs += [dict(lie=z["lie"], poly=z["poly_ll"], src="hand") for z in m["zones"]]
            h["zones_ll"] = zs
            h["zone_order"] = "given"
        h.pop("elevation", None)
    pkg.setdefault("truth", {})["source"] = "course_data/truth_sets_v2/%s (hand checked)" % slug
    pkg["truth"]["layers"] = sorted(layers)
    return pkg


def build(slug):
    auto = json.load(open(os.path.join(CD, "packages", slug, "package.json")))
    meta = json.load(open(os.path.join(HERE, "index.json")))["courses"][slug]
    pkg = truth_package(slug, auto, meta["corridor_set"])
    pkg["tee_set"] = meta["corridor_set"]
    json.dump(pkg, open(os.path.join(HERE, slug, "package.json"), "w"))
    print(slug, "->", os.path.join(HERE, slug, "package.json"))


if __name__ == "__main__":
    if sys.argv[1:2] == ["list"]:
        for s, m in available().items():
            print(s, m)
    elif sys.argv[1:2] == ["build"]:
        for s in sys.argv[2:]:
            build(s)
