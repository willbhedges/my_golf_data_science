"""The 2-minute pre-round check: which auto-built map items could change the plan, and what to ask the golfer.

  python3 course_data/product/verify.py --package course_data/packages/veenker/package.json --tees Blue
  python3 course_data/product/verify.py --request course_data/requests/verify_veenker.json
  options: --holes 7,10  --n 1500  --workers 4  --no-crops  --out <dir>

Writes <out> (default course_data/packages/<slug>/out/review/):
  review.json   every review item (schema review/1): hole, type, severity, a plain-words question, a NAIP crop
                (JPEG data URI, item outlined) with the overlay geometry in crop px, the answers the golfer can give
                and what each does to the plan (precomputed), plus the per-hole base plan and frame
  index.html    the phone review page (review_page.py + review_page_template.html), no network calls
  review.md     the same list as a table

What is an item (research/auto_course_lookup.md section 8, "show the golfer only what changes the decision"):
  tee      the chosen set's tee on every tee-shot hole; tested by moving it back / forward along the tee line and
           left / right, by 20 / 10 yds scaled by how unsure the platform is (p_wrong / 0.2, clipped 0.5-1.5:
           confidence 0.8 -> 20/10 yds, 0.9 -> 10/5, a walk-back -> 30/15). The page shows all tees on one
           "tee sheet" card.
  hazard   penal polygons (trees, long grass, water, sand, OB) of one lie on one side of the landing corridor
           (150-340 yds, +/-45 yds of the plan's aim), from any source (vision, OSM, the course boundary) unless
           the golfer verified them; grouped as a golfer would name them ("the trees left"); tested by removing
           the group and by moving its edge 10 yds toward and away from the fairway (sideways, or along the line
           for a hazard across the corridor)
  fairway  each side's fairway edge in the corridor; tested 10 yds narrower and 10 yds wider
  cut      no first cut mapped beside the fairway (OSM rarely has one); tested by adding a 6-yd first cut
  gap      a side of the 200-330 band with nothing penal mapped 25-65 yds off the aim; tested by adding trees
  check    a hole the absurd-aim guard flags (decide.aim_problems): unconstrained best vs best printable aim
Par 3s carry only a tee item (the plan plays them by the card yardage), green unless card vs measured > 15 yds.

Sensitivity: the strategy model at the quick plan's central settings (decide.set_prior_means), N = 1500 swings
with fixed seeds (common random numbers), coarse aims (5 yds, refined to 2.5 around the best). Base: every club
over the hole's aim range with the guard. Each perturbation re-runs best_aim for the pick and the runner-up only,
within +/-20 yds of their base aims. Per outcome:
  regret   what playing the printed plan (old club, old target) costs in the perturbed world vs its new best
  red      the pick changes or its aim moves > 5 yds (target compared in the base frame) AND regret >= 0.02
           (the plan's own tie band is 0.01; below 0.02 a flip is a coin toss). `strict` keeps the plain rule.
  amber    a change that fails the regret bar, or the hole's best EV moves > 0.01
Per item: p_wrong = prior probability the map item is wrong (PRIORS: tee 1 - platform confidence, +0.15 when
card and measured differ > 5 yds; vision trees 0.4 / long grass 0.5 (QA corridor IoU 0.27 / 0.15); OSM hazards
0.15; course-boundary OB 0.4; OSM fairway edge 0.3; missing first cut 0.5; unmapped side 0.2; CHECK 0.5) and
exp_regret = p_wrong x the worst regret over its tested answers. The post-pass (assign_severity, re-runnable from
review.json without simulating) makes an item red when one of its outcomes is red and exp_regret >= 0.005, then
keeps at most RED_CARDS = 4 red cards per course by exp_regret (all red tees count as one card, the tee sheet);
the rest become amber ("over the budget"). Everything else amber or green as its outcomes are.
Runtime ~2-4 min a course on Actions (4 workers).
"""
import argparse
import base64
import copy
import datetime as dt
import io
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _product_package():
    """product/package.py (platform/ has a package.py too; whichever loaded first owns the name 'package')."""
    m = sys.modules.get("package")
    if m is not None and os.path.dirname(os.path.abspath(getattr(m, "__file__", "") or "")) == HERE:
        return m
    import importlib.util
    name = "product_package"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, "package.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


PK = _product_package()                             # (puts course_data/imagery + mozingo on sys.path)
import decide                                       # noqa: E402
import render as R                                  # noqa: E402

t = decide.t

SCHEMA = "review/1"
N_SWINGS = 1500
SEED = 31
ALONG = (150.0, 340.0)        # landing corridor (yds along the tee line)
HALF = 45.0                   # +/- yds of the base aim
GAP_ALONG = (200.0, 330.0)
GAP_LAT = (25.0, 65.0)        # yds off the aim line on that side
GAP_EMPTY = 0.10              # strip share covered by penal zones below which the side is "unmapped"
MIN_AREA = 40.0               # sq yds of a hazard group inside the corridor to be worth a test
EDGE = 10.0                   # hazard / fairway edge move (yds)
TEE_ALONG, TEE_ACROSS = 20.0, 10.0   # at p_wrong 0.2 (platform confidence 0.8); scaled by p_wrong / 0.2
TEE_SCALE = (0.5, 1.5)
CUT_W = 6.0                   # first-cut width added by the "cut" test (yds)
AIM_RED = 5.0
EV_AMBER = 0.01
REGRET_RED = 0.02             # a change is red only if the printed play now costs >= this (tie band is 0.01)
ER_RED = 0.005                # ... and p_wrong x worst regret >= this
ER_AMBER = 0.002              # amber needs p_wrong x worst regret >= this (else the answer cannot matter)
RED_CARDS = 4                 # red card budget per course (all tees = one card)
PRIORS = {"tee": None, "vision:recovery": 0.4, "vision:native": 0.5, "vision:water": 0.3, "vision:sand": 0.3,
          "vision:ob": 0.4, "osm": 0.15, "boundary": 0.4, "fairway": 0.3, "cut": 0.5, "gap": 0.2, "check": 0.5}
PENAL = ("recovery", "native", "water", "sand", "ob")
WORDS = {"recovery": "trees", "native": "long grass", "water": "water", "sand": "sand", "ob": "out of bounds"}
SEV_RANK = {"red": 0, "amber": 1, "green": 2}


def log(*a):
    print(*a, flush=True)


# ----------------------------------------------------------------------------- package -> model hole
def is_uncertain(z):
    if z.get("verified"):
        return False
    src = str(z.get("src", ""))
    return src.startswith("vision") or "inferred" in src or float(z.get("p", 1.0)) < 1.0


def zone_prior(z, lie):
    """Prior probability a mapped zone's edge is materially wrong (see PRIORS)."""
    src = str(z.get("src", ""))
    if z.get("verified"):
        return 0.0
    if src.endswith("course_boundary"):
        return PRIORS["boundary"]
    if src.startswith("vision") or "inferred" in src:
        return PRIORS.get(f"vision:{lie}", 0.4)
    return PRIORS["osm"]


