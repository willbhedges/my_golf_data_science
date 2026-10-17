"""Population coverage of the `osm_feature_ref` source: OSM greens / pins / tees that carry their own hole `ref`.

For each surveyed state (course_data/generalize/surveys), one Overpass query fetches every golf green, pin and
tee with a ref plus every golf=hole way (centres only). Features are assigned to the nearest eligible surveyed
course within 1.5 km. Output: osm_ref_population.json with, per state and overall, the share of courses with
>= 9 numbered greens, split by whether the course already has >= 9 hole lines (the case where this source adds
information the pipeline does not already have).

  python course_data/zero_tap/evidence/osm_ref_population.py
"""
import glob
import json
import math
import os
import re
import sys
import time
import urllib.parse
from collections import Counter, defaultdict

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]


def q(state):
    return f"""[out:json][timeout:900];
area["ISO3166-2"="US-{state}"][admin_level=4]->.st;
(way["golf"="green"]["ref"](area.st); node["golf"="pin"]["ref"](area.st); way["golf"="tee"]["ref"](area.st);
 node["golf"="tee"]["ref"](area.st); way["golf"="hole"](area.st););
out center tags;"""


def fetch(state):
    for attempt in range(4):
        url = OVERPASS[attempt % 2]
        try:
            r = requests.post(url, data={"data": q(state)}, timeout=1000,
                              headers={"User-Agent": "golf-hole-evidence-research (github.com/willbhedges)"})
            if r.status_code == 200:
                return r.json()["elements"]
            print(state, url, r.status_code, file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(state, url, e, file=sys.stderr)
        time.sleep(30 * (attempt + 1))
    return None


def km(a, b):
    kx = 111.32 * math.cos(math.radians((a[1] + b[1]) / 2))
    return math.hypot((a[0] - b[0]) * kx, (a[1] - b[1]) * 110.54)


def main():
    out = dict(schema="osm_ref_population/1", states={}, overall=None)
    tot = Counter()
    for f in sorted(glob.glob(os.path.join(ROOT, "course_data/generalize/surveys/survey_*.json"))):
        sv = json.load(open(f))
        st = sv["state"]
        courses = [c for c in sv["courses"] if c.get("center") and not re.search(r"(?i)disc|mini|foot ?golf|putt", c.get("name") or "")]
        els = fetch(st)
        if els is None:
            out["states"][st] = dict(error="overpass failed")
            continue
        per = defaultdict(Counter)
        for e in els:
            t = e.get("tags", {})
            ctr = e.get("center") or ({"lon": e["lon"], "lat": e["lat"]} if "lon" in e else None)
            if not ctr:
                continue
            p = (ctr["lon"], ctr["lat"])
            best = min(courses, key=lambda c: km(p, c["center"]), default=None)
            if best is None or km(p, best["center"]) > 1.5:
                continue
            kind = t.get("golf")
            if kind == "hole":
                per[best["osm"]]["hole"] += 1
            elif re.match(r"^\s*\d{1,2}\s*$", t.get("ref", "")):
                per[best["osm"]][kind] += 1
        c = Counter(courses=len(courses))
        for co in courses:
            k = per.get(co["osm"], Counter())
            has_lines = k["hole"] >= 9
            has_ref = (k["green"] + k["pin"]) >= 9
            c["with_hole_lines"] += has_lines
            c["with_green_refs"] += has_ref
            c["with_green_refs_no_lines"] += has_ref and not has_lines
            c["without_hole_lines"] += not has_lines
            c["with_tee_refs"] += k["tee"] >= 9
            c[f"tier_{co.get('tier')}"] += 1
            c[f"tier_{co.get('tier')}_green_refs"] += has_ref
        out["states"][st] = dict(c)
        tot.update(c)
        time.sleep(5)
    tot = dict(tot)
    if tot.get("courses"):
        tot["share_with_green_refs"] = round(tot["with_green_refs"] / tot["courses"], 3)
        tot["share_of_unlined_with_green_refs"] = round(
            tot["with_green_refs_no_lines"] / max(1, tot["without_hole_lines"]), 3)
        tot["share_with_hole_lines"] = round(tot["with_hole_lines"] / tot["courses"], 3)
    out["overall"] = tot
    with open(os.path.join(HERE, "osm_ref_population.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(tot, indent=1))


if __name__ == "__main__":
    main()
