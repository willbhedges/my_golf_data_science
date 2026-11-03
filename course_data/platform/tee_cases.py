"""Break the auto build's tee errors on the hand-truth courses into cases (ERROR_BUDGET.md "Tee positions").

    python3 course_data/platform/rebuild_tees_trees.py --set v1 --layers tees --out A1
    python3 course_data/platform/rebuild_tees_trees.py --set v2 --layers tees,trees --out A2
    python3 course_data/platform/error_budget.py --set v1 --auto-dir A1 --configs +tees,-tees --out EB1.json
    python3 course_data/platform/error_budget.py --set v2 --auto-dir A2 --configs +tees,-tees --out EB2.json
    python3 course_data/platform/tee_cases.py --v1 A1 EB1.json --v2 A2 EB2.json [--out cases.json]

Per scored tee shot: the auto tee of the scored set (the package) against the truth tee (error_budget.truth_holes),
the auto config's match / regret, +tees (auto with the truth tee) and -tees (truth with the auto tee). A tee more
than TEE_TOL yds from the truth gets one case, first that applies:
  wrong set mapping / card   the package has no such set, or its card yardage is > TEE_TOL off the truth card's
  review tee snap            the tee came from a review override (package review_tee_point)
  walkback from card         localizer walk-back along the hole line (no pad fits the card)
  lidar / texture pad        an unmapped pad (lidar, texture, segment, scene)
  no OSM hole way            the tee stage could not run (no golf=hole ways): the package tee was kept
  no OSM tee at the truth    the truth tee is more than BOX_YD from every OSM tee box
  box right, point off       the auto tee is on the OSM box that holds the truth tee
  wrong box in the complex   the truth tee is on another OSM box
The truth tee method (truth_sets_v2 tee_method: "pad" / "hand" measured, "estimated" = moved along the line to
the card length, i.e. no visible box) is kept per row: estimated truth tees cannot judge a tee rule.
Reads only the auto packages, the run jsons and the truth files; writes nothing into the build path.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(CD, "tees"))
sys.path.insert(0, HERE)
import error_budget as E  # noqa: E402  (removes HERE from sys.path: import it last)

TEE_TOL = 10.0
BOX_YD = 5.0
PAD_METHODS = ("lidar_pad", "texture_pad", "segment_pad", "scene_pad")


def case_of(err, method, choice="", has_set=True, auto_card=None, truth_card=None, truth_box=None,
            auto_box=None, tee_id=None, stage_ran=True):
    """The case name for one tee (module docstring). truth_box / auto_box: (yds to the nearest OSM box, its id)."""
    m, choice = str(method or ""), str(choice or "")
    if err is None:
        return "no tee"
    if err <= TEE_TOL:
        return "ok"
    if not has_set or (auto_card and truth_card and abs(float(auto_card) - float(truth_card)) > TEE_TOL):
        return "wrong set mapping / card"
    if "review" in m or "review" in choice:
        return "review tee snap"
    if m.startswith("walkback"):
        return "walkback from card"
    if m.startswith(PAD_METHODS):
        return "lidar / texture pad"
    if not stage_ran:
        return "no OSM hole way (package tee kept)"
    if truth_box is None or truth_box[0] > BOX_YD:
        return "no OSM tee at the truth tee"
    if tee_id is not None and str(tee_id) == str(truth_box[1]):
        return "box right, point off"
    if auto_box is not None and auto_box[0] <= 1.0 and str(auto_box[1]) == str(truth_box[1]):
        return "box right, point off"
    return "wrong box in the complex"


def osm_boxes(pkg_dir):
    p = os.path.join(pkg_dir, "raw", "osm.geojson")
    if not os.path.exists(p):
        return None
    out = []
    for f in json.load(open(p))["features"]:
        pr, g = f["properties"], f["geometry"]
        if pr.get("golf") == "tee" and g and g["type"] in ("Polygon", "Point"):
            cs = g["coordinates"][0] if g["type"] == "Polygon" else [g["coordinates"]]
            out.append(dict(id=pr.get("osm_id"), coords=[(c[1], c[0]) for c in cs]))
    return out


def tee_row(cfg, pkg, truth, boxes, row):
    import place_tee as pt
    from shapely.geometry import Point, Polygon
    S, ref = cfg["tees"], row["hole"]
    td = truth[ref]
    has_set = any(k.lower() == S.lower() for k in (pkg["holes"].get(ref, {}).get("tees") or {}))
    pkgp = E.prepare(pkg, S)
    h = pkgp["holes"].get(ref)
    ent = E.tee_entry(h, S, pkgp.get("tee_set")) if h else {}
    a, t = ent.get("tee_ll"), td.get("tee_ll")
    out = dict(method=ent.get("method"), tee_id=ent.get("tee_id"), auto_card=ent.get("card_yards"),
               measured=ent.get("measured_yards"), truth_method=row.get("tee_method"))
    if not a or not t:
        return dict(out, err=None, case="no tee")
    fr = pt.Frame(t[1], t[0])
    ax, tx = fr.fwd(a[1], a[0]), fr.fwd(t[1], t[0])
    err = math.hypot(ax[0] - tx[0], ax[1] - tx[1])
    line = h.get("hole_line_ll") or []
    if len(line) >= 2:                                   # + along = the auto tee nearer the green; + across = right
        p0, p1 = fr.fwd(line[0][1], line[0][0]), fr.fwd(line[1][1], line[1][0])
        n = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1.0
        u = ((p1[0] - p0[0]) / n, (p1[1] - p0[1]) / n)
        d = (ax[0] - tx[0], ax[1] - tx[1])
        out.update(along=round(d[0] * u[0] + d[1] * u[1], 1), across=round(-d[0] * u[1] + d[1] * u[0], 1))
    near_t = near_a = None
    for b in boxes or []:
        ring = [fr.fwd(*c) for c in b["coords"]]
        g = Polygon(ring).buffer(0) if len(ring) >= 3 else Point(ring[0])
        dt, da = g.distance(Point(tx)), g.distance(Point(ax))
        near_t = (dt, b["id"]) if near_t is None or dt < near_t[0] else near_t
        near_a = (da, b["id"]) if near_a is None or da < near_a[0] else near_a
    ty = next((v for k, v in (td.get("yards") or {}).items() if k.lower() == S.lower()), None)
    choice = str(ent.get("tee_choice") or "")
    stage_ran = boxes is not None and ("tee stage" in choice or "rebuild" in choice)
    out.update(err=round(err, 1), truth_card=ty, truth_box=None if near_t is None else [round(near_t[0], 1), near_t[1]],
               case=case_of(err, ent.get("method"), choice, has_set, ent.get("card_yards"), ty, near_t, near_a,
                            ent.get("tee_id"), stage_ran))
    return out


def rows_for(setname, auto_dir, eb_json):
    res = json.load(open(eb_json))
    cfgs = {c["slug"]: c for c in E.SETS[setname]()}
    out = []
    for c in res["courses"]:
        if "rows" not in c or c["slug"] in E.NO_CARD:
            continue
        cfg = cfgs[c["slug"]]
        pkg = json.load(open(os.path.join(auto_dir, c["slug"], "package.json")))
        src = os.path.join(E.ROOT, cfg["package"]) if cfg.get("package") else \
            os.path.join(CD, "packages", c["slug"], "package.json")
        boxes, truth = osm_boxes(os.path.dirname(src)), E.truth_holes(cfg)
        for r in c["rows"]:
            cf = r["configs"]
            x = tee_row(cfg, pkg, truth, boxes, r)
            x.update(slug=c["slug"], hole=r["hole"], set=setname, tie=r["truth"]["tie"],
                     **{f"{k}_{f}": (cf.get(n) or {}).get(f) for k, n in (("auto", "auto"), ("plus", "+tees"),
                                                                          ("minus", "-tees")) for f in ("match", "regret")})
            out.append(x)
    return out


def table(rows):
    cases = {}
    for r in rows:
        cases.setdefault(r["case"], []).append(r)
    lines = ["| case | tees | measured truth | auto misses | fixed by +tees | broken by +tees | regret recovered by +tees | "
             "-tees: truth plans broken | -tees regret |", "|" + "---|" * 9]
    for k, v in sorted(cases.items(), key=lambda kv: (kv[0] == "ok", -len(kv[1]))):
        meas = sum(not str(x["truth_method"] or "").startswith("estimated") for x in v)
        rec = sum((x["auto_regret"] or 0) - (x["plus_regret"] or 0) for x in v)
        lines.append(f"| {k} | {len(v)} | {meas} | {sum(not x['auto_match'] for x in v)} | "
                     f"{sum((not x['auto_match']) and bool(x['plus_match']) for x in v)} | "
                     f"{sum(x['auto_match'] and x['plus_match'] is False for x in v)} | {rec:.3f} | "
                     f"{sum(x['minus_match'] is False for x in v)} | {sum(x['minus_regret'] or 0 for x in v):.3f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1", nargs=2, metavar=("AUTO_DIR", "EB_JSON"))
    ap.add_argument("--v2", nargs=2, metavar=("AUTO_DIR", "EB_JSON"))
    ap.add_argument("--out")
    a = ap.parse_args()
    rows = []
    for s in ("v1", "v2"):
        if getattr(a, s):
            rows += rows_for(s, *getattr(a, s))
    print(table(rows))
    if a.out:
        json.dump(rows, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
