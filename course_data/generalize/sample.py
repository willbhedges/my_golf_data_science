"""Seeded, stratified random sample of US golf courses with their OSM coverage (GitHub Actions: Overpass).

  python course_data/generalize/sample.py states --seed 20261017            -> the seeded state list (offline)
  python course_data/generalize/sample.py survey CA --out work/survey_CA.json  (Actions, one state per job)
  python course_data/generalize/sample.py combine work/survey_*.json --seed 20261017 --per-tier 7
        -> course_data/generalize/sample.json (the sample) + population.json (tier shares per state)

States: three per Census region (Northeast, Midwest, South, West; lower 48 only: NAIP covers them), drawn with
random.Random(seed). Population: every named leisure=golf_course way / relation / node in those states whose
name is not a mini / disc / foot golf, driving range or practice facility, with bbox area >= 12 ha (nodes have
no area and are kept: they are the least mapped courses). OSM golf features (hole, green, tee, fairway, bunker)
are counted per course by centre-in-bbox (the smallest containing bbox wins, so a course inside a bigger one does
not lose its features).

Tiers (`tier`):
  full     >= 18 golf=hole ways, or >= 9 with < 14 greens (a mapped 9-hole course)
  partial  some golf=hole ways but not full, or no hole ways and >= 9 greens
  none     everything else (a boundary, maybe a few greens / bunkers)
Sample: `per_tier` courses per tier, uniformly from the pooled population (random.Random(seed + tier index)).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(CD, "platform")]

REGIONS = {
    "Northeast": ["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"],
    "Midwest": ["IL", "IN", "MI", "OH", "WI", "IA", "KS", "MN", "MO", "NE", "ND", "SD"],
    "South": ["DE", "FL", "GA", "MD", "NC", "SC", "VA", "WV", "AL", "KY", "MS", "TN", "AR", "LA", "OK", "TX"],
    "West": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY", "CA", "OR", "WA"],
}
EXCLUDE = re.compile(r"\b(mini|miniature|minigolf|putt[- ]?putt|putting course|disc|frisbee|foot ?golf|"
                     r"driving range|golf range|practice|range|simulator|topgolf|top golf|drive shack|"
                     r"adventure golf|crazy golf)\b", re.I)
MIN_HA = 12.0
KEYS = ("hole", "green", "tee", "fairway", "bunker")


def states(seed, per_region=3):
    rnd = random.Random(seed)
    out = []
    for reg in sorted(REGIONS):
        out += sorted(rnd.sample(REGIONS[reg], per_region))
    return out


def tier(c):
    h, g = c.get("hole", 0), c.get("green", 0)
    if h >= 18 or (h >= 9 and g < 14):
        return "full"
    if h > 0 or g >= 9:
        return "partial"
    return "none"


def bbox_ha(b):
    if not b:
        return 0.0
    dy = (b["maxlat"] - b["minlat"]) * 111320.0
    dx = (b["maxlon"] - b["minlon"]) * 111320.0 * math.cos(math.radians((b["maxlat"] + b["minlat"]) / 2))
    return dx * dy / 1e4


def survey(state):
    import platform_common as pc
    iso = "US-" + pc.state_code(state)
    q = f"""[out:json][timeout:400];
    area["ISO3166-2"="{iso}"]["admin_level"="4"]->.st;
    nwr["leisure"="golf_course"](area.st);
    out tags center bb;"""
    els = pc.overpass(q, timeout=420).get("elements", [])
    q2 = f"""[out:json][timeout:900];
    area["ISO3166-2"="{iso}"]["admin_level"="4"]->.st;
    nwr["golf"~"^(hole|green|tee|fairway|bunker)$"](area.st);
    out tags center;"""
    feats = pc.overpass(q2, timeout=920).get("elements", [])
    rows = []
    for e in els:
        t = e.get("tags", {})
        b = e.get("bounds")
        c = e.get("center") or ({"lat": e["lat"], "lon": e["lon"]} if "lat" in e else None)
        if not c and b:
            c = {"lat": (b["minlat"] + b["maxlat"]) / 2, "lon": (b["minlon"] + b["maxlon"]) / 2}
        rows.append(dict(name=t.get("name"), osm=f"{e['type']}/{e['id']}", state=pc.state_code(state),
                         center=[round(c["lon"], 6), round(c["lat"], 6)] if c else None,
                         bounds=b, area_ha=round(bbox_ha(b), 1),
                         tags={k: v for k, v in t.items() if k in ("access", "fee", "holes", "golf:course",
                                                                   "operator", "website", "addr:city", "par",
                                                                   "golf", "membership", "club")},
                         counts={}))
    boxed = sorted([r for r in rows if r["bounds"]], key=lambda r: r["area_ha"])
    for f in feats:
        ctr = f.get("center") or ({"lat": f["lat"], "lon": f["lon"]} if "lat" in f else None)
        k = f.get("tags", {}).get("golf")
        if not ctr or k not in KEYS:
            continue
        for r in boxed:                                  # smallest bbox first
            b = r["bounds"]
            if b["minlat"] <= ctr["lat"] <= b["maxlat"] and b["minlon"] <= ctr["lon"] <= b["maxlon"]:
                r["counts"][k] = r["counts"].get(k, 0) + 1
                break
    for r in rows:
        r.pop("bounds")
        r["tier"] = tier(r["counts"])
    return dict(state=pc.state_code(state), surveyed_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                n_elements=len(rows), n_features=len(feats), courses=rows)


def national_counts():
    """US-wide golf=hole ways and leisure=golf_course elements (light count queries)."""
    import platform_common as pc
    out = {}
    for k, sel in (("golf_courses", 'nwr["leisure"="golf_course"]'), ("hole_ways", 'way["golf"="hole"]'),
                   ("greens", 'nwr["golf"="green"]')):
        q = f"""[out:json][timeout:600];
        area["ISO3166-1"="US"]["admin_level"="2"]->.us;
        {sel}(area.us);
        out count;"""
        try:
            el = pc.overpass(q, tries=2, timeout=620).get("elements", [])
            out[k] = int((el[0].get("tags") or {}).get("total", 0)) if el else None
        except Exception as e:                                   # noqa: BLE001
            out[k] = f"failed: {e!r}"[:200]
    return out


def eligible(r):
    nm = r.get("name")
    if not nm or EXCLUDE.search(nm):
        return False
    if (r.get("tags") or {}).get("golf") in ("driving_range", "miniature", "pitch_and_putt"):
        return False
    return r["osm"].startswith("node/") or r["area_ha"] >= MIN_HA


def slug_for(r, used):
    import platform_common as pc
    s = f"{pc.slugify(r['name'])}_{r['state'].lower()}"
    base, i = s, 2
    while s in used:
        s, i = f"{base}_{i}", i + 1
    used.add(s)
    return s


def combine(paths, seed, per_tier, out_dir):
    surveys = [json.load(open(p)) for p in paths]
    pop = [r for s in surveys for r in s["courses"] if eligible(r)]
    # one facility mapped twice (node + area with the same name): keep the area
    areas = {(r["state"], r["name"].lower()) for r in pop if not r["osm"].startswith("node/")}
    pop = [r for r in pop if not (r["osm"].startswith("node/") and (r["state"], r["name"].lower()) in areas)]
    tiers = ("full", "partial", "none")
    by = {t: sorted([r for r in pop if r["tier"] == t], key=lambda r: r["osm"]) for t in tiers}
    used, sample = set(), []
    for i, t in enumerate(tiers):
        rnd = random.Random(seed + i)
        for r in rnd.sample(by[t], min(per_tier, len(by[t]))):
            sample.append(dict(r, slug=slug_for(r, used)))
    per_state = {}
    for s in surveys:
        rs = [r for r in s["courses"] if eligible(r)]
        per_state[s["state"]] = dict(eligible=len(rs), all_elements=s["n_elements"],
                                     **{t: sum(r["tier"] == t for r in rs) for t in tiers})
    popd = dict(seed=seed, states=[s["state"] for s in surveys], built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                n=len(pop), tiers={t: len(by[t]) for t in tiers},
                tier_share={t: round(len(by[t]) / max(len(pop), 1), 4) for t in tiers}, per_state=per_state,
                rule=dict(exclude=EXCLUDE.pattern, min_ha=MIN_HA, tiers="see sample.py docstring"),
                national=next((s.get("national") for s in surveys if s.get("national")), None))
    os.makedirs(out_dir, exist_ok=True)
    json.dump(dict(seed=seed, per_tier=per_tier, n=len(sample), courses=sample), open(os.path.join(out_dir, "sample.json"), "w"), indent=1)
    json.dump(popd, open(os.path.join(out_dir, "population.json"), "w"), indent=1)
    print(json.dumps(popd["tiers"]), popd["tier_share"])
    for r in sample:
        print(r["tier"], r["slug"], r["name"], r["state"], r["osm"], r["counts"])
    return sample, popd


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["states", "survey", "combine"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--seed", type=int, default=20261017)
    ap.add_argument("--per-tier", type=int, default=7)
    ap.add_argument("--out")
    ap.add_argument("--national", action="store_true")
    a = ap.parse_args()
    if a.cmd == "states":
        print(json.dumps(states(a.seed)))
    elif a.cmd == "survey":
        for st in a.args:
            res = survey(st)
            if a.national:
                res["national"] = national_counts()
            out = a.out or os.path.join(HERE, "work", f"survey_{st}.json")
            os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
            json.dump(res, open(out, "w"))
            from collections import Counter
            print(st, res["n_elements"], "courses", Counter(r["tier"] for r in res["courses"] if eligible(r)))
    else:
        combine(a.args, a.seed, a.per_tier, a.out or HERE)


if __name__ == "__main__":
    main()
