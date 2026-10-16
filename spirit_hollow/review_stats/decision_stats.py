"""Drop-in statistical fixes for spirit_hollow/decision.py (review patch, not wired in).

Nothing here edits decision.py; import it next to decision and swap the calls:

    import decision as D, decision_stats as DS
    E = {h: {} for h in holes}
    for si, th in enumerate(D.prior_draws()):
        D.apply(th); z = ...
        for h in holes:
            DS.accumulate(E[h], DS.ev_grid_halves(h, z))      # instead of D.ev_grid
    for h in holes:
        res[h] = DS.summarize(E[h])                            # replaces the per-hole block in main()

What changes, and why (see REVIEW.md):
  1. Each (club, aim) EV is kept as two independent half-sample means (swings 0..N/2-1 and
     N/2..N-1). That costs nothing extra and gives, per draw, an unbiased estimate of the
     simulation-noise variance of any paired difference: Var_noise(d) ~= ((d_A - d_B) / 2)^2.
  2. Margin SE is split into prior (theta) and swing (z) parts, so you can see whether more
     swings (N) or more draws (S) is what buys precision, and how many are needed.
  3. Winner's curse: the pick and the runner-up are chosen on one half of the draws and scored
     on the other (two-fold cross-fitting, contiguous Sobol halves, which are themselves nets).
  4. EVPI: the naive per-draw min over a noisy club x aim grid is biased low, so EVPI is biased
     high. Cross-fitted EVPI (choose on half the swings, score on the other half) is biased low.
     Report both as a bracket.
  5. P(best): the naive per-draw argmin counts swing noise as disagreement between "worlds".
     Two corrected versions: cross-fitted (own aim per draw chosen on A, scored on B), and a
     noise-deconvolved version at the posterior aims (shrink each per-draw club difference
     toward its mean so its variance equals the estimated prior part only).
"""
import numpy as np
from scipy.stats import norm

import decision as D
import tee_strategy as t


# --------------------------------------------------------------------------- simulation
def aims_for_club(h, c):
    return D.aims_for(h) if c not in t.IRONS else np.arange(-25, 45.1, D.AIM_STEP)


def ev_grid_halves(h, z):
    """Like decision.ev_grid, but returns (aims, ev_first_half, ev_second_half) per club."""
    k = z.shape[1] // 2
    out = {}
    for c in D.clubs_for(h):
        aims = aims_for_club(h, c)
        A, B = np.empty(len(aims)), np.empty(len(aims))
        for i, a in enumerate(aims):
            s = t.simulate(h, c, a, z=z)[3]
            A[i], B[i] = s[:k].mean(), s[k:].mean()
        out[c] = (aims, A, B)
    return out


def accumulate(Eh, grid):
    """Eh[c] = dict(aims, A=list of rows, B=list of rows)."""
    for c, (aims, A, B) in grid.items():
        e = Eh.setdefault(c, dict(aims=aims, A=[], B=[]))
        e["A"].append(A)
        e["B"].append(B)


def stack(Eh):
    """-> clubs, aims dict, MA, MB (dict club -> draws x aims)."""
    clubs = list(Eh)
    aims = {c: Eh[c]["aims"] for c in clubs}
    MA = {c: np.vstack(Eh[c]["A"]) for c in clubs}
    MB = {c: np.vstack(Eh[c]["B"]) for c in clubs}
    return clubs, aims, MA, MB


# --------------------------------------------------------------------------- pieces
def posterior_pick(M, clubs, rows=None):
    """argmin over (club, aim) of the mean over `rows` of M. Returns pick, runner, aim index per club."""
    rows = slice(None) if rows is None else rows
    col = {c: int(M[c][rows].mean(0).argmin()) for c in clubs}
    ev = {c: float(M[c][rows].mean(0)[col[c]]) for c in clubs}
    order = sorted(clubs, key=ev.get)
    return order[0], order[1], col, ev


def error_budget(dA, dB, target=0.005):
    """Split per-draw paired differences d = (dA + dB)/2 into prior and swing variance.

    Returns sigma2_theta (between-draw), sigma2_z (swing noise of d at the current N),
    the iid SE at the current S, and S needed for SE < target at N x {1, 2, 4}.
    """
    d = (dA + dB) / 2
    S = len(d)
    s2_tot = float(d.var(ddof=1))
    s2_z = float(np.mean(((dA - dB) / 2) ** 2))
    s2_th = max(s2_tot - s2_z, 0.0)
    need = {m: int(np.ceil((s2_th + s2_z / m) / target ** 2)) for m in (1, 2, 4)}
    return dict(sigma2_theta=s2_th, sigma2_z=s2_z, se=float(np.sqrt(s2_tot / S)),
                share_z=s2_z / s2_tot if s2_tot > 0 else float("nan"), S_needed_by_N_mult=need)


