"""End-to-end hole inference of the any-course pipeline (platform/stage_select.py) vs the previous package.py
defaults, on the shared validation set (course_data/generalize/validation_set.json), per data tier.

  python course_data/platform/pipeline_eval.py select --shard 0/6 --out s0.json   # TRAIN split: the method grid
  python course_data/platform/pipeline_eval.py final  --shard 0/6 --out f0.json   # TEST split: baseline vs selector
                                                                                    #   + golfer-confirm taps
  python course_data/platform/pipeline_eval.py merge select|final shards*.json      # -> pipeline_select.json /
                                                                                    #    pipeline_eval.json
  python course_data/platform/pipeline_eval.py one <slug> [--tier mapped_card]      # smoke test

Tiers are simulated from each fully mapped course (truth = its OSM golf=hole ways 1..18, routing.score: green
within 20 yds, tee within 40 yds of the first 60 % of the true line). Hole ways and every ref are always hidden.
  mapped_card      OSM greens / tees / fairways kept; card = the web card, else pars + lengths of the hidden ways
  unmapped_card    OSM greens / tees / fairways removed too (only buildings / parking / paths stay); same card
  mapped_nocard    as mapped_card without a card
  unmapped_nocard  as unmapped_card without a card
Methods
  baseline   what package.py did before the selector: card -> routing v2 on OSM (mapped) or segment model + lidar
             (unmapped) inputs; no card -> no routing, geometry/build_holes.infer_holes (holes numbered in OSM green
             order); confirm = routing v2's golf_confirm/1 Session (card tiers), else tap every tee + green
  selector   stage_select.infer_holes (SELECT per tier, fallbacks on error) - the code package.py now runs
  grid       (select only) v2, structure, v2+structure at several lam, with / without perception candidates
The structure solver here uses STRUCTURE_PARAMS=course_data/structure/params_noval.json: refitted without any
validation-set course (the shipped params.json had the generalize courses, test split included, in its dev set).
Perception scenes: models trained on the perception train states; courses in its held-out states (GA KY MN UT ME
WY) are reported apart as `perception-clean`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
os.environ.setdefault("STRUCTURE_PARAMS", os.path.join(CD, "structure", "params_noval.json"))
sys.path[:0] = [HERE, os.path.join(CD, "generalize")]
import numpy as np  # noqa: E402
import routing as R  # noqa: E402
import routing_v2 as R2  # noqa: E402
import stage_select as SS  # noqa: E402

GEN = os.path.join(CD, "generalize")
TIERS = ("mapped_card", "unmapped_card", "mapped_nocard", "unmapped_nocard")
PERC_TEST_STATES = {"GA", "KY", "MN", "UT", "ME", "WY"}
LAMS = (0.25, 0.5, 1.0, 2.0, 4.0)
MAX_TAPS = 30
OUT_SELECT = os.path.join(HERE, "pipeline_select.json")
OUT_FINAL = os.path.join(HERE, "pipeline_eval.json")
OUT_V3 = os.path.join(HERE, "pipeline_eval_v3.json")
V3_TIERS = ("mapped_card", "unmapped_card")


def log(*a):
    print(*a, flush=True)


def rd(p):
    try:
        return json.load(open(p))
    except (OSError, ValueError):
        return None


def courses_of(split):
    vs = json.load(open(os.path.join(GEN, "validation_set.json")))
    return [c for c in vs["courses"] if c["split"] == split]


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
                yards={"osm": [int(round(truth[str(i)]["length_yd"])) if str(i) in truth else None
                               for i in range(1, n + 1)]})


def load(row):
    slug = row["slug"]
    d = os.path.join(GEN, "courses", slug)
    fc, course = rd(os.path.join(d, "osm_golf.geojson")), rd(os.path.join(d, "course.json")) or {}
    if not fc:
        return None
    truth = {k: v for k, v in R.truth_from_fc(fc).items() if int(k) <= 18}
    web = card_of(rd(os.path.join(d, "scorecard.json")))
    card = web or synthetic_card(truth)
    seg = rd(os.path.join(d, "segment.geojson"))
    pads = [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]])
            for p in (rd(os.path.join(d, "pads.json")) or [])]

    def strip(f, drop):
        p = {k: v for k, v in f["properties"].items() if k not in ("ref", "name")} \
            if f["properties"].get("golf") else f["properties"]
        return None if f["properties"].get("golf") in drop else dict(f, properties=p)
    fc_h = dict(fc, features=[g for g in (strip(f, {"hole", "pin"}) for f in fc["features"]) if g])
    fc_u = dict(fc, features=[g for g in (strip(f, {"hole", "pin", "green", "tee", "fairway"}) for f in fc["features"]) if g])
    return dict(slug=slug, state=row.get("state"), truth=truth, card=card, card_kind="web" if web else "osm-derived",
                course=course, seg=seg, pads=pads, fc_h=fc_h, fc_u=fc_u, scene=SS.load_scene(slug),
                perception_clean=row.get("state") in PERC_TEST_STATES)


def variant(c, tier):
    fc = c["fc_h"] if tier.startswith("mapped") else c["fc_u"]
    card = c["card"] if tier.endswith("_card") else None
    return fc, card


def score(res, truth):
    if not res or not res.get("holes"):
        n = len(truth)
        return dict(hole_number_acc=0.0, green_assign_acc=0.0, all_correct=False, flagged=0, wrong=n,
                    wrong_unflagged=n)
    s = R.score(res, truth)
    s.pop("per_hole", None)
    return {k: s[k] for k in ("hole_number_acc", "green_assign_acc", "all_correct", "flagged", "wrong",
                              "wrong_unflagged", "physical_holes_found") if k in s}


# ----------------------------------------------------------------------------- methods
def baseline(c, tier, margins=True):
    """package.py before the selector (route_missing_holes + geometry fallback)."""
    fc, card = variant(c, tier)
    if not card:
        return SS.geometry_holes(fc), dict(method="geometry")
    inp = R.inputs_from_fc(fc, segment=c["seg"], pads=c["pads"], boundary=c["course"].get("boundary"),
                           osm_features=tier.startswith("mapped"))
    res = R2.route(inp, card, fc=fc, boundary=c["course"].get("boundary"), margins=margins)
    res["_inp"] = inp
    return res, dict(method="v2")


def method(c, tier, name, margins=False):
    """Grid entries: v2 | structure | v2s:<lam> | v2p (perception candidates) | v2ps:<lam> | selector."""
    fc, card = variant(c, tier)
    kw = dict(seg=c["seg"], pads=c["pads"], scene=c["scene"], margins=margins)
    if name == "selector":
        return SS.infer_holes(fc, card, c["course"], select=SS.SELECT, **kw)
    if name == "sequence_v3":                     # the selector with SELECT_V3 (falls back like package.py)
        return SS.infer_holes(fc, card, dict(c["course"], slug=c["slug"]), select=dict(SS.SELECT, **SS.SELECT_V3), **kw)
    if name == "baseline":
        return baseline(c, tier, margins)
    persp = name.startswith("v2p")
    if name in ("v2", "v2p"):
        force = dict(method="v2", perception=persp)
    elif name == "structure":
        force = dict(method="structure")
    else:
        force = dict(method="v2+structure", lam=float(name.split(":")[1]), perception=persp)
    prof = SS.profile(fc, card, c["scene"])
    try:
        res, det = SS.run_method(force["method"], fc, card, c["course"], c["seg"], c["pads"], c["scene"], prof,
                                 lam=force.get("lam", 1.0), use_perception=force.get("perception", False),
                                 margins=margins)
        return res, dict(method=force["method"], **det)
    except Exception as e:                                       # noqa: BLE001
        return {}, dict(method=force["method"], error=f"{type(e).__name__}: {e}"[:200])


def grid(tier):
    names = ["baseline", "v2", "structure"] + [f"v2s:{l}" for l in LAMS]
    if tier.startswith("unmapped"):
        names += ["v2p"] + [f"v2ps:{l}" for l in LAMS]
    return names


# ----------------------------------------------------------------------------- golfer confirm (oracle)
def confirm_taps(c, res, card, n_holes, max_taps=MAX_TAPS):
    """Oracle golfer answers platform/confirm.py's questions (policy eig) on the routing's own inputs (struct_prior
    included) until every hole is right. -> dict(taps (None if not within max_taps), wrong_left, stop_*)."""
    import confirm as CF
    inp = res.get("_inp")
    if inp is None:                                   # no routing session (geometry / structure alone)
        return dict(taps=None if len(c["truth"]) else 0, locate_all=2 * len(c["truth"]), session=False)
    fc = c["fc_h"]
    s = CF.Session(inp, card, fc=fc, boundary=c["course"].get("boundary"), n_holes=None if card else n_holes)
    truth = c["truth"]
    stop = None
    while True:
        if s.res.get("cost") is None:
            return dict(taps=None, wrong_left=None, session=True)
        sc = R.score(s.res, truth)
        ok = {r: e["hole_ok"] for r, e in sc["per_hole"].items()}
        wrong = [r for r, v in ok.items() if not v]
        if stop is None and s.done():
            stop = (s.taps, len(wrong))
        if not wrong or s.taps >= max_taps:
            st = stop or (s.taps, len(wrong))
            return dict(taps=s.taps if not wrong else None, wrong_left=len(wrong), stop_rule_taps=st[0],
                        stop_rule_wrong=st[1], session=True)
        qs = s.questions(k=200, policy="eig")
        if not qs:
            return dict(taps=None, wrong_left=len(wrong), session=True)
        q = qs[0]
        r = q["ref"]
        if q["kind"] == "confirm":
            s.answer(dict(question=q["id"], answer="yes" if ok.get(r, True) else "no"))
        else:
            t = truth.get(r)
            h = s.res["holes"][r]
            ans = dict(tee_ll=list(t["tee_ll"]), green_ll=list(t["green_ll"])) if t else \
                dict(tee_ll=h.get("tee_ll"), green_ll=h.get("green_ll"))
            s.answer(dict(question=q["id"], answer=ans))


# ----------------------------------------------------------------------------- runs
def run_select(rows):
    out = []
    for row in rows:
        SS.clear_cache()
        c = load(row)
        if c is None or len(c["truth"]) < 9:
            continue
        rec = dict(slug=c["slug"], state=c["state"], card_kind=c["card_kind"], scene=c["scene"] is not None,
                   perception_clean=c["perception_clean"], tiers={})
        for tier in TIERS:
            rec["tiers"][tier] = {}
            for name in grid(tier):
                t0 = time.time()
                res, det = method(c, tier, name, margins=False)
                s = score(res, c["truth"])
                s.update(seconds=round(time.time() - t0, 1), **{k: v for k, v in det.items() if k in ("method", "error")})
                rec["tiers"][tier][name] = s
            log(c["slug"], tier, {k: v["hole_number_acc"] for k, v in rec["tiers"][tier].items()})
        out.append(rec)
    return out


def run_final(rows, confirm=True):
    out = []
    for row in rows:
        SS.clear_cache()
        c = load(row)
        if c is None or len(c["truth"]) < 9:
            continue
        rec = dict(slug=c["slug"], state=c["state"], card_kind=c["card_kind"], scene=c["scene"] is not None,
                   perception_clean=c["perception_clean"], n_true=len(c["truth"]), tiers={})
        for tier in TIERS:
            fc, card = variant(c, tier)
            rec["tiers"][tier] = {}
            for name in ("baseline", "selector", "v2", "structure"):
                t0 = time.time()
                res, det = method(c, tier, name, margins=name in ("baseline", "selector"))
                s = score(res, c["truth"])
                s.update(seconds=round(time.time() - t0, 1),
                         **{k: v for k, v in det.items() if k in ("method", "error", "tier", "fallbacks", "lam",
                                                                   "router_inputs", "structure_input")})
                if confirm and name in ("baseline", "selector"):
                    t1 = time.time()
                    try:
                        s["confirm"] = confirm_taps(c, res, card, SS.profile(fc, card, c["scene"])["n_holes"])
                    except Exception as e:                       # noqa: BLE001
                        s["confirm"] = dict(taps=None, error=f"{type(e).__name__}: {e}"[:200])
                    s["confirm"]["seconds"] = round(time.time() - t1, 1)
                rec["tiers"][tier][name] = s
            log(c["slug"], tier, {k: (v["hole_number_acc"], (v.get("confirm") or {}).get("taps"))
                                  for k, v in rec["tiers"][tier].items()})
        out.append(rec)
    return out


def run_v3(rows):
    """TEST split, card tiers: the current selector (SELECT: v2 + structure prior) vs sequence_v3 (SELECT_V3:
    formation-v2 pairs + sequence solver v3, with the selector's fallbacks). No confirm: sequence_v3's golfer
    confirm session is the same v2 + structure session, so its taps equal the selector's."""
    out = []
    for row in rows:
        SS.clear_cache()
        c = load(row)
        if c is None or len(c["truth"]) < 9:
            continue
        rec = dict(slug=c["slug"], state=c["state"], card_kind=c["card_kind"], scene=c["scene"] is not None,
                   perception_clean=c["perception_clean"], n_true=len(c["truth"]), tiers={})
        for tier in V3_TIERS:
            rec["tiers"][tier] = {}
            for name in ("selector", "sequence_v3"):
                t0 = time.time()
                try:
                    res, det = method(c, tier, name, margins=False)
                except Exception as e:                           # noqa: BLE001
                    res, det = {}, dict(error=f"{type(e).__name__}: {e}"[:200])
                s = score(res, c["truth"])
                s.update(seconds=round(time.time() - t0, 1),
                         **{k: v for k, v in det.items() if k in ("method", "error", "tier", "fallbacks", "lam",
                                                                   "structure_input", "certain", "course_confidence")})
                rec["tiers"][tier][name] = s
            log(c["slug"], tier, {k: (v["hole_number_acc"], v.get("all_correct"), v.get("method"))
                                  for k, v in rec["tiers"][tier].items()})
        out.append(rec)
    return out


# ----------------------------------------------------------------------------- aggregation
def agg_rows(recs, tier, name, subset=None):
    rs = [r for r in recs if (subset is None or subset(r)) and name in r["tiers"].get(tier, {})]
    if not rs:
        return None
    ss = [r["tiers"][tier][name] for r in rs]
    out = dict(n=len(rs), hole_number_acc=round(float(np.mean([s["hole_number_acc"] for s in ss])), 3),
               green_acc=round(float(np.mean([s["green_assign_acc"] for s in ss])), 3),
               all_correct=round(float(np.mean([bool(s["all_correct"]) for s in ss])), 3),
               wrong_per_course=round(float(np.mean([s["wrong"] for s in ss])), 2),
               flags_per_course=round(float(np.mean([s["flagged"] for s in ss])), 2),
               errors=sum(1 for s in ss if s.get("error")))
    cf = [s.get("confirm") for s in ss if s.get("confirm")]
    if cf:
        n_true = [r["n_true"] for r in rs if r["tiers"][tier][name].get("confirm")]
        taps = [(x.get("taps") if x.get("session") else 2 * n) for x, n in zip(cf, n_true)]
        ok = [t for t in taps if t is not None]
        out.update(reach_100=round(len(ok) / len(cf), 3), mean_taps=round(float(np.mean(ok)), 2) if ok else None,
                   median_taps=float(np.median(ok)) if ok else None,
                   # every course counted: a course not done within MAX_TAPS falls back to tapping all its holes
                   mean_taps_all=round(float(np.mean([t if t is not None else 2 * n for t, n in zip(taps, n_true)])), 2),
                   within_4=round(sum(t <= 4 for t in ok) / len(cf), 3), within_8=round(sum(t <= 8 for t in ok) / len(cf), 3),
                   session=sum(1 for x in cf if x.get("session")))
    return out


def merge(kind, paths):
    recs = []
    for p in paths:
        recs += json.load(open(p))["rows"]
    recs.sort(key=lambda r: r["slug"])
    names = sorted({n for r in recs for t in r["tiers"].values() for n in t})
    subsets = {"all": None, "perception-clean": lambda r: r["perception_clean"]}
    summary = {}
    for tier in TIERS:
        for sname, sub in subsets.items():
            for name in names:
                a = agg_rows(recs, tier, name, sub)
                if a:
                    summary.setdefault(tier, {}).setdefault(sname, {})[name] = a
    out = dict(schema="pipeline_eval/1", kind=kind, split="train" if kind == "select" else "test",
               made_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               structure_params=os.path.relpath(os.environ["STRUCTURE_PARAMS"], os.path.dirname(CD)),
               select=SS.SELECT, summary=summary, rows=recs)
    path = OUT_SELECT if kind == "select" else (OUT_V3 if kind == "v3" else OUT_FINAL)
    json.dump(out, open(path, "w"), indent=1, default=float)
    for tier in TIERS:
        for sname in subsets:
            for name, a in sorted(summary.get(tier, {}).get(sname, {}).items()):
                log(tier, sname, name, a)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["select", "final", "v3", "merge", "one"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--out")
    ap.add_argument("--tier")
    ap.add_argument("--no-confirm", action="store_true")
    a = ap.parse_args()
    if a.cmd == "merge":
        return merge(a.args[0], a.args[1:])
    i, n = (int(x) for x in a.shard.split("/"))
    if a.cmd == "one":
        row = next(r for s in ("train", "test") for r in courses_of(s) if r["slug"] == a.args[0])
        SS.clear_cache()
        c = load(row)
        for tier in ([a.tier] if a.tier else TIERS):
            for name in grid(tier) + ["selector"]:
                t0 = time.time()
                res, det = method(c, tier, name)
                log(tier, name, score(res, c["truth"]), {k: v for k, v in det.items() if k != "profile"},
                    round(time.time() - t0, 1), "s")
        return
    rows = courses_of("train" if a.cmd == "select" else "test")[i::n]
    recs = run_select(rows) if a.cmd == "select" else (run_v3(rows) if a.cmd == "v3" else
                                                       run_final(rows, confirm=not a.no_confirm))
    json.dump(dict(kind=a.cmd, shard=a.shard, rows=recs), open(a.out or f"pipeline_{a.cmd}_{i}.json", "w"),
              indent=1, default=float)


if __name__ == "__main__":
    main()
