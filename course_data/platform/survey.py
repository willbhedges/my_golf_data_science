"""OSM golf coverage survey of whole states (Actions only): which courses are well mapped?

  python course_data/platform/survey.py IA MO      -> course_data/packages/_survey/<STATE>.json

For every leisure=golf_course area in the state: golf=hole / tee / green / fairway / bunker counts and
tree / long-grass polygons whose centre falls inside the course bbox, plus a mapping score. Used to pick
demo courses and to tell a golfer up front how much OSM will give them.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import platform_common as pc  # noqa: E402

KEYS = ("hole", "tee", "green", "fairway", "bunker", "water_hazard", "lateral_water_hazard", "rough")


def score(c):
    h = min(c.get("hole", 0) / 18, 1)
    return round(0.4 * h + 0.15 * min(c.get("green", 0) / 18, 1) + 0.15 * min(c.get("fairway", 0) / 14, 1)
                 + 0.1 * min(c.get("bunker", 0) / 20, 1) + 0.1 * min(c.get("tee", 0) / 36, 1)
                 + 0.1 * min(c.get("trees", 0) / 10, 1), 3)


def survey(state):
    iso = "US-" + pc.state_code(state)
    q = f"""[out:json][timeout:300];
    area["ISO3166-2"="{iso}"]["admin_level"="4"]->.st;
    (way["leisure"="golf_course"](area.st); relation["leisure"="golf_course"](area.st););
    out tags center bb;"""
    courses = pc.overpass(q, timeout=320).get("elements", [])
    q2 = f"""[out:json][timeout:600];
    area["ISO3166-2"="{iso}"]["admin_level"="4"]->.st;
    (way["leisure"="golf_course"](area.st); relation["leisure"="golf_course"](area.st);)->.gc;
    .gc map_to_area->.ga;
    (nwr["golf"](area.ga); way["natural"~"wood|scrub|grassland|heath"](area.ga); way["landuse"~"forest|meadow"](area.ga););
    out tags center;"""
    feats = pc.overpass(q2, timeout=620).get("elements", [])
    rows = []
    for c in courses:
        b = c.get("bounds")
        if not b:
            continue
        rows.append(dict(name=c.get("tags", {}).get("name"), osm=f"{c['type']}/{c['id']}",
                         town=c.get("tags", {}).get("addr:city"), bounds=b, counts={}))
    for f in feats:
        ctr = f.get("center") or ({"lat": f["lat"], "lon": f["lon"]} if "lat" in f else None)
        if not ctr:
            continue
        t = f.get("tags", {})
        key = t.get("golf") if t.get("golf") in KEYS else (
            "trees" if t.get("natural") in ("wood", "scrub") or t.get("landuse") == "forest" else
            "long_grass" if t.get("natural") in ("grassland", "heath") or t.get("landuse") == "meadow" else None)
        if not key:
            continue
        for r in rows:
            b = r["bounds"]
            if b["minlat"] <= ctr["lat"] <= b["maxlat"] and b["minlon"] <= ctr["lon"] <= b["maxlon"]:
                r["counts"][key] = r["counts"].get(key, 0) + 1
                break
    for r in rows:
        r["score"] = score(r["counts"])
        r.pop("bounds")
    rows.sort(key=lambda r: -r["score"])
    out = dict(state=pc.state_code(state), surveyed_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               n_courses=len(rows), n_with_holes=sum(1 for r in rows if r["counts"].get("hole")),
               n_18_holes=sum(1 for r in rows if r["counts"].get("hole", 0) >= 18), courses=rows)
    pc.write_json(os.path.join(pc.PACKAGES, "_survey", f"{pc.state_code(state)}.json"), out)
    print(state, out["n_courses"], "courses,", out["n_with_holes"], "with holes,", out["n_18_holes"], "with 18;",
          "top:", [(r["name"], r["town"], r["score"], r["counts"]) for r in rows[:8]])
    return out


if __name__ == "__main__":
    for s in sys.argv[1:]:
        survey(s)