def crossfit_margin(M, clubs, S):
    """Two-fold cross-fitting over draws: choose pick/runner/aims on one half, score on the other."""
    h = S // 2
    folds = [np.arange(0, h), np.arange(h, S)]
    ev_in, ev_out, mar_in, mar_out = [], [], [], []
    for f in (0, 1):
        sel, ev_rows = folds[1 - f], folds[f]
        p, r, col, ev = posterior_pick(M, clubs, sel)
        ev_in.append(ev[p])
        mar_in.append(ev[r] - ev[p])
        e_p = M[p][ev_rows, col[p]].mean()
        e_r = M[r][ev_rows, col[r]].mean()
        ev_out.append(e_p)
        mar_out.append(e_r - e_p)
    return dict(optimism_ev=float(np.mean(ev_out) - np.mean(ev_in)),   # >0: in-sample EV too rosy
                margin_in=float(np.mean(mar_in)), margin_out=float(np.mean(mar_out)))


def evpi_bracket(MA, MB, clubs, pick, col_pick):
    """(naive, cross-fitted) EVPI. naive >= true >= crossfit, in expectation."""
    M = {c: (MA[c] + MB[c]) / 2 for c in clubs}
    v_pick = M[pick][:, col_pick]
    naive_min = np.min(np.stack([M[c].min(1) for c in clubs]), 0)
    cf = []
    for sel, ev in ((MA, MB), (MB, MA)):
        # per draw: club and aim chosen on `sel`, value read from `ev`
        allsel = np.hstack([sel[c] for c in clubs])
        allev = np.hstack([ev[c] for c in clubs])
        j = allsel.argmin(1)
        cf.append(allev[np.arange(len(j)), j])
    cf_min = np.mean(cf, 0)
    return float(np.mean(v_pick - naive_min)), float(np.mean(v_pick - cf_min))


def p_best_naive(M, clubs):
    w = np.argmin(np.stack([M[c].min(1) for c in clubs]), 0)
    return {c: float(np.mean(w == i)) for i, c in enumerate(clubs)}


def p_best_crossfit(MA, MB, clubs):
    """Own best aim per draw chosen on one half of the swings, club compared on the other half."""
    out = {c: 0.0 for c in clubs}
    for sel, ev in ((MA, MB), (MB, MA)):
        S = sel[clubs[0]].shape[0]
        vals = np.stack([ev[c][np.arange(S), sel[c].argmin(1)] for c in clubs])
        w = vals.argmin(0)
        for i, c in enumerate(clubs):
            out[c] += 0.5 * float(np.mean(w == i))
    return out


def p_best_deconvolved(MA, MB, clubs, col):
    """P(club is best) at the posterior aims, with swing noise removed by variance-matched shrinkage.

    For each club c, D_c[s] = V_c[s] - V_ref[s] (ref = posterior pick). Its observed variance is
    Var_theta + Var_noise; Var_noise is estimated from the two half samples. Shrinking every
    D_c[s] toward its mean by sqrt(Var_theta / Var_obs) gives a sample with the right prior
    spread; counting winners on it removes the noise-induced pull toward 50/50. (Exact for
    Gaussian D with homoscedastic noise; a good first-order fix otherwise.) Also returns the
    analytic pairwise Gaussian P(pick beats c) = Phi(mean / sd_theta).
    """
    ref = min(clubs, key=lambda c: ((MA[c] + MB[c]) / 2)[:, col[c]].mean())
    VA = {c: MA[c][:, col[c]] for c in clubs}
    VB = {c: MB[c][:, col[c]] for c in clubs}
    Dsh, pair = {}, {}
    for c in clubs:
        dA, dB = VA[c] - VA[ref], VB[c] - VB[ref]
        d = (dA + dB) / 2
        if c == ref:
            Dsh[c] = np.zeros_like(d)
            continue
        v_obs = d.var(ddof=1)
        v_z = np.mean(((dA - dB) / 2) ** 2)
        lam = np.sqrt(max(v_obs - v_z, 0.0) / v_obs) if v_obs > 0 else 0.0
        Dsh[c] = d.mean() + lam * (d - d.mean())
        sd_th = np.sqrt(max(v_obs - v_z, 0.0))
        pair[c] = float(norm.cdf(d.mean() / sd_th)) if sd_th > 0 else float(d.mean() > 0)
    w = np.argmin(np.stack([Dsh[c] for c in clubs]), 0)
    return {c: float(np.mean(w == i)) for i, c in enumerate(clubs)}, pair


