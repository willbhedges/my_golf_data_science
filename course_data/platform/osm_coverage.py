"""OSM coverage of a course: what is mapped, and how much of each hole's landing zone it explains.

coverage(fc, holes) -> dict, used in package.json["coverage"] and the workflow summary.
  features   counts inside the course boundary (holes, tees, greens, fairways, bunkers, water, trees,
             long grass, OB evidence, buildings, cart paths) + tagging quality (hole par / handicap,
             tee boxes with a colour or ref)
  holes      per hole: green polygon, tee method, landing-zone shares by lie and by source
  summary    holes with a mapped green, with trees/long grass in the landing zone, mean OSM share,
             and a 0-1 `osm_score` (how far OSM alone gets the strategy model)
"""
from collections import Counter

PENAL = ("recovery", "native", "water", "sand", "ob")


def _tags_inside(fc):
    for f in fc["features"]:
        p = f["properties"]
        if p.get("inside_course") is False:
            continue
        yield p, f["geometry"]["type"]


def feature_counts(fc):
    c = Counter()
    for p, gt in _tags_inside(fc):
        g = p.get("golf")
        if g:
            c[f"golf={g}"] += 1
        nat, lu = p.get("natural"), p.get("landuse")
        if nat in ("wood", "scrub") or lu == "forest":
            c["trees_polygons"] += 1
        if nat == "tree_row":
            c["tree_rows"] += 1
        if nat == "tree":
            c["single_trees"] += 1
        if nat in ("grassland", "heath") or lu == "meadow" or g == "native" or \
                str(p.get("rough", p.get("golf:rough", ""))).lower() in ("deep", "native", "long", "high"):
            c["long_grass_polygons"] += 1
        if nat in ("water", "wetland") or g in ("water_hazard", "lateral_water_hazard") or p.get("water"):
            c["water_polygons" if gt != "LineString" else "water_lines"] += 1
        if p.get("waterway") and gt == "LineString":
            c["water_lines"] += 1
        if g == "out_of_bounds":
            c["ob_tagged"] += 1
        if p.get("building"):
            c["buildings"] += 1
        if lu in ("residential", "commercial", "industrial", "retail"):
            c["built_up_landuse"] += 1
        if g == "tee" and any(k in p for k in ("tee", "golf:tee", "colour", "color")):
            c["tees_with_colour"] += 1
        if g == "tee" and "ref" in p:
            c["tees_with_ref"] += 1
        if g == "hole" and str(p.get("par", "")).isdigit():
            c["holes_with_par"] += 1
        if g == "hole" and p.get("handicap"):
            c["holes_with_handicap"] += 1
    return dict(sorted(c.items()))


def coverage(fc, holes):
    """holes: package holes (yard frame) with `confidence` (osm/imagery/inferred) and `landing_lies`."""
    counts = feature_counts(fc)
    per = {}
    for k, h in holes.items():
        c = h.get("confidence", {})
        ll = h.get("landing_lies", {})
        pv = h.get("provenance", {})
        per[k] = dict(par=h["par"], green_polygon=pv.get("green") == "osm_green", tee=pv.get("tee"),
                      landing_osm=c.get("osm"), landing_imagery=c.get("imagery"), landing_inferred=c.get("inferred"),
                      landing_lies=ll, score=c.get("score"), band=c.get("band"))
    long_holes = [k for k, h in holes.items() if h["par"] >= 4]
    trees = [k for k in long_holes if (per[k]["landing_lies"].get("recovery", 0) + per[k]["landing_lies"].get("native", 0)) > 0]
    greens = [k for k in holes if per[k]["green_polygon"]]
    n = max(len(holes), 1)
    mean_osm = sum(per[k]["landing_osm"] or 0 for k in long_holes) / max(len(long_holes), 1)
    expected = 18 if counts.get("golf=hole", 0) > 9 else 9
    osm_score = (0.25 * min(counts.get("golf=hole", 0) / expected, 1) + 0.15 * len(greens) / n
                 + 0.10 * min(counts.get("golf=tee", 0) / (2 * n), 1) + 0.10 * min(counts.get("golf=fairway", 0) / max(len(long_holes), 1), 1)
                 + 0.20 * len(trees) / max(len(long_holes), 1) + 0.20 * mean_osm)
    return dict(features=counts, holes=per,
                summary=dict(holes_built=len(holes), holes_mapped=counts.get("golf=hole", 0),
                             greens_found=len(greens), tee_boxes=counts.get("golf=tee", 0),
                             tees_with_colour=counts.get("tees_with_colour", 0),
                             holes_with_trees_or_long_grass_in_landing_zone=len(trees),
                             of_par4_5=len(long_holes), mean_landing_osm_share=round(mean_osm, 3),
                             mean_confidence=round(sum(per[k]["score"] or 0 for k in per) / n, 3),
                             osm_score=round(osm_score, 3)))
