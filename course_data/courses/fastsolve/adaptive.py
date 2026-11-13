"""Adaptive wind grids: one C call (kernel.c fs_grid) per (hole, tee offset, temperature) does every wind cell and
club: coarse basin search, 0.5-yd window, racing on paired block differences, sequential doubling of scrambled Sobol
swings until the pick is separated at 99 % and the aim is within +/-1 yd at 99 %, or the cap. NOT the engine's
numbers (other swings, other N): see README "Adaptive solve" for the agreement with the exact outputs.

    import adaptive
    WG2.solve = adaptive.install(M, D, WG2, cap=4096)        # then wind_grid_v2.main() as always (run.py --adaptive)

Each cell record is the wind grid's (pick, margin, runner, clubs{aim, ev, zone, carry, total, width, drift,
at_bound}) plus n_swings (the leader's), margin_se, tie (cap reached without 99 % separation), aim_se, and per club n.
"""
import ctypes
import os

import numpy as np

import fast

c_dp, c_i8p = fast.c_dp, fast.c_i8p


class Shot(ctypes.Structure):
    _fields_ = [(k, ctypes.c_double) for k in ("rho", "kappa", "skew", "mis_slight", "ms_lo", "ms_hi", "ms_lat",
                                               "mis_heavy", "mh_lo", "mh_hi", "mh_lat", "bias", "roll_noise",
                                               "rough_roll")] + [("v1_roll", ctypes.c_int)]


class Adapt(ctypes.Structure):
    _fields_ = [(k, ctypes.c_int) for k in ("n_coarse", "n0", "cap", "bs", "cstep", "half")] + \
               [(k, ctypes.c_double) for k in ("window", "aim_tol", "delta", "drop_t")] + [("min_all", ctypes.c_int)]


DEFAULTS = dict(n_coarse=128, n0=512, cap=4096, bs=64, cstep=6, half=20, window=0.005, aim_tol=1.0, delta=0.04,
                drop_t=3.0, min_all=512, seed=31)
STATS = dict(cells=0, balls=0, ties=0, aim_wide=0, grids=0)


def _lib():
    L = fast.lib()
    if not getattr(L, "_grid", False):
        i, d = ctypes.c_int, ctypes.c_double
        L.fs_grid.argtypes = [c_i8p, c_i8p, c_dp, i, i, d, d, d, c_dp, i, i, i, c_dp, c_dp, ctypes.POINTER(ctypes.c_int),
                              ctypes.POINTER(Shot), d, d, i, ctypes.POINTER(Adapt), c_dp, c_dp,
                              ctypes.POINTER(ctypes.c_longlong), i]
        L.fs_grid.restype = None
        L._grid = True
    return L


