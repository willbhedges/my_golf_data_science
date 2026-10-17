"""v2 tee decisions: robust club + aim per hole, with aim windows, change ladder and sensitivities.

  V2_HOLES=1,11 V2_DRAWS=64 V2_OUT=parts/v2_1.json python3 spirit_hollow/v2/decide.py

Per hole:
  * S scrambled-Sobol prior draws (default 64). In each draw a fresh map jitter, one set of N common
    swings, and every club's expected strokes on a 0.5-yd aim grid (-60..+60).
  * Robust aim per club = argmin of the prior-averaged curve: Gaussian-smoothed (1 yd), then Brent
    (bounded) on a cubic spline of it, reported to 0.5 yd. Aim window = contiguous aims within
    0.005 strokes of that minimum. A flag if the optimum sits within 2 yds of the search bound.
  * Pick = lowest prior-averaged EV at its robust aim; margin vs runner-up paired over draws (+ SE),
    two-fold cross-fitted margin (choose on half the draws, score on the other half).
  * Central world (prior means, N=20000): EV curves for the page, outcome shares, the "ladder" from
    v1's world to v2 one change at a time, sensitivities and a common-width sweep.
"""
import json
import os
import sys
import time

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import minimize_scalar
from scipy.stats import norm, qmc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model as M                               # noqa: E402

AIMS = np.arange(-60, 60.001, 0.5)
AIM_LIMIT = 40.0          # course.py's aim_min / aim_max on every hole (v1 searched only +/-25)
WINDOW = 0.005
TIE = 0.01
DIMS = ["width", "r2w", "r4w", "c_common", "c_drv", "c_2w", "c_4w", "c_iron", "depth", "soft_roll",
        "rough_roll", "trees", "lost_edge", "lost_deep", "mis_slight", "mis_heavy", "rho", "kappa", "bias",
        "temp_f", "temp_k", "m_rough", "m_sand", "am_slope", "first_cut", "punch_adv", "punch_fail",
        "block_sev", "tree_restricted", "map_seed"]


def prior_draws(s=64, seed=2026):
    u = qmc.Sobol(len(DIMS), scramble=True, seed=seed).random(s)
    z = norm.ppf(np.clip(u, 1e-9, 1 - 1e-9))
    c = {k: i for i, k in enumerate(DIMS)}
    U = lambda k, lo, hi: lo + (hi - lo) * u[:, c[k]]          # noqa: E731
    out = []
    width = 70.0 * np.exp(z[:, c["width"]] * np.log(80 / 70) / 1.645)      # driver 95% width, 90% 62-80
    r2w = (65 / 70) * np.exp(0.04 * z[:, c["r2w"]])                         # golfer's 65:60:50 ratios
    r4w = (54 / 70) * np.exp(0.06 * z[:, c["r4w"]])
    cols = dict(
        c_common=5.0 * z[:, c["c_common"]], c_drv=3.0 * z[:, c["c_drv"]], c_2w=3.0 * z[:, c["c_2w"]],
        c_4w=3.0 * z[:, c["c_4w"]], c_iron=3.0 * z[:, c["c_iron"]],
        depth=1.25 * np.exp(0.2 * z[:, c["depth"]]), soft_roll=U("soft_roll", 0.5, 3.5),
        rough_roll=U("rough_roll", 0.15, 0.5), trees=U("trees", 0.6, 1.0),
        lost_edge=U("lost_edge", 0.1, 0.4), lost_deep=U("lost_deep", 0.5, 0.8),
        mis_slight=U("mis_slight", 0.08, 0.16), mis_heavy=U("mis_heavy", 0.01, 0.04),
        rho=U("rho", -0.1, 0.3), kappa=U("kappa", 0.0, 0.16), bias=2.0 * z[:, c["bias"]],
        temp_f=U("temp_f", 44, 52), temp_k=U("temp_k", 0.0005, 0.0009),
        m_rough=U("m_rough", 0.55, 0.95), m_sand=U("m_sand", 0.9, 1.3), am_slope=U("am_slope", 0.0006, 0.0018),
        first_cut=U("first_cut", 0.2, 0.5), punch_adv=U("punch_adv", 20, 50), punch_fail=U("punch_fail", 0.0, 0.2),
        block_sev=U("block_sev", 0.2, 0.6), tree_restricted=U("tree_restricted", 0.0, 0.2),
        map_seed=(u[:, c["map_seed"]] * 1e9).astype(int))
    for i in range(s):
        wd = width[i]
        w4 = wd * r4w[i]
        P = M.central(
            width={"Driver": wd, "2-wood": wd * r2w[i], "4-wood": w4,
                   "Long iron": w4 * 40 / 50, "Mid iron": w4 * 34 / 50},
            c_common=cols["c_common"][i],
            c_club={"Driver": cols["c_drv"][i], "2-wood": cols["c_2w"][i], "4-wood": cols["c_4w"][i],
                    "Long iron": cols["c_iron"][i], "Mid iron": cols["c_iron"][i]})
        P["depth_mult"] = float(cols["depth"][i])
        for k in ("soft_roll", "rough_roll", "trees", "lost_edge", "lost_deep", "mis_slight", "mis_heavy", "rho",
                  "kappa", "bias", "temp_f", "temp_k", "m_rough", "m_sand", "am_slope", "first_cut", "punch_adv",
                  "punch_fail", "block_sev", "tree_restricted"):
            P[k] = float(cols[k][i])
        P["map_seed"] = int(cols["map_seed"][i])
        out.append(P)
    return out


