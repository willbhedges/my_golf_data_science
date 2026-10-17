"""Generalization report: "pick a random US course - do we know where each hole and green is?" (offline).

  python course_data/generalize/report.py [--plots]   -> course_data/generalize/REPORT.md, results.json
                                                          (+ courses/<slug>/routing.png with --plots)

Reads the sample (sample.json, population.json) and every courses/<slug>/ written by run_course.py on Actions,
re-runs platform/routing.py from the committed inputs (so routing changes need no Actions run) and scores it.

Per course
  found        resolve.py by name + state returns the sampled OSM element (status ok, same element)
  today        the platform package as built now: holes with an OSM hole line, a green polygon (OSM or the
               segment gap-fill), a tee from a box / lidar pad (not a walk-back) - result.json["today"]
  routed       routing.py in production mode (mapped holes are anchors): holes placed, holes flagged `check`
Validation (courses with >= 9 numbered OSM golf=hole ways; the ways and every ref tag are hidden):
  V-osm        inputs = OSM greens / tees / fairways + segment-model + lidar pads (a partially mapped course)
  V-model      inputs = segment-model greens / tees / fairways + lidar pads only (an unmapped course)
  each with the web scorecard when one was found, else a card made from the hidden OSM ways (pars + line
  lengths; marked `card*`), and once with no card at all.
Overall: per-tier success rates weighted by the population's tier shares (population.json):
  (a) today      every card hole has a hole line and a green polygon (tees from a box reported separately)
  (b) routing    full tier: as today; partial / none tiers: P(scorecard found) x P(routing all correct |
                 V-osm resp. V-model, with a card); "after a golfer check": every wrong hole was flagged.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(CD, "platform")]
import routing as R  # noqa: E402

TIERS = ("full", "partial", "none")


def rd(p, default=None):
    try:
        return json.load(open(p))
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


def pads_in(js):
    return [dict(id=p["id"], centroid=p["centroid"], coords=[tuple(c) for c in p["coords"]]) for p in (js or [])]


def validate(d, card, fc, course, seg, pads):
    truth = R.truth_from_fc(fc)
    truth = {k: v for k, v in truth.items() if int(k) <= 18}
    if len(truth) < 9:
        return None
    out = dict(n_true=len(truth))
    used_card, kind = (card, "web") if card else (synthetic_card(truth), "osm-derived")
    out["card_kind"] = kind
    base = geometry_fallback(fc, truth)
    if base:
        out["today_fallback_nocard"] = base
    for name, osm_feats in (("v_osm", True), ("v_model", False)):
        if not osm_feats and not seg:
            continue
        inp = R.inputs_from_fc(fc, segment=seg, pads=pads, boundary=course.get("boundary"), hide_holes=True,
                               osm_features=osm_feats)
        for cname, cc in (("card", used_card), ("nocard", None)):
            res = R.route(inp, cc, margins=cc is not None)
            sc = R.score(res, truth)
            sc.pop("per_hole")
            sc["inputs"] = res.get("inputs")
            out[f"{name}_{cname}"] = sc
            if cname == "card":
                out[f"{name}_res"] = res
    return out


def geometry_fallback(fc, truth):
    """Today's package without hole ways: geometry/build_holes.infer_holes (greedy green -> tee pairing, numbered
    in OSM order), scored like the router."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("gen_bh", os.path.join(CD, "geometry", "build_holes.py"))
        bh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bh)
        fc0 = dict(fc, features=[f for f in fc["features"] if f["properties"].get("golf") != "hole"])
        world = bh.World(fc0)
        holes = {}
        for h in bh.infer_holes(world):
            a, b = bh._ll(world, h["line"][0]), bh._ll(world, h["line"][-1])
            holes[h["props"]["ref"]] = dict(tee_ll=list(a), green_ll=list(b), status="ok",
                                            straight_yd=float(np.hypot(*R.Proj(*a).fwd(*b))))
        sc = R.score(dict(holes=holes), truth)
        sc.pop("per_hole")
        return sc
    except Exception as e:                                       # noqa: BLE001
        print("geometry fallback failed:", repr(e))
        return None