def tee_prior(ent, resid):
    if ent.get("verified"):
        return 0.0
    p = 1.0 - float(ent.get("confidence") if ent.get("confidence") is not None else 0.7)
    if resid is not None and resid > 5:
        p += 0.15
    if ent.get("method") == "walkback":
        p = max(p, 0.5)
    return float(np.clip(p, 0.05, 0.7))


def tee_entry(h, tee_set):
    return PK._tee_entry(h, tee_set)


def frame_for(h, tee_set, tee_ll=None):
    t_ll, _, length, ent = tee_entry(h, tee_set)
    if tee_ll is not None:
        t_ll = [float(tee_ll[0]), float(tee_ll[1])]
    green_ll = PK._ll(h.get("green_ll"))
    par = int(h.get("par") or 4)
    aim_ll, how = PK._tee_line_mod().aim_point(t_ll, h.get("hole_line_ll"), green_ll,
                                               float(length) if length else None, par)
    return R.Frame(t_ll, aim_ll, ppy=PK.PPY, tee_px=PK.TEE_PX, proj=PK.PROJ), t_ll, green_ll, length, ent


def hole_model(h, tee_set, tee_ll=None, zones_ll=None, window=True):
    """A tee_strategy hole dict (pixel frame, as product/package.load builds it) + its Frame. tee_ll / zones_ll
    override the package's (the perturbations). window: keep only zones near the tee-shot (exact for the
    simulation, which never reaches past ~400 yds, and much faster)."""
    fr, t_ll, green_ll, length, ent = frame_for(h, tee_set, tee_ll)
    raw = h.get("zones_ll") if zones_ll is None else zones_ll
    zones = []
    for z, (lie, poly) in zip(PK._zone_meta(raw), PK._zones(raw)):
        if not poly or len(poly) < 3:
            continue
        boundary = lie == "ob" and str(z.get("src", "")).endswith("course_boundary")
        lie = PK.LIE_MAP.get(lie, lie)
        if lie not in PK.MODEL_LIES:
            continue
        q = fr.ll_to_px(np.array(poly, float)[:, :2])
        if window:
            yd = (q - np.array(PK.TEE_PX)) / PK.PPY            # x right, y = -along
            if yd[:, 1].max() < -420 or yd[:, 1].min() > 15 or yd[:, 0].max() < -130 or yd[:, 0].min() > 130:
                continue
        zones.append(("ob_boundary" if boundary else lie, [(float(x), float(y)) for x, y in q]))
    zones = PK.order_zones(zones, PK.zone_order_mode(None, h))
    green_px = tuple(float(v) for v in fr.ll_to_px([green_ll])[0])
    par = int(h.get("par") or 4)
    L = int(round(float(length))) if length else int(round(np.hypot(*(np.array(green_px) - PK.TEE_PX)) / PK.PPY))
    hd = dict(par=par, length=L, tee=PK.TEE_PX, dot270=(PK.TEE_PX[0], PK.TEE_PX[1] - 270 * PK.PPY),
              green=green_px, zones=zones, aim_min=-60, aim_max=60)
    line_ll = h.get("hole_line_ll")
    if line_ll and len(line_ll) >= 2:
        hd["play_line"] = [(float(x), float(y)) for x, y in
                           fr.ll_to_px(np.array([p[:2] for p in line_ll] + [green_ll], float))]
    for extra in ("extra_roll", "irons"):
        if h.get(extra) is not None:
            hd[extra] = h[extra]
    if PK.irons_offered(h, hd):
        hd["irons"] = True
    e = PK._elev(ent.get("elevation") or h.get("elevation"))
    if e:
        hd["elev"] = e
    return hd, fr


# ----------------------------------------------------------------------------- decision (coarse, fast)
KEY = "v"          # the one hole bound into tee_strategy at a time


def _bind(hd):
    t.HOLES = {KEY: hd}


def _ev(club, aim, z):
    return float(t.simulate(KEY, club, float(aim), z=z)[3].mean())


def _limits(club):
    return (-25.0, 45.0) if club in decide._IRONS0 else (-60.0, 60.0)


def search(club, z, center=0.0, half=60.0, step=5.0, guard=True):
    """(aim, ev) of the best (printable if guard) aim: a coarse grid, widened if the best sits on its edge,
    then refined by +/- step/2. Also returns the unconstrained best (raw_aim, raw_ev)."""
    lo, hi = _limits(club)
    cache = {}

    def ev(a):
        a = round(float(a), 2)
        if a not in cache:
            cache[a] = _ev(club, a, z)
        return cache[a]

    grid = [a for a in np.arange(center - half, center + half + 1e-6, step) if lo - 1e-6 <= a <= hi + 1e-6]
    if not grid:
        grid = [float(np.clip(center, lo, hi))]
    for a in grid:
        ev(a)
    for _ in range(6):                                   # widen while the raw best is on the grid edge
        keys = sorted(cache)
        b = min(cache, key=cache.get)
        if b == keys[0] and b - step >= lo - 1e-6:
            ev(b - step)
        elif b == keys[-1] and b + step <= hi + 1e-6:
            ev(b + step)
        else:
            break

    def ok(a):
        return not guard or not decide.aim_problems(KEY, club, a)

    for _ in range(2):                                   # refine around the raw and the printable best
        b = min(cache, key=cache.get)
        good = [a for a in cache if ok(a)]
        bp = min(good, key=cache.get) if good else None
        for c in {b, bp} - {None}:
            for a in (c - step / 2, c + step / 2):
                if lo - 1e-6 <= a <= hi + 1e-6:
                    ev(a)
    raw = min(cache, key=cache.get)
    good = [a for a in cache if ok(a)]
    best = min(good, key=cache.get) if good else raw
    return dict(aim=float(best), ev=float(cache[best]), printable=bool(good),
                raw_aim=float(raw), raw_ev=float(cache[raw]), n_sims=len(cache))


def base_plan(hd, z):
    _bind(hd)
    res = {c: search(c, z) for c in decide.clubs_for(KEY)}
    printable = [c for c in res if res[c]["printable"]] or list(res)
    order = sorted(printable, key=lambda c: res[c]["ev"])
    pick = order[0]
    runner = order[1] if len(order) > 1 else min((c for c in res if c != pick), key=lambda c: res[c]["ev"])
    raw_club = min(res, key=lambda c: res[c]["raw_ev"])
    return dict(pick=pick, runner=runner, aim=res[pick]["aim"], ev=res[pick]["ev"],
                margin=res[runner]["ev"] - res[pick]["ev"], clubs=res,
                raw=dict(club=raw_club, aim=res[raw_club]["raw_aim"], ev=res[raw_club]["raw_ev"]))