def key(h):
    return int(h) if str(h).isdigit() else str(h)


# ------------------------------------------------------------------------------- aim optimisation
def robust_aim(aims, curve, lo=-AIM_LIMIT, hi=AIM_LIMIT):
    """Continuous argmin of a (prior-averaged) EV curve: smooth 1 yd, Brent on a cubic spline."""
    step = aims[1] - aims[0]
    sm = gaussian_filter1d(curve, 1.0 / step, mode="nearest")
    lo = aims[0] if lo is None else lo
    hi = aims[-1] if hi is None else hi
    inside = (aims >= lo - 1e-9) & (aims <= hi + 1e-9)
    i = int(np.argmin(np.where(inside, sm, np.inf)))
    cs = CubicSpline(aims, sm)
    a_lo, a_hi = max(lo, aims[i] - 3), min(hi, aims[i] + 3)
    r = minimize_scalar(cs, bounds=(a_lo, a_hi), method="bounded", options=dict(xatol=0.05))
    aim = float(np.round(r.x * 2) / 2)
    best = float(cs(r.x))
    ok = sm <= best + WINDOW
    j = int(np.argmin(np.abs(aims - aim)))
    a, b = j, j
    while a > 0 and ok[a - 1] and inside[a - 1]:
        a -= 1
    while b < len(aims) - 1 and ok[b + 1] and inside[b + 1]:
        b += 1
    ev = float(np.interp(aim, aims, curve))
    at_bound = bool(aim <= lo + 1 or aim >= hi - 1)
    return dict(aim=aim, ev=ev, ev_smooth=best, window=[float(aims[a]), float(aims[b])], at_bound=at_bound,
                window_width=float(aims[b] - aims[a]))


def interp_rows(aims, M2, aim):
    """Each draw's EV at a given aim (linear between grid points)."""
    return np.array([np.interp(aim, aims, row) for row in M2])


# ------------------------------------------------------------------------------- central world
def curves(h, P, n, seed, clubs, jitter=None):
    hd = M.HOLES[h]
    R = M.Raster(hd, jitter)
    S = R.strokes(P, hd["length"])
    z = M.draws_z(n, seed)
    out = {}
    for c in clubs:
        ev, _ = M.ev_curve(R, S, hd, c, P, z, AIMS)
        out[c] = ev
    return R, S, z, out


def solve_world(h, P, n=12000, seed=7, clubs=None):
    clubs = clubs or M.ALL_CLUBS
    R, S, z, cv = curves(h, P, n, seed, clubs)
    res = {c: robust_aim(AIMS, cv[c]) for c in clubs}
    order = sorted(clubs, key=lambda c: res[c]["ev"])
    return dict(pick=order[0], runner=order[1], aim=res[order[0]]["aim"],
                margin=res[order[1]]["ev"] - res[order[0]]["ev"],
                clubs={c: dict(aim=res[c]["aim"], ev=round(res[c]["ev"], 4), window=res[c]["window"]) for c in clubs})


LADDER = [
    ("v1 world (v2 engine, v1 clubs)", {}, "v1"),
    ("+ irons on every hole", {}, "all"),
    ("+ soft course: 0.5-3.5 yd roll", dict(soft_roll=2.0, roll_noise=0.5, v1_roll=False), "all"),
    ("+ 48°F", dict(temp_k=0.00075), "all"),
    ("+ mishits 5-8% short (+ 2.5% heavy)", dict(mis_slight=0.12, mis_slight_carry=(0.92, 0.95), mis_slight_lat=1.15,
                                                mis_heavy=0.025), "all"),
    ("+ correlated miss (rho, curvature loss)", dict(rho=0.1, kappa=0.08), "all"),
    ("+ penalty rules (S&D, water entry, graded lost ball)", dict(v1_penalties=False, lost_edge=0.25,
                                                                 lost_deep=0.65, tree_restricted=0.10), "all"),
    ("+ punch-out tree cost", dict(broadie_recovery=False), "all"),
    ("+ trees blocking the line to the green", dict(block_sev=0.4), "all"),
    ("+ scratch-5 amateur scoring table (= v2 central)", dict(table="am"), "all"),
]


