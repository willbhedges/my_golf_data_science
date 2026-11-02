"""Golfer native-grass confirm tap: "Native (unmown) grass along hole 7?" -> Left / Right / Both / None.

Why (course_data/mapper/EVAL_BLIND.md, round 3 follow-up and round 4): on mixed parkland / native courses the
photo-only mapper finds a fraction of the native the golfer knows is there (Eagle Bend: owner says 2 L+R, 3 L, 5 L,
6 L; the mapper found 2 L), and one-sided native can be worse than none. The yes / no per side is what moves the
plan, not the exact edge (a mapper edge at the photo mowing line and the truth's 10-yd convention score the same).
So the product asks the golfer, per hole, on the few holes where the answer changes the club or the aim.

    import native_confirm as NC
    pri = NC.priors(edits_json, agent_pkg, frames)                 # per hole, per side: p(native) from the mapper
    qs = NC.select(agent_pkg, frames, pri, NC.EBDecider("Gold"))   # the questions worth a tap (<= CAP per course)
    pkg2 = NC.apply_answers(agent_pkg, {q["hole"]: "L" for q in qs}, frames, pri)
    # or item by item: NC.apply_answer(h, item, "both") (product/apply_answers.py does this for type "native")

Answer -> map (per side, in the hole's corridor frame: x = yds right of the corridor-set tee line):
  native on side S  long grass (lie "native", src "golfer:native") on that side of the tee line, along A0..A1 and
                    out to REACH yds, beyond max(MIN_BEYOND, the mapper's mown-rough width on that side, capped at
                    MAX_BEYOND) of the package fairway / first cut / green (the truth's "native_beyond" convention:
                    box minus the fairway grown by the rough width). Existing native stays (union).
    ... "well out"  (optional `out` = the "yes" sides where it starts well out): the island rule. The native
                    already drawn on that side stays as drawn and the band is added only along the stretches
                    (ISLAND_STEP-yd along slices) with nothing native within ISLAND_NEAR yds of the fairway (Mariah
                    Hills: native as islands 25+ yds out). Measured (mapper/EVAL_BLIND.md, 2026-11-02 island fix):
                    on every "yes" (ISLAND_MODE "always") it costs Prairie Dunes, whose mapped native is near but
                    gappy (pooled <= 4 questions worse); as a golfer's second tap it changes nothing at <= 4 / <= 6
                    questions, so the pages do not ask it. apply_answers.py takes it if a golfer says so.
  no native on S    every native zone (auto / vision / agent) on that side of the tee line is cut away.
Precedence is the package's (native lowest): trees, water, sand, OB and the fairway stay on top.

Which holes to ask (select): for each corridor hole the planner re-decides the four answer states (L, R, both,
none; every hole of the course in one batch per state) and the current map. A hole is a candidate when some state
with prior >= MIN_STATE_P changes the club or moves the aim > AIM_TOL yds. Value of the tap =
sum_s p(s) * regret_s(current plan) (strokes lost by playing today's plan in the world where the answer is s,
on that state's map). Ask the top CAP holes by value with value >= MIN_VOI. Priors p(native on a side) come from
the mapper's per-side verdict (edits.json holes.<n>.long_grass) and its native edits (side_prior): a one-sided
native verdict raises the other side's prior (Eagle Bend 2), "uncertain" raises a "none", "woods" / "pond" lowers it.
"""
from __future__ import annotations