def grid(M, D, WG2, h, P, R, S, cells, z, opts):
    """Every (speed, rel) of `cells` for hole h in world P -> list of cell records."""
    L = _lib()
    W = WG2.W
    hd = M.HOLES[h]
    clubs = list(M.ALL_CLUBS)
    nc, nk = len(cells), len(clubs)
    par, lim = np.empty((nc, nk, 5)), np.empty((nc, nk, 2))
    page = {}
    for ci, (sp, rel) in enumerate(cells):
        for ki, c in enumerate(clubs):
            carry, roll, sl, sc = M.club_numbers(hd, c, P)
            drift = 0.0
            if sp:
                carry, roll, sl, sc, drift = WG2.wind_hook(c, sp, rel)(carry, roll, sl, sc)
            par[ci, ki] = (carry, roll, sl, sc, drift)
            lim[ci, ki] = (-D.AIM_LIMIT - drift, D.AIM_LIMIT - drift)
            carry0, total0, width0, depth0 = M.CLUBS[c]
            cy = carry0 * (1.0 - P["temp_k"] * (70.0 - P["temp_f"]))
            rl = P["soft_roll"] if P.get("soft_roll") is not None else (total0 - carry0) * P["roll_mult"]
            tup = (cy, cy + rl, P["width"][c], depth0 * P["depth_mult"])
            page[ci, ki] = W.adjust(tup, sp, rel, club_name=c) if sp else tup + (0.0,)
    sp_ = Shot(P["rho"], P["kappa"], P.get("skew") or 0.0, P["mis_slight"], P["mis_slight_carry"][0],
               P["mis_slight_carry"][1], P["mis_slight_lat"], P["mis_heavy"], P["mis_heavy_carry"][0],
               P["mis_heavy_carry"][1], P["mis_heavy_lat"], P["bias"], P["roll_noise"], P["rough_roll"],
               int(bool(P.get("v1_roll", False))))
    op = Adapt(*[opts[k] for k in ("n_coarse", "n0", "cap", "bs", "cstep", "half")],
               *[opts[k] for k in ("window", "aim_tol", "delta", "drop_t")], opts["min_all"])
    aims = WG2.AIMS
    lie = np.ascontiguousarray(R.lie, np.int8)
    pad = np.zeros(lie.size + 8, np.int8)
    pad[:lie.size] = lie.ravel()
    S = np.ascontiguousarray(S, np.float64)
    z = np.ascontiguousarray(z, np.float64)
    hyp = (ctypes.c_int * nk)(*[int(c in M.HYPOTHETICAL) for c in clubs])
    oc, oe = np.empty((nc, nk, 6)), np.empty((nc, 8))
    balls = ctypes.c_longlong(0)
    P_ = lambda a, t: a.ctypes.data_as(t)                                  # noqa: E731
    L.fs_grid(P_(lie, c_i8p), P_(pad, c_i8p) if L.simd else None, P_(S, c_dp), lie.shape[0], lie.shape[1], float(M.A0),
              float(M.L0), 1.0 / M.RES, P_(z, c_dp), z.shape[1], nc, nk, P_(par, c_dp), P_(lim, c_dp), hyp,
              ctypes.byref(sp_), float(aims[0]), float(aims[1] - aims[0]), len(aims), ctypes.byref(op), P_(oc, c_dp),
              P_(oe, c_dp), ctypes.byref(balls), fast.nthreads())
    out = []
    for ci in range(nc):
        res = {}
        for ki, c in enumerate(clubs):
            c2, t2, w2, d2, drift = page[ci, ki]
            o = oc[ci, ki]
            res[c] = dict(aim=float(o[0]), ev=float(o[1]), zone=[float(o[2]), float(o[3])], carry=float(c2),
                          total=float(t2), width=float(w2), drift=float(drift), at_bound=bool(o[4]), n=int(o[5]))
        e = oe[ci]
        out.append(dict(pick=clubs[int(e[0])], margin=float(e[2]), runner=clubs[int(e[1])], clubs=res,
                        n_swings=int(e[4]), margin_se=float(e[3]), tie=not bool(e[5]), aim_se=float(e[7]),
                        aim_ok=bool(e[6])))
        STATS["ties"] += int(not e[5])
        STATS["aim_wide"] += int(not e[6])
    STATS["cells"] += nc
    STATS["balls"] += balls.value
    STATS["grids"] += 1
    return out


def install(M, D, WG2, **over):
    """-> a solve(h, P, R, S, z, speed, rel) for wind_grid_v2.main: the first cell asked of a (hole, world) runs the
    whole grid in C, the other cells are read from it."""
    opts = dict(DEFAULTS, **{k: v for k, v in over.items() if v is not None})
    z = fast.sobol_draws(opts["cap"], opts["seed"])
    cache = {}

    def solve(h, P, R, S, z_unused, speed, rel):
        key = (h, id(R), P["temp_f"])
        if cache.get("key") != key:
            cells = [(sp, r) for sp in WG2.SPEEDS for r in ([0] if sp == 0 else WG2.DIRS)]
            if (speed, rel) not in cells:
                cells.append((speed, rel))
            cache.update(key=key, cells={c: r for c, r in zip(cells, grid(M, D, WG2, h, P, R, S, cells, z, opts))})
        return cache["cells"][(speed, rel)]
    solve._adaptive = opts
    return solve
