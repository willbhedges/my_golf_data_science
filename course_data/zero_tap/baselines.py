"""Baseline rows for the zero-tap scoreboard: today's methods written as zero_tap_result/1.

  python course_data/zero_tap/baselines.py --method routing_v2 --tier osm_card [--split dev] [--shard 0/6]
  python course_data/zero_tap/baselines.py --method all --shard 0/6          (workflow zero_tap_bench.yml)

Methods (results/<method>/<tier>/<slug>.json):
  routing_v2   course_data/platform/routing_v2.py route() (production entry, facility split). Tiers osm_card /
               nocard: OSM greens + tees + fairways (holes hidden) + segment model + lidar pads when cached;
               unmapped_card / unmapped_nocard: segment model + lidar pads only (+ the OSM file without golf features
               for car parks / buildings / paths). certain = no hole flagged `check`; confidence = posterior mass of
               the best routing (top_p[0]).
  structure    course_data/structure/ solver (scene -> CRF route, exact posterior). osm_card / nocard: the OSM
               scene (holes hidden by scene.py); unmapped_*: the perception agent's blind scene
               (perception/scenes/<slug>/scene.json.gz, course_scene/1) - i.e. the perception baseline.
               certain = every hole confidence >= 0.8; confidence = p_route (else the min hole confidence).
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(CD, "platform"), os.path.join(CD, "structure")]
import bench as B  # noqa: E402

METHODS = {"routing_v2": ("osm_card", "nocard", "unmapped_card", "unmapped_nocard"),
           "structure": ("osm_card", "nocard", "unmapped_card", "unmapped_nocard")}


def _pads(js):
    return [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]]) for p in (js or [])]


def run_routing_v2(x, tier):
    import routing as R
    import routing_v2 as R2
    if tier.startswith("unmapped") and not x["segment"]:
        return None
    inp = R.inputs_from_fc(x["fc"], segment=x["segment"], pads=_pads(x["pads"]),
                           boundary=x["course"].get("boundary"), hide_holes=True,
                           osm_features=not tier.startswith("unmapped"))
    res = R2.route(inp, x["card"], fc=x["fc"], boundary=x["course"].get("boundary"))
    holes = []
    for ref, h in (res.get("holes") or {}).items():
        boxes = [b for b in (h.get("back_tee_ll"),) if b]
        holes.append(dict(number=int(ref), par=h.get("par"), green_ll=h.get("green_ll"), tee_ll=h.get("tee_ll"),
                          tee_boxes_ll=boxes, green_id=h.get("green_id"), tee_id=h.get("tee_id"),
                          confidence=h.get("p_hole"), status=h.get("status")))
    top = res.get("top_p") or [0.0]
    return dict(certain=bool(holes) and res.get("status") == "ok" and res.get("n_check", 1) == 0,
                confidence=float(top[0]), n_holes=res.get("n_holes"), holes=holes,
                extra=dict(status=res.get("status"), n_check=res.get("n_check"), facility_split=res.get("facility_split")))


def run_structure(x, tier):
    import structure as ST
    if tier.startswith("unmapped"):
        if not x["scene"]:
            return None
        res, _ = ST.run(scene_obj=x["scene"], card=x["card"])
    else:
        res, _ = ST.run(fc=x["fc"], course=x["course"], card=x["card"])
    holes = []
    for ref, h in (res.get("holes") or {}).items():
        holes.append(dict(number=int(ref), par=h.get("par"), green_ll=h.get("green_ll"), tee_ll=h.get("tee_ll"),
                          tee_boxes_ll=h.get("tee_boxes_ll") or [], green_id=h.get("green_id"), tee_id=h.get("tee_id"),
                          confidence=h.get("confidence"), status=h.get("status")))
    confs = [h["confidence"] for h in holes if h.get("confidence") is not None]
    conf = res.get("p_route")
    if conf is None:
        conf = min(confs) if confs else 0.0
    return dict(certain=bool(holes) and all(h.get("status") == "ok" for h in holes), confidence=float(conf),
                n_holes=res.get("n_holes"), holes=holes, extra=dict(status=res.get("status"), card_used=res.get("card_used")))


RUN = {"routing_v2": run_routing_v2, "structure": run_structure}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--method", default="all")
    ap.add_argument("--tier", default="all")
    ap.add_argument("--split", default="all")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--slugs", default="")
    ap.add_argument("--out", default=B.RESULTS)
    a = ap.parse_args()
    k, of = (int(v) for v in a.shard.split("/"))
    methods = list(METHODS) if a.method == "all" else a.method.split(",")
    rows = B.courses(None if a.split == "all" else a.split)
    if a.slugs:
        rows = [r for r in rows if r["slug"] in a.slugs.split(",")]
    rows = [r for j, r in enumerate(rows) if j % of == k]
    for r in rows:
        for m in methods:
            for tier in (METHODS[m] if a.tier == "all" else a.tier.split(",")):
                if tier.startswith("unmapped") and not (r["files"].get("segment") or r["files"].get("scene")):
                    continue
                t0 = time.time()
                try:
                    x = B.inputs(r, tier)
                    out = RUN[m](x, tier)
                    if out is None:
                        continue
                except Exception as e:                                # noqa: BLE001
                    traceback.print_exc()
                    out = dict(certain=False, confidence=0.0, holes=[], error=repr(e)[:300])
                    x = dict(card_kind=None)
                out.update(schema="zero_tap_result/1", method=m, tier=tier, slug=r["slug"], card_kind=x.get("card_kind"),
                           version=VERSION.get(m), seconds=round(time.time() - t0, 1))
                B.write_result(out, os.path.join(a.out, m, tier))
                sc = B.score_course(out, B.truth(r["slug"]))
                print(f"{r['slug'][:28]:28s} {m:10s} {tier:15s} N={sc['N']:2d} formed {sc['formed']:2d} num {sc['number']:2d} "
                      f"ok={int(sc['course_ok'])} certain={int(sc['certain'])} conf={sc['confidence']:.3f} "
                      f"{sc['primary']} {out['seconds']}s", flush=True)


def _git_version(path):
    import subprocess
    try:
        return subprocess.check_output(["git", "log", "-1", "--format=%h", "--", path], cwd=CD,
                                       stderr=subprocess.DEVNULL).decode().strip() or None
    except Exception:                                                  # noqa: BLE001
        return None


VERSION = {"routing_v2": _git_version(os.path.join(CD, "platform", "routing_v2.py")),
           "structure": _git_version(os.path.join(CD, "structure", "solver.py"))}

if __name__ == "__main__":
    main()
