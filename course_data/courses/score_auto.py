"""Score the blind automatic package against the hand-checked truth of a tournament course, hole by hole.

  python3 course_data/courses/score_auto.py --slug pine_dunes [--auto course_data/courses/pine_dunes/auto/package.json]
        [--label before|after] [--n 8000]

Truth: course_data/truth/<slug>/holes_truth.json (hole number, par, tee per set, green centre / outline, hand checked
on whole-hole sheets: NAIP + CIR + 3DEP lidar canopy + other NAIP years) and hand_zones_ll.json (landing corridors,
course_data/truth/corridor.py). Per hole:
  routing   the auto hole's green within 25 yds of the truth green of the SAME number (else: which truth hole it is)
  par       auto par = truth par
  tees      per set on the card: auto tee_ll vs truth tee (yds); missing = no auto tee for that set
  green     auto green centre vs truth (yds); par 3: auto has a green outline and the hole is planned as a par 3
  hazards   corridor IoU (220-340 yds x +/-45 along the truth tee line, scoreboard.hand_geometry) for trees,
            long grass, water, OB, + fairway
  picks     product quick decision (decide.run quick, n swings) on the auto package vs on the truth package (truth
            tees + greens + hand corridor zones), same club / tie, regret = truth-map EV of the auto club - truth
            EV of the truth club (strokes)
Writes course_data/courses/<slug>/score_<label>.json and .md.
"""
import argparse
import copy
import json
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
for p in (os.path.join(CD, "product"), os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo"), os.path.join(CD, "qa")):
    if p not in sys.path:
        sys.path.insert(0, p)


def yd(a, b):
    import render as R
    fr = R.Frame(a, [a[0], a[1] + 0.001], ppy=1.0, proj="utm")
    return float(np.linalg.norm(fr.ll_to_yds([a])[0] - fr.ll_to_yds([b])[0]))


def truth_package(slug, auto_pkg, tees):
    """The auto package with the truth's tees (every set), greens, par, and the hand corridor zones on top of the
    auto zones (auto zones outside the hand footprint are kept; inside it the hand map wins: a 'rough' footprint
    zone masks them, then the hand zones in traced order)."""
    T = json.load(open(os.path.join(CD, "truth", slug, "holes_truth.json")))
    hzp = os.path.join(CD, "truth", slug, "hand_zones_ll.json")
    HZ = json.load(open(hzp))["holes"] if os.path.exists(hzp) else {}
    pkg = copy.deepcopy(auto_pkg)
    import render as R
    for ref, th in T["holes"].items():
        h = pkg["holes"].get(ref)
        if h is None:
            continue
        h["par"] = th["par"]
        if th.get("card"):
            h["yards"] = dict(th["card"])
        h["green_ll"] = th["green_ll"]
        if th.get("green_poly_ll"):
            h["green_polygon_ll"] = th["green_poly_ll"]
        if th.get("hole_line_ll"):
            h["hole_line_ll"] = th["hole_line_ll"]
        tees_ = h.setdefault("tees", {})
        for s, ll in (th.get("tees") or {}).items():
            e = tees_.setdefault(s, {})
            e["tee_ll"] = ll
            e.pop("aim_ll", None)               # re-derived by the product's tee-line rule from the truth tee
            e["method"], e["confidence"] = "hand", 1.0
        st = tees if tees in (th.get("tees") or {}) else None
        if st:
            h["tee_ll"] = th["tees"][st]
            h.pop("aim_ll", None)
        m = HZ.get(ref)
        if m:
            zs = [z for z in (h.get("zones_ll") or [])]
            zs.append(dict(lie="rough", poly=m["footprint_ll"], src="hand:footprint"))
            zs += [dict(lie=z["lie"], poly=z["poly_ll"], src="hand") for z in m["zones"]]
            for z in th.get("extra_zones", []):
                zs.append(dict(lie=z["lie"], poly=z["poly_ll"], src="hand:extra"))
            h["zones_ll"] = zs
            h["zone_order"] = "given"
        elif th.get("extra_zones"):
            h["zones_ll"] = (h.get("zones_ll") or []) + [dict(lie=z["lie"], poly=z["poly_ll"], src="hand:extra")
                                                          for z in th["extra_zones"]]
        h.pop("elevation", None)                  # recomputed along the truth tee line by product/package.py
    pkg.setdefault("truth", {})["source"] = "course_data/truth/%s (hand checked)" % slug
    return pkg, T, HZ


def plan(pkg, tees, n, name):
    import package as PK
    import decide
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "package.json")
        json.dump(pkg, open(p, "w"))
        C = PK.load(p, tees)
        mp = os.path.join(td, "course.py")
        PK.write_module(C, mp)
        mod = PK.import_module(mp, name=name)
    res = decide.run(copy.deepcopy(mod.HOLES), "quick", log=lambda *a: None, n=n)
    out = {str(k): dict(pick=v["pick"], runner=v["runner"], margin=v["margin"], tie=v["tie"], aim=v["aim"],
                        check=v.get("check"), ev={c: r["ev"] for c, r in v["clubs"].items()}) for k, v in res.items()}
    return out, C, mod


