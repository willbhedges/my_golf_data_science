"""Experiment: answer the review's items with the Spirit Hollow hand map as the golfer, re-plan, and compare club
agreement with the hand-traced decision (spirit_hollow/output/final_decision.json).

  python3 course_data/product/verify_hand_truth.py [--review <review.json>] [--levels red,amber] [--workers 4]
  (verify.py runs it when its request says "experiment": "hand_truth")

Oracle (course_data/spirit_hollow/hand_zones_ll.json: the hand-checked zones in WGS84; holes 2 and 9 use the "F"
box = Black, as product/compare_golden.py; tees = QA's truth since a06670b: the hand map's tee moved up its line to
the real Black box by spirit_hollow/course.py BLACK_TEE_FORWARD):
  tee     the Black-box tee in the review's frame for that hole: moved (dx, dy) if > 5 yds away, else confirm
  fairway the hand fairway's edge on that side vs ours (median over 10-yd bands): moved (+ = narrower) if > 5 yds
  cut     hand first cut covers >= 300 sq yds beside the fairway in the corridor -> present, else confirm
  hazard  same lie in the hand map, same side of the aim, inside the corridor (150-340 yds, +/-45 of the aim):
          none (< 20% of the auto area) -> "absent", unless other hand trouble (trees / long grass / water)
          covers half of it -> "confirm"; otherwise the median inner-edge offset over 10-yd bands -> "moved" if
          > 5 yds (clamped +/-30), else "confirm"
  gap     hand trouble covers >= 30% of the tested strip -> "present", else "confirm"
  check   not answered (the hand map has no line-of-play truth)
Then apply_answers.apply -> a copy of the package (never the real one), decide.quick_hole on the changed holes.
Answer levels: the red items, red + amber, every tested item. Club agreement before (the same quick plan on the
unmodified package) vs after, against three truths:
  final     spirit_hollow/output/final_decision.json (the published Bayesian pick; QA's scoreboard truth)
  qa_hand   QA's "hand map, quick" (course_data/qa/scoreboard.json truth_cache: course.py with Black boxes
            through the product's quick decision)
  same_plan this plan pipeline on the hand map (hand zones + Black-box tees in the package), i.e. map error only
Ceilings: the same quick plan with the hand map's tee, its zones, or both, on every hand-mapped hole (what
perfect answers to every possible question could reach; the rest of the gap is the hole line, the plan's own
noise and ties).
Writes <review dir>/experiment_hand_truth.json and .md.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import apply_answers as AA                          # noqa: E402
import render as R                                  # noqa: E402
import verify as V                                  # noqa: E402

PK = V.PK

HAND = os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")
GOLDEN = os.path.join(ROOT, "spirit_hollow", "output", "final_decision.json")
TROUBLE = ("recovery", "native", "water")


SH_COURSE = os.path.join(ROOT, "spirit_hollow", "course.py")
QA_SCOREBOARD = os.path.join(CD, "qa", "scoreboard.json")


def black_forward():
    """spirit_hollow/course.py BLACK_TEE_FORWARD (read, not imported: the module has side effects)."""
    import ast
    for line in open(SH_COURSE):
        if line.startswith("BLACK_TEE_FORWARD"):
            return {str(k): float(v) for k, v in ast.literal_eval(line.split("=", 1)[1].strip()).items()}
    return {}


def black_tee(hh, key, fwd=None):
    """The hand map's tee moved up its (screenshot) line to the real Black box."""
    fwd = black_forward() if fwd is None else fwd
    tee = hh.get("tee_ll")
    d = fwd.get(str(key), 0.0)
    if not tee or not d or not hh.get("dot270_ll"):
        return tee
    fr = R.Frame(tee, hh["dot270_ll"], ppy=1.0, tee_px=(0.0, 0.0), proj="enu")
    return [float(v) for v in fr.yds_to_ll([[0.0, -d]])[0]]


