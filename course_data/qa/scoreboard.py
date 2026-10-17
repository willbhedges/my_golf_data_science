"""The product scoreboard: type a US course + tees -> how close is the hole-by-hole plan to the truth?

  python3 course_data/qa/scoreboard.py                     # full run (Actions: .github/workflows/scoreboard.yml)
  python3 course_data/qa/scoreboard.py --check             # + regression guards (exit 1 on a regression)
  python3 course_data/qa/scoreboard.py --check --full      # Actions: + the product's full Bayesian decision
                                                           #   (headline where the truth is Bayesian)
  python3 course_data/qa/scoreboard.py --from-out          # light: score the committed out/decision.json
                                                           #   files instead of re-running the decision
  python3 course_data/qa/scoreboard.py --courses spirit_hollow --n 1000 --workers 1 --dry-run   # smoke test

One command -> course_data/qa/scoreboard.json (current + history) and course_data/qa/SCOREBOARD.md.

What is scored, per course (Spirit Hollow, Mozingo Lake, Veenker):
  product plan  the product's own decision step on the committed platform package: product/package.load
                (the golfer's tee set) -> product/decide.run(mode="quick", n=8000), i.e. exactly what
                plan.py --quick prints (club, aim, CHECK flags), without the imagery / book / wind stages.
  truth         Spirit Hollow: spirit_hollow/output/final_decision.json (the published Bayesian pick per
                tee shot, ties marked) on spirit_hollow/course.py (hand map; tees on the real Black boxes,
                course.BLACK_TEE_FORWARD; 2B / 9B are the Gold boxes of the screenshots, so those two are
                scored against a Gold-tee product plan). Also reported: the hand map run through the same
                quick decision as the product ("hand-quick": isolates map error from model settings).
                Mozingo Lake: the hand map (mozingo/tee_strategy.HOLES) through the same quick decision
                (results_table.md predates the 10-16 model changes, so it is not used).
                Veenker, Coldwater, Ellis: the hand-checked landing-corridor maps course_data/truth/<slug>/
                hand_zones_ll.json (traced on NAIP 2023 0.3 m + other NAIP years + 3DEP lidar canopy, 150-340
                yds x +/-60 of the card set's tee line; course_data/truth/corridor.py, NOTES.md) put into the
                committed package in place of its zones (zone order as traced; unzoned = rough; tees, greens,
                elevation from the package) and run through the same quick decision ("hand map, quick", as
                Mozingo). Their geometry columns compare the product's lies with the hand map in the corridor.
  metrics       same club; same-or-tie (same, or one plan calls the two clubs a tie, margin < 0.01, and the
                other plan picked that tie's runner-up); regret = truth EV of the product's club - truth EV
                of the truth's club (strokes, on the hand map); tee / green within 10 yds of the hand map
                (WGS84, course_data/spirit_hollow/hand_zones_ll.json, Black tee moved up its line by
                BLACK_TEE_FORWARD); hazard IoU in the landing corridor (220-340 yds along the hand tee line,
                +/-45 yds, 5-yd grid, inside the screenshot footprint) for trees (recovery), long grass
                (native), water and OB, lies as the model sees them (product zone precedence vs hand-map
                order); CHECK holes; runtime of the decision step (and plan.py's last full runtime).

Re-baseline: put {"rebaseline": {"id": "...", "reason": "..."}} in course_data/requests/qa_scoreboard.json; the next
full run records the reason on its history rows and skips the drop check once (a change of headline mode or of the
truth also resets the baseline).

Regression guards (--check, CI): fail if (a) same-club count drops by more than 1 hole vs the last
non-regressed history row of that course with the same truth fingerprint, or (b) any printed aim is more
than 40 yds off the tee line without a CHECK flag.
"""
import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