def ladder(h, n):
    P = M.v1_world()
    rows = []
    for name, ch, cl in LADDER:
        P = dict(P, **ch)
        clubs = M.clubs_for(h, all_clubs=(cl == "all"))
        r = solve_world(h, P, n, clubs=clubs)
        rows.append(dict(step=name, pick=r["pick"], aim=r["aim"], margin=round(r["margin"], 4), runner=r["runner"]))
    return rows


def sensitivities(h, n):
    C = M.central()
    w = C["width"]
    var = {
        "central": {},
        "width 82 (published 5-hcp average)": dict(width={c: v * 82 / 70 for c, v in w.items()}),
        "width 60 (tighter)": dict(width={c: v * 60 / 70 for c, v in w.items()}),
        "v1-final width ratios (70/66/59.5)": dict(width=dict(w, **{"2-wood": 70 * 0.94, "4-wood": 70 * 0.85})),
        "PGA Tour scoring table": dict(table="tour"),
        "v1 roll (~25 yds driver)": dict(soft_roll=None),
        "no heavy mishits": dict(mis_heavy=0.0),
        "fade: right tail 30% longer": dict(skew=0.3),
        "draw: left tail 30% longer": dict(skew=-0.3),
        "no line-of-sight cost": dict(block_sev=0.0),
        "70°F": dict(temp_f=70.0),
        "lost ball rare (10-40%)": dict(lost_edge=0.1, lost_deep=0.4),
        "lost ball likely (40-90%)": dict(lost_edge=0.4, lost_deep=0.9),
        "trees always chip-out": dict(trees=1.0),
    }
    out = {}
    for name, ch in var.items():
        r = solve_world(h, M.central(**ch), n)
        out[name] = dict(pick=r["pick"], aim=r["aim"], margin=round(r["margin"], 4), runner=r["runner"],
                         clubs=r["clubs"] if name == "central" else None)
    return out


def width_sweep(h, n):
    C = M.central()
    picks, evs = [], []
    ws = [55, 60, 65, 70, 75, 80, 85, 90]
    for W in ws:
        P = M.central(width={c: v * W / 70 for c, v in C["width"].items()})
        r = solve_world(h, P, n, seed=9)
        picks.append(r["pick"])
        evs.append({c: v["ev"] for c, v in r["clubs"].items()})
    flips = []
    for i in range(len(ws) - 1):
        if picks[i] != picks[i + 1]:
            a, b = picks[i], picks[i + 1]
            d0, d1 = evs[i][a] - evs[i][b], evs[i + 1][a] - evs[i + 1][b]
            x = ws[i] + (ws[i + 1] - ws[i]) * (-d0) / (d1 - d0) if d1 != d0 else ws[i]
            flips.append(dict(width=round(float(x), 1), frm=a, to=b))
    return [dict(width=w_, pick=p) for w_, p in zip(ws, picks)], flips