def truths(tee_set):
    out = {"final": {k: v["pick"] for k, v in json.load(open(GOLDEN)).items()}}
    try:
        tc = json.load(open(QA_SCOREBOARD))["truth_cache"]["spirit_hollow"]["res"]
        out["qa_hand"] = {k: v["pick"] for k, v in tc.items()}
    except Exception:                                        # noqa: BLE001
        pass
    return out


def hand_key(ref, tee_set, hand):
    box = "B" if tee_set.lower() == "gold" else "F"
    return ref if ref in hand["holes"] else (ref + box if ref + box in hand["holes"] else None)


def _hand_polys(hh, fr, lies, clip=None):
    """Union of the hand map's effective area of `lies` (later zones win, as tee_strategy.lie_at), clipped."""
    eff = {}
    for z in hh.get("zones") or []:
        lie = PK.LIE_MAP.get(z.get("lie"), z.get("lie"))
        if len(z.get("poly_ll") or []) < 3:
            continue
        try:
            p = V.shapely_poly(V.to_yd(fr, z["poly_ll"]))
        except Exception:                                    # noqa: BLE001
            continue
        if clip is not None:
            p = p.intersection(clip.buffer(5))
        if p.is_empty:
            continue
        for k in list(eff):
            if k != lie:
                eff[k] = eff[k].difference(p)
        eff[lie] = eff[lie].union(p) if lie in eff else p
    from shapely.ops import unary_union
    parts = [eff[k] for k in lies if k in eff and not eff[k].is_empty]
    if not parts:
        return None
    u = unary_union(parts)
    return u.intersection(clip) if clip is not None else u


def _band_bounds(g, a0):
    if g is None or g.is_empty:
        return None
    b = g.intersection(V.box(-1e3, 1e3, a0, a0 + 10))
    return None if b.is_empty or b.area < 5 else b.bounds


def _edges(geom, side, bands):
    out = []
    for a0 in bands:
        if geom is None or geom.is_empty:
            out.append(None)
            continue
        if side == "across":
            out.append(None)
            continue
        g = geom.intersection(V.box(-1e3, 1e3, a0, a0 + 10))
        if g.is_empty or g.area < 5:
            out.append(None)
            continue
        minx, _, maxx, _ = g.bounds
        out.append(maxx if side == "left" else minx)
    return out