def target_lateral(fr, club, aim, base_fr):
    """Lateral yds (base frame) of the club's carry target at `aim` in frame fr."""
    carry = decide._carry(club)
    ll = fr.yds_to_ll([[float(aim), -carry]])
    return float(base_fr.ll_to_yds(ll)[0][0])


def replan(hd, fr, base, base_fr, z, half=20.0):
    """Re-run best_aim for the base pick and runner-up only (within +/-half of their base aims)."""
    _bind(hd)
    out, old_aim = {}, {}
    for c in (base["pick"], base["runner"]):
        b = base["clubs"][c]
        # centre on the base target (re-expressed in this frame when the tee moved)
        ctr = b["aim"]
        if fr is not base_fr:
            ctr = b["aim"] + (b["aim"] - target_lateral(fr, c, b["aim"], base_fr))
        old_aim[c] = ctr
        out[c] = search(c, z, center=float(np.round(ctr / 2.5) * 2.5), half=half)
    new = min(out, key=lambda c: out[c]["ev"] if out[c]["printable"] else out[c]["ev"] + 10)
    aim_b = target_lateral(fr, new, out[new]["aim"], base_fr) if fr is not base_fr else out[new]["aim"]
    d_ev = out[new]["ev"] - base["ev"]
    club_changed = new != base["pick"]
    shift = aim_b - base["aim"]
    # regret: what playing the printed plan (old club, old target) costs in this world vs the new best
    regret = max(0.0, _ev(base["pick"], old_aim[base["pick"]], z) - out[new]["ev"])
    changed = club_changed or abs(shift) > AIM_RED
    strict = "red" if changed else ("amber" if abs(d_ev) > EV_AMBER else "green")
    sev = outcome_severity(changed, regret, d_ev)
    return dict(pick=new, aim=round(aim_b, 1), aim_frame=round(out[new]["aim"], 1), ev=round(out[new]["ev"], 4),
                d_ev=round(d_ev, 4), club_changed=club_changed, aim_shift=round(shift, 1), severity=sev,
                strict=strict, regret=round(regret, 4), evs={c: round(v["ev"], 4) for c, v in out.items()})


def outcome_severity(changed, regret, d_ev):
    return "red" if changed and regret >= REGRET_RED else ("amber" if changed or abs(d_ev) > EV_AMBER else "green")


def aim_words(a):
    a = float(a)
    if abs(a) < 2.5:
        return "on the line"
    return f"{abs(a):.0f} yds {'right' if a > 0 else 'left'}"


def change_text(label, base, o):
    if o is None:
        return "No change to the plan."
    if o["club_changed"]:
        return f"Hole {label}: {base['pick']} → {o['pick']}, aim {aim_words(o['aim'])}."
    if abs(o["aim_shift"]) > AIM_RED:
        d = o["aim_shift"]
        return f"Hole {label}: still {o['pick']}, aim moves {abs(d):.0f} yds {'right' if d > 0 else 'left'}."
    if abs(o["d_ev"]) > EV_AMBER:
        return (f"Hole {label}: still {o['pick']} {aim_words(o['aim'])}; the hole plays "
                f"{abs(o['d_ev']):.2f} strokes {'harder' if o['d_ev'] > 0 else 'easier'}.")
    return f"No change: {o['pick']} {aim_words(o['aim'])}."


def worst(sevs):
    return min(sevs, key=lambda s: SEV_RANK[s]) if sevs else "green"


# ----------------------------------------------------------------------------- geometry helpers (base yard frame)
def to_yd(fr, poly_ll):
    """[[x right, along], ...] in yds."""
    q = fr.ll_to_yds(np.array(poly_ll, float)[:, :2])
    return np.c_[q[:, 0], -q[:, 1]]


def to_ll(fr, pts_xa):
    pts_xa = np.asarray(pts_xa, float)
    return fr.yds_to_ll(np.c_[pts_xa[:, 0], -pts_xa[:, 1]]).tolist()


def shapely_poly(pts):
    from shapely.geometry import Polygon
    p = Polygon(pts)
    if not p.is_valid:
        p = p.buffer(0)
    return p


def box(x0, x1, a0, a1):
    from shapely.geometry import box as _box
    return _box(min(x0, x1), min(a0, a1), max(x0, x1), max(a0, a1))


def hazard_groups(h, fr, base):
    """{(lie, side): {idx: [...], area, along: (a0, a1), axis, toward}} for uncertain penal polygons in the corridor."""
    aim = base["aim"]
    corr = box(aim - HALF, aim + HALF, *ALONG)
    groups = {}
    for i, z in enumerate(h.get("zones_ll") or []):
        if not isinstance(z, dict) or z.get("verified"):
            continue
        lie = PK.LIE_MAP.get(z.get("lie"), z.get("lie"))
        if lie not in PENAL or len(z.get("poly") or []) < 3:
            continue
        try:
            p = shapely_poly(to_yd(fr, z["poly"]))
            inter = p.intersection(corr)
        except Exception:                                   # noqa: BLE001
            continue
        if inter.is_empty or inter.area < 1.0:
            continue
        minx, mina, maxx, maxa = inter.bounds
        if minx < aim - 3 and maxx > aim + 3 and (maxx - minx) > 30:
            side = "across"
        else:
            side = "left" if inter.centroid.x < aim else "right"
        g = groups.setdefault((lie, side), dict(idx=[], area=0.0, a0=1e9, a1=-1e9, inner=[], pw=0.0, geo=[]))
        g["idx"].append(i)
        g["area"] += inter.area
        g["pw"] += inter.area * zone_prior(z, lie)
        g["geo"].append(inter)
        g["a0"], g["a1"] = min(g["a0"], mina), max(g["a1"], maxa)
        g["inner"].append(maxx if side == "left" else minx if side == "right" else mina)
    out = {}
    for (lie, side), g in groups.items():
        if g["area"] < MIN_AREA:
            continue
        toward = {"left": (1.0, 0.0), "right": (-1.0, 0.0), "across": (0.0, -1.0)}[side]
        if side == "left":
            edge = max(g["inner"]) - aim
        elif side == "right":
            edge = min(g["inner"]) - aim
        else:
            edge = min(g["inner"])
        from shapely.ops import unary_union
        out[(lie, side)] = dict(g, toward=toward, edge=float(edge), p_wrong=round(g["pw"] / g["area"], 3),
                                clip=unary_union(g.pop("geo")))
    return out


def shifted(h, fr, idx, vec, d):
    zl = copy.deepcopy(h["zones_ll"])
    for i in idx:
        xa = to_yd(fr, zl[i]["poly"]) + np.array(vec) * d
        zl[i]["poly"] = to_ll(fr, xa)
    return zl


def removed(h, idx):
    s = set(idx)
    return [z for i, z in enumerate(h["zones_ll"]) if i not in s]


