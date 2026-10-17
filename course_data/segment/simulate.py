"""Simulate a poorly mapped course: delete OSM fairways + bunkers on half the holes, restore with the segment
gap-fill, and measure how club picks change (product/plan.py quick on Actions).

    python3 course_data/segment/simulate.py build   [--slug veenker] [--holes odd]   # light: packages
    python3 course_data/segment/simulate.py compare [--slug veenker] [--holes odd] | --dir <sim folder>

build writes course_data/segment/sim_<slug>[_even]/{full,degraded,filled}/package.json:
  full      the platform package as built (OSM + vision)
  degraded  every OSM fairway / bunker way "owned" by a chosen hole (its centroid is nearest that hole's
            line) removed from every hole's zones_ll, then platform reframe()
  filled    degraded + gapfill.segment_gapfill (U-Net fairway / bunker, NIR water; only where OSM lacks)
plus geometry.json: area of the deleted OSM fairway / sand and how much of it the gap-fill restored.
compare reads <variant>/out/decision.json (+ full_repeat for the run-to-run noise of quick mode) and
writes course_data/segment/sim_<slug>/sim.{json,md}.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import gapfill as G  # noqa: E402

VARIANTS = ("full", "full_repeat", "degraded", "filled")


def owners(pkg, proj, slug):
    """OSM fairway / bunker features of raw/osm.geojson -> ({(osm_id, lie): hole ref}, {(osm_id, lie): geom_m}),
    the owner being the hole whose line is nearest the feature's centroid."""
    from shapely.geometry import LineString, shape
    lines = {k: proj.fwd(LineString(h["hole_line_ll"])) for k, h in pkg["holes"].items() if h.get("hole_line_ll")}
    fc = json.load(open(os.path.join(CD, "packages", slug, "raw", "osm.geojson")))
    own, geom = {}, {}
    for f in fc["features"]:
        lie = {"fairway": "fairway", "bunker": "sand"}.get(f["properties"].get("golf"))
        if not lie or f["geometry"]["type"] not in ("Polygon", "MultiPolygon"):
            continue
        g = proj.fwd(shape(f["geometry"]))
        g = g if g.is_valid else g.buffer(0)
        key = (f"{f['properties'].get('osm_type')}/{f['properties'].get('osm_id')}", lie)
        geom[key] = g
        own[key] = min(lines, key=lambda k: lines[k].distance(g.centroid))
    return own, geom


def _dropped(z, proj, dele):
    """True when an OSM fairway/sand zone is (mostly) one of the deleted features."""
    if z.get("lie") not in ("fairway", "sand") or not str(z.get("src", "")).startswith("osm"):
        return False
    g = proj.fwd(G._poly(z["poly"]))
    D = dele.get(z["lie"])
    return D is not None and g.area > 0 and g.intersection(D).area / g.area >= 0.5