def oracle(it, hv, hh, fr):
    """Hand-map answer for one review item (or None)."""
    base_aim = hv["base"]["aim"]
    if it["type"] == "tee":
        tee = hv.get("_truth_tee")
        if not tee:
            return None
        x, a = V.to_yd(fr, [tee])[0]
        if np.hypot(x, a) < 5:
            return dict(answer="confirm")
        return dict(answer="moved", dx=round(float(x), 1), dy=round(float(a), 1))
    side = it.get("side")
    corr = V.box(base_aim - V.HALF, base_aim + V.HALF, *V.ALONG)
    if side == "left":
        region = corr.intersection(V.box(base_aim - V.HALF - 1, base_aim, *V.ALONG))
    elif side == "right":
        region = corr.intersection(V.box(base_aim, base_aim + V.HALF + 1, *V.ALONG))
    else:
        region = corr
    if hh.get("footprint_ll"):
        region = region.intersection(V.shapely_poly(V.to_yd(fr, hh["footprint_ll"])))
    if it["type"] == "fairway":
        pkg_h = hv["_pkg_hole"]
        from shapely.ops import unary_union
        auto = unary_union([V.shapely_poly(V.to_yd(fr, pkg_h["zones_ll"][i]["poly"])) for i in it["zone_idx"]])
        hand = _hand_polys(hh, fr, ("fairway",), V.box(base_aim - V.HALF - 30, base_aim + V.HALF + 30, *V.ALONG))
        if hand is None or hand.is_empty:
            return None
        auto = auto.intersection(V.box(base_aim - V.HALF - 30, base_aim + V.HALF + 30, *V.ALONG))
        bands = np.arange(V.ALONG[0], V.ALONG[1], 10.0)
        lo = lambda g, a0: _band_bounds(g, a0)                # noqa: E731
        diffs = []
        for a0 in bands:
            ea, eh = lo(auto, a0), lo(hand, a0)
            if ea is None or eh is None:
                continue
            diffs.append(eh[0] - ea[0] if side == "left" else ea[2] - eh[2])
        if not diffs:
            return None
        d = float(np.median(diffs))
        return dict(answer="confirm") if abs(d) < 5 else dict(answer="moved", shift=round(float(np.clip(d, -30, 30)), 1))
    if it["type"] == "cut":
        cut = _hand_polys(hh, fr, ("first_cut",), V.box(base_aim - V.HALF - 30, base_aim + V.HALF + 30, *V.ALONG))
        a = cut.area if cut is not None and not cut.is_empty else 0.0
        return dict(answer="present" if a >= 300 else "confirm", _area=round(a))
    if it["type"] == "gap":
        strip = V.shapely_poly(it["strip_xa"])
        u = _hand_polys(hh, fr, TROUBLE, strip)
        cov = (u.area / strip.area) if u is not None and not u.is_empty else 0.0
        return dict(answer="present" if cov >= 0.3 else "confirm", _cov=round(cov, 2))
    if it["type"] != "hazard":
        return None
    pkg_h = hv["_pkg_hole"]
    from shapely.ops import unary_union
    auto = unary_union([V.shapely_poly(V.to_yd(fr, pkg_h["zones_ll"][i]["poly"])) for i in it["zone_idx"]]).intersection(region)
    if auto.is_empty or auto.area < 1:
        return None
    hand = _hand_polys(hh, fr, (it["lie"],), region)
    if hand is None or hand.is_empty or hand.area < 0.2 * auto.area:
        other = _hand_polys(hh, fr, TROUBLE, region)
        if other is not None and not other.is_empty and other.intersection(auto).area >= 0.5 * auto.area:
            return dict(answer="confirm", _why="other hand trouble there")
        return dict(answer="absent")
    if side == "across":
        d = auto.bounds[1] - hand.bounds[1]            # toward = closer to the tee
    else:
        bands = np.arange(V.ALONG[0], V.ALONG[1], 10.0)
        ea, eh = _edges(auto, side, bands), _edges(hand, side, bands)
        diffs = [(h_ - a_) if side == "left" else (a_ - h_) for a_, h_ in zip(ea, eh) if a_ is not None and h_ is not None]
        if not diffs:
            return dict(answer="confirm")
        d = float(np.median(diffs))
    if abs(d) < 5:
        return dict(answer="confirm")
    return dict(answer="moved", shift=round(float(np.clip(d, -30, 30)), 1))


def hand_package(pkg, hand, tee_set, tees=True, zones=True):
    """A copy of the package with the hand map's tee (tee_ll) and/or zones on every hand-mapped tee hole."""
    import copy
    new = copy.deepcopy(pkg)
    for ref, h in new["holes"].items():
        hk = hand_key(ref, tee_set, hand)
        if hk is None:
            continue
        hh = hand["holes"][hk]
        if tees and hh.get("tee_ll"):
            ent = AA._tee(h, tee_set)
            tee = [float(v) for v in black_tee(hh, hk)[:2]]
            aim, _ = PK._tee_line_mod().aim_point(tee, h.get("hole_line_ll"), PK._ll(h.get("green_ll")),
                                                  float((ent or {}).get("card_yards") or h.get("length") or 0) or None,
                                                  int(h.get("par") or 4))
            if ent is not None:
                ent.update(tee_ll=tee, aim_ll=aim)
            h["tee_ll"], h["aim_ll"] = tee, aim
        if zones and hh.get("zones"):
            h["zones_ll"] = [dict(lie=z["lie"], poly=z["poly_ll"], src="hand", p=1.0)
                             for z in hh["zones"] if len(z.get("poly_ll") or []) >= 3]
    return new