def plot(path, fc, course, res, truth, seg_inp):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    inp = seg_inp
    pr = inp["proj"]
    fig, ax = plt.subplots(figsize=(7, 7))
    for f in inp["fairways"]:
        xy = pr.ring(f["poly"])
        ax.fill(xy[:, 0], xy[:, 1], color="#cfe8c4" if f["src"] == "osm" else "#e4f2dc", zorder=0)
    for g in inp["greens"]:
        x, y = pr.fwd(*g["ll"])
        ax.plot(x, y, "o", color="#1b7f2a" if g["src"] == "osm" else "#7bd389", ms=6)
    for t in inp["tees"]:
        x, y = pr.fwd(*t["ll"])
        ax.plot(x, y, "s", color={"osm": "#222", "segment": "#a23ea8", "lidar": "#e08a00"}[t["src"]], ms=2.5)
    for r, t in (truth or {}).items():
        xy = pr.ring(t["line"])
        ax.plot(xy[:, 0], xy[:, 1], "-", color="#3b6fd8", lw=1.5, alpha=.45)
    for r, h in res["holes"].items():
        if h.get("tee_ll") and h.get("green_ll"):
            a = pr.fwd(*h["tee_ll"])
            b = pr.fwd(*h["green_ll"])
            col = "#c0392b" if h["status"] == "ok" else "#f39c12"
            ax.annotate("", b, a, arrowprops=dict(arrowstyle="->", color=col, lw=1.2))
            ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, r, color=col, fontsize=8, weight="bold")
    if inp.get("clubhouse"):
        x, y = pr.fwd(*inp["clubhouse"][:2])
        ax.plot(x, y, "*", color="gold", ms=14, mec="k")
    ax.set_aspect("equal")
    ax.set_title(f"{course.get('name')} - routed (red ok, orange check); blue = OSM holes", fontsize=8)
    ax.tick_params(labelsize=6)
    fig.savefig(path, dpi=70, bbox_inches="tight")
    plt.close(fig)


