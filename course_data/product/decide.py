"""Tee-shot decisions for any course module (the 'quick' and the 'full' / pro path).

quick  prior-mean point estimate: the strategy model at the central settings of the final Bayesian run
       (driver pattern 70 yds, carry-depth x1.25, tree penalty 0.8, half of long-grass balls lost, 15%
       slight mishits, PGA Tour baselines); best aim per club on a 2.5-yd grid, aim zone = every aim within
       0.02 strokes of the best. Same settings as spirit_hollow/wind_grid.py's calm cell.
full   spirit_hollow/final_decision.py, made course-agnostic: the reviewer's prior (review_stats/prior_patch.py,
       driver width centred 70 yds, 90% 62-80, depth x1.25, tour baselines), S scrambled-Sobol draws x N
       swings with common random numbers, and the reviewer's reporting (review_stats/decision_stats.py:
       cross-fitted margin, error budget, EVPI bracket, noise-corrected P(best), all-clubs width sweep).

spirit_hollow/decision.py hard-codes `import course`; here a small stand-in module (`_Core`, registered as
`decision` while prior_patch / decision_stats are imported) supplies the same names (BASE, apply, reset,
aims_for, clubs_for, ev_grid, CENTER_WIDTH, AIM_STEP) for whatever course is loaded, so the reviewer's
statistics run unchanged on any course. Nothing under spirit_hollow/ is edited.

Holes run in parallel (one process per hole; each draw's swings are seeded by the draw index, so every hole
sees the same worlds).
"""
import copy
import importlib
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "mozingo"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tee_strategy as t                            # noqa: E402

ZONE_TOL = 0.02
AIM_STEP = 2.5
AIM_LIMIT = 60          # ARCHITECTURE 9.2: tee lines on dog-legs point at the corner -> search +/-60
CENTER_WIDTH = 70.0
SHARES = ("fairway", "first_cut", "rough", "sand", "recovery", "native", "water", "ob")

BASE = {}


def bind(holes):
    """Point the model (and the Bayesian core) at a course's HOLES dict."""
    t.HOLES = holes
    BASE.clear()
    BASE.update(clubs=copy.deepcopy(_CLUBS0), irons=copy.deepcopy(_IRONS0), holes=copy.deepcopy(holes),
                sev=t.TREE_SEVERITY, lost=t.NATIVE_LOST, mis=dict(t.MISHIT_RATE))


_CLUBS0, _IRONS0 = copy.deepcopy(t.CLUBS), copy.deepcopy(t.IRONS)


def set_prior_means():
    """Central settings of the final Bayesian run (spirit_hollow/wind_grid.set_prior_means)."""
    s = CENTER_WIDTH / 65.0
    t.CLUBS = {k: (c, tot, w * s, d * 1.25) for k, (c, tot, w, d) in _CLUBS0.items()}
    t.IRONS = {k: (c, tot, w * s, d * 1.25) for k, (c, tot, w, d) in _IRONS0.items()}
    t.TREE_SEVERITY, t.NATIVE_LOST = 0.8, 0.5
    t.MISHIT_RATE = {k: 0.15 for k in t.MISHIT_RATE}
    t.HCP_BASELINE = False


def aims_for(h, club=None):
    hd = t.HOLES[h]
    if club in t.IRONS or club in _IRONS0:
        return np.arange(-25, 45.01, AIM_STEP)
    lo = max(hd.get("aim_min", -AIM_LIMIT), -AIM_LIMIT)
    hi = min(hd.get("aim_max", AIM_LIMIT), AIM_LIMIT)
    return np.arange(lo, hi + 0.01, AIM_STEP)


def clubs_for(h):
    return list(_CLUBS0) + (list(_IRONS0) if t.HOLES[h].get("irons") else [])


def _z(n, seed):
    rng = np.random.default_rng(seed)
    return np.vstack([rng.standard_normal((2, n)), rng.random((2, n))])


def _club_result(h, c, aim, z):
    _, lie, to_green, strokes = t.simulate(h, c, aim, z=z)
    return dict(aim=float(aim), ev=float(strokes.mean()), approach=float(np.median(to_green)),
                share={k: float(np.mean(lie == k)) for k in SHARES})


