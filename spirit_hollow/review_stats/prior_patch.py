"""Suggested replacement prior for decision.py (review patch, not wired in).

Changes vs decision.prior_draws/apply (reasons in REVIEW.md section 3):
  * driver width centred on research.md (sigma ~21 yd -> 95% window ~82), 90% ~ 72-94,
    instead of median 70 (which puts research.md's point estimate at the prior's ~97th pct).
  * club-to-club width RATIOS are uncertain (they decide driver vs fairway wood); the app's
    65:60:50 fixes them exactly. Here 2-wood/driver ~ LN(0.94, 0.04), 4-wood/driver ~ LN(0.85, 0.06).
  * carry = common factor (swing speed, air, temperature) N(0, 6) + club-specific N(0, 3), not
    independent per club.
  * carry-depth scale (the CLUBS 4th field) x LN(1.5, 0.25): depth/4 = 7 yd is tight for a 5 hcp.
  * rough roll share U(0.15, 0.5) (fixed 0.3 in tee_strategy).
  * scoring table: 5-hcp baseline with probability 0.75, tour with 0.25 (decision.py always uses tour).
S should be a power of 2 (Sobol balance); 128 suggested.

    import prior_patch as PP
    for th in PP.prior_draws(128): PP.apply(th); ...
    PP.reset()
"""
import numpy as np
from scipy.stats import norm, qmc

import decision as D
import tee_strategy as t

DIMS = ["width", "r2w", "r4w", "c_common", "c_drv", "c_2w", "c_4w", "depth", "roll", "rough_roll",
        "trees", "lost", "mishit", "hcp", "map_seed"]
_SAVE = dict(rough_roll=t.ROUGH_ROLL, hcp=t.HCP_BASELINE)


def prior_draws(s=128, seed=11, width_median=82.0, width_hi90=94.0):
    u = qmc.Sobol(len(DIMS), scramble=True, seed=seed).random(s)
    z = norm.ppf(u)
    c = {k: i for i, k in enumerate(DIMS)}
    th = dict(
        width=np.exp(np.log(width_median / 65.0) + z[:, c["width"]] * np.log(width_hi90 / width_median) / 1.645),
        r2w=np.exp(np.log(0.94) + 0.04 * z[:, c["r2w"]]),
        r4w=np.exp(np.log(0.85) + 0.06 * z[:, c["r4w"]]),
        c_common=6.0 * z[:, c["c_common"]],
        c_drv=3.0 * z[:, c["c_drv"]], c_2w=3.0 * z[:, c["c_2w"]], c_4w=3.0 * z[:, c["c_4w"]],
        depth=np.exp(np.log(1.5) + 0.25 * z[:, c["depth"]]),
        roll=0.75 + 0.45 * u[:, c["roll"]],
        rough_roll=0.15 + 0.35 * u[:, c["rough_roll"]],
        trees=0.6 + 0.4 * u[:, c["trees"]],
        lost=0.35 + 0.30 * u[:, c["lost"]],
        mishit=0.10 + 0.10 * u[:, c["mishit"]],
        hcp=u[:, c["hcp"]] < 0.75,
        map_seed=(u[:, c["map_seed"]] * 1e9).astype(int))
    return [{k: th[k][i] for k in DIMS} for i in range(s)]


def apply(theta):
    """Map a v2 draw onto decision.apply (map jitter, trees, lost, mishit), then override clubs."""
    D.apply(dict(width=theta["width"], c_drv=0.0, c_2w=0.0, c_4w=0.0, roll=theta["roll"],
                 trees=theta["trees"], lost=theta["lost"], mishit=theta["mishit"], map_seed=theta["map_seed"]))
    # driver width in yds = 65 * width; other clubs = driver width x ratio
    wd = D.BASE["clubs"]["Driver"][2] * theta["width"]
    ratio = {"Driver": 1.0, "2-wood": theta["r2w"], "4-wood": theta["r4w"]}
    off = {k: theta["c_common"] + theta[f] for k, f in (("Driver", "c_drv"), ("2-wood", "c_2w"), ("4-wood", "c_4w"))}
    t.CLUBS = {k: (c + off[k], c + off[k] + (tot - c) * theta["roll"], wd * ratio[k], d * theta["depth"])
               for k, (c, tot, w, d) in D.BASE["clubs"].items()}
    w4 = wd * theta["r4w"]
    t.IRONS = {k: (c + off["4-wood"], c + off["4-wood"] + (tot - c) * theta["roll"],
                   w4 * w / D.BASE["clubs"]["4-wood"][2], d * theta["depth"])
               for k, (c, tot, w, d) in D.BASE["irons"].items()}
    t.ROUGH_ROLL = float(theta["rough_roll"])
    t.HCP_BASELINE = bool(theta["hcp"])


def reset():
    D.reset()
    t.ROUGH_ROLL, t.HCP_BASELINE = _SAVE["rough_roll"], _SAVE["hcp"]