def score(slug, auto_path, label, n=8000):
    import scoreboard as SB
    auto = json.load(open(auto_path))
    tees = json.load(open(os.path.join(HERE, slug, "config.json")))["tees"]
    tpkg, T, HZ = truth_package(slug, auto, tees)
    os.makedirs(os.path.join(HERE, slug, "truth"), exist_ok=True)
    json.dump(tpkg, open(os.path.join(HERE, slug, "truth", "package.json"), "w"))      # the plan's map (v2_course)
    rows = []
    a_res, aC, amod = plan(auto, tees, n, f"sa_{slug}_auto")
    t_res, tC, tmod = plan(tpkg, tees, n, f"sa_{slug}_truth")
    truth_greens = {r: th["green_ll"] for r, th in T["holes"].items()}
    for ref, th in sorted(T["holes"].items(), key=lambda kv: int(kv[0])):
        h = auto["holes"].get(ref)
        r = dict(hole=ref, par=th["par"])
        if h is None:
            r["routing"] = "missing in auto"
            rows.append(r)
            continue
        g = h.get("green_ll")
        r["green_err"] = round(yd(g, th["green_ll"]), 1) if g else None
        if r["green_err"] is None or r["green_err"] > 25:
            near = min(truth_greens, key=lambda k: yd(g, truth_greens[k])) if g else None
            r["routing"] = f"green is truth hole {near}'s" if near and near != ref and yd(g, truth_greens[near]) < 25 \
                else "green off (> 25 yds)"
        else:
            r["routing"] = "ok"
        r["par_ok"] = int(h.get("par") or 0) == th["par"]
        r["auto_par"] = h.get("par")
        te = {}
        for s, ll in (th.get("tees") or {}).items():
            a = ((h.get("tees") or {}).get(s) or {}).get("tee_ll")
            te[s] = round(yd(a, ll), 1) if a else None
        r["tee_err"] = te
        k = int(ref) if ref.isdigit() else ref
        if th["par"] == 3:
            p3 = aC.par3.get(k) or aC.par3.get(ref)
            r["par3_planned"] = p3 is not None
            r["par3_green_outline"] = bool(h.get("green_polygon_ll") or h.get("green_polygon"))
            if p3:
                r["par3_center_auto"], r["par3_center_truth"] = p3["center"], (tC.par3.get(k) or {}).get("center")
                r["par3_haz_auto"], r["par3_haz_truth"] = p3["haz"], (tC.par3.get(k) or {}).get("haz")
        else:
            cfg = dict(slug=slug, hand=os.path.relpath(os.path.join(CD, "truth", slug, "hand_zones_ll.json"), ROOT),
                       tees=tees)
            if ref in HZ:
                try:
                    r["geo"] = SB.hand_geometry(cfg, ref, aC, k)
                except Exception as e:                       # noqa: BLE001
                    r["geo"] = dict(error=f"{type(e).__name__}: {e}")
            pa, pt = a_res.get(str(k)), t_res.get(str(k))
            if pa and pt:
                same, tie = SB.agree(pa, pt)
                r.update(pick_auto=pa["pick"], aim_auto=round(pa["aim"], 1), pick_truth=pt["pick"],
                         aim_truth=round(pt["aim"], 1), same=same, same_or_tie=tie,
                         regret=SB.regret(pa, pt), check_auto=pa.get("check"))
        r["note"] = th.get("note", "")
        rows.append(r)
    S = summary(rows)
    out = dict(slug=slug, label=label, auto=os.path.relpath(auto_path, ROOT), tees=tees, n=n, rows=rows, summary=S)
    json.dump(out, open(os.path.join(HERE, slug, f"score_{label}.json"), "w"), indent=1, default=float)
    open(os.path.join(HERE, slug, f"score_{label}.md"), "w").write(md(out))
    print(md(out))
    return out