def p_best_fixed_aims_naive(MA, MB, clubs, col):
    V = np.stack([((MA[c] + MB[c]) / 2)[:, col[c]] for c in clubs])
    w = V.argmin(0)
    return {c: float(np.mean(w == i)) for i, c in enumerate(clubs)}


# --------------------------------------------------------------------------- summary
def summarize(Eh, target_se=0.005):
    """Drop-in replacement for the per-hole block of decision.main()."""
    clubs, aims, MA, MB = stack(Eh)
    M = {c: (MA[c] + MB[c]) / 2 for c in clubs}
    S = M[clubs[0]].shape[0]
    pick, runner, col, ev = posterior_pick(M, clubs)
    dA = MA[runner][:, col[runner]] - MA[pick][:, col[pick]]
    dB = MB[runner][:, col[runner]] - MB[pick][:, col[pick]]
    budget = error_budget(dA, dB, target_se)
    evpi_naive, evpi_cf = evpi_bracket(MA, MB, clubs, pick, col[pick])
    pb_dec, pair = p_best_deconvolved(MA, MB, clubs, col)
    return dict(
        pick=pick, aim=float(aims[pick][col[pick]]), ev=ev[pick], runner=runner,
        margin=float(((dA + dB) / 2).mean()), margin_se=budget["se"], error_budget=budget,
        crossfit=crossfit_margin(M, clubs, S),
        evpi_naive=evpi_naive, evpi_crossfit=evpi_cf,
        p_best_naive=p_best_naive(M, clubs), p_best_crossfit=p_best_crossfit(MA, MB, clubs),
        p_best_fixed_aims_naive=p_best_fixed_aims_naive(MA, MB, clubs, col),
        p_best_fixed_aims_deconvolved=pb_dec, p_pick_beats=pair,
        clubs={c: dict(aim=float(aims[c][col[c]]), ev=ev[c]) for c in clubs})


# --------------------------------------------------------------------------- break-evens
def width_sweep(h, mode="driver_only", widths=(55, 60, 65, 70, 75, 80, 85, 90), n=6000):
    """decision.py's break-even sweep, plus mode="common": every club scaled by the same factor
    (the direction the prior actually moves in), so the club-to-club width ratio stays fixed."""
    mean_th = dict(width=D.CENTER_WIDTH / 65.0, c_drv=0.0, c_2w=0.0, c_4w=0.0, roll=1.0, trees=0.8,
                   lost=0.5, mishit=0.15, map_seed=0)
    zb = np.vstack([np.random.default_rng(9).standard_normal((2, n)), np.random.default_rng(10).random((2, n))])
    rows = []
    try:
        for W in widths:
            m = W / 65.0
            D.apply(dict(mean_th, width=m))
            t.HOLES = __import__("copy").deepcopy(D.BASE["holes"])
            if mode == "driver_only":
                for k, (c, tot, w, d) in D.BASE["clubs"].items():
                    t.CLUBS[k] = (c, tot, w * (m if k == "Driver" else D.CENTER_WIDTH / 65.0), d)
                # decision.py's sweep leaves the irons scaled by m (apply() does that); hold them
                # at the centre width too, so only the driver moves
                t.IRONS = {k: (c, tot, w * D.CENTER_WIDTH / 65.0, d) for k, (c, tot, w, d) in D.BASE["irons"].items()}
            g = D.ev_grid(h, zb)
            rows.append({c: float(ev.min()) for c, (_, ev) in g.items()})
    finally:
        D.reset()
    picks = [min(r, key=r.get) for r in rows]
    flips = []
    for i in range(len(widths) - 1):
        p0, p1 = picks[i], picks[i + 1]
        if p0 != p1:
            d0 = rows[i][p0] - rows[i][p1]
            d1 = rows[i + 1][p0] - rows[i + 1][p1]
            flips.append((widths[i] + (widths[i + 1] - widths[i]) * (-d0) / (d1 - d0), p0, p1))
    return picks, flips, rows
