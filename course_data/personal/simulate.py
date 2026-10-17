"""Synthetic golfers: draw shots from a known pattern (for the recovery study and the tests).

truth = a dict of natural parameters for one golfer (as bayes.Model.params returns, one draw):
  {"W", "nu", "ps", "ph", "f", "dm", "roll", "clubs": {club: {width, carry, sd_c, bias, roll}}}

lm_shots / course_shots draw from the same generative model the likelihood uses (well specified), with
optional v2 extras (rho: push-slice/pull-hook carry correlation, kappa: curvature carry loss) to test
what happens when the data come from the richer simulator than the fitting model.
"""
import numpy as np

from bayes import HEAVY, SLIGHT, t_q


def truth_from(model, x):
    p = model.params(np.atleast_2d(x))
    one = lambda v: float(np.asarray(v)[0])                     # noqa: E731
    out = {k: one(v) for k, v in p.items() if k not in ("clubs", "sessions")}
    out["clubs"] = {k: {kk: one(vv) for kk, vv in c.items()} for k, c in p["clubs"].items()}
    out["sessions"] = {k: one(v) for k, v in p["sessions"].items()}
    return out


def _strike(truth, club, n, rng, range_=False, rho=0.0, kappa=0.0):
    c = truth["clubs"][club]
    nu = truth["nu"]
    width = c["width"] / (truth["f"] if range_ else 1.0)
    s = width / (2 * float(t_q(nu)))
    u = rng.random(n)
    kind = np.where(u < truth["ps"], 1, np.where(u < truth["ps"] + truth["ph"], 2, 0))
    t = rng.standard_t(nu, n) if np.isfinite(nu) else rng.standard_normal(n)
    zc = rng.standard_normal(n)
    mult = np.choose(kind, [1.0, SLIGHT["lat"], HEAVY["lat"]])
    lat = c["bias"] + s * mult * t
    zl = t / np.sqrt(np.maximum(np.var(t), 1e-9)) if rho else 0.0
    carry = c["carry"] + c["sd_c"] * (np.sqrt(1 - rho ** 2) * zc - rho * zl)
    if kappa:
        carry = carry - kappa * s * (np.abs(t) - np.sqrt(2 / np.pi))
    fr = rng.random(n)
    carry = np.where(kind == 1, c["carry"] * (SLIGHT["lo"] + (SLIGHT["hi"] - SLIGHT["lo"]) * fr), carry)
    carry = np.where(kind == 2, c["carry"] * (HEAVY["lo"] + (HEAVY["hi"] - HEAVY["lo"]) * fr), carry)
    return carry, lat, kind


def lm_shots(truth, club, n, rng, session="s0", ball="premium", session_offset=0.0, **kw):
    carry, lat, _ = _strike(truth, club, n, rng, range_=True, **kw)
    carry = carry + session_offset + rng.normal(0, 1.5, n)
    return [dict(club=club, carry=float(a), side=float(b), session=session, ball=ball, source="sim")
            for a, b in zip(carry, lat)]


def course_shots(truth, club, n, rng, aim_sd=3.0, gps_sd=5.0, cond_sd=8.0, beyond=35.0, **kw):
    """On-course tee shots: total = carry + roll (+-25 %) + conditions + GPS; lateral + aim + GPS noise.
    A ball more than `beyond` yds offline is a penalty / lost ball: recorded as censored on its side."""
    carry, lat, _ = _strike(truth, club, n, rng, **kw)
    c = truth["clubs"][club]
    roll = c["roll"] * (1 + 0.25 * (2 * rng.random(n) - 1))
    total = carry + roll + rng.normal(0, cond_sd, n) + rng.normal(0, gps_sd, n)
    obs_lat = lat + rng.normal(0, aim_sd, n) + rng.normal(0, gps_sd, n)
    out = []
    for i in range(n):
        if abs(lat[i]) > beyond:
            out.append(dict(club=club, total=None, lateral=None, censored="right" if lat[i] > 0 else "left",
                            beyond=beyond, aim_sd=aim_sd, gps_sd=gps_sd, cond_sd=cond_sd, source="sim"))
        else:
            out.append(dict(club=club, total=float(total[i]), lateral=float(obs_lat[i]), censored=None,
                            beyond=beyond, aim_sd=aim_sd, gps_sd=gps_sd, cond_sd=cond_sd, source="sim"))
    return out