def agreement_all(picks, tv, tee_set):
    box = "B" if tee_set.lower() == "gold" else "F"
    out = {}
    for name, t in tv.items():
        same, n = 0, 0
        for k, p in picks.items():
            g = t.get(k) or t.get(k + box)
            if g is None:
                continue
            n += 1
            same += p == g
        out[name] = [same, n]
    return out


def run(pkg_path, review, out_dir, levels=None, workers=1, log=print):
    hand = json.load(open(HAND))
    pkg = json.load(open(pkg_path))
    tee_set = review["tee_set"]
    fwd = black_forward()
    exp_dir = os.path.join(out_dir, "experiment_hand_truth")
    os.makedirs(exp_dir, exist_ok=True)
    tv = truths(tee_set)
    refs = [k for k, hv in review["holes"].items() if hv.get("base")]

    def plan(path, which):
        r = AA.replan(path, tee_set, which, workers=workers, log=lambda *a: None)
        return {k: dict(pick=v["pick"], aim=round(v["aim"], 1), tie=bool(v["tie"])) for k, v in r.items()}

    log(f"hand-truth experiment: quick plan on {len(refs)} holes (before, ceilings)")
    before = plan(pkg_path, refs)
    ceilings = {}
    for name, tees, zones in (("hand_tees", True, False), ("hand_zones", False, True), ("hand_all", True, True)):
        npath = os.path.join(exp_dir, f"package_{name}.json")
        with open(npath, "w") as fh:
            json.dump(hand_package(pkg, hand, tee_set, tees=tees, zones=zones), fh, separators=(",", ":"))
        ceilings[name] = plan(npath, refs)
        os.remove(npath)
    tv["same_plan"] = {k: v["pick"] for k, v in ceilings["hand_all"].items()}
    result = dict(tee_set=tee_set, review_built=review["built"], truths=sorted(tv), before=before,
                  before_agree=agreement_all({k: v["pick"] for k, v in before.items()}, tv, tee_set),
                  ceilings={k: dict(picks=v, agree=agreement_all({h: x["pick"] for h, x in v.items()}, tv, tee_set))
                            for k, v in ceilings.items()}, levels={})
    log(f"  before {result['before_agree']}; ceilings " + "; ".join(f"{k} {v['agree']}" for k, v in result["ceilings"].items()))
    lv_defs = levels or (("red",), ("red", "amber"), ("red", "amber", "green"))
    for lv in lv_defs:
        answers, log_ans = [], []
        for it in review["items"]:
            if it["severity"] not in lv or not it.get("tested"):
                continue
            hv = dict(review["holes"].get(it["hole"]) or {})
            hk = hand_key(it["hole"], tee_set, hand)
            if hk is None or not hv.get("frame") or not hv.get("base"):
                continue
            hh = hand["holes"][hk]
            hv["_pkg_hole"] = pkg["holes"][it["hole"]]
            hv["_truth_tee"] = black_tee(hh, hk, fwd)
            fr = R.Frame.from_json(hv["frame"])
            a = oracle(it, hv, hh, fr)
            if a is None:
                log_ans.append(dict(id=it["id"], severity=it["severity"], answer=None, why="no oracle"))
                continue
            ans = dict(id=it["id"], hole=it["hole"], **{k: v for k, v in a.items() if not k.startswith("_")})
            answers.append(ans)
            log_ans.append(dict(ans, severity=it["severity"], **{k[1:]: v for k, v in a.items() if k.startswith("_")}))
        doc = dict(schema="review_answers/1", slug=review["slug"], tee_set=tee_set, review_built=review["built"],
                   answered="oracle:hand_zones_ll+black_boxes", answers=answers)
        name = "_".join(lv) if len(lv) < 3 else "all"
        new, changed, warn = AA.apply(pkg, review, doc, log=log)
        after = dict(before)
        if changed:
            npath = os.path.join(exp_dir, f"package_{name}.json")
            with open(npath, "w") as fh:
                json.dump(new, fh, separators=(",", ":"))
            after.update(plan(npath, list(changed)))
            os.remove(npath)
        with open(os.path.join(exp_dir, f"answers_{name}.json"), "w") as fh:
            json.dump(doc, fh, indent=1)
        ag = agreement_all({k: v["pick"] for k, v in after.items()}, tv, tee_set)
        result["levels"][name] = dict(answers=log_ans, n_answers=len(answers),
                                      n_changing=sum(1 for x in answers if x["answer"] not in ("confirm",)),
                                      changed_holes=sorted(changed), warnings=warn, after=after, agree=ag)
        log(f"  {name}: {len(answers)} answers, changed {sorted(changed)}; agreement {ag}")
    result["truth_picks"] = tv
    with open(os.path.join(out_dir, "experiment_hand_truth.json"), "w") as fh:
        json.dump(result, fh, indent=1, default=float)
    with open(os.path.join(out_dir, "experiment_hand_truth.md"), "w") as fh:
        fh.write(report_md(result))
    return result