# ----------------------------------------------------------------------------- quick
def quick_hole(h, n=8000, seed=31):
    set_prior_means()
    z = _z(n, seed)
    res, curves = {}, {}
    for c in clubs_for(h):
        aims = aims_for(h, c)
        ev = np.array([t.simulate(h, c, a, z=z)[3].mean() for a in aims])
        i = int(ev.argmin())
        while (i == 0 or i == len(aims) - 1) and abs(aims[i]) < 120:   # best aim on the grid edge: widen
            step = -AIM_STEP if i == 0 else AIM_STEP
            more = aims[i] + step * np.arange(1, 9)
            mev = np.array([t.simulate(h, c, a, z=z)[3].mean() for a in more])
            aims, ev = (np.r_[more[::-1], aims], np.r_[mev[::-1], ev]) if i == 0 else (np.r_[aims, more], np.r_[ev, mev])
            i = int(ev.argmin())
        res[c] = _club_result(h, c, aims[i], z)
        curves[c] = (aims, ev)
    best = min(res, key=lambda c: res[c]["ev"])
    runner = min((c for c in res if c != best), key=lambda c: res[c]["ev"])
    aims, ev = curves[best]
    ok = aims[ev <= ev.min() + ZONE_TOL]
    return dict(pick=best, aim=res[best]["aim"], ev=res[best]["ev"], runner=runner,
                margin=res[runner]["ev"] - res[best]["ev"], zone=[float(ok.min()), float(ok.max())],
                clubs=res, tie=bool(res[runner]["ev"] - res[best]["ev"] < 0.01), mode="quick", n=n)


# ----------------------------------------------------------------------------- full (Bayesian)
class _Core(types.ModuleType):
    """Course-agnostic replacement for spirit_hollow/decision.py's module-level API."""
    CENTER_WIDTH = CENTER_WIDTH
    AIM_STEP = AIM_STEP

    @property
    def BASE(self):
        return BASE

    @staticmethod
    def apply(theta, holes_subset=None):
        off = {"Driver": theta["c_drv"], "2-wood": theta["c_2w"], "4-wood": theta["c_4w"]}
        t.CLUBS = {k: (c + off[k], c + off[k] + (tot - c) * theta["roll"], w * theta["width"], d)
                   for k, (c, tot, w, d) in BASE["clubs"].items()}
        t.TREE_SEVERITY, t.NATIVE_LOST = theta["trees"], theta["lost"]
        t.MISHIT_RATE = {k: theta["mishit"] for k in BASE["mis"]}
        t.IRONS = {k: (c + theta["c_4w"], c + theta["c_4w"] + (tot - c) * theta["roll"], w * theta["width"], d)
                   for k, (c, tot, w, d) in BASE["irons"].items()}
        rng = np.random.default_rng(theta["map_seed"])
        holes = {}
        for h, hd in BASE["holes"].items():           # every hazard outline moved by N(0, 2.5 yds)
            hd = dict(hd)
            ppy = t.hole_frame(hd)[3]
            hd["zones"] = [(nm, [(x + dx, y + dy) for x, y in poly])
                           for nm, poly in hd["zones"] for dx, dy in [rng.normal(0, 2.5 * ppy / 1.414, 2)]]
            holes[h] = hd
        t.HOLES = holes

    @staticmethod
    def reset():
        t.CLUBS = copy.deepcopy(BASE["clubs"])
        t.IRONS = copy.deepcopy(BASE["irons"])
        t.HOLES = copy.deepcopy(BASE["holes"])
        t.TREE_SEVERITY, t.NATIVE_LOST = BASE["sev"], BASE["lost"]
        t.MISHIT_RATE = dict(BASE["mis"])

    @staticmethod
    def aims_for(h):
        return aims_for(h)

    @staticmethod
    def clubs_for(h):
        return clubs_for(h)

    @staticmethod
    def ev_grid(h, z):
        return {c: (aims_for(h, c), np.array([t.simulate(h, c, a, z=z)[3].mean() for a in aims_for(h, c)]))
                for c in clubs_for(h)}