def course_row(d, plots=False):
    slug = os.path.basename(d)
    res = rd(os.path.join(d, "result.json"), {}) or {}
    s = res.get("sample", {})
    row = dict(slug=slug, name=s.get("name"), state=s.get("state"), tier=s.get("tier"), osm=s.get("osm"),
               access=(s.get("tags") or {}).get("access"), counts=s.get("counts"), fatal=res.get("fatal"))
    rb = res.get("resolve_by_name") or {}
    row["found"] = bool(rb.get("status") == "ok" and rb.get("same_element"))
    row["resolve_status"] = rb.get("status") or ("error" if "resolve_by_name" in res.get("errors", {}) else None)
    row["resolve_alt"] = None if row["found"] else (rb.get("name") or (rb.get("candidates") or [[None]])[0][0])
    sc = rd(os.path.join(d, "scorecard.json"), {}) or {}
    card = card_of(sc)
    n_card, pars, _ = R.card_holes(card) if card else (None, None, None)
    row.update(scorecard=sc.get("chosen"), card_holes=n_card,
               card_par=sum(p for p in (pars or []) if p) or None)
    osm = (res.get("osm") or {}).get("features", {})
    row.update(osm_holes=osm.get("golf=hole", 0), osm_greens=osm.get("golf=green", 0), osm_tees=osm.get("golf=tee", 0),
               osm_fairways=osm.get("golf=fairway", 0))
    seg = rd(os.path.join(d, "segment.geojson"))
    row["naip"] = (res.get("imagery") or {}).get("year")
    row["seg_greens"] = sum(1 for f in (seg or {}).get("features", []) if f["properties"]["class"] == "green"
                            and f["properties"]["p"] >= 0.6) if seg else None
    row["seg_tees"] = sum(1 for f in (seg or {}).get("features", []) if f["properties"]["class"] == "tee") if seg else None
    pads = rd(os.path.join(d, "pads.json"))
    row["lidar_pads"] = len(pads) if pads is not None else None
    t = res.get("today") or {}
    row["expected"] = n_card or (18 if row["osm_holes"] >= 12 or (row["osm_greens"] or 0) >= 14 else
                                 (9 if row["osm_holes"] >= 5 else 18))
    row.update(today_holes=t.get("holes_built", 0), today_green=t.get("with_green_polygon", 0),
               today_green_seg=t.get("green_segment", 0), today_tee=t.get("with_tee_box", 0),
               today_reason=None if t.get("holes_built") else str(t.get("reason") or (res.get("errors") or {}).get("package_today"))[:120])
    exp = row["expected"]
    # placed correctly today = every card hole has its own numbered OSM golf=hole way and a green polygon (holes the
    # geometry fallback infers from tee / green pairs are numbered in OSM order: ~8 % right, see the baseline row)
    refs = set((res.get("osm") or {}).get("hole_refs") or [])
    row["osm_refs_complete"] = all(str(i) in refs for i in range(1, exp + 1))
    row["today_all"] = bool(row["osm_refs_complete"] and t.get("holes_built", 0) >= exp
                            and t.get("with_green_polygon", 0) >= exp)
    row["today_all_tees"] = bool(row["today_all"] and t.get("with_tee_box", 0) >= exp)
    # routing, production mode, recomputed offline
    fc = rd(os.path.join(d, "osm_golf.geojson"))
    course = rd(os.path.join(d, "course.json"), {}) or {}
    if fc and course.get("status") == "ok":
        P = pads_in(pads)
        inp = R.inputs_from_fc(fc, segment=seg, pads=P, boundary=course.get("boundary"))
        rt = R.route(inp, card, margins=card is not None)
        hs = rt.get("holes", {})
        row.update(routed=sum(1 for h in hs.values() if h.get("green_ll") and h.get("tee_ll")),
                   routed_check=sum(1 for h in hs.values() if h["status"] != "ok"),
                   routed_anchored=sum(1 for h in hs.values() if h.get("anchored")),
                   routed_inputs=rt.get("inputs"), routed_n=rt.get("n_holes"))
        w = res.get("with_routing") or {}
        row.update(pkg_routed_holes=w.get("holes_built"), pkg_routed_green=w.get("with_green_polygon"),
                   pkg_routed_tee=w.get("with_tee_box"))
        v = validate(d, card, fc, course, seg, P)
        if v:
            if plots and v.get("v_osm_res"):
                plot(os.path.join(d, "routing.png"), fc, course, v["v_osm_res"], R.truth_from_fc(fc),
                     R.inputs_from_fc(fc, segment=seg, pads=P, boundary=course.get("boundary"), hide_holes=True))
            for k in [k for k in v if k.endswith("_res")]:
                v.pop(k)
            row["validation"] = v
        elif plots and hs:
            plot(os.path.join(d, "routing.png"), fc, course, rt, R.truth_from_fc(fc), inp)
    return row


def rate(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs), len(xs)) if xs else (None, 0)


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def summarise(rows, pop):
    share = (pop or {}).get("tier_share") or {t: 1 / 3 for t in TIERS}
    by = {t: [r for r in rows if r["tier"] == t and not r.get("fatal")] for t in TIERS}
    vals = [r["validation"] for r in rows if r.get("validation")]
    agg = {}
    for key in ("today_fallback_nocard", "v_osm_card", "v_model_card", "v_osm_nocard", "v_model_nocard"):
        vs = [v[key] for v in vals if key in v]
        if not vs:
            continue
        agg[key] = dict(
            n=len(vs),
            hole_number_acc=round(float(np.mean([x["hole_number_acc"] for x in vs])), 3),
            green_assign_acc=round(float(np.mean([x["green_assign_acc"] for x in vs])), 3),
            physical_holes_found=round(float(np.mean([x["physical_holes_found"] for x in vs])), 3),
            median_length_err_yd=round(float(np.median([x["median_length_err_yd"] for x in vs if x["median_length_err_yd"] is not None] or [np.nan])), 1),
            all_correct=round(float(np.mean([x["all_correct"] for x in vs])), 3),
            correct_after_check=round(float(np.mean([x["wrong_unflagged"] == 0 for x in vs])), 3),
            needs_check=round(float(np.mean([x["flagged"] > 0 for x in vs])), 3),
            mean_flagged=round(float(np.mean([x["flagged"] for x in vs])), 2),
            web_card_share=round(float(np.mean([v.get("card_kind") == "web" for v in vals if key in v])), 3))
    out = dict(tier_share=share, per_tier={}, validation=agg)
    for t in TIERS:
        rs = by[t]
        found, _ = rate([r["found"] for r in rs])
        card, _ = rate([r["scorecard"] is not None for r in rs])
        today, n = rate([r["today_all"] for r in rs])
        naip, _ = rate([r.get("naip") is not None for r in rs])
        out["per_tier"][t] = dict(n=n, found=found, scorecard=card, naip=naip, today_all=today)
    # (a) today
    a = sum(share[t] * (out["per_tier"][t]["today_all"] or 0) for t in TIERS)
    # (b) routing
    vo, vm = agg.get("v_osm_card", {}), agg.get("v_model_card", {})
    b, b_chk, need = 0.0, 0.0, 0.0
    for t in TIERS:
        pt = out["per_tier"][t]
        if t == "full":
            # complete OSM holes count as today; the rest (a missing / duplicated way) are routed around the anchors
            tod = pt["today_all"] or 0
            p_card = pt["scorecard"] or 0
            p_ok = tod + (1 - tod) * p_card * (vo.get("all_correct") or 0)
            p_chk = tod + (1 - tod) * p_card * (vo.get("correct_after_check") or 0)
            p_need = (1 - tod)
        else:
            v = vo if t == "partial" else vm
            p_card = pt["scorecard"] or 0
            p_ok = p_card * (v.get("all_correct") or 0)
            p_chk = p_card * (v.get("correct_after_check") or 0)
            p_need = p_card * (v.get("needs_check") or 0) + (1 - p_card)
        pt.update(routing_all_correct=p_ok, routing_after_check=p_chk, needs_check=p_need)
        b += share[t] * p_ok
        b_chk += share[t] * p_chk
        need += share[t] * p_need
    out["overall"] = dict(today=round(a, 3), routing=round(b, 3), routing_after_golfer_check=round(b_chk, 3),
                          needs_golfer_check=round(need, 3))
    return out


