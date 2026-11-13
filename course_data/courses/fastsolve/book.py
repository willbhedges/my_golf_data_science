"""The calm-day book's prior-draw loop (decide.bayes) with three opt-in shortcuts. A careful copy of decide.bayes's
logic (the engine is not edited): with res=None, maps=0, race=0 it returns decide.bayes's dict, number for number
(the means come from the same kernel sums in the same order).

    import book
    book.install(M, D, res=1.0, maps=16, race=1)      # D.bayes -> book.bayes in THIS process (run.py --book-*)

res    raster cell (yds) of the prior-draw maps and value rasters (the engine: 0.5). The map edges are jittered by
       2.5 yds per draw; 1.0 paints a quarter of the cells. Only inside bayes: shares, ladder, sensitivities and the
       width sweep stay on the 0.5-yd raster.
maps   crossed design: K jittered maps (the map seeds of the first K prior draws) painted once per hole; draw s uses
       map s mod K. The map jitter is independent of the value parameters. 0 = one map per draw (the engine).
race   after the first RACE_START draws, every RACE_STEP draws: a club whose paired difference to the leader (each at
       its own best aim so far, same draws) exceeds TIE + RACE_T standard errors is not simulated any further. The
       leader and the runner-up are never dropped, so pick, margin, margin SE, cross-fit and the swing-noise share
       are over all draws. A dropped club is reported from the draws it has: its EV (and curve) are the pick's EV
       plus its paired margin to the pick over those draws, and it carries `draws` (< the book's).
"""
import numpy as np
from scipy.ndimage import gaussian_filter1d

RACE_START, RACE_STEP, RACE_T = 16, 8, 3.0
STATS = dict(curves=0, curves_full=0)


def bayes(M, D, h, S=64, N=3000, res=None, maps=0, race=0, seed=None):
    F = getattr(M, "_fastsolve", None)
    if F is None or F.mode is None:                       # no kernel for this engine set-up: the engine's own
        return D._bayes0(h, S, N)
    res0 = M.RES
    if res:
        M.RES = float(res)
    try:
        return _bayes(M, D, F, h, S, N, int(maps or 0), bool(race), seed)
    finally:
        M.RES = res0