# ------------------------------------------------------------------------------- Bayes run
def bayes(h, S=64, N=3000):
    hd = M.HOLES[h]
    draws = prior_draws(S)
    E = {c: [] for c in M.ALL_CLUBS}
    EA = {c: [] for c in M.ALL_CLUBS}
    EB = {c: [] for c in M.ALL_CLUBS}
    for s, P in enumerate(draws):
        R = M.Raster(hd, P["map_seed"])
        Sc = R.strokes(P, hd["length"])
        z = M.draws_z(N, 1000 + s)
        for c in M.ALL_CLUBS:
            _, (a, l, lie, sv) = M.ev_curve(R, Sc, hd, c, P, z, AIMS)
            v = 1.0 + sv
            k = N // 2
            EA[c].append(v[:k].mean(0))
            EB[c].append(v[k:].mean(0))
            E[c].append(v.mean(0))
    Mx = {c: np.vstack(E[c]) for c in M.ALL_CLUBS}
    MA = {c: np.vstack(EA[c]) for c in M.ALL_CLUBS}
    MB = {c: np.vstack(EB[c]) for c in M.ALL_CLUBS}
    res = {c: robust_aim(AIMS, Mx[c].mean(0)) for c in M.ALL_CLUBS}
    order = sorted(M.ALL_CLUBS, key=lambda c: res[c]["ev"])
    pick, runner = order[0], order[1]
    vp = interp_rows(AIMS, Mx[pick], res[pick]["aim"])
    vr = interp_rows(AIMS, Mx[runner], res[runner]["aim"])
    d = vr - vp
    dA = interp_rows(AIMS, MA[runner], res[runner]["aim"]) - interp_rows(AIMS, MA[pick], res[pick]["aim"])
    dB = interp_rows(AIMS, MB[runner], res[runner]["aim"]) - interp_rows(AIMS, MB[pick], res[pick]["aim"])
    s2_z = float(np.mean(((dA - dB) / 2) ** 2))
    # cross-fit: choose club + aim on one half of the draws, score on the other half
    half = S // 2
    folds = [np.arange(half), np.arange(half, S)]
    cf_margin, cf_same = [], []
    for f in (0, 1):
        sel, ev = folds[1 - f], folds[f]
        rr = {c: robust_aim(AIMS, Mx[c][sel].mean(0)) for c in M.ALL_CLUBS}
        o = sorted(M.ALL_CLUBS, key=lambda c: rr[c]["ev"])
        p_, r_ = o[0], o[1]
        e_p = interp_rows(AIMS, Mx[p_][ev], rr[p_]["aim"]).mean()
        e_r = interp_rows(AIMS, Mx[r_][ev], rr[r_]["aim"]).mean()
        cf_margin.append(e_r - e_p)
        cf_same.append(p_ == pick)
    # central-draw aim (v1 style: the aim for the prior-mean world) for comparison
    per_draw_aim = {c: [float(AIMS[int(row.argmin())]) for row in Mx[c]] for c in (pick, runner)}
    return dict(
        pick=pick, runner=runner, aim=res[pick]["aim"], ev=res[pick]["ev"], window=res[pick]["window"],
        at_bound=res[pick]["at_bound"], margin=float(d.mean()), margin_se=float(d.std(ddof=1) / np.sqrt(S)),
        swing_noise_share=s2_z / float(d.var(ddof=1)) if d.var() > 0 else None,
        crossfit_margin=float(np.mean(cf_margin)), crossfit_same_pick=cf_same,
        p_pick_beats_runner=float(np.mean(d > 0)), tie=bool(min(d.mean(), np.mean(cf_margin)) < TIE),
        per_draw_aim_sd=float(np.std(per_draw_aim[pick])),
        clubs={c: dict(aim=res[c]["aim"], ev=round(res[c]["ev"], 4), window=res[c]["window"],
                       window_width=res[c]["window_width"], at_bound=res[c]["at_bound"],
                       curve=[round(float(x), 4) for x in gaussian_filter1d(Mx[c].mean(0), 2.0)[::2]])
               for c in M.ALL_CLUBS},
        curve_aims=[float(x) for x in AIMS[::2]], draws=S, swings=N)


def shares_at(h, P, club, aim, n=20000):
    hd = M.HOLES[h]
    R = M.Raster(hd)
    Sc = R.strokes(P, hd["length"])
    z = M.draws_z(n, 5)
    _, (a, l, lie, s) = M.ev_curve(R, Sc, hd, club, P, z, np.array([aim]))
    sh = M.outcome_shares(R, lie[:, 0], a[:, 0], l[:, 0])
    car, dev, roll = M.shots(hd, club, P, z)
    sh["median_to_green"] = float(np.median(R.dist[R.idx(a[:, 0], l[:, 0])]))
    sh["mean_carry"] = float(car.mean())
    return {k: round(v, 4) for k, v in sh.items()}


def main():
    only = [x.strip() for x in os.environ.get("V2_HOLES", "").split(",") if x.strip()]
    S = int(os.environ.get("V2_DRAWS", 64))
    N = int(os.environ.get("V2_SWINGS", 3000))
    NC = int(os.environ.get("V2_CENTRAL_SWINGS", 12000))
    parts = os.environ.get("V2_PARTS", "bayes,ladder,sens,sweep").split(",")
    holes = [key(h) for h in only] if only else list(M.HOLES)
    out = {}
    for h in holes:
        t0 = time.time()
        r = {}
        if "bayes" in parts:
            r = bayes(h, S, N)
            r["shares"] = shares_at(h, M.central(), r["pick"], r["aim"])
        if "ladder" in parts:
            r["ladder"] = ladder(h, NC)
        if "sens" in parts:
            r["sens"] = sensitivities(h, NC)
        if "sweep" in parts:
            r["width_sweep"], r["width_flips"] = width_sweep(h, NC // 2)
        out[str(h)] = r
        print(h, r.get("pick"), r.get("aim"), r.get("window"), "margin %.3f" % r.get("margin", 0),
              "cf %.3f" % r.get("crossfit_margin", 0), f"{time.time() - t0:.0f}s", flush=True)
    path = os.environ.get("V2_OUT") or os.path.join(HERE, "output", "v2_decisions.json")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote", path)


if __name__ == "__main__":
    main()