def densify(xa, step=5.0):
    out = []
    n = len(xa)
    for i in range(n):
        a, b = xa[i], xa[(i + 1) % n]
        k = max(1, int(np.hypot(*(b - a)) // step))
        out += [a + (b - a) * j / k for j in range(k)]
    return np.array(out)


def fairway_idx(h):
    return [i for i, z in enumerate(h.get("zones_ll") or [])
            if isinstance(z, dict) and z.get("lie") == "fairway" and not z.get("verified") and len(z.get("poly") or []) >= 3]


def fairway_sides(h, fr, base):
    """{side: dict(edge, along, area, clip)} for fairway in the corridor on each side of the aim."""
    from shapely.ops import unary_union
    aim = base["aim"]
    polys = {i: shapely_poly(to_yd(fr, h["zones_ll"][i]["poly"])) for i in fairway_idx(h)}
    own = box(aim - 10, aim + 10, *ALONG)                  # this hole's fairway crosses the aim line
    idx = [i for i, p in polys.items() if p.intersects(own)] or \
          [i for i, p in polys.items() if p.intersects(box(aim - HALF, aim + HALF, *ALONG))]
    if not idx:
        return {}, idx
    fw = unary_union([polys[i] for i in idx])
    out = {}
    for side, x0, x1 in (("left", aim - HALF - 30, aim), ("right", aim, aim + HALF + 30)):
        g = fw.intersection(box(x0, x1, *ALONG))
        if g.is_empty or g.area < 50:
            continue
        minx, a0, maxx, a1 = g.bounds
        if (side == "left" and minx <= x0 + 1) or (side == "right" and maxx >= x1 - 1):
            continue                                       # the edge is beyond the corridor
        out[side] = dict(edge=float((minx if side == "left" else maxx) - aim), along=[round(a0), round(a1)],
                         area=g.area, clip=g)
    return out, idx


def fairway_moved(h, fr, idx, side, d, aim):
    """Fairway edge on `side` moved d yds toward the centre (d > 0 narrower), full inside the corridor and
    tapered to 0 over 25 yds outside it."""
    zl = copy.deepcopy(h["zones_ll"])
    for i in idx:
        xa = densify(to_yd(fr, zl[i]["poly"]))
        a = xa[:, 1]
        w = np.clip(1 - np.maximum(ALONG[0] - a, a - ALONG[1]) / 25.0, 0, 1)
        m = ((xa[:, 0] < aim) & (xa[:, 0] > aim - HALF - 30) if side == "left"
             else (xa[:, 0] > aim) & (xa[:, 0] < aim + HALF + 30))
        xa[m, 0] += (d if side == "left" else -d) * w[m]
        zl[i]["poly"] = to_ll(fr, xa)
    return zl


def holefree(g, depth=0):
    """Polygons without holes covering g (split by bbox halves where a piece has interiors)."""
    from shapely.geometry import Polygon
    parts = list(getattr(g, "geoms", [g]))
    out = []
    for p in parts:
        if p.is_empty or p.geom_type != "Polygon" or p.area < 2:
            continue
        if not p.interiors or depth > 6:
            out.append(Polygon(p.exterior))
            continue
        minx, miny, maxx, maxy = p.bounds
        if maxx - minx > maxy - miny:
            halves = (box(minx, (minx + maxx) / 2, miny, maxy), box((minx + maxx) / 2, maxx, miny, maxy))
        else:
            halves = (box(minx, maxx, miny, (miny + maxy) / 2), box(minx, maxx, (miny + maxy) / 2, maxy))
        for hb in halves:
            out += holefree(p.intersection(hb), depth + 1)
    return out


def cut_polys(h, fr):
    """A CUT_W-yd first cut around the fairway in the tee-shot window, not over penal zones; hole-free, in yds."""
    from shapely.ops import unary_union
    zl = h.get("zones_ll") or []
    if any(isinstance(z, dict) and z.get("lie") == "first_cut" for z in zl):
        return []
    fw = [shapely_poly(to_yd(fr, z["poly"])) for z in zl
          if isinstance(z, dict) and z.get("lie") == "fairway" and len(z.get("poly") or []) >= 3]
    if not fw:
        return []
    pen = [shapely_poly(to_yd(fr, z["poly"])) for z in zl if isinstance(z, dict) and len(z.get("poly") or []) >= 3
           and PK.LIE_MAP.get(z.get("lie"), z.get("lie")) in PENAL]
    f = unary_union(fw)
    ring = f.buffer(CUT_W).difference(f)
    if pen:
        ring = ring.difference(unary_union(pen))
    ring = ring.intersection(box(-150, 150, ALONG[0] - 50, ALONG[1] + 40))
    return [np.array(p.exterior.coords)[:-1] for p in holefree(ring) if p.area >= 4]


def gap_strip(base, side):
    aim = base["aim"]
    sg = -1 if side == "left" else 1
    x0, x1 = aim + sg * GAP_LAT[0], aim + sg * GAP_LAT[1]
    return [[x0, GAP_ALONG[0]], [x1, GAP_ALONG[0]], [x1, GAP_ALONG[1]], [x0, GAP_ALONG[1]]]


def gap_sides(h, fr, base):
    """Sides of the landing band with (almost) nothing penal mapped 25-65 yds off the aim."""
    from shapely.ops import unary_union
    polys = []
    for z in h.get("zones_ll") or []:
        lie = PK.LIE_MAP.get(z.get("lie"), z.get("lie")) if isinstance(z, dict) else None
        if lie in PENAL and len(z.get("poly") or []) >= 3:
            try:
                polys.append(shapely_poly(to_yd(fr, z["poly"])))
            except Exception:                               # noqa: BLE001
                pass
    u = unary_union(polys) if polys else None
    out = []
    done = h.get("verification") or {}
    for side in ("left", "right"):
        if done.get(f"open_{side}"):
            continue
        s = shapely_poly(gap_strip(base, side))
        cov = (u.intersection(s).area / s.area) if u is not None else 0.0
        if cov < GAP_EMPTY:
            out.append((side, round(cov, 3)))
    return out


# ----------------------------------------------------------------------------- crops
_IMG = {}


def imagery_for(pkg, pkg_path):
    d = ((pkg.get("imagery") or {}).get("dir") or ((pkg.get("sources") or {}).get("imagery") or {}).get("dir"))
    slug = (pkg.get("course") or {}).get("slug")
    cands = [d and (d if os.path.isabs(d) else os.path.join(ROOT, d)),
             os.path.join(os.path.dirname(os.path.abspath(pkg_path)), "imagery"),
             slug and os.path.join(CD, "imagery", slug)]
    for c in cands:
        if c and os.path.isdir(c):
            if c not in _IMG:
                try:
                    _IMG[c] = R.Imagery(c)
                except Exception as e:                      # noqa: BLE001
                    log(f"  ! imagery {c}: {type(e).__name__}: {e}")
                    _IMG[c] = None
            return _IMG[c]
    return None


CROP = {"tee": dict(x=(-45.0, 45.0), along=(-45.0, 75.0), s=3.0),
        "landing": dict(x=(-75.0, 75.0), along=(110.0, 350.0), s=2.0)}


def crop_spec(kind, base_aim):
    c = dict(CROP["tee" if kind == "tee" else "landing"])
    if kind != "tee":
        c["x"] = (base_aim + c["x"][0], base_aim + c["x"][1])
    return c


def to_crop(spec, pts_xa):
    pts_xa = np.asarray(pts_xa, float)
    s = spec["s"]
    return np.c_[(pts_xa[:, 0] - spec["x"][0]) * s, (spec["along"][1] - pts_xa[:, 1]) * s]


def render_crop(img, base_fr, spec, outline_polys=(), quality=70):
    """JPEG data URI of the NAIP crop (base frame, tee line straight up), item outlines burned in thin."""
    from PIL import Image, ImageDraw
    s = spec["s"]
    W = int(round((spec["x"][1] - spec["x"][0]) * s))
    H = int(round((spec["along"][1] - spec["along"][0]) * s))
    fr = R.Frame(base_fr.tee_ll, base_fr.aim_ll, ppy=s, tee_px=(-spec["x"][0] * s, spec["along"][1] * s),
                 proj=base_fr.proj, size=(W, H))
    if img is not None:
        arr, _ = R.render(fr, img)
        im = Image.fromarray(arr[..., :3])
    else:
        im = Image.new("RGB", (W, H), (90, 110, 90))
    dr = ImageDraw.Draw(im)
    for poly in outline_polys:
        q = [tuple(map(float, p)) for p in poly]
        if len(q) >= 3:
            dr.line(q + [q[0]], fill=(255, 255, 255), width=1)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return dict(img="data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii"), w=W, h=H, s=s,
                x0=spec["x"][0], along_top=spec["along"][1])


def r1(a):
    return [[round(float(x), 1), round(float(y), 1)] for x, y in a]


# ----------------------------------------------------------------------------- per hole
def hole_label(k):
    return str(k)


def verify_hole(job):
    """All review items of one hole. job = (ref, h, tee_set, n, seed, crops?, pkg_path, pkg_imagery_meta)."""
    ref, h, tee_set, n, seed, want_crops, pkg_path, pkg_meta = job
    t0 = time.time()
    decide.set_prior_means()
    z = decide._z(n, seed)
    par = int(h.get("par") or 4)
    t_ll, _, length, ent = tee_entry(h, tee_set)
    tee_info = dict(method=ent.get("method"), confidence=ent.get("confidence"),
                    card=ent.get("card_yards"), measured=ent.get("measured_yards"))
    resid = (abs(float(tee_info["measured"]) - float(tee_info["card"]))
             if tee_info["measured"] is not None and tee_info["card"] is not None else None)
    img = imagery_for(pkg_meta, pkg_path) if want_crops else None
    items = []
    if par == 3 or t_ll is None:
        sev = "amber" if (resid or 0) > 15 or (ent.get("method") == "walkback") else "green"
        items.append(dict(id=f"{ref}-tee", hole=str(ref), type="tee", severity=sev, par=3,
                          question=f"Is the {tee_set} tee on hole {ref} where we have it?",
                          detail=_tee_detail(tee_set, tee_info, resid) + " Par 3: the plan plays the card yardage.",
                          confidence=tee_info, options=[], tested=False))
        return dict(ref=str(ref), par=par, items=items, seconds=round(time.time() - t0, 1))

    hd, fr = hole_model(h, tee_set)
    base = base_plan(hd, z)
    base_out = dict(pick=base["pick"], aim=round(base["aim"], 1), ev=round(base["ev"], 4), runner=base["runner"],
                    margin=round(base["margin"], 4), raw=base["raw"])
    label = hole_label(ref)

    # (a) tee -------------------------------------------------------------------------------------
    p_tee = tee_prior(ent, resid)
    if ent.get("verified"):
        items.append(dict(id=f"{ref}-tee", hole=str(ref), type="tee", severity="green", par=par,
                          question=f"Is the {tee_set} tee here?", detail="Checked by you.", confidence=tee_info,
                          options=[], tested=False, p_wrong=0.0))
        moves = {}
    else:
        sc = float(np.clip(p_tee / 0.2, *TEE_SCALE))
        ta, tx = round(TEE_ALONG * sc, 1), round(TEE_ACROSS * sc, 1)
        moves = {"back": (0.0, -ta), "forward": (0.0, ta), "left": (-tx, 0.0), "right": (tx, 0.0)}
    samples = []
    for name, (dx, da) in moves.items():
        new_tee = to_ll(fr, [[dx, da]])[0]
        hd2, fr2 = hole_model(h, tee_set, tee_ll=new_tee)
        o = replan(hd2, fr2, base, fr, z)
        samples.append(dict(name=name, dx=dx, dy=da, outcome=o, text=change_text(label, base, o)))
    if samples:
        items.append(dict(id=f"{ref}-tee", hole=str(ref), type="tee", par=par, p_wrong=p_tee,
                          question=f"Is the {tee_set} tee here?",
                          detail=_tee_detail(tee_set, tee_info, resid), confidence=tee_info, tested=True,
                          options=[dict(answer="confirm", label="Looks right", outcome=None, text=change_text(label, base, None)),
                                   dict(answer="moved", label="Move the tee", drag="free", samples=samples)]))

    # (b) hazards -----------------------------------------------------------------------------------
    for (lie, side), g in sorted(hazard_groups(h, fr, base).items(), key=lambda kv: -kv[1]["area"]):
        o_rm = replan(*hole_model(h, tee_set, zones_ll=removed(h, g["idx"])), base, fr, z)
        samples = []
        for name, d in (("closer", EDGE), ("farther", -EDGE)):
            o = replan(*hole_model(h, tee_set, zones_ll=shifted(h, fr, g["idx"], g["toward"], d)), base, fr, z)
            samples.append(dict(name=name, shift=d, outcome=o, text=change_text(label, base, o)))
        opts = [dict(answer="confirm", label="Looks right", outcome=None, text=change_text(label, base, None)),
                dict(answer="absent", label="Not there", outcome=o_rm, text=change_text(label, base, o_rm)),
                dict(answer="moved", label="Edge is elsewhere", drag="axis", samples=samples)]
        a0, a1 = max(g["a0"], ALONG[0]), min(g["a1"], ALONG[1])
        what = WORDS.get(lie, lie)
        srcs = sorted({str(h["zones_ll"][i].get("src")) for i in g["idx"]})
        if side == "across":
            q = f"{'Are' if lie == 'recovery' else 'Is'} there {what} across the fairway at {a0:.0f}-{a1:.0f} yds?"
        else:
            q = (f"{'Do' if lie == 'recovery' else 'Does'} the {what} on the {side} come this close to the fairway "
                 f"({abs(g['edge']):.0f} yds {side} of the aim at {a0:.0f}-{a1:.0f} yds)?")
        items.append(dict(id=f"{ref}-{lie}-{side}", hole=str(ref), type="hazard", par=par, p_wrong=g["p_wrong"],
                          lie=lie, side=side, question=q,
                          detail=f"Mapped from {', '.join(srcs)}. {len(g['idx'])} outline"
                                 f"{'s' if len(g['idx']) > 1 else ''} in the landing area.",
                          zone_idx=g["idx"], zone_fp=[[round(float(v), 7) for v in h["zones_ll"][i]["poly"][0][:2]] for i in g["idx"]],
                          toward=list(g["toward"]), edge=round(g["edge"], 1), along=[round(a0), round(a1)],
                          area=round(g["area"]), options=opts, tested=True, _clip=g["clip"]))

    # (c) fairway edges and first cut -----------------------------------------------------------------
    sides, fidx = fairway_sides(h, fr, base)
    for side, f in sides.items():
        samples = []
        for name, d in (("narrower", EDGE), ("wider", -EDGE)):
            o = replan(*hole_model(h, tee_set, zones_ll=fairway_moved(h, fr, fidx, side, d, base["aim"])), base, fr, z)
            samples.append(dict(name=name, shift=d, outcome=o, text=change_text(label, base, o)))
        items.append(dict(id=f"{ref}-fairway-{side}", hole=str(ref), type="fairway", par=par, side=side,
                          p_wrong=PRIORS["fairway"],
                          question=(f"Is the {side} edge of the fairway here ({abs(f['edge']):.0f} yds {side} of the aim "
                                    f"at {f['along'][0]}-{f['along'][1]} yds)?"),
                          detail="Mapped from OpenStreetMap; mowing lines move and OSM fairways are often drawn loosely.",
                          zone_idx=fidx, zone_fp=[[round(float(v), 7) for v in h["zones_ll"][i]["poly"][0][:2]] for i in fidx],
                          toward=[1.0, 0.0] if side == "left" else [-1.0, 0.0], edge=round(f["edge"], 1),
                          along=f["along"], tested=True, _clip=f["clip"],
                          options=[dict(answer="confirm", label="Looks right", outcome=None, text=change_text(label, base, None)),
                                   dict(answer="moved", label="Edge is elsewhere", drag="axis", samples=samples)]))
    cut = cut_polys(h, fr)
    if cut:
        zl = list(h["zones_ll"]) + [dict(lie="first_cut", poly=to_ll(fr, c), src="verify:cut_test", p=0.0) for c in cut]
        o = replan(*hole_model(h, tee_set, zones_ll=zl), base, fr, z)
        items.append(dict(id=f"{ref}-cut", hole=str(ref), type="cut", par=par, p_wrong=PRIORS["cut"],
                          question="Is there a first cut (a strip of shorter rough) along the fairway?",
                          detail=f"No first cut is mapped, so the plan treats everything off the fairway as rough. "
                                 f"Tested with a {CUT_W:.0f}-yd first cut.",
                          cut_xa=[r1(c) for c in cut], tested=True,
                          options=[dict(answer="confirm", label="No, rough to the edge", outcome=None,
                                        text=change_text(label, base, None)),
                                   dict(answer="present", label="Yes, a first cut", outcome=o, text=change_text(label, base, o))]))

    # (d) unmapped sides ----------------------------------------------------------------------------
    for side, cov in gap_sides(h, fr, base):
        strip = gap_strip(base, side)
        zl = list(h["zones_ll"]) + [dict(lie="recovery", poly=to_ll(fr, strip), src="verify:gap_test", p=0.0)]
        o = replan(*hole_model(h, tee_set, zones_ll=zl), base, fr, z)
        items.append(dict(id=f"{ref}-gap-{side}", hole=str(ref), type="gap", par=par, side=side, p_wrong=PRIORS["gap"],
                          question=f"Is it open on the {side} at {GAP_ALONG[0]:.0f}-{GAP_ALONG[1]:.0f} yds, "
                                   f"or are there trees or long grass?",
                          detail=f"Nothing is mapped {GAP_LAT[0]:.0f}-{GAP_LAT[1]:.0f} yds {side} of the aim there "
                                 f"(OpenStreetMap and the tree/long-grass layer are both empty; {cov:.0%} covered).",
                          strip_xa=r1(strip), tested=True,
                          options=[dict(answer="confirm", label="Open, as mapped", outcome=None,
                                        text=change_text(label, base, None)),
                                   dict(answer="present", label="Trees or long grass", outcome=o,
                                        text=change_text(label, base, o))]))

    # (e) absurd-aim guard ------------------------------------------------------------------------------
    raw = base["raw"]
    if raw["club"] != base["pick"] or abs(raw["aim"] - base["aim"]) > AIM_RED:
        _bind(hd)
        why = decide.aim_problems(KEY, raw["club"], raw["aim"])
        gain = max(0.0, base["ev"] - raw["ev"])           # what the printable plan gives up if the line is playable
        o_raw = dict(pick=raw["club"], aim=round(raw["aim"], 1), aim_frame=round(raw["aim"], 1), ev=round(raw["ev"], 4),
                     d_ev=round(raw["ev"] - base["ev"], 4), club_changed=raw["club"] != base["pick"],
                     aim_shift=round(raw["aim"] - base["aim"], 1), regret=round(gain, 4),
                     severity=outcome_severity(True, gain, raw["ev"] - base["ev"]), strict="red", evs={})
        items.append(dict(id=f"{ref}-check", hole=str(ref), type="check", par=par, p_wrong=PRIORS["check"],
                          question=(f"Could you play {raw['club']} {aim_words(raw['aim'])} of the tee line "
                                    f"({decide._carry(raw['club']):.0f} yds out)? Is that ground playable?"),
                          detail="The best line on the map was rejected by the plan's safety check: "
                                 + ("; ".join(why) or "it sits on the edge of the search") + ".",
                          raw=raw, tested=True,
                          options=[dict(answer="playable", label="Yes, playable", outcome=o_raw,
                                        text=change_text(label, base, o_raw)),
                                   dict(answer="not_playable", label="No, keep me on this hole", outcome=None,
                                        text=change_text(label, base, None))]))

    for it in items:
        score_item(it)
    if want_crops:                                       # crops for anything that may be shown
        for it in items:
            if it["prelim"] != "green":
                it["crop"] = _crop_for(it, h, fr, base, img)
    for it in items:
        it.pop("_clip", None)
    return dict(ref=str(ref), par=par, base=base_out, frame=fr.to_json(), items=items,
                seconds=round(time.time() - t0, 1), sims=sum(c["n_sims"] for c in base["clubs"].values()))


def outcomes(it):
    return [s["outcome"] for o in it.get("options", []) for s in ([o] + o.get("samples", [])) if s.get("outcome")]


def score_item(it):
    """worst regret over the item's answers, exp_regret = p_wrong x that, and the outcome-level severity."""
    oc = outcomes(it)
    it["worst_regret"] = round(max([o.get("regret", 0.0) for o in oc] or [0.0]), 4)
    it["exp_regret"] = round(float(it.get("p_wrong") or 0.0) * it["worst_regret"], 4)
    it["max_d_ev"] = round(max([abs(o["d_ev"]) for o in oc] or [0.0]), 4)
    it["prelim"] = worst([o["severity"] for o in oc]) if oc else it.get("severity", "green")
    it["strict"] = worst([o.get("strict", o["severity"]) for o in oc]) if oc else it["prelim"]
    return it


def assign_severity(items, er_red=ER_RED, red_cards=RED_CARDS, er_amber=ER_AMBER):
    """Course-level post-pass: red = a red outcome and exp_regret >= er_red, then at most red_cards red cards by
    exp_regret (all red tees together are one card, scored by their summed exp_regret); the rest amber."""
    for it in items:
        if not it.get("tested"):
            it.setdefault("severity", it.get("prelim", "green"))
            it.setdefault("strict", it["severity"])
            continue
        cand = it["prelim"] == "red" and it["exp_regret"] >= er_red
        it["severity"] = ("red" if cand else "amber" if it["prelim"] in ("red", "amber") and it["exp_regret"] >= er_amber
                          else "green")
        it.pop("over_budget", None)
    reds = [it for it in items if it["severity"] == "red"]
    tees = [it for it in reds if it["type"] == "tee"]
    cards = [("tees", sum(i["exp_regret"] for i in tees), tees)] if tees else []
    cards += [(it["id"], it["exp_regret"], [it]) for it in reds if it["type"] != "tee"]
    cards.sort(key=lambda c: -c[1])
    for _, _, its in cards[red_cards:]:
        for it in its:
            it["severity"], it["over_budget"] = "amber", True
    items.sort(key=lambda it: (SEV_RANK[it["severity"]], -float(it.get("exp_regret") or 0), -float(it.get("max_d_ev") or 0)))
    n_cards = min(len(cards), red_cards)
    return dict(red_cards=n_cards, red_candidates=sum(len(c[2]) for c in cards), red_candidate_cards=len(cards))


def _tee_detail(tee_set, info, resid):
    bits = []
    if info.get("card") is not None:
        bits.append(f"card {info['card']} yds" + (f", we measure {float(info['measured']):.0f}"
                                                  if info.get("measured") is not None else ""))
    m = info.get("method") or "unknown"
    how = {"tagged": "an OpenStreetMap tee tagged with this colour", "tee_axis": "the OSM tee box that fits the card",
           "tee_centroid": "the centre of an OSM tee box", "walkback": "walked back from the next set (no box found)",
           "lidar_pad": "a flat pad in the lidar"}.get(m, m)
    bits.append(f"placed from {how}")
    if info.get("confidence") is not None:
        bits.append(f"confidence {float(info['confidence']):.0%}")
    if resid is not None and resid > 15:
        bits.append(f"{resid:.0f} yds off the card: likely wrong box")
    return "; ".join(bits).capitalize() + "."


def _crop_for(it, h, fr, base, img):
    kind = "tee" if it["type"] == "tee" else "landing"
    spec = crop_spec(kind, base["aim"])
    polys_xa = []
    if it["type"] in ("hazard", "fairway"):
        polys_xa = [to_yd(fr, h["zones_ll"][i]["poly"]) for i in it["zone_idx"]]
    elif it["type"] == "gap":
        polys_xa = [np.array(it["strip_xa"], float)]
    elif it["type"] == "cut":
        polys_xa = [np.array(c, float) for c in it["cut_xa"]]
    cp = [to_crop(spec, p) for p in polys_xa]
    c = render_crop(img, fr, spec, outline_polys=cp if it["type"] in ("hazard", "fairway") else ())
    pick = base["pick"]
    carry = decide._carry(pick)
    w = t.CLUBS.get(pick, t.IRONS.get(pick, (0, 0, 60, 30)))
    ov = dict(polys=[r1(p) for p in cp],
              tee=r1(to_crop(spec, [[0.0, 0.0]]))[0],
              target=r1(to_crop(spec, [[base["aim"], carry]]))[0],
              ellipse=[round(w[2] / 2 * c["s"], 1), round(w[3] / 2 * c["s"], 1)],
              line=r1(to_crop(spec, [[0.0, 0.0], [base["aim"] * 400 / max(carry, 1), 400.0]])),
              pick=pick)
    if it["type"] in ("hazard", "fairway") and it.get("_clip") is not None:
        ov["toward"] = it["toward"]
        minx, a0, maxx, a1 = it["_clip"].bounds
        side = it.get("side")
        if it["type"] == "fairway":
            hp = [minx if side == "left" else maxx, (a0 + a1) / 2]
        elif side == "left":
            hp = [maxx, (a0 + a1) / 2]
        elif side == "right":
            hp = [minx, (a0 + a1) / 2]
        else:
            hp = [(minx + maxx) / 2, a0]
        ov["handle"] = r1(to_crop(spec, [hp]))[0]
    c["overlay"] = ov
    return c


# ----------------------------------------------------------------------------- book badges
BADGE = {"auto": "\u2713", "checked": "\u25d0", "unverified": "\u26a0"}


def worst_text(it):
    best = None
    for o in it.get("options", []):
        for x in [o] + o.get("samples", []):
            oc = x.get("outcome")
            if oc and (best is None or oc.get("regret", 0) > best[0]):
                best = (oc.get("regret", 0), x.get("text", ""))
    return best[1] if best else ""


def badges(pkg, review):
    """{hole ref: {state, symbol, line}} for the book (research section 8): auto (no open red check), checked
    (the golfer answered this hole's review items), unverified (an unanswered red item: its question and what
    changes if the map is wrong). {} without a review."""
    if not review:
        return {}
    out = {}
    for ref, h in (pkg.get("holes") or {}).items():
        ver = h.get("verification") or {}
        answered = {k for k in ver if "-" in k}
        reds = [it for it in review.get("items", []) if it["hole"] == str(ref) and it["severity"] == "red"
                and it["id"] not in answered]
        if reds:
            it = reds[0]
            state, line = "unverified", f"Unverified: {it['question']} If not, {worst_text(it)}"
        elif answered:
            state, line = "checked", "Map checked by you before the round."
        else:
            state, line = "auto", ""
        out[str(ref)] = dict(state=state, symbol=BADGE[state], line=line)
    return out


# ----------------------------------------------------------------------------- course
def run(pkg_path, tees=None, holes=None, n=N_SWINGS, seed=SEED, workers=1, crops=True, out=None):
    T0 = time.time()
    pkg = json.load(open(pkg_path))
    tee_set = PK._resolve_set(pkg, tees)
    course = pkg.get("course") or {}
    slug = course.get("slug") or os.path.basename(os.path.dirname(os.path.abspath(pkg_path)))
    H = pkg["holes"]
    refs = [r for r in H if holes is None or str(r) in holes]
    refs.sort(key=lambda r: (str(r).rstrip("BFabf").zfill(3), str(r)))
    meta = dict(imagery=pkg.get("imagery"), sources=pkg.get("sources"), course=course)
    jobs = [(r, H[r], tee_set, n, seed, crops, pkg_path, meta) for r in refs]
    log(f"verify {course.get('name')} ({tee_set}): {len(jobs)} holes, N={n}, workers={workers}")
    res = []
    if workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            for r in pool.imap_unordered(verify_hole, jobs):
                res.append(r)
                _log_hole(r)
    else:
        for j in jobs:
            r = verify_hole(j)
            res.append(r)
            _log_hole(r)
    res.sort(key=lambda r: (r["ref"].rstrip("BFabf").zfill(3), r["ref"]))
    items = [it for r in res for it in r["items"]]
    budget = assign_severity(items)
    plan_picks = _plan_picks(pkg_path, slug)
    counts = {s: sum(1 for it in items if it["severity"] == s) for s in ("red", "amber", "green")}
    counts_strict = {s: sum(1 for it in items if it["strict"] == s) for s in ("red", "amber", "green")}
    by_type = {}
    for it in items:
        by_type.setdefault(it["type"], {"red": 0, "amber": 0, "green": 0})[it["severity"]] += 1
    review = dict(schema=SCHEMA, course=course.get("name"), slug=slug, tee_set=tee_set,
                  package=os.path.relpath(os.path.abspath(pkg_path), ROOT), package_built=pkg.get("built"),
                  built=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                  settings=dict(n=n, seed=seed, corridor_along=ALONG, corridor_half=HALF, edge_move=EDGE,
                                tee_moves=[TEE_ALONG, TEE_ACROSS], tee_scale=TEE_SCALE, aim_red=AIM_RED,
                                ev_amber=EV_AMBER, regret_red=REGRET_RED, er_red=ER_RED, er_amber=ER_AMBER, red_cards=RED_CARDS,
                                priors=PRIORS, cut_width=CUT_W,
                                model="decide.set_prior_means (quick plan's central settings)"),
                  imagery=dict(date=(pkg.get("imagery") or {}).get("naip_date"),
                               source=(pkg.get("imagery") or {}).get("source")),
                  counts=counts, counts_strict=counts_strict, by_type=by_type, budget=budget,
                  holes={r["ref"]: dict(par=r["par"], base=r.get("base"), frame=r.get("frame"),
                                        plan=plan_picks.get(r["ref"]), seconds=r["seconds"]) for r in res},
                  items=items, runtime_s=round(time.time() - T0, 1))
    out = out or os.path.join(CD, "packages", slug, "out", "review")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "review.json"), "w") as fh:
        json.dump(review, fh, separators=(",", ":"), default=float)
    with open(os.path.join(out, "review.md"), "w") as fh:
        fh.write(review_md(review))
    import review_page
    html = review_page.build(review, os.path.join(out, "index.html"))
    log(f"{counts} in {review['runtime_s']:.0f}s -> {os.path.relpath(out, ROOT)} "
        f"(page {os.path.getsize(html) / 1e6:.2f} MB)")
    return review, out