def _bayes(M, D, F, h, S, N, K, race, seed):
    AIMS, robust_aim, interp_rows, TIE = D.AIMS, D.robust_aim, D.interp_rows, D.TIE
    hd = M.HOLES[h]
    draws = D.prior_draws(S, hole=h) if seed is None else D.prior_draws(S, seed=seed, hole=h)
    E = {c: [] for c in M.ALL_CLUBS}
    EA = {c: [] for c in M.ALL_CLUBS}
    EB = {c: [] for c in M.ALL_CLUBS}
    alive = list(M.ALL_CLUBS)
    rasters = {}
    k = N // 2
    for s, P in enumerate(draws):
        if K:
            R = rasters.get(s % K)
            if R is None:
                R = rasters[s % K] = M.Raster(hd, draws[s % K]["map_seed"])
        else:
            R = M.Raster(hd, P["map_seed"])
        Sc = R.strokes(P, hd["length"])
        z = M.draws_z(N, 1000 + s)
        for c in alive:
            st, vA, vB, vt = F.sums(R, Sc, hd, c, P, z, AIMS, None, ksplit=k)
            EA[c].append(vA / k)
            EB[c].append(vB / (N - k))
            E[c].append(vt / N)
        STATS["curves"] += len(alive)
        STATS["curves_full"] += len(M.ALL_CLUBS)
        n = s + 1
        if race and n >= RACE_START and n < S and (n - RACE_START) % RACE_STEP == 0 and len(alive) > 2:
            rr = {c: robust_aim(AIMS, np.mean(E[c], axis=0)) for c in alive}
            real = sorted((c for c in alive if c not in M.HYPOTHETICAL), key=lambda c: rr[c]["ev"])
            lead, second = real[0], real[1]
            vl = interp_rows(AIMS, E[lead], rr[lead]["aim"])
            for c in list(alive):
                if c in (lead, second):
                    continue
                d = interp_rows(AIMS, E[c], rr[c]["aim"]) - vl
                if d.mean() > TIE + RACE_T * d.std(ddof=1) / np.sqrt(n):
                    alive.remove(c)
    Mx = {c: np.vstack(E[c]) for c in M.ALL_CLUBS}
    MA = {c: np.vstack(EA[c]) for c in M.ALL_CLUBS}
    MB = {c: np.vstack(EB[c]) for c in M.ALL_CLUBS}
    res = {c: robust_aim(AIMS, Mx[c].mean(0)) for c in M.ALL_CLUBS}
    order = sorted((c for c in M.REAL_CLUBS if c in alive), key=lambda c: res[c]["ev"])
    pick, runner = order[0], order[1]
    vp = interp_rows(AIMS, Mx[pick], res[pick]["aim"])
    vr = interp_rows(AIMS, Mx[runner], res[runner]["aim"])
    # a club the race stopped: its paired margin to the pick over the draws it has; reported EV = pick's EV + that
    shift, used = {}, {}
    for c in M.ALL_CLUBS:
        nc = len(Mx[c])
        if nc < S:
            dm = float((interp_rows(AIMS, Mx[c], res[c]["aim"]) - vp[:nc]).mean())
            shift[c] = (res[pick]["ev"] + dm) - res[c]["ev"]
            used[c] = nc
    hy = M.HYBRID
    nh = len(Mx[hy])
    vh = interp_rows(AIMS, Mx[hy], res[hy]["aim"])
    dh = vh - vp[:nh]
    d = vr - vp
    dA = interp_rows(AIMS, MA[runner], res[runner]["aim"]) - interp_rows(AIMS, MA[pick], res[pick]["aim"])
    dB = interp_rows(AIMS, MB[runner], res[runner]["aim"]) - interp_rows(AIMS, MB[pick], res[pick]["aim"])
    s2_z = float(np.mean(((dA - dB) / 2) ** 2))
    # cross-fit: choose club + aim on one half of the draws, score on the other half (clubs with every draw)
    half = S // 2
    folds = [np.arange(half), np.arange(half, S)]
    cf_margin, cf_same = [], []
    for f in (0, 1):
        sel, ev = folds[1 - f], folds[f]
        rr = {c: robust_aim(AIMS, Mx[c][sel].mean(0)) for c in order}
        o = sorted(order, key=lambda c: rr[c]["ev"])
        p_, r_ = o[0], o[1]
        e_p = interp_rows(AIMS, Mx[p_][ev], rr[p_]["aim"]).mean()
        e_r = interp_rows(AIMS, Mx[r_][ev], rr[r_]["aim"]).mean()
        cf_margin.append(e_r - e_p)
        cf_same.append(p_ == pick)
    per_draw_aim = {c: [float(AIMS[int(row.argmin())]) for row in Mx[c]] for c in (pick, runner)}

    def club(c):
        sh = shift.get(c, 0.0)
        out = dict(aim=res[c]["aim"], ev=round(res[c]["ev"] + sh, 4), window=res[c]["window"],
                   window_width=res[c]["window_width"], at_bound=res[c]["at_bound"],
                   curve=[round(float(x) + sh, 4) for x in gaussian_filter1d(Mx[c].mean(0), 2.0)[::2]])
        if c in used:
            out["draws"] = used[c]
        return out
    return dict(
        pick=pick, runner=runner, aim=res[pick]["aim"], ev=res[pick]["ev"], window=res[pick]["window"],
        at_bound=res[pick]["at_bound"], margin=float(d.mean()), margin_se=float(d.std(ddof=1) / np.sqrt(S)),
        swing_noise_share=s2_z / float(d.var(ddof=1)) if d.var() > 0 else None,
        crossfit_margin=float(np.mean(cf_margin)), crossfit_same_pick=cf_same,
        p_pick_beats_runner=float(np.mean(d > 0)), tie=bool(min(d.mean(), np.mean(cf_margin)) < TIE),
        per_draw_aim_sd=float(np.std(per_draw_aim[pick])),
        temp_f=M.hole_temp(h),
        hybrid=dict(aim=res[hy]["aim"], vs_pick=float(dh.mean()),
                    se=float(dh.std(ddof=1) / np.sqrt(nh)), p_beats_pick=float(np.mean(dh < 0))),
        clubs={c: club(c) for c in M.ALL_CLUBS},
        curve_aims=[float(x) for x in AIMS[::2]], draws=S, swings=N)


def install(M, D, res=None, maps=0, race=0):
    """D.bayes -> this module's, in this process. Idempotent; install(M, D) with no options restores the engine's."""
    if not hasattr(D, "_bayes0"):
        D._bayes0 = D.bayes
    if not (res or maps or race):
        D.bayes = D._bayes0
        return D.bayes

    def fast_bayes(h, S=64, N=3000):
        return bayes(M, D, h, S, N, res=res, maps=maps, race=race)
    fast_bayes._book = dict(res=res, maps=maps, race=race)
    D.bayes = fast_bayes
    return fast_bayes