def _review_modules():
    """Import review_stats/prior_patch + decision_stats against the course-agnostic core."""
    rs = os.path.join(ROOT, "spirit_hollow", "review_stats")
    saved = sys.modules.get("decision")
    sys.modules["decision"] = _Core("decision")
    sys.path.insert(0, rs)
    try:
        for m in ("prior_patch", "decision_stats"):
            sys.modules.pop(m, None)
        PP = importlib.import_module("prior_patch")
        DS = importlib.import_module("decision_stats")
    finally:
        sys.path.remove(rs)
        if saved is not None:
            sys.modules["decision"] = saved
    DS.aims_for_club = lambda h, c: aims_for(h, c)        # irons -25..45, woods +/-60 (contract 9.2)
    return PP, DS


def final_draws(S):
    """final_decision.draws(): driver width centred 70 (90% to 80), depth x1.25, tour baselines."""
    PP, _ = _review_modules()
    th = PP.prior_draws(S, width_median=70.0, width_hi90=80.0)
    for d in th:
        d["depth"] = d["depth"] / 1.5 * 1.25
        d["hcp"] = False
    return th


def full_hole(h, S=64, N=3000, seed=2027, sweep=True):
    PP, DS = _review_modules()
    draws = final_draws(S)
    E = {}
    for i, th in enumerate(draws):
        PP.apply(th)
        t.HCP_BASELINE = False
        DS.accumulate(E, DS.ev_grid_halves(h, _z(N, seed + i)))
    PP.reset()
    r = DS.summarize(E)
    cf = float(r["crossfit"]["margin_out"])
    r["crossfit_margin"] = cf
    r["tie"] = bool(min(r["margin"], cf) < 0.01)
    clubs, aims, MA, MB = DS.stack(E)
    curve = ((MA[r["pick"]] + MB[r["pick"]]) / 2).mean(0)
    ok = aims[r["pick"]][curve <= curve.min() + ZONE_TOL]
    r["zone"] = [float(ok.min()), float(ok.max())]
    if sweep:
        picks, flips, _ = DS.width_sweep(h, mode="common")
        r["width_sweep"] = [dict(width=w, pick=p) for w, p in zip((55, 60, 65, 70, 75, 80, 85, 90), picks)]
        r["width_flips"] = [dict(width=float(x), frm=a, to=b) for x, a, b in flips]
    # book numbers (shares, approach) at the posterior aims under the central settings
    set_prior_means()
    t.HOLES = BASE["holes"]
    z = _z(8000, 31)
    for c, v in r["clubs"].items():
        v.update(_club_result(h, c, v["aim"], z), ev=v["ev"])
    r["conf"] = int(round(100 * r["p_best_fixed_aims_deconvolved"].get(r["pick"], 0.0)))
    r["mode"], r["S"], r["N"] = "full", S, N
    return r


# ----------------------------------------------------------------------------- runner
def _work(args):
    mode, h, kw = args
    t.HOLES = copy.deepcopy(BASE["holes"])
    out = quick_hole(h, **kw) if mode == "quick" else full_hole(h, **kw)
    return h, out


def run(holes, mode="quick", workers=None, log=print, **kw):
    """{key: result} for every tee hole. kw: n (quick) or S, N (full)."""
    bind(holes)
    keys = list(holes)
    workers = workers or min(len(keys), os.cpu_count() or 1)
    jobs = [(mode, h, kw) for h in keys]
    out = {}
    if workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            for h, r in pool.imap_unordered(_work, jobs):
                out[h] = r
                log(f"  {h}: {r['pick']} aim {r['aim']:+.1f} margin {r['margin']:.3f}{' (tie)' if r['tie'] else ''}")
    else:
        for j in jobs:
            h, r = _work(j)
            out[h] = r
            log(f"  {h}: {r['pick']} aim {r['aim']:+.1f} margin {r['margin']:.3f}{' (tie)' if r['tie'] else ''}")
    return {h: out[h] for h in keys}
