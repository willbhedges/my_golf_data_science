"""The shared routing / structure validation set: which courses, which split, where the cached inputs live (offline).

  python course_data/generalize/validation_set.py      -> course_data/generalize/validation_set.json

Every course of sample.json whose OSM golf=hole ways give >= 9 numbered holes (the hidden truth) is listed with
its split:
  test   the 32 held-out courses of `sample.py holdout` (8 per Census region): never used to tune anything -
         report them only, once per method version
  train  everything else with truth (the 32 holdout train courses + the 19 earlier validation / full courses)
Cached inputs per course (committed under course_data/generalize/courses/<slug>/, written by run_course.py on
GitHub Actions; ODbL for the OSM file):
  osm_golf.geojson  OSM golf / building / parking / cart-path features of the course. The truth is its golf=hole
                    ways: drop them and every `ref` tag before inference (routing.inputs_from_fc(hide_holes=True))
  segment.geojson   NAIP segment-model greens / tees / fairways (p, area_m2)
  pads.json         lidar flat-pad tee candidates
  scorecard.json    web cards found (normalised, scorecard/1) - `card` below says whether one exists
  course.json       resolve output (boundary)
Truth: routing.truth_from_fc(osm_golf) (refs 1..18), scored with routing.score (green within 20 yds, tee within
40 yds of the first 60 % of the true line).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(os.path.dirname(HERE), "platform")]


def build():
    import routing as R
    smp = json.load(open(os.path.join(HERE, "sample.json")))
    rows = []
    for c in smp["courses"]:
        d = os.path.join(HERE, "courses", c["slug"])
        p = os.path.join(d, "osm_golf.geojson")
        row = dict(slug=c["slug"], name=c["name"], state=c["state"], osm=c["osm"], tier=c["tier"],
                   region=c.get("region"), split=c.get("split"), dir=os.path.relpath(d, os.path.dirname(os.path.dirname(HERE))))
        if not os.path.exists(p):
            if c.get("split"):
                rows.append(dict(row, status="pending (no Actions run yet)"))
            continue
        fc = json.load(open(p))
        truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
        if len(truth) < 9:
            continue
        sc = json.load(open(os.path.join(d, "scorecard.json"))) if os.path.exists(os.path.join(d, "scorecard.json")) else {}
        files = {k: os.path.exists(os.path.join(d, f)) for k, f in (("osm", "osm_golf.geojson"), ("segment", "segment.geojson"),
                                                                    ("pads", "pads.json"), ("course", "course.json"))}
        row.update(status="ok", split=row["split"] or "train", truth_holes=len(truth),
                   card=bool(sc.get("cards")), card_source=sc.get("chosen"), files=files,
                   cart_paths=sum(1 for f in fc["features"] if f["geometry"]["type"] == "LineString"
                                  and f["properties"].get("golf") != "hole"))
        rows.append(row)
    out = dict(schema="validation_set/1", built_from="sample.json (seed %s) + courses/" % smp.get("seed"),
               doc=__doc__.strip().split("\n\n", 1)[1], n=len(rows),
               splits={s: sum(r.get("split") == s and r["status"] == "ok" for r in rows) for s in ("train", "test")},
               courses=rows)
    json.dump(out, open(os.path.join(HERE, "validation_set.json"), "w"), indent=1)
    print(out["splits"], sum(r["status"] != "ok" for r in rows), "pending")
    return out


def load(split=None, ready=True):
    """[row] of validation_set.json, optionally one split; ready=True keeps rows whose inputs exist."""
    vs = json.load(open(os.path.join(HERE, "validation_set.json")))
    return [r for r in vs["courses"] if (split is None or r.get("split") == split) and (not ready or r["status"] == "ok")]


if __name__ == "__main__":
    build()