QA = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(QA)
ROOT = os.path.dirname(CD)
PROD = os.path.join(CD, "product")
for _p in (PROD, os.path.join(CD, "imagery"), os.path.join(ROOT, "mozingo")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

OUT_JSON = os.path.join(QA, "scoreboard.json")
OUT_MD = os.path.join(QA, "SCOREBOARD.md")
FINAL = os.path.join(ROOT, "spirit_hollow", "output", "final_decision.json")
SH_COURSE = os.path.join(ROOT, "spirit_hollow", "course.py")
HAND_LL = os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")
SHOT_SETS = os.path.join(CD, "spirit_hollow", "screenshot_tee_sets.json")
MZ_HAND = os.path.join(ROOT, "mozingo", "tee_strategy.py")

COURSES = [
    dict(slug="spirit_hollow", name="Spirit Hollow", package="course_data/packages/spirit_hollow/package.json",
         tees="Black", truth="spirit_hollow"),
    dict(slug="mozingo_lake", name="Mozingo Lake", package="course_data/packages/mozingo_lake/package.json",
         tees="App", truth="mozingo"),
    dict(slug="veenker", name="Veenker", package="course_data/packages/veenker/package.json",
         tees="Blue", truth="hand", hand="course_data/truth/veenker/hand_zones_ll.json"),
    dict(slug="coldwater", name="Coldwater Golf Links", package="course_data/packages/coldwater/package.json",
         tees="Blue", truth="hand", hand="course_data/truth/coldwater/hand_zones_ll.json"),
    dict(slug="ellis", name="Ellis", package="course_data/packages/ellis/package.json",
         tees="Blue", truth="hand", hand="course_data/truth/ellis/hand_zones_ll.json"),
]
HAND_LABEL = "hand map, quick"
CLUB_BAR = 0.80
TIE = 0.01
AIM_GUARD = 40.0
HAZ = {"trees": "recovery", "long grass": "native", "water": "water", "ob": "ob"}
ALONG = np.arange(220, 340.1, 5.0)
LAT = np.arange(-45, 45.1, 5.0)


def log(*a):
    print(*a, flush=True)


def sha(*paths):
    h = hashlib.sha1()
    for p in paths:
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()[:10]


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:                                              # noqa: BLE001
        return ""


def load_module(path, name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------- product plan
def product_plan(cfg, tees, keys=None, n=8000, workers=None, from_out=False, mode="quick", S=64, N=3000):
    """{str key: decide result} for the product on the committed package, the Course, seconds.
    mode "full" = decide.full_hole (the Bayesian path plan.py runs by default): S prior draws x N swings."""
    import package as PK                                   # course_data/product/package.py
    C = PK.load(os.path.join(ROOT, cfg["package"]), tees)
    if from_out and tees == cfg["tees"]:
        f = os.path.join(ROOT, os.path.dirname(cfg["package"]), "out", "decision.json")
        plan = os.path.join(os.path.dirname(f), "plan.json")
        if os.path.exists(f):
            res = json.load(open(f))
            pj = json.load(open(plan)) if os.path.exists(plan) else {}
            if pj.get("tee_set") and pj["tee_set"] != C.tee_set:
                log(f"  ! {f}: tee set {pj['tee_set']} != {C.tee_set}")
            return {str(k): v for k, v in res.items() if keys is None or str(k) in keys}, C, None
    if from_out:
        return {}, C, None
    import decide
    with tempfile.TemporaryDirectory() as td:
        mp = os.path.join(td, "course.py")
        PK.write_module(C, mp)
        mod = PK.import_module(mp, name=f"sb_{cfg['slug']}_{tees}".replace(" ", "_"))
    holes = {k: v for k, v in mod.HOLES.items() if keys is None or str(k) in keys}
    t0 = time.time()
    kw = dict(n=n) if mode == "quick" else dict(S=S, N=N, sweep=False)
    res = decide.run(holes, mode, workers=workers, log=lambda *a: None, **kw)
    return {str(k): v for k, v in res.items()}, C, round(time.time() - t0, 1)


def hand_quick(holes, n=8000, workers=None):
    """The hand map through the product's quick decision (same model settings as the product)."""
    import decide
    res = decide.run(copy.deepcopy(holes), "quick", workers=workers, log=lambda *a: None, n=n)
    return {str(k): dict(pick=v["pick"], runner=v["runner"], margin=v["margin"], tie=v["tie"], aim=v["aim"],
                         ev={c: r["ev"] for c, r in v["clubs"].items()}) for k, v in res.items()}


def cached_hand_quick(prev, name, holes, fp, n, workers, dry):
    c = ((prev or {}).get("truth_cache") or {}).get(name)
    if c and c.get("fp") == fp and c.get("n") == n and set(c["res"]) >= {str(k) for k in holes}:
        log(f"  hand-quick {name}: cached ({fp})")
        TRUTH_RAW[name] = c
        return c["res"], True
    if dry:
        return None, False
    t0 = time.time()
    r = hand_quick(holes, n=n, workers=workers)
    log(f"  hand-quick {name}: {len(r)} holes in {time.time() - t0:.0f} s")
    TRUTH_RAW[name] = dict(fp=fp, n=n, res=r, built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"))
    return r, False


# ----------------------------------------------------------------------------- truth
_SH = None


def sh_course():
    global _SH
    if _SH is None:
        sys.path.insert(0, os.path.join(ROOT, "spirit_hollow"))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                _SH = load_module(SH_COURSE, "sb_spirit_hollow_course")
        finally:
            sys.path.remove(os.path.join(ROOT, "spirit_hollow"))
    return _SH


def sh_truth_sets():
    """{traced key: tee set the hand map plays from}: the real Black box where course.py moved the tee
    (BLACK_TEE_FORWARD), otherwise the set the 18Birdies screenshot shows (screenshot_tee_sets.json)."""
    shots = {k: v["set"] for k, v in json.load(open(SHOT_SETS))["holes"].items()}
    fwd = {str(k) for k in getattr(sh_course(), "BLACK_TEE_FORWARD", {})} if not os.environ.get("SH_SCREENSHOT_TEES") else set()
    return {str(k): ("Black" if str(k) in fwd else shots.get(str(k), "Black")) for k in sh_course().HOLES}


def final_truth():
    d = json.load(open(FINAL))
    return {k: dict(pick=v["pick"], runner=v.get("runner"), margin=v.get("margin"), tie=bool(v.get("tie")),
                    aim=v.get("aim"), ev={c: r["ev"] for c, r in (v.get("clubs") or {}).items()}) for k, v in d.items()}


# ----------------------------------------------------------------------------- geometry (Spirit Hollow)
def _hand_frame(R, tee_ll, d270_ll):
    return R.Frame(tee_ll, d270_ll, ppy=1.0, tee_px=(0.0, 0.0), proj="enu")


def _inside(poly, pts):
    from matplotlib.path import Path
    return Path(np.asarray(poly, float)[:, :2]).contains_points(pts)


def sh_geometry(key, set_name, C, k_prod):
    """tee / green error (yds) and landing-corridor IoU per hazard: product package vs the GPS hand map."""
    import render as R
    import tee_strategy as t
    hz = json.load(open(HAND_LL))["holes"].get(key)
    if not hz or k_prod not in C.holes:
        return None
    fr0 = _hand_frame(R, hz["tee_ll"], hz["dot270_ll"])
    fwd = getattr(sh_course(), "BLACK_TEE_FORWARD", {})
    move = float(dict((str(a), b) for a, b in fwd.items()).get(key, 0)) if not os.environ.get("SH_SCREENSHOT_TEES") else 0.0
    tee_ll = fr0.yds_to_ll([[0.0, -move]])[0]
    fr = _hand_frame(R, tee_ll, fr0.yds_to_ll([[0.0, -(270.0 + move)]])[0])
    pf = R.Frame.from_json(C.frames[k_prod])
    p_tee = np.asarray(C.frames[k_prod]["tee_ll"], float)
    p_green = pf.px_to_ll([C.holes[k_prod]["green"]])[0]

    def yd(a, b):
        return float(np.linalg.norm(fr.ll_to_yds([a])[0] - fr.ll_to_yds([b])[0]))
    out = dict(tee_err=round(yd(p_tee, tee_ll), 1), green_err=round(yd(p_green, hz["green_ll"]), 1))
    al, la = np.meshgrid(ALONG, LAT)
    xy = np.c_[la.ravel(), -al.ravel()]
    ll = fr.yds_to_ll(xy)
    keep = _inside(hz["footprint_ll"], ll) if hz.get("footprint_ll") else np.ones(len(ll), bool)
    ll = ll[keep]
    hand = np.array(["rough"] * len(ll), dtype=object)
    for z in hz["zones"]:
        if len(z["poly_ll"]) >= 3:
            hand[_inside(z["poly_ll"], ll)] = z["lie"]
    prod = t.lie_at(C.holes[k_prod], pf.ll_to_px(ll))
    iou = {}
    for name, lie in HAZ.items():
        A, B = hand == lie, prod == lie
        u = int(np.sum(A | B))
        if u:
            iou[name] = round(float(np.sum(A & B) / u), 3)
    out.update(iou=iou, corridor_pts=int(len(ll)))
    return out


# ----------------------------------------------------------------------------- hand-checked corridor maps
def hand_package(cfg):
    """The committed package with each mapped tee shot's zones replaced by the hand map (order as traced)."""
    pkg = json.load(open(os.path.join(ROOT, cfg["package"])))
    hz = json.load(open(os.path.join(ROOT, cfg["hand"])))
    for ref, h in pkg["holes"].items():
        m = hz["holes"].get(str(ref))
        if m:
            st = m.get("tee_set") or cfg["tees"]
            ent = (h.get("tees") or {}).get(st)
            if ent is not None:             # the hand-checked tee (the package's tee when the map was traced):
                ent["tee_ll"] = m["tee_ll"]    # later package rebuilds that move the tee do not move the truth
            h["zones_ll"] = [dict(lie=z["lie"], poly=z["poly_ll"], src="hand") for z in m["zones"]]
            h["zone_order"] = "given"
            h.pop("irons", None)                  # irons offered by the product rule on the hand map
    return pkg, hz


def hand_holes(cfg):
    """{key: model hole} of the hand map (only the mapped tee shots), product frames / tees / elevation."""
    import package as PK
    pkg, hz = hand_package(cfg)
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, os.path.dirname(cfg["package"]))) as td:
        p = os.path.join(td, "package.json")
        json.dump(pkg, open(p, "w"))
        C = PK.load(p, cfg["tees"])
        mp = os.path.join(td, "course.py")
        PK.write_module(C, mp)
        mod = PK.import_module(mp, name=f"sb_hand_{cfg['slug']}")
    return {k: v for k, v in mod.HOLES.items() if str(k) in hz["holes"]}


def hand_geometry(cfg, key, C, k_prod):
    """tee / green offset and corridor IoU per hazard: product package vs the hand-checked corridor map."""
    import render as R
    import tee_strategy as t
    hz = json.load(open(os.path.join(ROOT, cfg["hand"])))["holes"].get(key)
    if not hz or k_prod not in C.holes:
        return None
    fr = _hand_frame(R, hz["tee_ll"], hz["dot270_ll"])
    pf = R.Frame.from_json(C.frames[k_prod])
    p_tee = np.asarray(C.frames[k_prod]["tee_ll"], float)
    p_green = pf.px_to_ll([C.holes[k_prod]["green"]])[0]

    def yd(a, b):
        return float(np.linalg.norm(fr.ll_to_yds([a])[0] - fr.ll_to_yds([b])[0]))
    out = dict(tee_err=round(yd(p_tee, hz["tee_ll"]), 1),
               green_err=round(yd(p_green, hz["green_ll"]), 1) if hz.get("green_ll") else None)
    al, la = np.meshgrid(ALONG, LAT)
    ll = fr.yds_to_ll(np.c_[la.ravel(), -al.ravel()])
    ll = ll[_inside(hz["footprint_ll"], ll)]
    hand = np.array(["rough"] * len(ll), dtype=object)
    for z in hz["zones"]:
        if len(z["poly_ll"]) >= 3:
            hand[_inside(z["poly_ll"], ll)] = z["lie"]
    prod = t.lie_at(C.holes[k_prod], pf.ll_to_px(ll))
    iou = {}
    for name, lie in HAZ.items():
        A, B = hand == lie, prod == lie
        u = int(np.sum(A | B))
        if u:
            iou[name] = round(float(np.sum(A & B) / u), 3)
    fw = {}
    for lie in ("fairway",):
        A, B = hand == lie, prod == lie
        if int(np.sum(A | B)):
            fw[lie] = round(float(np.sum(A & B) / np.sum(A | B)), 3)
    out.update(iou=iou, iou_fairway=fw.get("fairway"), corridor_pts=int(len(ll)))
    return out


# ----------------------------------------------------------------------------- scoring
def agree(p, tr):
    """(same club, same-or-tie)."""
    same = p["pick"] == tr["pick"]
    tie = same or (tr.get("tie") and p["pick"] == tr.get("runner")) or \
        (p.get("tie") and p.get("runner") == tr["pick"])
    return bool(same), bool(tie)


def regret(p, tr):
    ev = tr.get("ev") or {}
    if p["pick"] not in ev or tr["pick"] not in ev:
        return None
    return round(float(ev[p["pick"]] - ev[tr["pick"]]), 4)


def aim_violations(res, course):
    bad = []
    for k, r in res.items():
        if abs(float(r.get("aim", 0))) > AIM_GUARD + 1e-6 and not r.get("check"):
            bad.append(f"{course} {k}: {r['pick']} aim {r['aim']:+.1f} yds without CHECK")
    return bad


def row_for(key, p, tr, alt=None, geo=None, tee_set=None):
    r = dict(hole=key, tee_set=tee_set, pick=p["pick"], aim=round(float(p["aim"]), 1), tie=bool(p.get("tie")),
             runner=p.get("runner"), margin=round(float(p.get("margin") or 0), 4), check=list(p.get("check") or []))
    if tr:
        s, st = agree(p, tr)
        r.update(truth=tr["pick"], truth_tie=bool(tr.get("tie")), truth_runner=tr.get("runner"), same=s,
                 same_or_tie=st, regret=regret(p, tr))
    if alt:
        s, st = agree(p, alt)
        r.update(hand_quick=alt["pick"], hand_quick_tie=bool(alt.get("tie")), same_hand_quick=s,
                 regret_hand_quick=regret(p, alt))
        if tr:      # the ceiling of quick mode: the hand map itself, through the product's decision, vs the truth
            r["hand_quick_same_truth"] = agree(alt, tr)[0]
    if geo:
        r.update(geo)
    return r


def summarise(rows, has_truth):
    S = dict(n=len(rows), checks=sum(1 for r in rows if r["check"]))
    if has_truth:
        sc = [r for r in rows if "same" in r]
        S["n_truth"] = len(sc)
        S["same"] = sum(r["same"] for r in sc)
        S["same_or_tie"] = sum(r["same_or_tie"] for r in sc)
        S["same_pct"] = round(S["same"] / len(sc), 3) if sc else None
        S["same_or_tie_pct"] = round(S["same_or_tie"] / len(sc), 3) if sc else None
        rg = [r["regret"] for r in sc if r.get("regret") is not None]
        S["mean_regret"] = round(float(np.mean(rg)), 4) if rg else None
        S["max_regret"] = round(float(np.max(rg)), 4) if rg else None
        hq = [r for r in rows if "same_hand_quick" in r]
        if hq:
            S["same_hand_quick"] = sum(r["same_hand_quick"] for r in hq)
            S["n_hand_quick"] = len(hq)
            rq = [r["regret_hand_quick"] for r in hq if r.get("regret_hand_quick") is not None]
            S["mean_regret_hand_quick"] = round(float(np.mean(rq)), 4) if rq else None
            cz = [r["hand_quick_same_truth"] for r in hq if "hand_quick_same_truth" in r]
            if cz:
                S["ceiling_quick"] = sum(cz)
    fl = [r for r in rows if "same_full" in r]
    if has_truth and fl:
        S["n_full"] = len(fl)
        S["same_full"] = sum(r["same_full"] for r in fl)
        S["same_or_tie_full"] = sum(r["same_or_tie_full"] for r in fl)
        rg = [r["regret_full"] for r in fl if r.get("regret_full") is not None]
        S["mean_regret_full"] = round(float(np.mean(rg)), 4) if rg else None
        S["max_regret_full"] = round(float(np.max(rg)), 4) if rg else None
        S["checks_full"] = sum(1 for r in fl if r.get("full_check"))
    # headline: full (Bayesian) mode where the truth is Bayesian and full mode ran on every scored hole, else quick
    full_ok = has_truth and fl and len(fl) == S.get("n_truth")
    S["headline"] = "full" if full_ok else "quick"
    if has_truth:
        for k in ("same", "same_or_tie", "mean_regret", "max_regret"):
            S[f"{k}_quick"] = S.get(k)
            S[f"{k}_head"] = S.get(f"{k}_full") if full_ok else S.get(k)
    g = [r for r in rows if "tee_err" in r]
    if g:
        S["tee10"] = sum(r["tee_err"] <= 10 for r in g)
        S["green10"] = sum(r["green_err"] is not None and r["green_err"] <= 10 for r in g)
        fw = [r["iou_fairway"] for r in g if r.get("iou_fairway") is not None]
        if fw:
            S["iou_fairway"] = round(float(np.mean(fw)), 3)
        S["n_geo"] = len(g)
        S["iou"] = {}
        for name in HAZ:
            v = [r["iou"][name] for r in g if name in r["iou"]]
            if v:
                S["iou"][name] = dict(mean=round(float(np.mean(v)), 3), n=len(v), pass06=sum(x > 0.6 for x in v))
    return S


def score_course(cfg, a, prev):
    t0 = time.time()
    log(f"== {cfg['name']} ({cfg['tees']})")
    res, C, secs = product_plan(cfg, cfg["tees"], n=a.n, workers=a.workers, from_out=a.from_out,
                                keys=set(a.holes.split(",")) if a.holes else None)
    out = dict(course=cfg["name"], slug=cfg["slug"], tees=C.tee_set, package=cfg["package"],
               package_commit=git("log", "-1", "--format=%h %cI", "--", cfg["package"]),
               source="committed out/decision.json" if a.from_out else f"product/decide.run quick n={a.n}",
               decision_s=secs)
    pj = os.path.join(ROOT, os.path.dirname(cfg["package"]), "out", "plan.json")
    if os.path.exists(pj):
        p = json.load(open(pj))
        out["last_plan"] = dict(built=p.get("built"), runtime_s=p.get("runtime_s"), mode=p.get("mode"),
                                decision_s=(p.get("stage_seconds") or {}).get("3 decision (quick)"))
    rows, extra_res = [], {}
    if cfg["truth"] == "spirit_hollow":
        sets = sh_truth_sets()
        final = final_truth()
        out["truth"] = "spirit_hollow/output/final_decision.json (hand map course.py; Black boxes; 2B/9B Gold)"
        out["truth_fp"] = sha(FINAL)
        out["truth_commit"] = git("log", "-1", "--format=%h %cI", "--", "spirit_hollow/output/final_decision.json")
        hq = None
        if not a.no_hand_quick:
            only = set(a.holes.split(",")) if a.holes else None
            hh = {k: v for k, v in sh_course().HOLES.items() if not only or str(k).rstrip("BF") in only}
            hq, _ = cached_hand_quick(prev, "spirit_hollow", hh, sha(SH_COURSE, os.path.join(PROD, "decide.py")),
                                      a.n, a.workers, a.dry_run or a.from_out)
        views = {cfg["tees"]: (res, C)}
        gold = sorted({sets[k] for k in sets if sets[k] != cfg["tees"]})
        for st in gold:
            ks = {k.rstrip("BF") for k in sets if sets[k] == st}
            if a.holes:
                ks &= set(a.holes.split(","))
            r2, C2, s2 = product_plan(cfg, st, keys=ks, n=a.n, workers=a.workers)
            views[st] = (r2, C2)
            extra_res[st] = r2
            if s2:
                out["decision_s"] = round((out["decision_s"] or 0) + s2, 1)
        full = {}
        if a.full:
            for st in sorted({sets[str(k)] for k in sh_course().HOLES}):
                ks = {str(k).rstrip("BF") for k in sh_course().HOLES if sets[str(k)] == st}
                if a.holes:
                    ks &= set(a.holes.split(","))
                if not ks:
                    continue
                rf, _, sf = product_plan(cfg, st, keys=ks, workers=a.workers, mode="full", S=a.full_S, N=a.full_N)
                full[st] = rf
                out["decision_full_s"] = round((out.get("decision_full_s") or 0) + (sf or 0), 1)
                log(f"  full mode ({st}, S={a.full_S} x N={a.full_N}): {len(rf)} holes in {sf:.0f} s")
            out["full_mode"] = dict(S=a.full_S, N=a.full_N)
            out["source"] += f" + full (decide.full_hole S={a.full_S} x N={a.full_N})"
        for key in sh_course().HOLES:
            key = str(key)
            st = sets.get(key, cfg["tees"])
            r_, C_ = views.get(st, (None, None))
            ref = key.rstrip("BF")
            if not r_ or ref not in r_ or key not in final:
                continue
            kp = int(ref) if ref.isdigit() else ref
            try:
                geo = sh_geometry(key, st, C_, kp)
            except Exception as e:                                 # noqa: BLE001
                geo = dict(geo_error=f"{type(e).__name__}: {e}")
            row = row_for(key, r_[ref], final[key], (hq or {}).get(key), geo, st)
            fr = (full.get(st) or {}).get(ref)
            if fr:
                sf_, stf = agree(fr, final[key])
                row.update(full_pick=fr["pick"], full_aim=round(float(fr["aim"]), 1), full_tie=bool(fr.get("tie")),
                           full_runner=fr.get("runner"), full_check=list(fr.get("check") or []), same_full=sf_,
                           same_or_tie_full=stf, regret_full=regret(fr, final[key]))
            rows.append(row)
    elif cfg["truth"] == "hand":
        hp = os.path.join(ROOT, cfg["hand"])
        if not os.path.exists(hp):
            raise SystemExit(f"no hand map {cfg['hand']}")
        out["truth"] = f"hand-checked corridor map {cfg['hand']} in the package, through the product's quick decision"
        out["truth_label"] = HAND_LABEL
        fp = sha(hp, os.path.join(PROD, "decide.py"), os.path.join(PROD, "package.py"))
        out["truth_fp"] = fp
        out["truth_commit"] = git("log", "-1", "--format=%h %cI", "--", cfg["hand"])
        hh = hand_holes(cfg)
        keys = [k for k in hh if str(k) in res]
        if a.holes:
            keys = [k for k in keys if str(k) in set(a.holes.split(","))]
        tr, _ = cached_hand_quick(prev, cfg["slug"], {k: hh[k] for k in keys}, fp, a.n, a.workers,
                                  a.dry_run or a.from_out)
        for k in res:
            k = str(k)
            kp = int(k) if k.isdigit() else k
            geo = None
            if k in {str(x) for x in keys}:
                try:
                    geo = hand_geometry(cfg, k, C, kp)
                except Exception as e:                             # noqa: BLE001
                    geo = dict(geo_error=f"{type(e).__name__}: {e}")
            rows.append(row_for(k, res[k], (tr or {}).get(k), geo=geo))
    elif cfg["truth"] == "mozingo":
        hand = HAND_HOLES
        out["truth"] = "hand map mozingo/tee_strategy.HOLES through the product's quick decision"
        fp = sha(MZ_HAND, os.path.join(PROD, "decide.py"))
        out["truth_fp"] = fp
        out["truth_commit"] = git("log", "-1", "--format=%h %cI", "--", "mozingo/tee_strategy.py")
        keys = [k for k in hand if str(k) in res]
        tr, cached = cached_hand_quick(prev, "mozingo", {k: hand[k] for k in keys}, fp, a.n, a.workers,
                                       a.dry_run or a.from_out)
        for k in keys:
            k = str(k)
            rows.append(row_for(k, res[k], (tr or {}).get(k)) if tr and k in tr else row_for(k, res[k], None))
    else:
        out["truth"] = "none (no hand map for this course yet)"
        out["truth_fp"] = None
        for k in res:
            rows.append(row_for(k, res[k], None))
    out["holes"] = rows
    out["summary"] = summarise(rows, cfg["truth"] is not None)
    out["aim_violations"] = aim_violations(res, cfg["name"]) + sum((aim_violations(r, f"{cfg['name']} ({st})")
                                                                    for st, r in extra_res.items()), [])
    if cfg["truth"] == "spirit_hollow" and a.full:
        out["aim_violations"] += sum((aim_violations(r, f"{cfg['name']} (full, {st})") for st, r in full.items()), [])
    out["seconds"] = round(time.time() - t0, 1)
    return out


HAND_HOLES = None
TRUTH_RAW = {}            # hand-quick truth computed or reused in this run -> scoreboard.json truth_cache


# ----------------------------------------------------------------------------- history + guards
def history_row(c, date, commit):
    S = c["summary"]
    return dict(date=date, commit=commit, course=c["slug"], truth_fp=c.get("truth_fp"), n=S.get("n_truth", S["n"]),
                headline=S.get("headline", "quick"),
                same=S.get("same_head", S.get("same")), same_or_tie=S.get("same_or_tie_head", S.get("same_or_tie")),
                same_quick=S.get("same"), same_full=S.get("same_full"),
                mean_regret=S.get("mean_regret_head", S.get("mean_regret")),
                max_regret=S.get("max_regret_head", S.get("max_regret")),
                tee10=S.get("tee10"), green10=S.get("green10"), n_geo=S.get("n_geo"),
                iou={k: v["mean"] for k, v in (S.get("iou") or {}).items()},
                checks=S.get("checks_full") if S.get("headline") == "full" else S["checks"],
                same_hand_quick=S.get("same_hand_quick"), ceiling_quick=S.get("ceiling_quick"),
                decision_s=c.get("decision_s"), source=c.get("source"))


REQUEST = os.path.join(CD, "requests", "qa_scoreboard.json")


def pending_rebaseline(history):
    """A one-shot re-baseline from course_data/requests/qa_scoreboard.json {"rebaseline": {"id", "reason"}}:
    applied by the first full run that has not recorded that id yet (the row carries baseline_reset)."""
    try:
        rb = json.load(open(REQUEST)).get("rebaseline")
    except Exception:                                              # noqa: BLE001
        return None
    if not rb or any(h.get("baseline_id") == rb.get("id") for h in history):
        return None
    return rb


def guards(courses, history, rebaseline=None):
    fails, notes = [], []
    for c in courses:
        fails += c["aim_violations"]
        S = c["summary"]
        cur = S.get("same_head", S.get("same"))
        if cur is None:
            continue
        if rebaseline:
            notes.append(f"{c['course']}: re-baselined ({rebaseline['reason']})")
            continue
        base = [h for h in history if h["course"] == c["slug"] and not h.get("regression") and h.get("same") is not None]
        if not base:
            notes.append(f"{c['course']}: no baseline yet")
            continue
        b = base[-1]
        if b.get("truth_fp") != c.get("truth_fp") or b.get("n") != S.get("n_truth"):
            notes.append(f"{c['course']}: truth changed since {b['date']} (baseline reset)")
            continue
        if b.get("headline", "quick") != S.get("headline", "quick"):
            notes.append(f"{c['course']}: headline mode {b.get('headline', 'quick')} -> {S.get('headline')} since "
                         f"{b['date']} (baseline reset)")
            continue
        if cur < b["same"] - 1:
            fails.append(f"{c['course']}: same club ({S.get('headline', 'quick')}) {cur}/{S['n_truth']} vs "
                         f"{b['same']}/{b['n']} on {b['date']} ({b['commit']}): dropped by {b['same'] - cur} holes (> 1)")
    return fails, notes


# ----------------------------------------------------------------------------- markdown
def pct(a, n):
    return "n/a" if a is None or not n else f"{a}/{n} ({a / n:.0%})"


def fmt(v, f="{:.3f}"):
    return "n/a" if v is None else f.format(v)


def write_md(board):
    from scoreboard_gaps import GAPS, NOTES                 # hand-written, ranked by expected club gain
    L = ["# Product scoreboard: any US course + tees -> hole-by-hole plan", "",
         f"Generated by `python3 course_data/qa/scoreboard.py` at {board['generated']} on commit `{board['commit']}` "
         f"(regenerated by `.github/workflows/scoreboard.yml` on every push to platform / product / vision / segment / "
         f"ob / tees code and after every package or plan rebuild). Target: same club as the truth on >= "
         f"{CLUB_BAR:.0%} of tee shots (18Birdies-level).", "",
         "| course (tees) | truth | **same club** (headline mode) | same or tie | mean / max regret (strokes) | "
         "quick mode: same club | same club as hand map, "
         "quick (map error only) | quick-mode ceiling (hand map vs truth) | tee <= 10 yds | "
         "green <= 10 yds | IoU trees | IoU long grass | IoU water | IoU OB | CHECK holes | decision runtime |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in board["courses"]:
        S = c["summary"]
        iou = S.get("iou") or {}

        def i(name):
            v = iou.get(name)
            return "n/a" if not v else f"{v['mean']:.2f} ({v['pass06']}/{v['n']} > 0.6)"
        tr = c.get("truth_label") or {"spirit_hollow": "final_decision.json", "mozingo_lake": HAND_LABEL}.get(c["slug"], "none")
        rt = f"{c['decision_s']:.0f} s" if c.get("decision_s") else "n/a"
        mapo = pct(S.get("same_hand_quick"), S.get("n_hand_quick")) if S.get("n_hand_quick") else \
            (pct(S.get("same"), S.get("n_truth")) if tr == HAND_LABEL else "n/a")
        if c.get("last_plan", {}).get("runtime_s"):
            rt += f" (plan.py {c['last_plan']['runtime_s'] / 60:.0f} min, {c['last_plan']['built']})"
        hd = S.get("headline", "quick")
        if c.get("decision_full_s"):
            rt += f"; full mode {c['decision_full_s'] / 60:.0f} min"
        chk = S.get("checks_full") if hd == "full" else S["checks"]
        L.append(f"| {c['course']} ({c['tees']}) | {tr} | **{pct(S.get('same_head', S.get('same')), S.get('n_truth'))}** "
                 f"({hd}) | {pct(S.get('same_or_tie_head', S.get('same_or_tie')), S.get('n_truth'))} | "
                 f"{fmt(S.get('mean_regret_head', S.get('mean_regret')))} / {fmt(S.get('max_regret_head', S.get('max_regret')))} | "
                 f"{pct(S.get('same'), S.get('n_truth'))} | {mapo} | {pct(S.get('ceiling_quick'), S.get('n_hand_quick'))} | "
                 f"{pct(S.get('tee10'), S.get('n_geo'))} | {pct(S.get('green10'), S.get('n_geo'))} | {i('trees')} | "
                 f"{i('long grass')} | {i('water')} | {i('ob')} | {chk}/{S['n']} | {rt} |")
    L += ["", "Notes: " + " ".join(NOTES), ""]
    if board.get("guards"):
        g = board["guards"]
        L += ["## Regression guards", "",
              ("**FAIL**: " + "; ".join(g["fails"])) if g["fails"] else "PASS: no club-agreement drop > 1 hole, "
              "no printed aim > 40 yds off the tee line without CHECK.", ""]
        if g.get("notes"):
            L += ["Baselines: " + "; ".join(g["notes"]), ""]
    L += ["## Biggest remaining gaps (ranked by expected club-agreement gain)", ""] + GAPS + [""]
    for c in board["courses"]:
        S = c["summary"]
        L += [f"## {c['course']} ({c['tees']}): per tee shot", "",
              f"Package `{c['package']}` ({c.get('package_commit') or '?'}); plan: {c['source']}; truth: {c['truth']}"
              + (f" ({c['truth_commit']})" if c.get("truth_commit") else "") + ".", ""]
        has_geo = any("tee_err" in r for r in c["holes"])
        hdr = "| hole | tee set | product pick (aim) | truth | same | regret |"
        sep = "|---|---|---|---|---|---|"
        has_full = any("full_pick" in r for r in c["holes"])
        if has_full:
            hdr += " product full mode | same (full) |"
            sep += "---|---|"
        if any("hand_quick" in r for r in c["holes"]):
            hdr += " hand map, quick |"
            sep += "---|"
        if has_geo:
            hdr += " tee err | green err | IoU trees / long grass / water / OB |"
            sep += "---|---|---|"
        hdr += " CHECK |"
        sep += "---|"
        L += [hdr, sep]
        for r in c["holes"]:
            pk = f"{r['pick']}{' (tie: ' + r['runner'] + ')' if r['tie'] else ''} ({r['aim']:+.0f})"
            tr = (r.get("truth", "-") + (f" (tie: {r['truth_runner']})" if r.get("truth_tie") else "")) if "truth" in r else "-"
            same = "-" if "same" not in r else ("yes" if r["same"] else ("tie" if r["same_or_tie"] else "**no**"))
            line = f"| {r['hole']} | {r.get('tee_set') or c['tees']} | {pk} | {tr} | {same} | {fmt(r.get('regret'))} |"
            if has_full:
                if "full_pick" in r:
                    fs = "yes" if r["same_full"] else ("tie" if r["same_or_tie_full"] else "**no**")
                    line += (f" {r['full_pick']}{' (tie: ' + str(r['full_runner']) + ')' if r['full_tie'] else ''} "
                             f"({r['full_aim']:+.0f}){' CHECK' if r.get('full_check') else ''} | {fs} |")
                else:
                    line += " - | - |"
            if "| hand map, quick |" in hdr:
                line += (f" {r.get('hand_quick', '-')}{' (tie)' if r.get('hand_quick_tie') else ''} |")
            if has_geo:
                io_ = r.get("iou") or {}
                line += (f" {r.get('tee_err', '-')} | {r.get('green_err', '-')} | "
                         + " / ".join(str(io_.get(n, "-")) for n in HAZ) + " |")
            line += (" " + "; ".join(r["check"])[:120] + " |") if r["check"] else " |"
            L.append(line)
        if S.get("same_hand_quick") is not None:
            L += ["", f"Same club as the hand map through the product's own quick decision (map error only): "
                      f"{S['same_hand_quick']}/{S['n_hand_quick']} (mean regret {fmt(S.get('mean_regret_hand_quick'))})."]
            if S.get("ceiling_quick") is not None:
                L.append(f"Ceiling of quick mode: the hand map itself through the quick decision picks the truth's club on "
                         f"{S['ceiling_quick']}/{S['n_hand_quick']} tee shots (model-settings error only).")
        L.append("")
    L += ["## History", "", "Same club / same or tie / regret are the headline mode of each row (quick until full mode "
          "ran; the quick and full counts are both listed). Notes record re-baselines and attributions.", "",
          "| date (UTC) | commit | course | same club (mode) | quick / full | same or tie | mean / max regret | tee10 | "
          "green10 | IoU trees / long grass / water / OB | CHECK | decision s | source | note |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for h in board["history"][-60:]:
        iou = h.get("iou") or {}
        qf = (f"{fmt(h.get('same_quick', h.get('same')), '{}')} / {fmt(h.get('same_full'), '{}')}"
              if h.get("same") is not None else "n/a")
        note = "; ".join(x for x in (("**re-baseline**: " + h["baseline_reset"]) if h.get("baseline_reset") else "",
                                     h.get("note") or "") if x)
        L.append(f"| {h['date']} | {h['commit']} | {h['course']} | {pct(h.get('same'), h.get('n'))} "
                 f"({h.get('headline', 'quick')}) | {qf} | "
                 f"{pct(h.get('same_or_tie'), h.get('n'))} | {fmt(h.get('mean_regret'))} / {fmt(h.get('max_regret'))} | "
                 f"{pct(h.get('tee10'), h.get('n_geo'))} | {pct(h.get('green10'), h.get('n_geo'))} | "
                 + " / ".join(fmt(iou.get(n), '{:.2f}') for n in HAZ)
                 + f" | {h.get('checks')} | {fmt(h.get('decision_s'), '{:.0f}')} | {h.get('source', '')}"
                 + (" **regression**" if h.get("regression") else "") + f" | {note} |")
    L += ["", "Definitions: see the docstring of `course_data/qa/scoreboard.py`. Same or tie = same club, or one plan "
          "calls the two clubs a tie (margin < 0.01 strokes) and the other plan picked that tie's runner-up. Regret = "
          "strokes lost on the hand map (truth EVs) by playing the product's club. IoU = landing corridor 220-340 yds "
          "along the hand tee line, +/-45 yds, lies as the model sees them; mean over holes where either map has the class."]
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(L) + "\n")


# ----------------------------------------------------------------------------- main
def main():
    global HAND_HOLES
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--courses", help="comma-separated slugs (default: all three)")
    ap.add_argument("--n", type=int, default=8000, help="swings per aim (the product's quick mode uses 8000)")
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--holes", help="only these hole refs (smoke tests)")
    ap.add_argument("--from-out", action="store_true", help="score the committed out/decision.json (no sims)")
    ap.add_argument("--no-hand-quick", action="store_true", help="Spirit Hollow: skip the hand-map quick run")
    ap.add_argument("--check", action="store_true", help="regression guards; exit 1 on a regression")
    ap.add_argument("--dry-run", action="store_true", help="print, do not write scoreboard.json / SCOREBOARD.md")
    ap.add_argument("--full", action="store_true",
                    help="also run the product's full Bayesian decision (decide.full_hole) where the truth is Bayesian "
                         "(Spirit Hollow); it becomes the headline there. ~11 min on 4 cores (Actions)")
    ap.add_argument("--full-S", type=int, default=64)
    ap.add_argument("--full-N", type=int, default=3000)
    ap.add_argument("--md-only", action="store_true", help="re-render SCOREBOARD.md from scoreboard.json")
    ap.add_argument("--adopt", help="CI: take this freshly computed scoreboard.json as current, keeping the union of "
                                    "its history and the history in course_data/qa/scoreboard.json (concurrent runs)")
    a = ap.parse_args()
    sys.path.insert(0, QA)
    prev = json.load(open(OUT_JSON)) if os.path.exists(OUT_JSON) else {}
    if a.adopt:
        new = json.load(open(a.adopt))
        seen, hist = set(), []
        for h in (prev.get("history") or []) + (new.get("history") or []):
            key = (h.get("date"), h.get("course"), h.get("commit"))
            if key not in seen:
                seen.add(key)
                hist.append(h)
        new["history"] = sorted(hist, key=lambda h: h.get("date") or "")
        new["truth_cache"] = {**(prev.get("truth_cache") or {}), **(new.get("truth_cache") or {})}
        with open(OUT_JSON, "w") as fh:
            json.dump(new, fh, indent=1, default=float)
        write_md(new)
        log(f"adopted {a.adopt}: {len(new['history'])} history rows")
        return 0
    if a.md_only:
        write_md(prev)
        log(f"wrote {os.path.relpath(OUT_MD, ROOT)}")
        return 0
    import tee_strategy as t
    HAND_HOLES = copy.deepcopy(t.HOLES)                    # Mozingo's hand map, before decide rebinds t.HOLES
    want = set(a.courses.split(",")) if a.courses else None
    courses = []
    for cfg in COURSES:
        if want and cfg["slug"] not in want:
            continue
        if cfg.get("hand") and not os.path.exists(os.path.join(ROOT, cfg["hand"])):
            log(f"== {cfg['name']}: no hand map yet ({cfg['hand']}): skipped")
            continue
        try:
            courses.append(score_course(cfg, a, prev))
        except SystemExit as e:
            courses.append(dict(course=cfg["name"], slug=cfg["slug"], tees=cfg["tees"], package=cfg["package"],
                                error=str(e), holes=[], summary=dict(n=0, checks=0), aim_violations=[],
                                source="-", truth="-"))
        c = courses[-1]
        log(json.dumps(c["summary"], default=float))
    date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    commit = git("rev-parse", "--short", "HEAD")
    history = list(prev.get("history") or [])
    partial = bool(a.holes or (want and len(want) < len(COURSES)) or a.n != 8000)
    rb = None if partial else pending_rebaseline(history)
    fails, notes = guards(courses, history, rb) if a.check else ([], [])
    cache = dict(prev.get("truth_cache") or {})    # hand-quick truth, recomputed only when the hand map or
    cache.update(TRUTH_RAW)                          # decide.py changes (fingerprint fp)
    board = dict(schema="scoreboard/1", generated=date + " UTC", commit=commit, courses=courses,
                 guards=dict(fails=fails, notes=notes) if a.check else prev.get("guards"),
                 truth_cache=cache, history=history)
    if not partial:
        reg = {f.split(":")[0] for f in fails}
        for c in courses:
            row = history_row(c, date, commit)
            row["regression"] = c["course"] in reg or any(c["course"] in f for f in fails)
            if rb:
                row.update(baseline_id=rb.get("id"), baseline_reset=rb.get("reason"))
            history.append(row)
    for f in fails:
        log("REGRESSION:", f)
    for n_ in notes:
        log("note:", n_)
    if a.dry_run or partial:
        log("(dry run / partial run: scoreboard.json and SCOREBOARD.md not written)")
        for c in courses:
            for r in c["holes"]:
                log("  ", {k: v for k, v in r.items() if k not in ("check",)})
    else:
        with open(OUT_JSON, "w") as fh:
            json.dump(board, fh, indent=1, default=float)
        write_md(board)
        log(f"wrote {os.path.relpath(OUT_JSON, ROOT)}, {os.path.relpath(OUT_MD, ROOT)}")
    return 1 if (a.check and fails) else 0


if __name__ == "__main__":
    sys.exit(main())
