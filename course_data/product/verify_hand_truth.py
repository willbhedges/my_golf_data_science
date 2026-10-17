"""Experiment: answer the review's items with the Spirit Hollow hand map as the golfer, re-plan, and compare club
agreement with the hand-traced decision (spirit_hollow/output/final_decision.json).

  python3 course_data/product/verify_hand_truth.py [--review <review.json>] [--levels red,amber] [--workers 4]
  (verify.py runs it when its request says "experiment": "hand_truth")

Oracle (course_data/spirit_hollow/hand_zones_ll.json: the hand-checked zones and tee in WGS84; holes 2 and 9 use
the "F" box = Black, as product/compare_golden.py):
  tee     the hand tee in the review's frame for that hole: moved (dx, dy) if > 5 yds away, else confirm
  hazard  same lie in the hand map, same side of the aim, inside the corridor (150-340 yds, +/-45 of the aim):
          none (< 20% of the auto area) -> "absent", unless other hand trouble (trees / long grass / water)
          covers half of it -> "confirm"; otherwise the median inner-edge offset over 10-yd bands -> "moved" if
          > 5 yds (clamped +/-30), else "confirm"
  gap     hand trouble covers >= 30% of the tested strip -> "present", else "confirm"
  check   not answered (the hand map has no line-of-play truth)
Then apply_answers.apply -> a copy of the package (never the real one), decide.quick_hole on the changed holes, and
club agreement before (the same quick plan on the unmodified package, all tee holes) vs after.
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
        tee = hh.get("tee_ll")
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
            tee = [float(v) for v in hh["tee_ll"][:2]]
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


def agreement(picks, golden, tee_set):
    box = "B" if tee_set.lower() == "gold" else "F"
    rows, same, n = [], 0, 0
    for k, p in sorted(picks.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 99):
        g = golden.get(k) or golden.get(k + box)
        if g is None:
            continue
        n += 1
        ok = p["pick"] == g["pick"]
        same += ok
        rows.append(dict(hole=k, auto=p["pick"], aim=round(p["aim"], 1), tie=bool(p.get("tie")), hand=g["pick"],
                         hand_tie=bool(g.get("tie")), same=ok))
    return dict(same=same, n=n, rows=rows)


def run(pkg_path, review, out_dir, levels=("red",), workers=1, log=print):
    hand = json.load(open(HAND))
    golden = json.load(open(GOLDEN))
    pkg = json.load(open(pkg_path))
    tee_set = review["tee_set"]
    exp_dir = os.path.join(out_dir, "experiment_hand_truth")
    os.makedirs(exp_dir, exist_ok=True)
    # before: the quick plan on the unmodified package, every tee hole (same code and seeds as after)
    refs = [k for k, hv in review["holes"].items() if hv.get("base")]
    log(f"hand-truth experiment: quick plan on {len(refs)} holes (before)")
    before = AA.replan(pkg_path, tee_set, refs, workers=workers, log=log)
    result = dict(tee_set=tee_set, review_built=review["built"], levels={})
    result["before"] = agreement({k: dict(pick=r["pick"], aim=r["aim"], tie=r["tie"]) for k, r in before.items()},
                                 golden, tee_set)
    for lv in [tuple(levels)] + ([("red", "amber")] if tuple(levels) == ("red",) else []):
        answers, log_ans = [], []
        for it in review["items"]:
            if it["severity"] not in lv:
                continue
            hv = dict(review["holes"].get(it["hole"]) or {})
            hk = hand_key(it["hole"], tee_set, hand)
            if hk is None or not hv.get("frame") or not hv.get("base"):
                log_ans.append(dict(id=it["id"], answer=None, why="hole not in the hand map"))
                continue
            hv["_pkg_hole"] = pkg["holes"][it["hole"]]
            fr = R.Frame.from_json(hv["frame"])
            a = oracle(it, hv, hand["holes"][hk], fr)
            if a is None:
                log_ans.append(dict(id=it["id"], answer=None, why="no oracle for this item type"))
                continue
            ans = dict(id=it["id"], hole=it["hole"], **{k: v for k, v in a.items() if not k.startswith("_")})
            answers.append(ans)
            log_ans.append(dict(ans, severity=it["severity"], question=it["question"],
                                **{k[1:]: v for k, v in a.items() if k.startswith("_")}))
        doc = dict(schema="review_answers/1", slug=review["slug"], tee_set=tee_set, review_built=review["built"],
                   answered="oracle:hand_zones_ll", answers=answers)
        name = "_".join(lv)
        new, changed, warn = AA.apply(pkg, review, doc, log=log)
        npath = os.path.join(exp_dir, f"package_{name}.json")
        with open(npath, "w") as fh:
            json.dump(new, fh, separators=(",", ":"))
        after_changed = AA.replan(npath, tee_set, list(changed), workers=workers, log=log) if changed else {}
        os.remove(npath)                                    # large; reproducible from the answers
        after = {k: dict(pick=r["pick"], aim=r["aim"], tie=r["tie"]) for k, r in before.items()}
        for k, r in after_changed.items():
            after[k] = dict(pick=r["pick"], aim=r["aim"], tie=r["tie"])
        ag = agreement(after, golden, tee_set)
        with open(os.path.join(exp_dir, f"answers_{name}.json"), "w") as fh:
            json.dump(doc, fh, indent=1)
        result["levels"][name] = dict(answers=log_ans, changed_holes=sorted(changed), warnings=warn, after=ag,
                                      replanned={k: dict(before=dict(pick=before[k]["pick"], aim=round(before[k]["aim"], 1)),
                                                         after=dict(pick=r["pick"], aim=round(r["aim"], 1)))
                                                 for k, r in after_changed.items() if k in before})
        log(f"  {name}: {len(answers)} answers, changed {sorted(changed)}; club agreement "
            f"{result['before']['same']}/{result['before']['n']} -> {ag['same']}/{ag['n']}")
    # ceilings: the hand map's tee and/or zones on every hand-mapped hole (what perfect answers to everything could do)
    result["ceilings"] = {}
    for name, tees, zones in (("hand_tees", True, False), ("hand_zones", False, True), ("hand_all", True, True)):
        new = hand_package(pkg, hand, tee_set, tees=tees, zones=zones)
        npath = os.path.join(exp_dir, f"package_{name}.json")
        with open(npath, "w") as fh:
            json.dump(new, fh, separators=(",", ":"))
        res = AA.replan(npath, tee_set, refs, workers=workers, log=lambda *a: None)
        os.remove(npath)
        ag = agreement({k: dict(pick=r["pick"], aim=r["aim"], tie=r["tie"]) for k, r in res.items()}, golden, tee_set)
        result["ceilings"][name] = ag
        log(f"  ceiling {name}: club agreement {ag['same']}/{ag['n']}")
    with open(os.path.join(out_dir, "experiment_hand_truth.json"), "w") as fh:
        json.dump(result, fh, indent=1, default=float)
    with open(os.path.join(out_dir, "experiment_hand_truth.md"), "w") as fh:
        fh.write(report_md(result))
    return result


def report_md(r):
    b = r["before"]
    L = [f"# Hand-map answers vs the hand-traced decision ({r['tee_set']} tees)", "",
         f"Before (quick plan on the auto package): same club on {b['same']}/{b['n']} tee shots.", ""]
    for name, lv in r["levels"].items():
        a = lv["after"]
        L += [f"## Answering the {name.replace('_', ' + ')} items with the hand map", "",
              f"{len([x for x in lv['answers'] if x.get('answer')])} answers; geometry changed on holes "
              f"{', '.join(lv['changed_holes']) or 'none'}. Same club: **{b['same']}/{b['n']} -> {a['same']}/{a['n']}**.", "",
              "| Item | Sev | Hand-map answer |", "|---|---|---|"]
        for x in lv["answers"]:
            det = {k: v for k, v in x.items() if k in ("dx", "dy", "shift", "cov", "why")}
            L.append(f"| {x['id']} | {x.get('severity', '')} | {x.get('answer') or '-'} {det or ''} |")
        L += ["", "| Hole | Before | After | Hand map |", "|---|---|---|---|"]
        bd = {x["hole"]: x for x in b["rows"]}
        for x in a["rows"]:
            y = bd.get(x["hole"], {})
            L.append(f"| {x['hole']} | {y.get('auto')} {y.get('aim', 0):+.0f}{' (tie)' if y.get('tie') else ''} | "
                     f"{x['auto']} {x['aim']:+.0f}{' (tie)' if x['tie'] else ''} | {x['hand']}{' (tie)' if x['hand_tie'] else ''} |")
        L.append("")
    L += _ceiling_md(r)
    return "\n".join(L) + "\n"


def _ceiling_md(r):
    c = r.get("ceilings") or {}
    if not c:
        return []
    names = {"hand_tees": "hand tees only", "hand_zones": "hand zones only", "hand_all": "hand tees + zones"}
    L = ["## Ceilings: the hand map's geometry on every hole (perfect answers to everything)", "",
         "| Geometry | Same club |", "|---|---|", f"| auto package | {r['before']['same']}/{r['before']['n']} |"]
    L += [f"| {names.get(k, k)} | {v['same']}/{v['n']} |" for k, v in c.items()]
    hd = c.get("hand_all")
    if hd:
        L += ["", "Hand tees + zones, per hole:", "", "| Hole | Pick | Hand map |", "|---|---|---|"]
        L += [f"| {x['hole']} | {x['auto']} {x['aim']:+.0f}{' (tie)' if x['tie'] else ''} | "
              f"{x['hand']}{' (tie)' if x['hand_tie'] else ''} |" for x in hd["rows"]]
    return L + [""]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", default=os.path.join(CD, "packages", "spirit_hollow", "out", "review", "review.json"))
    ap.add_argument("--levels", default="red")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    rv = json.load(open(a.review))
    run(os.path.join(ROOT, rv["package"]), rv, os.path.dirname(a.review), levels=tuple(a.levels.split(",")),
        workers=a.workers)


if __name__ == "__main__":
    main()
