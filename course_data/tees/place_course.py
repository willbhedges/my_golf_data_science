"""Place every tee set of a scorecard on the course's OSM geometry.

    python course_data/tees/place_course.py [osm.geojson] [scorecard.json] [out.json]

Defaults are Spirit Hollow's files. Writes, per hole and tee set: lat/lon of the tee, the method
(tee_centroid / tee_axis / walkback), the OSM tee way used, and the check numbers (OSM line
length, tee box extent). Prints a per-hole table.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from place_tee import Frame, LineOfPlay, assign_tees_to_holes, place_tee_sets  # noqa: E402


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
    return holes, tees


def main():
    osm = sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "spirit_hollow" / "osm.geojson"
    card_path = sys.argv[2] if len(sys.argv) > 2 else HERE / "scorecard.json"
    out = sys.argv[3] if len(sys.argv) > 3 else HERE / "tee_positions.json"
    card = json.loads(Path(card_path).read_text())
    holes, tees = load_osm(osm)
    sets = card["tee_sets"]
    res = {}
    by_hole = assign_tees_to_holes({h: v["line"] for h, v in holes.items()}, tees)
    print(f"{'hole':>4} {'osm':>5} " + " ".join(f"{n[:12]:>16}" for n in sets))
    for h in range(1, 19):
        if h not in holes:
            continue
        yds = {n: s["yards"][h - 1] for n, s in sets.items() if s["yards"][h - 1]}
        placed = place_tee_sets(holes[h]["line"], by_hole[h], yds)
        fr = Frame(*holes[h]["line"][0])
        L = LineOfPlay([fr.fwd(*p) for p in holes[h]["line"]]).length
        res[str(h)] = dict(osm_par=holes[h]["par"], card_par=card["par"][h - 1], osm_line_yd=round(L, 1),
                           osm_hole_id=holes[h]["osm_id"], osm_tee_ids=[t["id"] for t in by_hole[h]],
                           tees={n: {k: v for k, v in r.items() if k != "candidates"} for n, r in placed.items()})
        cells = []
        for n, r in placed.items():
            tag = {"tee_centroid": "C", "tee_axis": "A", "walkback": "W"}[r["method"]]
            err = "" if r["error_yd"] in (None, 0) else f"+{r['error_yd']:.0f}"
            cells.append(f"{yds[n]:>4}{tag}{(str(r['tee_id'])[-5:] if r['tee_id'] else '-'):>6}{err:>4}")
        print(f"{h:>4} {L:>5.0f} " + " ".join(f"{c:>16}" for c in cells))
    Path(out).write_text(json.dumps(dict(source_osm=str(Path(osm).name), scorecard=str(Path(card_path).name),
                                         legend=dict(tee_centroid="middle of the matched OSM tee box",
                                                     tee_axis="point on the matched box at the card yardage",
                                                     walkback="no box matched: walked back from the green "
                                                              "along the hole line"),
                                         holes=res), indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