import copy
import itertools
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
for _p in (os.path.join(CD, "mapper"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import common as M  # noqa: E402

A0, A1 = 130.0, 400.0          # along window of the inserted native (truth_sets_v2 native_beyond a0 / a1)
REACH = 65.0                   # lateral reach of the inserted native (yds off the tee line)
MIN_BEYOND, MAX_BEYOND = 10.0, 25.0
ERASE_ALONG = (0.0, 480.0)     # "none": the native cut away on that side over this along range ...
ERASE_REACH = 150.0            # ... and out to here
SRC = "golfer:native"
SIDES = ("L", "R")
ANSWERS = ("L", "R", "both", "none")
CAP = 4                        # questions per course (the review page's red-card budget is 4 too)
AIM_TOL = 10.0                 # yds: an aim change beyond this is a plan change (error_budget.AIM_TOL)
MIN_VOI = 0.01                 # strokes: below the plan's tie band a tap is not worth asking
MIN_STATE_P = 0.05
ISLAND_NEAR = 40.0             # yds off the fairway edge: native already drawn this close on a side keeps that stretch
ISLAND_STEP = 10.0             # along slices of the island test
ISLAND_MIN_YD2 = 20.0          # native in a slice smaller than this does not count (slivers)
# where the island rule applies: "out" = on the sides the golfer says the native starts well out from the fairway
# (the second tap); "always" = on every "yes" side (measured worse pooled: EVAL_native_confirm.md); "never"
ISLAND_MODE = os.environ.get("NATIVE_ISLAND_MODE", "out")


def sides_of(answer):
    """"L" / "R" / "both" / "none" -> {"L": bool, "R": bool}."""
    a = str(answer).strip().lower()
    if a not in ("l", "r", "both", "none"):
        raise ValueError(f"native answer {answer!r} not in {ANSWERS}")
    return {"L": a in ("l", "both"), "R": a in ("r", "both")}


def answer_of(sides):
    L, R = bool(sides.get("L")), bool(sides.get("R"))
    return "both" if L and R else "L" if L else "R" if R else "none"


# ----------------------------------------------------------------------------- geometry (corridor frame)
def _sgn(side):
    return -1.0 if side == "L" else 1.0


def _xy_geom(fj, ring_ll):
    xy = M.ll_to_xy(fj, ring_ll)
    return M._poly(xy)


def mown_xy(fj, h):
    from shapely.ops import unary_union
    fw = [M._poly(z["xy"]) for z in M.auto_zones_xy(fj, h, ("fairway", "first_cut", "green"))]
    return unary_union(fw).buffer(0) if fw else None


def native_xy(fj, h):
    from shapely.ops import unary_union
    g = [_xy_geom(fj, M.ring_ll(z.get("poly"))) for z in h.get("zones_ll") or []
         if z.get("lie") == "native" and len(M.ring_ll(z.get("poly"))) >= 3]
    return unary_union(g).buffer(0) if g else None


def rough_width(fj, h, side, a0=180, a1=330, step=10, reach=60):
    """The mapper's mown-rough width on one side: median lateral gap from the fairway edge to the native already on
    the map on that side (None when there is none). Same sampling as write_layers.native_gaps."""
    from shapely.geometry import LineString
    nat, mown = native_xy(fj, h), mown_xy(fj, h)
    if nat is None or nat.is_empty:
        return None
    s = _sgn(side)
    d = []
    for a in range(a0, a1 + 1, step):
        ln = LineString([(0, a), (s * reach, a)])
        it = nat.intersection(ln)
        if it.is_empty:
            continue
        xs = [abs(c[0]) for p in getattr(it, "geoms", [it]) for c in p.coords]
        fx = 0.0
        fw = mown.intersection(ln) if mown is not None else None
        if fw is not None and not fw.is_empty:
            for p in getattr(fw, "geoms", [fw]):
                cx = [abs(c[0]) for c in p.coords]
                if cx and min(cx) < 15:
                    fx = max(fx, max(cx))
        d.append(max(0.0, min(xs) - fx))
    return float(np.median(d)) if d else None


def beyond_width(w_est):
    return float(min(MAX_BEYOND, max(MIN_BEYOND, w_est if w_est is not None else MIN_BEYOND)))


def insert_geom(fj, h, side, w):
    """Native on one side: the half box (tee line out to REACH, A0..A1) minus the fairway / first cut / green
    grown by w yds (shapely, corridor frame)."""
    x0, x1 = (-REACH, 0.0) if side == "L" else (0.0, REACH)
    return M.shape_geom({"beyond_fairway": dict(w=w, side=side, a0=A0, a1=A1, x0=x0, x1=x1)}, fj, h)


def covered_along(fj, h, side, near=ISLAND_NEAR, step=ISLAND_STEP, min_yd2=ISLAND_MIN_YD2):
    """[(a0, a1, x_inner)] along slices of A0..A1 where native is already drawn on that side within `near` yds of
    the package fairway / first cut / green (of the tee line when the hole has none); x_inner = yds off the tee
    line of that native's inner edge in the slice."""
    from shapely.geometry import box
    nat = native_xy(fj, h)
    if nat is None or nat.is_empty:
        return []
    mown = mown_xy(fj, h)
    s = _sgn(side)
    half = box(-REACH - near, A0, 0.0, A1) if side == "L" else box(0.0, A0, REACH + near, A1)
    zone = (mown.buffer(near) if mown is not None and not mown.is_empty else box(-near, A0, near, A1)).intersection(half)
    near_nat = nat.intersection(zone)
    if near_nat.is_empty:
        return []
    out, a = [], A0
    while a < A1 - 1e-6:
        b = min(A1, a + step)
        sl = box(min(0.0, s * (REACH + near)), a, max(0.0, s * (REACH + near)), b)
        q = near_nat.intersection(sl)
        if q.area >= min_yd2:
            xin = min(abs(c[0]) for p in M.polys_of(q, 0.0) for c in p.exterior.coords) if M.polys_of(q, 0.0) else 0.0
            out.append((int(a) if float(a).is_integer() else a, int(b) if float(b).is_integer() else b, round(xin, 1)))
        a = b
    return out


def band_spec(fj, h, widths=None, step=ISLAND_STEP):
    """The answer geometry in a compact, frame-relative form the app applies itself (confirm_engine.js nativeBand):
    per ISLAND_STEP-yd along slice of A0..A1 and side, the fairway / first cut / green edge (yds off the tee line,
    0 = none), the inner edge of native already drawn within ISLAND_NEAR yds of it (0 = none: the island rule),
    and the rough width
    (widths {side: w or None} as apply_answer takes them; None = the map's own rough width)."""
    from shapely.geometry import LineString
    mown = mown_xy(fj, h)
    n = int(round((A1 - A0) / step))
    out = dict(a0=A0, step=step, n=n, reach=REACH, fw={}, near={}, w={})
    for side in SIDES:
        sg = _sgn(side)
        cov = {a: x for a, _, x in covered_along(fj, h, side, step=step)}
        fw, near = [], []
        for i in range(n):
            a = A0 + i * step
            mid = a + step / 2
            e = 0.0
            if mown is not None and not mown.is_empty:
                it = mown.intersection(LineString([(0, mid), (sg * REACH, mid)]))
                for p in getattr(it, "geoms", [it]) if not it.is_empty else []:
                    cx = [abs(c[0]) for c in p.coords]
                    if cx and min(cx) < 15:
                        e = max(e, max(cx))
            fw.append(round(e, 1))
            k = int(a) if float(a).is_integer() else a
            near.append(max(cov[k], 0.1) if k in cov else 0)
        out["fw"][side], out["near"][side] = fw, near
        ww = rough_width(fj, h, side) if widths is None else widths.get(side)      # as apply_answer(s) does
        out["w"][side] = round(beyond_width(ww), 1)
    return out


def band_rects(spec, answer, out=None, mode=None):
    """band_spec + an answer (+ the sides where it starts well out) -> {side: [[a0, a1, x_in, x_out], ...] (native
    added) or None (native removed)}. The rule of set_side on slices: a "yes" side gets a rectangle beyond
    max(MIN_BEYOND, w) of the fairway edge out to REACH on every slice (on an island side: every slice without
    native already near); a "no" side clears that side."""
    want, isl = sides_of(answer), island_sides(out, mode)
    out = {}
    for side in SIDES:
        if not want[side]:
            out[side] = None
            continue
        sg, rs = _sgn(side), []
        for i in range(spec["n"]):
            x_in = spec["fw"][side][i] + spec["w"][side]
            if isl[side] and spec["near"][side][i]:
                continue
            if x_in >= spec["reach"]:
                continue
            a = spec["a0"] + i * spec["step"]
            rs.append([a, a + spec["step"], round(sg * x_in, 1), round(sg * spec["reach"], 1)])
        out[side] = rs
    return out


def erase_box(side):
    from shapely.geometry import box
    a0, a1 = ERASE_ALONG
    return box(-ERASE_REACH, a0, 0.0, a1) if side == "L" else box(0.0, a0, ERASE_REACH, a1)


def island_sides(out=None, mode=None):
    """{side: island rule applies} for the golfer's "starts well out" sides `out` ("L" / "R" / "both" / None)."""
    mode = mode or ISLAND_MODE
    if mode == "always":
        return {"L": True, "R": True}
    if mode == "never" or not out:
        return {"L": False, "R": False}
    return sides_of(out)


def set_side(h, fj, side, native, w=None, tag=None, islands=False):
    """Apply one side's answer to the package hole h (in place). -> sq yds added (native) or removed (none).
    islands: the native starts well out on this side; keep the mapped native as drawn and add the band only
    along the stretches with nothing native within ISLAND_NEAR yds of the fairway."""
    zones = list(h.get("zones_ll") or [])
    if native:
        g = insert_geom(fj, h, side, beyond_width(w))
        if islands:
            from shapely.geometry import box
            for a0, a1, _ in covered_along(fj, h, side):         # keep the mapper's islands: no band beside them
                g = g.difference(box(-ERASE_REACH, a0, ERASE_REACH, a1))
        n = 0.0
        for p in M.polys_of(g, 4.0):
            ring = M.xy_to_ll(fj, np.asarray(p.exterior.coords)[:-1])
            zones.append(dict(lie="native", poly=[[round(float(x), 7), round(float(y), 7)] for x, y in ring],
                              src=SRC, verified="golfer", p=1.0, side=side, answer=tag))
            n += p.area
        h["zones_ll"] = zones
        return n
    box = erase_box(side)
    out, cut = [], 0.0
    for z in zones:
        r = M.ring_ll(z.get("poly"))
        if z.get("lie") != "native" or len(r) < 3:
            out.append(z)
            continue
        g = _xy_geom(fj, r)
        if not g.intersects(box):
            out.append(z)
            continue
        rest = g.difference(box)
        cut += g.area - rest.area
        for p in M.polys_of(rest, 4.0):
            ring = M.xy_to_ll(fj, np.asarray(p.exterior.coords)[:-1])
            out.append(dict(z, poly=[[round(float(x), 7), round(float(y), 7)] for x, y in ring], golfer_clipped=True))
    h["zones_ll"] = out
    return -cut


def apply_answer(h, item, answer, out=None):
    """One hole, one answer ("L" / "R" / "both" / "none"; out: the "yes" sides where it starts well out from the
    fairway, "L" / "R" / "both" / None). item: a select() question (needs "frame" and "widths") or
    {"frame": fj, "widths": {...}}. -> {side: sq yds added (+) / removed (-)}."""
    fj = item["frame"] if "frame" in (item.get("frame") or {}) else {"frame": item["frame"]}
    want, isl = sides_of(answer), island_sides(out)
    res = {}
    for s in SIDES:
        res[s] = round(set_side(h, fj, s, want[s], (item.get("widths") or {}).get(s), tag=answer,
                                islands=isl[s] and want[s]), 1)
    h.setdefault("verification", {})["native_sides"] = dict(answer=answer_of(want), src="golfer",
                                                             out=answer_of({k: isl[k] and want[k] for k in SIDES}))
    return res


def apply_answers(pkg, answers, frames, widths=None, outs=None):
    """{ref: answer} -> new package (input untouched). widths {ref: {side: w}} (default: the map's own); outs
    {ref: "L" / "R" / "both"} the sides where the golfer says the native starts well out."""
    p = copy.deepcopy(pkg)
    for ref, ans in answers.items():
        if ref not in p["holes"] or ref not in frames:
            continue
        h = p["holes"][ref]
        w = (widths or {}).get(ref) or {s: rough_width(frames[ref], pkg["holes"][ref], s) for s in SIDES}
        apply_answer(h, {"frame": frames[ref], "widths": w}, ans, (outs or {}).get(ref))
    return p


# ----------------------------------------------------------------------------- priors from the mapper
def side_prior(verdict=None, has_edit=False, edit_conf=None, other_native=False):
    """p(native on this side) from the mapper's verdict text and its native edits on that side."""
    v = (verdict or "").strip().lower()
    unsure = "uncertain" in v or "unsure" in v
    if v.startswith("native") or (not v and has_edit):
        p = {"high": 0.9, "medium": 0.75, "low": 0.6}.get(edit_conf or "medium", 0.75)
        return p
    if v.startswith("none"):
        if unsure:
            p = 0.4
        elif any(w in v for w in ("woods", "pond", "water", "houses", "road")) and "rough" not in v:
            p = 0.1
        else:
            p = 0.25
    else:                                   # no verdict (round-3 mappers): only the edits are known
        p = 0.3
    if other_native:                        # one-sided native: the other side is suspect (Eagle Bend 2)
        p = max(p, 0.4) if p > 0.1 else p
    return p


def edit_sides(fj, h_agent, feats):
    """{side: confidence} of the agent's native adds on that hole (from agent_zones.geojson features)."""
    out = {}
    for f in feats:
        pr = f.get("properties") or {}
        if pr.get("op") != "add" or pr.get("lie") != "native":
            continue
        geom = f["geometry"]
        rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [c[0] for c in geom["coordinates"]]
        for r in rings:
            xy = M.ll_to_xy(fj, r)
            s = "L" if float(np.mean(xy[:, 0])) < 0 else "R"
            c = pr.get("confidence") or "medium"
            rank = {"low": 0, "medium": 1, "high": 2}
            if s not in out or rank.get(c, 1) > rank.get(out[s], 1):
                out[s] = c
    return out


def priors(edits, agent_zones, frames, pkg=None):
    """{ref: {"L": {p, verdict, edit, w}, "R": ...}} for every framed hole. edits = edits.json (dict or None),
    agent_zones = agent_zones.geojson (dict or None), pkg = the map the planner uses (for the rough width)."""
    eh = (edits or {}).get("holes") or {}
    by = {}
    for f in (agent_zones or {}).get("features") or []:
        by.setdefault(str((f.get("properties") or {}).get("hole")), []).append(f)
    out = {}
    for ref, fj in frames.items():
        lg = (eh.get(ref) or {}).get("long_grass") or {}
        es = edit_sides(fj, None, by.get(ref, []))
        nat = {s: str(lg.get(s) or "").lower().startswith("native") or (not lg.get(s) and s in es) for s in SIDES}
        row = {}
        for s in SIDES:
            o = "R" if s == "L" else "L"
            p = side_prior(lg.get(s), s in es, es.get(s), other_native=nat[o] and not nat[s])
            w = rough_width(fj, pkg["holes"][ref], s) if pkg is not None and ref in pkg["holes"] else None
            row[s] = dict(p=round(p, 3), verdict=lg.get(s), edit=es.get(s), w=None if w is None else round(w, 1))
        out[ref] = row
    return out


def state_p(pr, answer):
    want = sides_of(answer)
    return float(np.prod([pr[s]["p"] if want[s] else 1.0 - pr[s]["p"] for s in SIDES]))


# ----------------------------------------------------------------------------- selection
def plan_changed(a, b, tol=AIM_TOL):
    """Two plans {pick, aim} differ: another club, or the aim moved > tol yds (same frame: aim is lateral yds)."""
    return a["pick"] != b["pick"] or abs(float(a["aim"]) - float(b["aim"])) > tol


def select(pkg, frames, pri, decider, cap=CAP, min_voi=MIN_VOI, holes=None):
    """-> questions, sorted by value: [{id, type "native", hole, question, answers, prior {L, R}, widths, frame,
    value, plans {state: "club aim"}, regret {state: strokes}, asked}] for every candidate hole (asked = True for
    the top `cap` with value >= min_voi). decider(pkgs: {name: package}) -> {name: {ref: plan}} and
    decider.regret(name, ref, plan) -> EV(plan on that state's map) - EV(that state's own plan)."""
    refs = [r for r in frames if r in pkg["holes"] and (holes is None or r in holes)]
    widths = {r: {s: pri[r][s].get("w") for s in SIDES} for r in refs}
    states = {"current": pkg}
    for a in ANSWERS:
        states[a] = apply_answers(pkg, {r: a for r in refs}, frames, widths)
    plans = decider(states)
    qs = []
    for r in refs:
        cur = plans["current"].get(r)
        if cur is None:
            continue
        ps = {a: state_p(pri[r], a) for a in ANSWERS}
        changes = [a for a in ANSWERS if r in plans[a] and ps[a] >= MIN_STATE_P and plan_changed(cur, plans[a][r])]
        reg = {}
        for a in ANSWERS:
            if r in plans[a]:
                reg[a] = 0.0 if not plan_changed(cur, plans[a][r], tol=0.0) else max(0.0, float(decider.regret(a, r, cur)))
        voi = sum(ps[a] * reg.get(a, 0.0) for a in ANSWERS)
        qs.append(dict(id=f"native_{r}", type="native", hole=r,
                       question=f"Hole {r}: is there native (long, unmown) grass along the landing area?",
                       answers=list(ANSWERS), prior={s: pri[r][s]["p"] for s in SIDES},
                       verdict={s: pri[r][s].get("verdict") for s in SIDES},
                       widths={s: beyond_width(widths[r][s]) for s in SIDES}, frame=frames[r]["frame"],
                       geom=band_spec(frames[r], pkg["holes"][r], widths[r]),
                       value=round(voi, 4), changes=changes, state_p={a: round(v, 3) for a, v in ps.items()},
                       plans={a: f"{plans[a][r]['pick']} {plans[a][r]['aim']:+.0f}" for a in ["current", *ANSWERS] if r in plans[a]},
                       regret={a: round(v, 4) for a, v in reg.items()}, asked=False))
    qs.sort(key=lambda q: -q["value"])
    n = 0
    for q in qs:
        if n < cap and q["changes"] and q["value"] >= min_voi:
            q["asked"] = True
            n += 1
    return qs


class EBDecider:
    """The planner as the error budget runs it (decide.quick_hole, seed 31, common random numbers, cached by hole
    fingerprint): decider({name: package}) -> {name: {ref: {pick, aim, ev}}}; regret(name, ref, plan)."""

    def __init__(self, tee_set, n=4000, workers=1, cache=None, cache_path=None):
        p = os.path.join(CD, "platform")
        if p not in sys.path:
            sys.path.append(p)
        import error_budget as E
        self.E, self.S, self.n, self.workers = E, tee_set, n, workers
        self.cache = {} if cache is None else cache
        if cache_path:
            E.CACHE_JSON = cache_path
        self.holes = {}

    def __call__(self, pkgs):
        E = self.E
        jobs, keyed = {}, {}
        for name, pk in pkgs.items():
            C, H = E.load_models(E.prepare(pk, self.S), self.S, f"nc_{name}")
            for k, h in H.items():
                f = E.fp(h)
                jobs[f] = h
                keyed[(name, str(k))] = f
                self.holes[(name, str(k))] = h
        res = E.run_decisions(jobs, self.n, self.workers, self.cache)
        out = {name: {} for name in pkgs}
        for (name, ref), f in keyed.items():
            r = res[f]
            out[name][ref] = dict(pick=r["pick"], aim=float(r["aim"]), ev=float(r["ev"]))
        self._plans = out
        return out

    def regret(self, name, ref, plan):
        h = self.holes[(name, ref)]
        ck = f"rg|{self.E.fp(h)}|{plan['pick']}|{round(float(plan['aim']), 2)}|{self.n}"
        if ck not in self.cache:
            self.cache[ck] = self.E.truth_ev(h, plan["pick"], float(plan["aim"]), self.n)
        return self.cache[ck] - self._plans[name][ref]["ev"]


def items_for_review(qs):
    """The asked questions as review/1 items (product/verify.py schema; apply_answers.py type "native")."""
    keep = ("id", "type", "hole", "question", "answers", "prior", "widths", "frame", "value", "plans", "geom")
    return [dict({k: q[k] for k in keep}, severity="red") for q in qs if q.get("asked")]
