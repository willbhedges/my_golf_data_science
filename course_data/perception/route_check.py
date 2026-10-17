"""End-to-end check: feed the BLIND perceived scenes to the hole router and score hole recognition vs OSM.

    python course_data/perception/route_check.py [--scenes course_data/perception/scenes] [--slugs a b] [--out ...]

For every course with a scene and generalize inputs (course_data/generalize/courses/<slug>/: osm_golf.geojson
= the truth, scorecard.json, segment.geojson, pads.json), runs platform/routing.py (v1 `route`) on
  perception   routing.inputs_from_fc(scene.to_geojson(scene))      (our greens / tees / fairways / clubhouse)
  baseline     routing.inputs_from_fc(osm, segment, pads, hide_holes=True, osm_features=False)
               (= generalize/REPORT.md "model + lidar only (unmapped course)")
with the web scorecard when found, else pars + lengths from the hidden OSM ways (as generalize/report.py), and
without a card. Scored with routing.score. Writes ROUTING.md + routing.json next to REPORT.md.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(CD, "platform"), os.path.join(CD, "generalize"), CD]
GEN = os.path.join(CD, "generalize", "courses")


def rd(p, default=None):
    try:
        return json.load(gzip.open(p) if p.endswith(".gz") else open(p))
    except (OSError, ValueError):
        return default


def card_of(sc):
    if not sc or not sc.get("cards"):
        return None
    ch = sc.get("chosen")
    c = next((c for c in sc["cards"] if c["source"] == ch), sc["cards"][0])
    return c["card"]


def synthetic_card(truth):
    refs = sorted(truth, key=int)
    if len(refs) < 9:
        return None
    n = 18 if max(int(r) for r in refs) > 9 else 9
    return dict(par=[truth.get(str(i), {}).get("par") for i in range(1, n + 1)],
                yards={"osm": [int(round(truth[str(i)]["length_yd"])) if str(i) in truth else None for i in range(1, n + 1)]})


def routing_fc(sc, min_green=0.5, min_complex=0.4):
    """scene -> routing FeatureCollection: hole-kind greens only, tee boxes of confident complexes (incl. virtual)."""
    import scene as SC
    keep_c = {t["id"] for t in sc["tee_complexes"] if (t.get("p") or 0) >= min_complex}
    fc = SC.to_geojson(sc)
    out = []
    for f in fc["features"]:
        p = f["properties"]
        if p["class"] == "green" and (p.get("kind") == "practice" or (p.get("p") or 0) < min_green):
            continue
        if p["class"] == "tee_box" and p.get("complex") not in keep_c:
            continue
        out.append(f)
    return dict(fc, features=out)


def check(slug, scenes):
    import routing as R
    import scene as SC
    d = os.path.join(GEN, slug)
    sc = rd(os.path.join(scenes, slug, "scene.json.gz")) or rd(os.path.join(scenes, slug, "scene.json"))
    osm, course = rd(os.path.join(d, "osm_golf.geojson")), rd(os.path.join(d, "course.json"))
    if not sc or not osm or not course:
        return None
    truth = {k: v for k, v in R.truth_from_fc(osm).items() if int(k) <= 18}
    if len(truth) < 9:
        return None
    web = card_of(rd(os.path.join(d, "scorecard.json")))
    card = web or synthetic_card(truth)
    out = dict(slug=slug, n_true=len(truth), card_kind="web" if web else "osm-derived")
    pins = {"perception": R.inputs_from_fc(routing_fc(sc), boundary=course.get("boundary"))}
    seg = rd(os.path.join(d, "segment.geojson"))
    pads = [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]])
            for p in (rd(os.path.join(d, "pads.json")) or [])]
    if seg:
        try:
            pins["baseline"] = R.inputs_from_fc(osm, segment=seg, pads=pads, boundary=course.get("boundary"),
                                                hide_holes=True, osm_features=False)
        except TypeError:                                         # older routing without osm_features
            pass
    for name, inp in pins.items():
        for cname, cc in (("card", card), ("nocard", None)):
            t0 = time.time()
            res = R.route(inp, cc, margins=cc is not None)
            s = R.score(res, truth)
            s.pop("per_hole", None)
            s["seconds"] = round(time.time() - t0, 1)
            out[f"{name}_{cname}"] = s
    return out


def pool(rows, key):
    rs = [r[key] for r in rows if key in r]
    if not rs:
        return None
    n = sum(r["n_true"] for r in rs)

    def w(k):
        return round(sum(r[k] * r["n_true"] for r in rs if r.get(k) is not None) / max(n, 1), 3)
    return dict(courses=len(rs), holes=n, hole_number_acc=w("hole_number_acc"), green_assign_acc=w("green_assign_acc"),
                physical_holes_found=w("physical_holes_found"),
                all_correct=round(sum(bool(r.get("all_correct")) for r in rs) / len(rs), 3))


def main():
    from train import split_of
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", default=os.path.join(HERE, "scenes"))
    ap.add_argument("--slugs", nargs="*")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    slugs = a.slugs or sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(a.scenes, "*", "eval.json")))
    rows = []
    for s in slugs:
        try:
            r = check(s, a.scenes)
        except Exception as e:                                    # noqa: BLE001
            print(s, "failed", repr(e)[:300], flush=True)
            continue
        if r:
            ev = rd(os.path.join(a.scenes, s, "eval.json"), {}) or {}
            r["state"] = ev.get("state")
            r["split"] = split_of(r["state"])
            rows.append(r)
            print(s, r["split"], {k: (v.get("hole_number_acc"), v.get("physical_holes_found")) for k, v in r.items()
                                  if isinstance(v, dict)}, flush=True)
    P = {sp: {k: pool([r for r in rows if sp == "all" or r["split"] == sp], k)
              for k in ("perception_card", "baseline_card", "perception_nocard", "baseline_nocard")}
         for sp in ("test", "train", "all")}
    json.dump(dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), pooled=P, courses=rows),
              open(os.path.join(a.out, "routing.json"), "w"), indent=1, default=float)
    L = ["# Hole recognition from blind perception (routing v1 on perceived scenes)", "",
         "Generated by `course_data/perception/route_check.py`. Router: `platform/routing.py` `route` (unchanged). "
         "Truth: OSM golf=hole ways (hidden). `perception` = the router's inputs come only from `scene.json` (blind "
         "NAIP + lidar; clubhouse included); `baseline` = the generalize study's *model + lidar only* inputs "
         "(U-Net polygons + lidar pads + OSM clubhouse / buildings). Card = web scorecard, else pars + lengths from the "
         "hidden OSM ways. Test = held-out states (GA KY MN UT ME WY).", "",
         "| split | inputs | card | courses | holes | hole-number acc | green assignment | physical holes found | all holes correct |",
         "|---|---|---|---|---|---|---|---|---|"]
    for sp in ("test", "train", "all"):
        for k in ("perception_card", "baseline_card", "perception_nocard", "baseline_nocard"):
            v = P[sp][k]
            if not v:
                continue
            name, cname = k.split("_")
            L.append(f"| {sp} | {name} | {'yes' if cname == 'card' else 'no'} | {v['courses']} | {v['holes']} | "
                     f"{100 * v['hole_number_acc']:.0f}% | {100 * v['green_assign_acc']:.0f}% | "
                     f"{100 * v['physical_holes_found']:.0f}% | {100 * v['all_correct']:.0f}% |")
    L += ["", "## Per course (card)", "", "| course | st | split | perception hole acc | physical | baseline hole acc | physical |",
          "|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["split"], r.get("state") or "", r["slug"])):
        p, b = r.get("perception_card", {}), r.get("baseline_card", {})
        L.append(f"| {r['slug']} | {r.get('state')} | {r['split']} | {p.get('hole_number_acc')} | {p.get('physical_holes_found')} | "
                 f"{b.get('hole_number_acc', '-')} | {b.get('physical_holes_found', '-')} |")
    open(os.path.join(a.out, "ROUTING.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:20]))


if __name__ == "__main__":
    main()