def build(slug, holes_rule="odd"):
    from shapely.ops import unary_union
    src_pkg = os.path.join(CD, "packages", slug, "package.json")
    pkg = json.load(open(src_pkg))
    if any(z.get("gapfill") == "segment" for h in pkg["holes"].values() for z in h.get("zones_ll") or []):
        for h in pkg["holes"].values():                 # baseline = OSM (+ vision) only, no segment zones
            h["zones_ll"] = [z for z in h.get("zones_ll") or [] if z.get("gapfill") != "segment"]
            h.pop("tee_candidates_ll", None)
        pkg["stages"]["segment"] = "removed for the simulation baseline"
        pkg = G.platform_module().reframe(pkg)
    refs = sorted(pkg["holes"], key=lambda r: int("".join(c for c in r if c.isdigit()) or 0))
    chosen = [r for i, r in enumerate(refs) if (i % 2 == 0) == (holes_rule == "odd")]
    c = pkg["course"]["center"]
    proj = G.LocalProj(c[0], c[1])
    own, geom = owners(pkg, proj, slug)
    drop = {k for k, ref in own.items() if ref in chosen}
    dele_u = {lie: unary_union([geom[k] for k in drop if k[1] == lie]) for lie in ("fairway", "sand")}
    deg = copy.deepcopy(pkg)
    n_zones = 0
    for h in deg["holes"].values():
        keep = [z for z in h.get("zones_ll") or [] if not _dropped(z, proj, dele_u)]
        n_zones += len(h.get("zones_ll") or []) - len(keep)
        h["zones_ll"] = keep
    deg["stages"]["osm"] = deg["stages"].get("osm", "") + f" | SIMULATED: OSM fairways+bunkers removed on holes {','.join(chosen)}"
    deg = G.platform_module().reframe(deg)
    seg = os.path.join(HERE, slug, "segment.geojson")
    fil = G.segment_gapfill(deg, seg)
    od = sim_dir(slug, holes_rule)
    for name, p in (("full", pkg), ("degraded", deg), ("filled", fil)):
        os.makedirs(os.path.join(od, name), exist_ok=True)
        json.dump(p, open(os.path.join(od, name, "package.json"), "w"))
    os.makedirs(os.path.join(od, "full_repeat"), exist_ok=True)
    # geometry: how much of the deleted OSM area came back, and how much was added that OSM never had
    gm = {}
    added = {}
    for h in fil["holes"].values():
        for z in h.get("zones_ll") or []:
            if z.get("gapfill"):
                added.setdefault(z["lie"], {})[(z["poly"][0][0], z["poly"][0][1], len(z["poly"]))] = proj.fwd(G._poly(z["poly"]))
    for lie in ("fairway", "sand"):
        dele = unary_union([g for (s, l_), g in geom.items() if l_ == lie and (s, l_) in drop])
        kept = unary_union([g for (s, l_), g in geom.items() if l_ == lie and (s, l_) not in drop])
        add = unary_union(list(added.get(lie, {}).values())) if added.get(lie) else None
        inter = dele.intersection(add).area if add is not None else 0.0
        gm[lie] = dict(deleted_ways=sum(1 for k in drop if k[1] == lie), deleted_m2=round(dele.area),
                       added_m2=round(add.area) if add is not None else 0, restored_m2=round(inter),
                       recall=round(inter / dele.area, 3) if dele.area else None,
                       precision=round(inter / add.area, 3) if add is not None and add.area else None,
                       iou=round(inter / dele.union(add).area, 3) if add is not None else 0.0,
                       added_on_kept_m2=round(add.intersection(kept).area) if add is not None else 0)
    info = dict(slug=slug, chosen_holes=chosen, zone_entries_removed=n_zones, dropped=sorted(f"{s} {l_} -> hole {own[(s, l_)]}" for s, l_ in drop),
                segment_fill=fil.get("segment_fill"), geometry=gm)
    json.dump(info, open(os.path.join(od, "geometry.json"), "w"), indent=1)
    for v in VARIANTS:
        json.dump({"package": os.path.relpath(os.path.join(od, "full" if v == "full_repeat" else v, "package.json"), ROOT),
                   "tees": pkg.get("tee_set"), "mode": "quick", "out": os.path.relpath(os.path.join(od, v, "out"), ROOT)},
                  open(os.path.join(od, v, "plan_request.json"), "w"), indent=1)
    print(json.dumps(info, indent=1)[:3000])
    return info


def sim_dir(slug, holes_rule="odd"):
    return os.path.join(HERE, f"sim_{slug}" + ("" if holes_rule == "odd" else f"_{holes_rule}"))


