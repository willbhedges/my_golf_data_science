"""Build the zero-tap benchmark manifest (benchmark.json) and per-course truth (truth/<slug>.json), offline.

  python course_data/zero_tap/bench_set.py            -> benchmark.json, truth/*.json, prints the counts

Sources, reused as they are (no copies): generalize/validation_set.json courses (generalize/courses/<slug>/:
osm_golf.geojson, scorecard.json, segment.geojson, pads.json, course.json), structure/sets.json courses
(structure/data/<slug>/: osm.geojson.gz, course.json), and this benchmark's own selection.json
(zero_tap/data/<slug>/). Cards / segment / pads fetched later for structure courses live in zero_tap/data/<slug>/.
Perception scenes: perception/scenes/<slug>/scene.json.gz when present.

Split: by state (state_split.json), except the 31 generalize validation-set *test* courses (dev states) which stay
test. A course is in the benchmark (`in_bench`) when its truth is complete (truth.py).
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
sys.path[:0] = [HERE]
import truth as TR  # noqa: E402

MANIFEST = os.path.join(HERE, "benchmark.json")
TRUTH = os.path.join(HERE, "truth")


def rel(p):
    return os.path.relpath(p, ROOT) if p and os.path.exists(p) else None


def first(*ps):
    return next((p for p in ps if p and os.path.exists(p)), None)


def card_of(path):
    if not path or not os.path.exists(path):
        return None, None
    sc = json.load(open(path))
    if not sc.get("cards"):
        return None, None
    ch = sc.get("chosen")
    c = next((c for c in sc["cards"] if c["source"] == ch), sc["cards"][0])
    return c["card"], c["source"]


def region_of(st):
    sys.path.insert(0, os.path.join(CD, "generalize"))
    import sample as S
    return S.region_of(st)


def entries():
    split = json.load(open(os.path.join(HERE, "state_split.json")))["states"]
    out = []
    for c in json.load(open(os.path.join(CD, "generalize", "validation_set.json")))["courses"]:
        d = os.path.join(CD, "generalize", "courses", c["slug"])
        out.append(dict(slug=c["slug"], name=c["name"], state=c["state"], osm=c["osm"], source="generalize",
                        split="test" if c["split"] == "test" else split.get(c["state"], "dev"),
                        legacy_split=c["split"], osm_path=os.path.join(d, "osm_golf.geojson"),
                        course=os.path.join(d, "course.json"), card=os.path.join(d, "scorecard.json"),
                        segment=os.path.join(d, "segment.geojson"), pads=os.path.join(d, "pads.json")))
    for c in json.load(open(os.path.join(CD, "structure", "sets.json")))["courses"]:
        d = os.path.join(CD, "structure", "data", c["slug"])
        z = os.path.join(HERE, "data", c["slug"])
        out.append(dict(slug=c["slug"], name=c["name"], state=c["state"], osm=c["osm"], source="structure",
                        split=split[c["state"]], legacy_split=c["split"], osm_path=os.path.join(d, "osm.geojson.gz"),
                        course=os.path.join(d, "course.json"), card=os.path.join(z, "scorecard.json"),
                        segment=first(os.path.join(z, "segment.geojson.gz")), pads=os.path.join(z, "pads.json")))
    sel = os.path.join(HERE, "selection.json")
    if os.path.exists(sel):
        for c in json.load(open(sel))["courses"]:
            z = os.path.join(HERE, "data", c["slug"])
            out.append(dict(slug=c["slug"], name=c["name"], state=c["state"], osm=c["osm"], source="zero_tap",
                            split=split[c["state"]], legacy_split=None, osm_path=os.path.join(z, "osm.geojson.gz"),
                            course=os.path.join(z, "course.json"), card=os.path.join(z, "scorecard.json"),
                            segment=first(os.path.join(z, "segment.geojson.gz")), pads=os.path.join(z, "pads.json")))
    return out


def build():
    os.makedirs(TRUTH, exist_ok=True)
    rows, seen = [], set()
    for e in entries():
        if e["osm"] in seen:
            continue
        seen.add(e["osm"])
        if not os.path.exists(e["osm_path"]):
            continue
        fc = TR.load_fc(e["osm_path"])
        card, card_src = card_of(e["card"])
        t = TR.extract(fc, e["slug"], card)
        old = os.path.join(TRUTH, e["slug"] + ".json")
        if os.path.exists(old):                                 # keep hand checks across rebuilds
            prev = json.load(open(old))
            for k in ("hand_check", "fixes"):
                if prev.get(k):
                    t[k] = prev[k]
            if prev.get("hand_check", {}).get("verdict") == "bad":
                t["complete"] = False
                t["problems"].append("hand check: OSM truth wrong")
        json.dump(t, open(old, "w"), separators=(",", ":"))
        scene = first(os.path.join(CD, "perception", "scenes", e["slug"], "scene.json.gz"))
        ncard = len(card.get("par") or []) if card else 0
        card_fits = bool(card) and (ncard == t["kind"] or (t["kind"] in (27, 36) and ncard in (9, 18)))
        rows.append(dict(
            slug=e["slug"], name=e["name"], state=e["state"], region=region_of(e["state"]), osm=e["osm"],
            source=e["source"], split=e["split"], legacy_split=e["legacy_split"], kind=t["kind"], n_holes=t["n_holes"],
            in_bench=t["complete"], problems=t["problems"], greens_mapped=t["greens_mapped"],
            tees_mapped=t["tees_mapped"], par_known=t["par_known"],
            card=dict(source=card_src, holes=ncard, fits=card_fits, sets=list((card.get("tee_sets") or {}).keys()),
                      par_total=sum(int(p) for p in (card.get("par") or []) if str(p).isdigit()) or None) if card else None,
            files=dict(osm=rel(e["osm_path"]), course=rel(e["course"]), card=rel(e["card"]) if card else None,
                       segment=rel(e["segment"]), pads=rel(e["pads"]), scene=rel(scene),
                       truth=rel(old)),
            hand_checked=bool(t.get("hand_check"))))
    rows.sort(key=lambda r: (r["split"], r["state"], r["slug"]))
    ib = [r for r in rows if r["in_bench"]]
    summary = dict(
        courses=len(ib), candidates=len(rows),
        by_split=dict(Counter(r["split"] for r in ib)), by_kind=dict(Counter(str(r["kind"]) for r in ib)),
        by_region=dict(Counter(f"{r['region']}/{r['split']}" for r in ib)),
        states=dict(Counter(r["state"] for r in ib)),
        with_web_card=sum(1 for r in ib if r["card"] and r["card"]["fits"]),
        with_segment=sum(1 for r in ib if r["files"]["segment"]), with_scene=sum(1 for r in ib if r["files"]["scene"]),
        excluded=dict(Counter((r["problems"][0].split(":")[0] if r["problems"] else "?") for r in rows if not r["in_bench"])))
    man = dict(schema="zero_tap_benchmark/1", built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               doc="course_data/zero_tap/BENCH.md", summary=summary, courses=rows)
    json.dump(man, open(MANIFEST, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    return man


def load(split=None, in_bench=True):
    rows = json.load(open(MANIFEST))["courses"]
    return [r for r in rows if (not in_bench or r["in_bench"]) and (split is None or r["split"] == split)]


if __name__ == "__main__":
    build()