def md(rows, summ, pop, sample):
    L = ["# Any US course: do we know where every hole and green is?", "",
         "Generated by `course_data/generalize/report.py` from the seeded sample (`sample.py`, seed "
         f"{(sample or {}).get('seed')}) and the per-course Actions runs (`run_course.py`, `.github/workflows/generalize.yml`). "
         "Routing is `course_data/platform/routing.py`, re-run offline from each course's committed inputs.", ""]
    if pop:
        L += ["## Population (OSM, the surveyed states)", "",
              f"States: {', '.join(pop['states'])} (three per Census region, seeded). Eligible courses: **{pop['n']}** "
              f"(named leisure=golf_course, not mini / disc / foot golf / ranges, bbox >= {pop['rule']['min_ha']} ha or a node).", "",
              "| state | eligible | full (>= 18 hole ways) | partial | none |", "|---|---|---|---|---|"]
        for st, v in sorted(pop["per_state"].items()):
            L.append(f"| {st} | {v['eligible']} | {v['full']} ({v['full'] / max(v['eligible'], 1):.0%}) | {v['partial']} "
                     f"({v['partial'] / max(v['eligible'], 1):.0%}) | {v['none']} ({v['none'] / max(v['eligible'], 1):.0%}) |")
        L.append(f"| **all** | **{pop['n']}** | **{pop['tiers']['full']} ({pop['tier_share']['full']:.0%})** | "
                 f"**{pop['tiers']['partial']} ({pop['tier_share']['partial']:.0%})** | **{pop['tiers']['none']} ({pop['tier_share']['none']:.0%})** |")
        if pop.get("national"):
            L += ["", f"US-wide OSM counts: {json.dumps(pop['national'])}."]
        L.append("")
    o = summ["overall"]
    L += ["## Answer", "",
          f"* **Today**: every hole and green placed on **{o['today']:.0%}** of random US courses (population-weighted "
          "by tier) - essentially the courses where OSM volunteers mapped every golf=hole way.",
          f"* **With routing inference**: **{o['routing']:.0%}** fully correct with no human input; "
          f"**{o['routing_after_golfer_check']:.0%}** correct once a golfer confirms the holes the router flags.",
          f"* **Need a golfer check**: {o['needs_golfer_check']:.0%} of courses (a flagged hole, or no scorecard online).", ""]
    L += ["### Per tier", "", "| tier | population share | sampled | found by name | scorecard online | NAIP | today all holes | routing all correct | after golfer check | needs check |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for t in TIERS:
        p = summ["per_tier"][t]
        L.append(f"| {t} | {summ['tier_share'][t]:.0%} | {p['n']} | {pct(p['found'])} | {pct(p['scorecard'])} | {pct(p['naip'])} | "
                 f"{pct(p['today_all'])} | {pct(p.get('routing_all_correct'))} | {pct(p.get('routing_after_check'))} | {pct(p.get('needs_check'))} |")
    L += ["", "## Routing validation (OSM hole ways and refs hidden)", "",
          "| inputs | card | courses | hole-number acc | green assignment acc | physical holes found | median length err (yds) | all 18 correct | correct after check | needs check | flagged / course |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    names = {"v_osm": "OSM greens/tees + model + lidar", "v_model": "model + lidar only (unmapped course)",
             "today_fallback": "TODAY's fallback: geometry.infer_holes on OSM greens/tees"}
    for k, v in summ["validation"].items():
        inp, cd = k.rsplit("_", 1)
        L.append(f"| {names[inp]} | {'scorecard' if cd == 'card' else 'none'} | {v['n']} | {v['hole_number_acc']:.0%} | "
                 f"{v['green_assign_acc']:.0%} | {v['physical_holes_found']:.0%} | {v['median_length_err_yd']} | "
                 f"{v['all_correct']:.0%} | {v['correct_after_check']:.0%} | {v['needs_check']:.0%} | {v['mean_flagged']} |")
    L += ["", "Definitions: hole-number acc = routed hole n has the true hole n's green (within 20 yds) and its tee within "
          "40 yds of the first 60 % of the true line; green assignment = the green alone; physical holes = true (tee, green) "
          "pairs found under any number; length error = routed straight tee->green vs the true line's length from the routed "
          "tee; `correct after check` = every wrong hole carries a `check` flag. Card = the web scorecard when found, else "
          "pars + lengths from the hidden OSM ways (`card*` below).", "",
          "## Per course", "",
          "| course | st | tier | found | OSM holes / greens / tees | scorecard | NAIP | model greens (OSM) | today: line / green / tee | routed (check) | V-osm hole / green | V-model hole / green |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (TIERS.index(r["tier"]) if r["tier"] in TIERS else 9, r["slug"])):
        v = r.get("validation") or {}
        ck = "" if v.get("card_kind") == "web" else "*"
        vo = v.get("v_osm_card")
        vm = v.get("v_model_card")
        fs = "yes" if r["found"] else f"no ({r.get('resolve_status')}" + (f": {r['resolve_alt']}" if r.get("resolve_alt") else "") + ")"
        card_s = (r["scorecard"] or "none") + (f" ({r['card_holes']})" if r.get("card_holes") else "")
        seg_s = "-" if r["seg_greens"] is None else str(r["seg_greens"])

        def acc(x):
            return f"{x['hole_number_acc']:.0%} / {x['green_assign_acc']:.0%}{ck}" if x else "-"
        L.append(f"| {r['name']} | {r['state']} | {r['tier']} | {fs} | {r['osm_holes']} / {r['osm_greens']} / {r['osm_tees']} | "
                 f"{card_s} | {r.get('naip') or '-'} | {seg_s} ({r['osm_greens']}) | "
                 f"{r['today_holes']} / {r['today_green']} / {r['today_tee']} of {r['expected']} | "
                 f"{r.get('routed', '-')} ({r.get('routed_check', '-')}) | {acc(vo)} | {acc(vm)} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plots", action="store_true")
    a = ap.parse_args()
    pop = rd(os.path.join(HERE, "population.json"))
    sample = rd(os.path.join(HERE, "sample.json"))
    rows = []
    for d in sorted(glob.glob(os.path.join(HERE, "courses", "*"))):
        if os.path.exists(os.path.join(d, "result.json")):
            rows.append(course_row(d, plots=a.plots))
            print(rows[-1]["slug"], rows[-1].get("routed"), (rows[-1].get("validation") or {}).get("v_osm_card", {}).get("hole_number_acc"), flush=True)
    summ = summarise(rows, pop)
    json.dump(dict(summary=summ, courses=rows), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    open(os.path.join(HERE, "REPORT.md"), "w").write(md(rows, summ, pop, sample))
    print(json.dumps(summ["overall"]))


if __name__ == "__main__":
    main()
