"""Why does the product miss the truth's club (and lean shorter)? Per-miss layer swaps on all five truth courses.

  python3 course_data/qa/short_club_diagnosis.py [--courses ellis,veenker] [--workers 4]
  -> course_data/qa/short_club_diagnosis.{json,md}

For every scored tee shot where the product's quick pick (committed package, scoreboard harness) is not the
truth's club, the hole is re-decided (product/decide.run quick, n = 8000, same seeds) with ONE ingredient taken
from the truth's map at a time, everything else the product's:

  trees     lie recovery                       (lidar canopy + buffer vs the hand-traced tree line)
  ob        ob / ob_boundary                   (inferred OB vs hand OB)
  water     water
  fairway   fairway / first_cut / rough        (fairway width and the mown corridor)
  sand      sand
  native    native (long grass)
  tee       the hand map's tee position (package tee_ll -> the traced tee)
  all       every zone group (inside the hand map's footprint) -- the map ceiling
  all+tee   every zone group and the tee

Swapping a group: the product's zones of that group are removed INSIDE the hand map's traced footprint (the
150-340 yd corridor of the truth courses; the whole hole on Mozingo, whose screenshot map has no footprint) and
the hand map's zones of that group are added; product zones outside the footprint stay. Zone precedence is the
product's (package.ORDER).

Truth per course (as course_data/qa/scoreboard.py): Spirit Hollow final_decision.json (full Bayesian decision on
the hand map; its quick decision on the same map is scoreboard's 'hand map, quick' and isolates the decision
mode), Mozingo the screenshot hand map (mozingo/tee_strategy.HOLES; georeferenced through
course_data/vision_any/mozingo/traced_registration.json, rigid fit, dice ~0.5, so its swaps are approximate)
through the quick decision, Veenker / Coldwater / Ellis the hand-checked corridor maps through the quick decision.

Attribution of a miss: the single swaps that turn the pick into the truth's club (several = each named; a swap
that only makes it a tie is 'partial'); none but all / all+tee = 'combined'; the pick still differs with all+tee:
'decision mode' (Spirit Hollow, when the hand map's own quick decision already differs from the full Bayesian
truth), 'screenshot model' (Mozingo: frame / green / elevation of the screenshot map), else 'outside corridor /
zone order' (product zones beyond the hand map's footprint, e.g. OB that triggers the lay-up irons).
"""
import argparse
import copy
import json
import os
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
for p in (HERE, os.path.join(CD, "product"), os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
    if p not in sys.path:
        sys.path.insert(0, p)

OUT_JSON = os.path.join(HERE, "short_club_diagnosis.json")
OUT_MD = os.path.join(HERE, "short_club_diagnosis.md")
GROUPS = {"trees": {"recovery", "trees", "woods"}, "ob": {"ob", "ob_boundary"}, "water": {"water"},
          "fairway": {"fairway", "first_cut", "first_cut_band", "rough", "green", "tee"},
          "sand": {"sand", "bunker"}, "native": {"native", "long_grass", "tall_grass"}}
CLUB_ORDER = ["Driver", "2-wood", "3-wood", "4-wood", "5-wood", "Hybrid", "Long iron", "Mid iron", "Short iron"]
MZ_REG = os.path.join(CD, "vision_any", "mozingo", "traced_registration.json")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def group_of(lie):
    for g, s in GROUPS.items():
        if lie in s:
            return g
    return None


def rank(c):
    return CLUB_ORDER.index(c) if c in CLUB_ORDER else len(CLUB_ORDER)


# ----------------------------------------------------------------------------- hand maps as {key: (tee, fp, zones)}
def hand_ll(cfg, SB):
    """{scored key: dict(ref, tee_set, tee_ll, footprint_ll|None, zones=[(lie, poly_ll)])} of the truth's map."""
    out = {}
    if cfg["truth"] == "hand":
        hz = json.load(open(os.path.join(ROOT, cfg["hand"])))["holes"]
        for k, h in hz.items():
            out[k] = dict(ref=str(h.get("ref", k)), tee_set=h.get("tee_set") or cfg["tees"], tee_ll=h["tee_ll"],
                          footprint_ll=h.get("footprint_ll"), zones=[(z["lie"], z["poly_ll"]) for z in h["zones"]])
    elif cfg["truth"] == "spirit_hollow":
        import render as R
        hz = json.load(open(SB.HAND_LL))["holes"]
        sets = SB.sh_truth_sets()
        fwd = {str(a): float(b) for a, b in getattr(SB.sh_course(), "BLACK_TEE_FORWARD", {}).items()}
        for k, h in hz.items():
            fr0 = SB._hand_frame(R, h["tee_ll"], h["dot270_ll"])
            tee = fr0.yds_to_ll([[0.0, -fwd.get(k, 0.0)]])[0].tolist()     # course.py's Black box (as scoreboard)
            out[k] = dict(ref=k.rstrip("BF"), tee_set=sets.get(k, cfg["tees"]), tee_ll=tee,
                          footprint_ll=h.get("footprint_ll"), zones=[(z["lie"], z["poly_ll"]) for z in h["zones"]])
    elif cfg["truth"] == "mozingo":
        import tee_strategy as t
        reg = json.load(open(MZ_REG))
        for k, h in SB.HAND_HOLES.items():
            r = reg.get(str(k))
            if not r:
                continue
            A = np.asarray(r["affine_px_to_ll"], float)

            def ll(pts, A=A):
                P = np.asarray(pts, float)[:, :2]
                return (np.c_[P, np.ones(len(P))] @ A.T).tolist()
            out[str(k)] = dict(ref=str(k), tee_set=cfg["tees"], tee_ll=ll([h["tee"]])[0], footprint_ll=None,
                               zones=[(lie, ll(poly)) for lie, poly in h["zones"] if len(poly) >= 3])
    return out


def _polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [x for x in getattr(g, "geoms", []) if x.geom_type == "Polygon"]


def hybrid_zones(prod_zones, hand, swap):
    """Product zones_ll with the groups in `swap` replaced by the hand map's inside its footprint."""
    from shapely.geometry import Polygon
    fp = Polygon(hand["footprint_ll"]).buffer(0) if hand.get("footprint_ll") else None
    out = []
    for z in prod_zones:
        g = group_of(z["lie"])
        if g not in swap:
            out.append(z)
            continue
        if fp is None:
            continue
        try:
            rest = Polygon(np.asarray(z["poly"], float)[:, :2]).buffer(0).difference(fp)
        except Exception:                                               # noqa: BLE001
            continue
        for p in _polys(rest):
            if p.area > 0:
                out.append(dict(z, poly=[list(c) for c in p.exterior.coords[:-1]]))
    for lie, poly in hand["zones"]:
        if group_of(lie) in swap and len(poly) >= 3:
            out.append(dict(lie=lie, poly=[list(c)[:2] for c in poly], src="hand"))
    return out


# ----------------------------------------------------------------------------- one course
def model_holes(pkg, tee_set, keyed, name):
    """{new key: model hole} for (new key -> package ref) from a package dict."""
    import package as PK
    with tempfile.TemporaryDirectory(dir=os.path.join(CD, "packages", pkg["slug"])) as td:
        p = os.path.join(td, "package.json")
        json.dump(pkg, open(p, "w"))
        C = PK.load(p, tee_set)
        mp = os.path.join(td, "course.py")
        PK.write_module(C, mp)
        mod = PK.import_module(mp, name=name)
    H = {str(k): v for k, v in mod.HOLES.items()}
    return {nk: copy.deepcopy(H[ref]) for nk, ref in keyed.items() if ref in H}


def zones_of(h):
    z = h.get("zones_ll") if h.get("zones_ll") is not None else []
    return [dict(z_) for z_ in z if isinstance(z_, dict) and z_.get("poly")]


def diagnose_course(cfg, SB, prev, n, workers, keys=None):
    import decide
    a = argparse.Namespace(n=n, workers=workers, from_out=False, holes=None, no_hand_quick=False, dry_run=False,
                           full=False, full_S=64, full_N=3000)
    sc = SB.score_course(cfg, a, prev)
    rows = {str(r["hole"]): r for r in sc["holes"] if r.get("truth")}
    misses = [k for k, r in rows.items() if not r["same"] and (keys is None or k in keys)]
    hand = hand_ll(cfg, SB)
    tc = (prev.get("truth_cache") or {})
    truth_ev = {}
    if cfg["truth"] == "spirit_hollow":
        fin = SB.final_truth()
        truth_ev = {k: fin[k] for k in fin}
        hq = (SB.TRUTH_RAW.get("spirit_hollow") or tc.get("spirit_hollow") or {}).get("res", {})
    else:
        nm = "mozingo" if cfg["truth"] == "mozingo" else cfg["slug"]
        truth_ev = (SB.TRUTH_RAW.get(nm) or tc.get(nm) or {}).get("res", {})
        hq = truth_ev
    pkg0 = json.load(open(os.path.join(ROOT, cfg["package"])))
    out = []
    variants = list(GROUPS) + ["tee", "all", "all+tee"]
    for k in misses:
        r = rows[k]
        hd = hand.get(k)
        if hd is None:
            out.append(dict(course=cfg["slug"], hole=k, pick=r["pick"], truth=r["truth"], note="no georeferenced hand map"))
            continue
        ref, st = hd["ref"], hd["tee_set"] or cfg["tees"]
        ph = pkg0["holes"][ref]
        pz = zones_of(ph)
        present = {group_of(z["lie"]) for z in pz} | {group_of(l) for l, _ in hd["zones"]}
        built = {}
        for v in ["base"] + variants:
            if v in GROUPS and v not in present:
                continue
            pkg = copy.deepcopy(pkg0)
            h = pkg["holes"][ref]
            swap = set(GROUPS) if v.startswith("all") else ({v} if v in GROUPS else set())
            if swap:
                h["zones_ll"] = hybrid_zones(pz, hd, swap)
                h.pop("zones", None)
            if v in ("tee", "all+tee"):
                ent = (h.get("tees") or {}).get(st)
                if ent is not None:
                    ent["tee_ll"] = list(hd["tee_ll"])
                else:
                    h["tee_ll"] = list(hd["tee_ll"])
            built.update(model_holes(pkg, st, {f"{k}|{v}": ref}, f"diag_{cfg['slug']}_{k}_{v}".replace("+", "p")))
        res = decide.run(built, "quick", workers=workers, log=lambda *a_: None, n=n)
        tr = r["truth"]
        e = dict(course=cfg["slug"], hole=k, tee_set=st, pick=r["pick"], truth=tr, truth_tie=r.get("truth_tie"),
                 truth_runner=r.get("truth_runner"), regret=r.get("regret"),
                 direction="shorter" if rank(r["pick"]) > rank(tr) else "longer",
                 hand_quick=(hq.get(k) or {}).get("pick"), tee_err=r.get("tee_err"), iou=r.get("iou"), variants={})
        for v in ["base"] + variants:
            x = res.get(f"{k}|{v}")
            if not x:
                continue
            ev = {c: float(q["ev"]) for c, q in x["clubs"].items()}
            e["variants"][v] = dict(pick=x["pick"], tie=bool(x["tie"]), runner=x.get("runner"),
                                    margin=round(float(x["margin"]), 4),
                                    gap=round(ev[x["pick"]] - ev[tr], 4) if tr in ev else None,
                                    same=x["pick"] == tr, tie_truth=bool(x["pick"] == tr or (x["tie"] and x.get("runner") == tr)))
        e.update(attribute(e, cfg))
        out.append(e)
        vv = ", ".join(v + ":" + d["pick"] for v, d in e["variants"].items())
        log(f"  {cfg['slug']} {k}: {r['pick']} vs {tr} -> {e['cause']} ({vv})")
    return dict(course=cfg["slug"], name=cfg["name"], n=len(rows), same=sum(bool(r["same"]) for r in rows.values()),
                misses=out)


def attribute(e, cfg):
    V = e["variants"]
    if V.get("base", {}).get("pick") != e["pick"]:
        base_note = f"harness base pick {V.get('base', {}).get('pick')} != scoreboard {e['pick']}"
    else:
        base_note = None
    fix = [v for v in list(GROUPS) + ["tee"] if V.get(v, {}).get("same")]
    part = [v for v in list(GROUPS) + ["tee"] if not V.get(v, {}).get("same") and V.get(v, {}).get("tie_truth")]
    if fix:
        cause = "+".join(fix)
    elif V.get("all", {}).get("same") or V.get("all+tee", {}).get("same"):
        cause = "combined" + (f" (partial: {'+'.join(part)})" if part else "")
    elif cfg["truth"] == "spirit_hollow" and e.get("hand_quick") and e["hand_quick"] != e["truth"] and \
            V.get("all+tee", {}).get("pick") == e["hand_quick"]:
        cause = "decision mode: quick on the hand map != the full Bayesian truth"
    elif cfg["truth"] == "mozingo":
        cause = "screenshot model: frame / green / elevation" + (f" (partial: {'+'.join(part)})" if part else "")
    else:
        cause = "outside corridor / zone order" + (f" (partial: {'+'.join(part)})" if part else "")
    return dict(cause=cause, fixes=fix, partial=part, base_note=base_note)


# ----------------------------------------------------------------------------- report
def summary(courses):
    M = [m for c in courses for m in c["misses"] if m.get("variants")]
    S = dict(n=sum(c["n"] for c in courses), same=sum(c["same"] for c in courses), misses=len(M),
             shorter=sum(m["direction"] == "shorter" for m in M), longer=sum(m["direction"] == "longer" for m in M),
             by_cause={}, fixes_by_group={}, regret_by_cause={})
    for m in M:
        key = m["cause"].split(" (")[0].split(":")[0]
        S["by_cause"].setdefault(key, dict(n=0, shorter=0, longer=0, regret=0.0))
        S["by_cause"][key]["n"] += 1
        S["by_cause"][key][m["direction"]] += 1
        S["by_cause"][key]["regret"] = round(S["by_cause"][key]["regret"] + float(m.get("regret") or 0), 4)
        for g in m["fixes"]:
            S["fixes_by_group"].setdefault(g, dict(n=0, shorter=0, longer=0))
            S["fixes_by_group"][g]["n"] += 1
            S["fixes_by_group"][g][m["direction"]] += 1
    return S


def write_md(R, path):
    S = R["summary"]
    L = ["# Short-club bias: what each product miss comes from (all five truth courses)", "",
         f"Generated by `course_data/qa/short_club_diagnosis.py` (product quick decision n = {R['n']}, committed packages "
         f"at {R['commit']}). Each miss is re-decided with one ingredient of the truth's map swapped into the product "
         "package (inside the hand map's footprint); see the module docstring for the method.", "",
         f"**{S['same']}/{S['n']} same club; {S['misses']} misses: {S['shorter']} shorter, {S['longer']} longer than the truth.**", "",
         "| cause (single swap that restores the truth's club) | misses | shorter | longer | regret (strokes) |",
         "|---|---|---|---|---|"]
    for k, v in sorted(S["by_cause"].items(), key=lambda kv: -kv[1]["n"]):
        L.append(f"| {k} | {v['n']} | {v['shorter']} | {v['longer']} | {v['regret']:.3f} |")
    L += ["", "Swaps that restore the truth's club, per group (a miss can count under several):", "",
          "| group | misses fixed | shorter | longer |", "|---|---|---|---|"]
    for k, v in sorted(S["fixes_by_group"].items(), key=lambda kv: -kv[1]["n"]):
        L.append(f"| {k} | {v['n']} | {v['shorter']} | {v['longer']} |")
    vs = list(GROUPS) + ["tee", "all", "all+tee"]
    L += ["", "## Per miss", "", "Cells: the pick with that ingredient from the truth's map (**bold** = the truth's club; "
          "'-' = the group is absent from both maps).", "",
          "| course | hole | product | truth | dir | regret | hand quick | " + " | ".join(vs) + " | cause |",
          "|---|---|---|---|---|---|---|" + "---|" * len(vs) + "---|"]
    for c in R["courses"]:
        for m in c["misses"]:
            if not m.get("variants"):
                L.append(f"| {c['course']} | {m['hole']} | {m['pick']} | {m['truth']} | | | | " + " | ".join("" for _ in vs) +
                         f" | {m.get('note', '')} |")
                continue
            cells = []
            for v in vs:
                d = m["variants"].get(v)
                cells.append("-" if not d else (f"**{d['pick']}**" if d["same"] else d["pick"] + (" (tie)" if d["tie_truth"] else "")))
            L.append(f"| {c['course']} | {m['hole']} | {m['pick']} | {m['truth']} | {m['direction']} | "
                     f"{m.get('regret') if m.get('regret') is not None else '-'} | {m.get('hand_quick') or '-'} | "
                     + " | ".join(cells) + f" | {m['cause']} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--courses")
    ap.add_argument("--n", type=int, default=8000)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--out-json", default=OUT_JSON)
    ap.add_argument("--out-md", default=OUT_MD)
    ap.add_argument("--reattribute", help="re-run only the attribution + report on a saved JSON")
    a = ap.parse_args()
    if a.reattribute:
        R = json.load(open(a.reattribute))
        cfgs = {c["slug"]: c for c in __import__("scoreboard").COURSES}
        for c in R["courses"]:
            for m in c["misses"]:
                if m.get("variants"):
                    m.update(attribute(m, cfgs[c["course"]]))
        R["summary"] = summary(R["courses"])
        json.dump(R, open(a.out_json, "w"), indent=1, default=float)
        write_md(R, a.out_md)
        print(open(a.out_md).read())
        return
    import scoreboard as SB
    import tee_strategy as t
    SB.HAND_HOLES = copy.deepcopy(t.HOLES)
    prev = json.load(open(SB.OUT_JSON)) if os.path.exists(SB.OUT_JSON) else {}
    prev.setdefault("truth_cache", {})
    want = set(a.courses.split(",")) if a.courses else None
    courses = []
    for cfg in SB.COURSES:
        if want and cfg["slug"] not in want:
            continue
        courses.append(diagnose_course(cfg, SB, prev, a.n, a.workers))
    R = dict(n=a.n, commit=SB.git("rev-parse", "--short", "HEAD"), courses=courses)
    R["summary"] = summary(courses)
    json.dump(R, open(a.out_json, "w"), indent=1, default=float)
    write_md(R, a.out_md)
    print(open(a.out_md).read())


if __name__ == "__main__":
    main()
