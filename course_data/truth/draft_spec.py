"""Draft a holes_spec.json (build_holes_truth.py) from OSM golf=hole lines + the routing map's features.json, to be
checked and corrected by hand on the map / hole sheets.

  python3 course_data/truth/draft_spec.py --slug hot_springs_arlington [--card card.json] [--pad-radius 70]

Per OSM hole (ref 1-18): green = the G feature nearest the line's last point (within 30 yds, else the line end),
line = the OSM line (first point = the tee area, inner points = corners), pads = every T feature within
`pad-radius` yds of the line's first 35%. card.json: {"source", "par": [...], "sets": {name: [18 yds]}}.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path.insert(0, os.path.join(CD, "imagery"))
import render as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--osm-slug")
    ap.add_argument("--card")
    ap.add_argument("--pad-radius", type=float, default=70.0)
    ap.add_argument("--package-lines", action="store_true", help="use the package hole lines where OSM has none")
    a = ap.parse_args()
    fpath = os.path.join(HERE, a.slug, "map", "features.json")
    F = json.load(open(fpath))["features"]
    fc = json.load(open(os.path.join(CD, "packages", a.osm_slug or a.slug, "raw", "osm.geojson")))
    holes = {}
    for f in fc["features"]:
        p = f["properties"]
        if p.get("golf") == "hole" and f["geometry"]["type"] == "LineString" and str(p.get("ref", "")).isdigit():
            holes[str(p["ref"])] = (np.asarray(f["geometry"]["coordinates"], float)[:, :2], p.get("par"))
    if a.package_lines:
        # holes OSM has no way for: the package's routed line (checked on the routing map before use)
        pkg = json.load(open(os.path.join(CD, "packages", a.osm_slug or a.slug, "package.json")))
        for ref, h in pkg["holes"].items():
            if ref not in holes and h.get("hole_line_ll"):
                holes[ref] = (np.asarray(h["hole_line_ll"], float)[:, :2], h.get("par"))
    spec = dict(source="draft_spec.py from OSM golf=hole lines (to be checked by hand)",
                features=os.path.relpath(fpath, ROOT), holes={})
    if a.card:
        spec["card"] = json.load(open(a.card))
    G = {k: v for k, v in F.items() if v["kind"] == "green"}
    T = {k: v for k, v in F.items() if v["kind"] == "tee"}
    for ref, (line, par) in sorted(holes.items(), key=lambda kv: int(kv[0])):
        fr = R.Frame(list(line[0]), list(line[-1]), ppy=1.0, proj="utm")
        end = fr.ll_to_yds([line[-1]])[0]
        gk = min(G, key=lambda k: np.linalg.norm(fr.ll_to_yds([G[k]["center_ll"]])[0] - end)) if G else None
        gd = float(np.linalg.norm(fr.ll_to_yds([G[gk]["center_ll"]])[0] - end)) if gk else 1e9
        xy = fr.ll_to_yds(line)
        seg = np.cumsum(np.r_[0, np.linalg.norm(np.diff(xy, axis=0), axis=1)])
        head = np.array([np.interp(t, seg, xy[:, 0]) for t in np.linspace(0, seg[-1] * 0.35, 12)])
        head = np.c_[head, [np.interp(t, seg, xy[:, 1]) for t in np.linspace(0, seg[-1] * 0.35, 12)]]
        pads = [k for k, v in T.items()
                if np.min(np.linalg.norm(head - fr.ll_to_yds([v["center_ll"]])[0], axis=1)) <= a.pad_radius]
        spec["holes"][ref] = dict(green=gk if gd <= 30 else [round(float(v), 7) for v in line[-1]],
                                  line=[[round(float(x), 7), round(float(y), 7)] for x, y in line[:-1]],
                                  pads=pads, osm_par=par, note="")
        print(ref, par, "green", gk, f"{gd:.0f}yd", "pads", pads, f"len {seg[-1]:.0f}")
    out = os.path.join(HERE, a.slug, "holes_spec.json")
    json.dump(spec, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