def compare(od):
    info = json.load(open(os.path.join(od, "geometry.json")))
    chosen = set(info["chosen_holes"])
    dec = {}
    for v in VARIANTS:
        p = os.path.join(od, v, "out", "decision.json")
        if os.path.exists(p):
            dec[v] = json.load(open(p))
    if "full" not in dec:
        sys.exit("no full/out/decision.json yet")
    base = dec["full"]
    rows, summ = [], {}
    for v, d in dec.items():
        if v == "full":
            continue
        for grp, keys in (("degraded holes", [k for k in base if k in chosen]),
                          ("other holes", [k for k in base if k not in chosen])):
            same = [k for k in keys if k in d and d[k]["pick"] == base[k]["pick"]]
            aim = [abs(d[k]["aim"] - base[k]["aim"]) for k in keys if k in d]
            dev = [d[k]["clubs"][base[k]["pick"]]["ev"] - d[k]["clubs"][d[k]["pick"]]["ev"]
                   for k in keys if k in d and base[k]["pick"] in d[k]["clubs"]]
            fw = [abs(d[k]["clubs"][d[k]["pick"]]["share"].get("fairway", 0)
                      - base[k]["clubs"][base[k]["pick"]]["share"].get("fairway", 0)) for k in keys if k in d]
            evd = [abs(d[k]["ev"] - base[k]["ev"]) for k in keys if k in d]
            summ[(v, grp)] = dict(n=len(keys), same_club=len(same),
                                  mean_abs_fairway_share_err=round(sum(fw) / max(len(fw), 1), 3),
                                  mean_abs_ev_err=round(sum(evd) / max(len(evd), 1), 3),
                                  aim_within_5=sum(a <= 5 for a in aim),
                                  mean_abs_aim_change=round(sum(aim) / max(len(aim), 1), 1),
                                  mean_ev_gap=round(sum(dev) / max(len(dev), 1), 3))
    for k in base:
        r = dict(hole=k, is_degraded=k in chosen, full=f"{base[k]['pick']} {base[k]['aim']:+.0f}")
        for v, d in dec.items():
            if v != "full" and k in d:
                r[v] = f"{d[k]['pick']} {d[k]['aim']:+.0f}"
                sh = d[k]["clubs"].get(d[k]["pick"], {}).get("share", {})
                r[v + "_fw"] = round(sh.get("fairway", 0), 2)
        r["full_fw"] = round(base[k]["clubs"][base[k]["pick"]]["share"].get("fairway", 0), 2)
        rows.append(r)
    out = dict(info=info, summary={f"{v} | {g}": s for (v, g), s in summ.items()}, rows=rows)
    json.dump(out, open(os.path.join(od, "sim.json"), "w"), indent=1)
    slug = info["slug"]
    L = [f"# Poorly mapped {slug}: OSM fairways + bunkers removed on holes {', '.join(info['chosen_holes'])}", "",
         "Generated by `course_data/segment/simulate.py` (plan.py quick on GitHub Actions). *full* = package as built; "
         "*full_repeat* = the same package re-run (quick-mode noise); *degraded* = OSM fairway/bunker ways of the chosen "
         "holes deleted; *filled* = degraded + segment gap-fill. Agreement is with *full*.", "",
         "## Geometry restored", "", "| lie | OSM ways deleted | deleted m2 | gap-fill added m2 | restored m2 | recall | precision | IoU |",
         "|---|---|---|---|---|---|---|---|"]
    for lie, g in info["geometry"].items():
        L.append(f"| {lie} | {g['deleted_ways']} | {g['deleted_m2']} | {g['added_m2']} | {g['restored_m2']} | "
                 f"{g['recall']} | {g['precision']} | {g['iou']} |")
    L += ["", "## Club picks vs the full package", "",
          "| variant | holes | same club | aim within 5 yds | mean abs aim change (yds) | fairway-share error of the pick | "
          "abs error of the expected strokes | EV cost of the full pick (strokes) |",
          "|---|---|---|---|---|---|---|---|"]
    for (v, g), s in summ.items():
        L.append(f"| {v} | {g} ({s['n']}) | {s['same_club']}/{s['n']} | {s['aim_within_5']}/{s['n']} | "
                 f"{s['mean_abs_aim_change']} | {s['mean_abs_fairway_share_err']} | {s['mean_abs_ev_err']} | {s['mean_ev_gap']} |")
    vs = [v for v in VARIANTS if v != "full" and v in dec]
    L += ["", "## Per hole (club, aim yds; fairway share of the pick)", "",
          "| hole | degraded? | full | " + " | ".join(vs) + " |", "|---|---|---|" + "---|" * len(vs)]
    for r in rows:
        L.append(f"| {r['hole']} | {'yes' if r['is_degraded'] else ''} | {r['full']} ({r['full_fw']}) | "
                 + " | ".join(f"{r.get(v, '-')} ({r.get(v + '_fw', '-')})" for v in vs) + " |")
    open(os.path.join(od, "sim.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "compare"])
    ap.add_argument("--slug", default="veenker")
    ap.add_argument("--holes", default="odd", choices=["odd", "even"])
    ap.add_argument("--dir", help="compare: the sim_* folder (default from --slug/--holes)")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a.slug, a.holes)
    else:
        compare(a.dir or sim_dir(a.slug, a.holes))


if __name__ == "__main__":
    main()