def summary(rows):
    tee_errs = [v for r in rows for v in (r.get("tee_err") or {}).values() if v is not None]
    tee_missing = sum(1 for r in rows for v in (r.get("tee_err") or {}).values() if v is None)
    picks = [r for r in rows if "pick_auto" in r]
    ious = {}
    for r in rows:
        for k, v in ((r.get("geo") or {}).get("iou") or {}).items():
            ious.setdefault(k, []).append(v)
    p3 = [r for r in rows if r["par"] == 3]
    return dict(
        holes=len(rows), routing_ok=sum(1 for r in rows if r.get("routing") == "ok"),
        par_ok=sum(1 for r in rows if r.get("par_ok")),
        green_within_10=sum(1 for r in rows if (r.get("green_err") or 99) <= 10),
        tees_within_10=sum(1 for v in tee_errs if v <= 10), tees_scored=len(tee_errs), tees_missing=tee_missing,
        tee_median_err=round(float(np.median(tee_errs)), 1) if tee_errs else None,
        par3_planned=sum(1 for r in p3 if r.get("par3_planned")), par3=len(p3),
        par3_outline=sum(1 for r in p3 if r.get("par3_green_outline")),
        same_club=sum(1 for r in picks if r["same"]), same_or_tie=sum(1 for r in picks if r["same_or_tie"]),
        tee_shots=len(picks), regret=round(sum((r.get("regret") or 0) for r in picks), 3),
        iou_mean={k: round(float(np.mean(v)), 3) for k, v in ious.items()})


def md(o):
    S = o["summary"]
    L = [f"# {o['slug']}: auto vs hand truth ({o['label']})", "",
         f"Auto package: `{o['auto']}`; tee set {o['tees']}; quick decision n={o['n']}.", "",
         f"* routing ok {S['routing_ok']}/{S['holes']}, par ok {S['par_ok']}/{S['holes']}, green within 10 yds "
         f"{S['green_within_10']}/{S['holes']}",
         f"* tees within 10 yds {S['tees_within_10']}/{S['tees_scored']} (median {S['tee_median_err']} yds; "
         f"{S['tees_missing']} set-holes with no auto tee)",
         f"* par 3s planned as par 3 {S['par3_planned']}/{S['par3']}, with a green outline {S['par3_outline']}/{S['par3']}",
         f"* tee-shot picks: same club {S['same_club']}/{S['tee_shots']}, same or tie {S['same_or_tie']}/{S['tee_shots']},"
         f" total regret {S['regret']} strokes",
         f"* corridor IoU (mean): " + ", ".join(f"{k} {v}" for k, v in S["iou_mean"].items()), "",
         "| hole | par | routing | green err | tee err by set | par 3 | auto pick | truth pick | regret | IoU |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in o["rows"]:
        te = ", ".join(f"{s[:2]} {v if v is not None else '-'}" for s, v in (r.get("tee_err") or {}).items())
        p3 = "" if r["par"] != 3 else ("planned" if r.get("par3_planned") else "NOT planned") + \
            ("" if r.get("par3_green_outline") else ", no outline")
        g = r.get("geo") or {}
        iou = ", ".join(f"{k[:5]} {v}" for k, v in (g.get("iou") or {}).items())
        if g.get("iou_fairway") is not None:
            iou += f", fw {g['iou_fairway']}"
        L.append(f"| {r['hole']} | {r['par']}{'' if r.get('par_ok', True) else ' (auto ' + str(r.get('auto_par')) + ')'} | "
                 f"{r.get('routing')} | {r.get('green_err')} | {te} | {p3} | "
                 f"{r.get('pick_auto', '')} {'' if 'aim_auto' not in r else '%+.0f' % r['aim_auto']} | "
                 f"{r.get('pick_truth', '')} {'' if 'aim_truth' not in r else '%+.0f' % r['aim_truth']} | "
                 f"{'' if r.get('regret') is None else r['regret']} | {iou} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--auto")
    ap.add_argument("--label", default="before")
    ap.add_argument("--n", type=int, default=8000)
    a = ap.parse_args()
    score(a.slug, a.auto or os.path.join(HERE, a.slug, "auto", "package.json"), a.label, a.n)


if __name__ == "__main__":
    main()