def _log_hole(r):
    b = r.get("base")
    s = {k: sum(1 for i in r["items"] if i.get("prelim", i.get("severity")) == k) for k in ("red", "amber")}
    log(f"  hole {r['ref']}: {(b['pick'] + ' ' + aim_words(b['aim'])) if b else 'par 3'}; "
        f"{len(r['items'])} items, red {s['red']} amber {s['amber']} ({r['seconds']}s)")


def _plan_picks(pkg_path, slug):
    p = os.path.join(os.path.dirname(os.path.abspath(pkg_path)), "out", "decision.json")
    if not os.path.exists(p):
        return {}
    d = json.load(open(p))
    return {str(k): dict(pick=v.get("pick"), aim=v.get("aim"), check=v.get("check") or []) for k, v in d.items()}


def review_md(rv):
    L = [f"# {rv['course']} ({rv['tee_set']} tees): pre-round check", "",
         f"{rv['counts']['red']} red, {rv['counts']['amber']} amber, {rv['counts']['green']} green items; "
         f"N={rv['settings']['n']} swings, built {rv['built']} in {rv['runtime_s']:.0f}s.", "",
         "| Sev | Hole | Type | Question | What changes (worst answer) |", "|---|---|---|---|---|"]
    for it in rv["items"]:
        if it["severity"] == "green":
            continue
        worst_txt = ""
        cands = []
        for o in it.get("options", []):
            for s in ([o] if "samples" not in o else o["samples"]):
                oc = s.get("outcome")
                if oc:
                    cands.append((SEV_RANK[oc["severity"]], -abs(oc["d_ev"]), s.get("text", "")))
        if cands:
            worst_txt = min(cands)[2]
        L.append(f"| {it['severity']} | {it['hole']} | {it['type']} | {it['question']} | {worst_txt} |")
    L += ["", "Base plan per hole (this check's own coarse run vs the quick plan's decision.json):", "",
          "| Hole | Check base | Plan |", "|---|---|---|"]
    for k, hv in rv["holes"].items():
        if hv.get("base"):
            p = hv.get("plan") or {}
            L.append(f"| {k} | {hv['base']['pick']} {hv['base']['aim']:+.1f} | "
                     f"{p.get('pick', '-')} {p.get('aim', 0):+.1f} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--package")
    ap.add_argument("--tees")
    ap.add_argument("--request", help="request file {package, tees, n, workers, experiment}")
    ap.add_argument("--holes", help="comma list")
    ap.add_argument("--n", type=int, default=N_SWINGS)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--no-crops", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    req = json.load(open(a.request)) if a.request else {}
    pkg = a.package or req.get("package")
    if not pkg:
        ap.error("--package or --request")
    workers = a.workers or req.get("workers") or (os.cpu_count() if os.environ.get("GITHUB_ACTIONS") else 1)
    holes = set((a.holes or req.get("holes") or "").split(",")) - {""} or None
    rv, out = run(pkg, a.tees or req.get("tees"), holes=holes, n=a.n if a.n != N_SWINGS else req.get("n", a.n),
                  workers=int(workers), crops=not a.no_crops, out=a.out or req.get("out"))
    if req.get("experiment") == "hand_truth":
        import verify_hand_truth
        verify_hand_truth.run(pkg, rv, out, workers=int(workers))
    return rv


if __name__ == "__main__":
    main()
