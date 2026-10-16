"""Place every tee set of a scorecard on the course's OSM geometry.

    python course_data/tees/place_course.py [osm.geojson] [scorecard.json] [out.json]

Defaults are Spirit Hollow's files. Writes, per hole and tee set: lat/lon of the tee, the method
(tee_centroid / tee_axis / lidar_pad / walkback), the OSM tee way used (or the lidar pad), and the check
numbers (OSM line length, tee box extent, measured distance to the green centroid). Prints a per-hole table.

Placement is place_tee.place_course_sets: all sets of a hole assigned together, back to front, measured to
the OSM green centroid along the hole line; lidar flat-pad candidates (lidar_pads.py, `--dem`, default
course_data/imagery/spirit_hollow/dem.tif when it exists) where a set has no OSM box.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from place_tee import Frame, LineOfPlay, place_course_sets  # noqa: E402

def load_osm(path):
    g = json.loads(Path(path).read_text())
    holes, tees, greens = {}, [], []
    for f in g["features"]:
        p, geo = f["properties"], f["geometry"]
        if p.get("golf") == "hole" and geo["type"] == "LineString" and p.get("ref"):
            holes[int(p["ref"])] = dict(line=[(c[1], c[0]) for c in geo["coordinates"]],
                                        par=int(p["par"]) if p.get("par") else None, osm_id=p.get("osm_id"))
        elif p.get("golf") == "tee":
            if geo["type"] == "Polygon":
                tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in geo["coordinates"][0]],
                                 tags={k: v for k, v in p.items() if k not in ("osm_type", "osm_id")}))
            elif geo["type"] == "Point":
                c = geo["coordinates"]
                tees.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0])], tags=p))
        elif p.get("golf") == "green" and geo["type"] == "Polygon":
            greens.append(dict(id=p.get("osm_id"), coords=[(c[1], c[0]) for c in geo["coordinates"][0]]))
    return holes, tees, greens


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--dem=")]
    dem = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--dem=")),
               str(HERE.parent / "imagery" / "spirit_hollow" / "dem.tif"))
    osm = args[0] if len(args) > 0 else HERE.parent / "spirit_hollow" / "osm.geojson"
    card_path = args[1] if len(args) > 1 else HERE / "scorecard.json"
    out = args[2] if len(args) > 2 else HERE / "tee_positions.json"
    card = json.loads(Path(card_path).read_text())
    holes, tees, greens = load_osm(osm)
    sets = card["tee_sets"]
    lines = {str(h): v["line"] for h, v in holes.items()}
    yards = {str(h): {n: s["yards"][h - 1] for n, s in sets.items() if s["yards"][h - 1]} for h in holes}
    pads = []
    if dem and Path(dem).exists():
        import lidar_pads
        pads = lidar_pads.detect_pads(str(dem), greens=greens, lines=lines)
    placed = place_course_sets(lines, tees, yards, greens=greens, pads=pads)
    by_hole = __import__("place_tee").assign_tees_to_holes(lines, tees)
    res = {}
    print(f"{'hole':>4} {'osm':>5} " + " ".join(f"{n[:12]:>16}" for n in sets))
    for h in range(1, 19):
        if h not in holes:
            continue
        hp = placed[str(h)]
        fr = Frame(*holes[h]["line"][0])
        L = LineOfPlay([fr.fwd(*p) for p in holes[h]["line"]]).length
        res[str(h)] = dict(osm_par=holes[h]["par"], card_par=card["par"][h - 1], osm_line_yd=round(L, 1),
                           osm_hole_id=holes[h]["osm_id"], osm_tee_ids=[t["id"] for t in by_hole[str(h)]],
                           green_centroid=hp["green"], sets_without_box=hp["sets_without_box"],
                           tees={n: {k: v for k, v in r.items() if k != "candidates"} for n, r in hp["tees"].items()})
        cells = []
        for n in sets:
            r = hp["tees"].get(n)
            if r is None:
                continue
            tag = {"tee_centroid": "C", "tee_axis": "A", "walkback": "W", "lidar_pad": "L"}[r["method"]]
            err = "" if r["error_yd"] in (None, 0) else f"+{r['error_yd']:.0f}"
            tag += "*" if r.get("borrowed") else ""
            cells.append(f"{yards[str(h)][n]:>4}{tag}{(str(r['tee_id'])[-5:] if r['tee_id'] else '-'):>6}{err:>4}")
        print(f"{h:>4} {L:>5.0f} " + " ".join(f"{c:>16}" for c in cells))
    Path(out).write_text(json.dumps(dict(source_osm=str(Path(osm).name), scorecard=str(Path(card_path).name),
                                         method="place_tee.place_course_sets (joint, ordered back to front, distances "
                                                "to the OSM green centroid; lidar pads where no OSM box)",
                                         lidar_pads=len(pads),
                                         legend=dict(tee_centroid="middle of the matched OSM tee box",
                                                     tee_axis="point on the matched box at the card yardage",
                                                     lidar_pad="point on a DEM-detected tee pad (no OSM box fits)",
                                                     walkback="no box matched: walked back from the green "
                                                              "along the hole line"),
                                         holes=res), indent=1))
    print("C = middle of an OSM tee box, A = on a box at the card yardage, L = on a lidar pad, W = walked back "
          "along the hole line (no box); * = box borrowed from a neighbouring hole; +n = yds outside the box")
    print("wrote", out)


if __name__ == "__main__":
    main()