def report_md(r):
    T = [t for t in ("final", "qa_hand", "same_plan") if t in r["truths"]]
    names = {"final": "final_decision.json", "qa_hand": "QA hand map, quick", "same_plan": "same plan on the hand map"}
    f = lambda a: " | ".join(f"{a[t][0]}/{a[t][1]}" for t in T)        # noqa: E731
    L = [f"# Hand-map answers vs three truths ({r['tee_set']} tees, Black-box tees)", "",
         "Same club on the tee shots of the hand map (Black: 2F / 9F).", "",
         "| Geometry | answers (changing) | " + " | ".join(names[t] for t in T) + " |",
         "|---|---|" + "---|" * len(T),
         f"| auto package (before) | - | {f(r['before_agree'])} |"]
    for k, v in r["levels"].items():
        lab = "every tested item" if k == "all" else f"the {k.replace('_', ' + ')} items"
        L.append(f"| answer {lab} | {v['n_answers']} ({v['n_changing']}) | {f(v['agree'])} |")
    cn = {"hand_tees": "hand Black-box tees, every hole", "hand_zones": "hand zones, every hole",
          "hand_all": "hand tees + zones, every hole"}
    for k, v in r["ceilings"].items():
        L.append(f"| {cn[k]} | - | {f(v['agree'])} |")
    L += ["", "Per hole (club picks):", "",
          "| Hole | before | " + " | ".join(f"after {k}" for k in r["levels"]) + " | hand all | final | QA hand | ",
          "|---|---|" + "---|" * (len(r["levels"]) + 3)]
    tp = r["truth_picks"]
    for h, b in r["before"].items():
        key = h if h in tp["final"] else h + "F"
        row = [h, b["pick"]] + [v["after"][h]["pick"] for v in r["levels"].values()] + \
              [r["ceilings"]["hand_all"]["picks"][h]["pick"], tp["final"].get(key, "-"), tp.get("qa_hand", {}).get(key, "-")]
        L.append("| " + " | ".join(row) + " |")
    for k, v in r["levels"].items():
        L += ["", f"## Answers: {k.replace('_', ' + ')}", "", "| Item | Sev | Answer |", "|---|---|---|"]
        for x in v["answers"]:
            det = {kk: vv for kk, vv in x.items() if kk in ("dx", "dy", "shift", "cov", "area", "why")}
            L.append(f"| {x['id']} | {x.get('severity', '')} | {x.get('answer') or '-'} {det or ''} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", default=os.path.join(CD, "packages", "spirit_hollow", "out", "review", "review.json"))
    ap.add_argument("--levels", default=None, help="e.g. red or red,amber (default: red; red+amber; all)")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    rv = json.load(open(a.review))
    run(os.path.join(ROOT, rv["package"]), rv, os.path.dirname(a.review),
        levels=[tuple(a.levels.split(","))] if a.levels else None, workers=a.workers)


if __name__ == "__main__":
    main()
