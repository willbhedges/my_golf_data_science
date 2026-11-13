"""holesolve: a full-hole value solver by backward induction on the hole's lie raster (README.md).

Research build beside the engine: imports course_data/courses/v2_course.py and spirit_hollow/v2/model.py, edits
nothing, writes only under holesolve/. One process per (course base, tall-grass rule): the engine is activated once.

    from solver import World, CONFIG
    W = World("gateway_national", "truth")            # Back tees; "truth_middle" = Middle
    cal = W.calibration()                              # flat-hole calibration (cached per process)
    hs = W.solve_hole(10, cal=cal)                     # the DP on hole 10 -> HoleSolve (V fields, policy)
    hs.query(a, l, "fairway")                          # every club's best direction and strokes from a spot
    W.tee_solve(10, hs.tee_values())                   # the engine's own tee-shot solve on the DP's values
"""
import ctypes
import hashlib
import os
import subprocess
import sys
import time

import numpy as np
from matplotlib.path import Path
from scipy import ndimage
from scipy.stats import norm, qmc

HERE = os.path.dirname(os.path.abspath(__file__))
# HOLESOLVE_SNAP=<dir>: a frozen copy of the engine and the course inputs at one commit
# (git archive <commit> -- <paths> | tar -x -C <dir>; README.md), because the shared checkout moves under a running
# study (hole 10's map changed between two of this build's runs). HOLESOLVE_STATE names it in the results.
SNAP = os.environ.get("HOLESOLVE_SNAP")
COURSES = os.path.join(os.path.abspath(SNAP), "course_data", "courses") if SNAP else os.path.dirname(HERE)
sys.path.insert(0, COURSES)


def state():
    if os.environ.get("HOLESOLVE_STATE"):
        return os.environ["HOLESOLVE_STATE"]
    try:
        r = subprocess.run(["git", "-C", HERE, "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
        return r.stdout.strip() + (" (working tree)" if not SNAP else " (snapshot)")
    except Exception:                                                     # noqa: BLE001
        return "?"

# ------------------------------------------------------------------------------------------------ assumptions
# Everything the DP assumes about shots that are not tee shots is in this block (the tee shot is the engine's own).
# Clubs off the deck and the lie rules are the ones written in gateway_national/PAR5.md (opt/par5_second.py DECK / LIE)
# and the part swings of opt/layup10.py (PITCH); none of them is measured.
CONFIG = dict(
    # (carry at 70 F, total, 95 % width, 95 % carry window); widths x 70/65 and depths x 1.25 as the engine's
    # central world; the engine's mishits, tilt and roll noise (model.shots)
    clubs={
        "4-wood": (240, 255, 50, 24),          # 255 off a tee less 15; Driver and 2-wood are not hit off the deck
        "Long iron": (210, 220, 40, 20),
        "5-iron": (198, 206, 37, 19),          # the par-3 bag's club between the two (par3_target.py BAG)
        "Mid iron": (185, 192, 34, 18),
        "7-iron": (174, 180, 32, 17),          # the par-3 bag's
        "8-iron": (162, 167, 30, 16),
        "9-iron": (150, 154, 28, 15),
        "PW": (138, 141, 26, 14),
        "GW": (126, 128, 24, 13),
        "SW": (113, 115, 22, 12),
        # part swings: carry c, total c + 2, width / depth in proportion to the SW's, floors 10 / 8 yds
        **{f"pitch {c}": (c, c + 2, max(10.0, 22.0 * c / 113.0), max(8.0, 12.0 * c / 113.0))
           for c in (100, 90, 80, 70, 60, 50, 40, 30)},
    },
    # lie of the START: (spread x, carry x, longest club allowed)
    lie_rules={"fairway": (1.0, 1.0, "4-wood"), "rough": (1.25, 0.96, "Long iron"), "sand": (1.5, 0.93, "Mid iron")},
    temp_f=45.0,                 # calm, 45 F (carry x (1 - temp_k (70 - T)), the course's temp_k)
    anchor_yds=30.0,             # inside this distance of the hole, and anywhere on the green: the engine's table
    grid_yds=4.0,                # state grid
    node_margin=(60.0, 45.0, 110.0, 60.0),   # states from a = 60 to green + 45; l to +/-110 or 60 beyond the green
    angles=(-40.0, 40.0, 1.0),   # directions, deg either side of the line to the middle of the green
    angle_stride=4,              # coarse pass every 4 deg, then every degree round the best
    swings=256,                  # scrambled-Sobol swings per club and lie (common to every state and direction)
    swing_seed=20261113,
    club_over=20.0,              # a club is offered when its stock total is <= distance to the middle + this ...
    club_min_frac=0.35,          # ... and >= min(this x distance, 100)
    band_yds=20.0,               # sweep order: 20-yd bands of distance to the hole, nearest first
    tol=2e-3, max_sweeps=6,
    narrow_after=0.05, narrow_margin=0.15,   # sweeps after the first: only clubs within 0.15 of the best (HoleSolve.solve)
    back_on_line=(1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 120, 150),   # yds back from the reference
    flat=dict(length=640.0, half_fairway=18.0, green_radius=14.0, rough_lateral=25.0),  # the calibration hole
    cal_step=1.0,                # the calibration term is tabulated every yard (it has club-gap structure: 5 yds
                                 # left +/-0.04 on the flat hole inside 100 yds, 1 yd leaves +/-0.007)
)
LC = ("fairway", "rough", "sand")


# ------------------------------------------------------------------------------------------------ C kernel
def _kernel():
    src = os.path.join(HERE, "kernel.c")
    flags = ["-O3", "-march=native", "-fopenmp", "-shared", "-fPIC"]
    tag = hashlib.sha1(open(src, "rb").read() + " ".join(flags).encode() + os.uname().machine.encode()).hexdigest()[:12]
    bdir = os.environ.get("HOLESOLVE_BUILD") or os.path.join(HERE, "_build")
    os.makedirs(bdir, exist_ok=True)
    so = os.path.join(bdir, f"kernel_{tag}.so")
    if not os.path.exists(so):
        subprocess.check_call([os.environ.get("CC", "gcc")] + flags + ["-o", so + ".tmp", src, "-lm"])
        os.replace(so + ".tmp", so)
    L = ctypes.CDLL(so)
    P = ctypes.c_void_p
    I, F = ctypes.c_int, ctypes.c_float
    L.hs_backup.argtypes = [P, P, P, I, I, F, F, F, F, I, I, P, P, P, I, P, I, I, P, P, P, P, P, P, P, P, P, P, P, P]
    L.hs_backup.restype = None
    L.hs_curve.argtypes = [P, P, P, I, I, F, F, F, F, I, P, P, P, I, P, F, F, F, F, P, P]
    L.hs_curve.restype = None
    return L


_K = None


def K():
    global _K
    if _K is None:
        _K = _kernel()
    return _K


def _p(x):
    return x.ctypes.data_as(ctypes.c_void_p)


def f32(x):
    return np.ascontiguousarray(x, np.float32)


# ------------------------------------------------------------------------------------------------ swings
def sobol_z(n, seed):
    """model.shots() inputs (z_lat, z_car, u_mishit, u_frac, u_roll) from a scrambled Sobol set."""
    u = qmc.Sobol(5, scramble=True, seed=seed).random(n)
    u = np.clip(u, 1e-9, 1 - 1e-9)
    return np.vstack([norm.ppf(u[:, 0]), norm.ppf(u[:, 1]), u[:, 2], u[:, 3], u[:, 4]])


class Bag:
    """The deck clubs' swings by lie of the start, from the engine's own model.shots()."""

    def __init__(self, M, P, cfg=CONFIG, spread=1.0, spread_of=None):
        self.names = list(cfg["clubs"])
        nc, ns = len(self.names), cfg["swings"]
        z = sobol_z(ns, cfg["swing_seed"])
        self.car = np.zeros((3, nc, ns), np.float32)
        self.dev = np.zeros((3, nc, ns), np.float32)
        self.roll = np.zeros((3, nc, ns), np.float32)
        self.stock = np.zeros((3, nc))
        self.allowed = np.zeros((3, nc), bool)
        for c, nm in enumerate(self.names):
            M.CLUBS["hs:" + nm] = tuple(float(x) for x in cfg["clubs"][nm])
        for i, lc in enumerate(LC):
            sp, cm, longest = cfg["lie_rules"][lc]
            first = self.names.index(longest)
            for c, nm in enumerate(self.names):
                key = "hs:" + nm
                s2 = sp * spread * ((spread_of or {}).get(nm, 1.0))
                P2 = dict(P)
                P2["width"] = dict(P["width"])
                P2["width"][key] = cfg["clubs"][nm][2] * (70.0 / 65.0) * s2
                P2["depth_mult"] = P["depth_mult"] * s2

                def hook(carry, roll, sl, sc, cm=cm):
                    return carry * cm, roll, sl, sc, 0.0
                car, dev, roll = M.shots({}, key, P2, z, wind=hook)
                self.car[i, c], self.dev[i, c], self.roll[i, c] = car, dev, roll
                c0, r0, _, _ = M.club_numbers({}, key, P2)
                self.stock[i, c] = c0 * cm + r0
                self.allowed[i, c] = c >= first


# ------------------------------------------------------------------------------------------------ ground
class Ground:
    """A lie raster in the tee frame with the engine's table values on it, prepared for the kernel."""

    def __init__(self, M, R, P, length, origin, lost=False, cfg=CONFIG):
        self.M, self.R, self.P, self.cfg = M, R, P, cfg
        self.A0, self.L0 = origin
        self.res = float(M.RES)
        self.lie = R.lie
        self.na, self.nl = R.lie.shape
        self.green = np.asarray(R.green, float)
        self.dist = R.dist
        self.S = np.asarray(R.strokes(P, length), float)                 # the engine's value of every cell
        hd = R.hd
        gp = hd.get("green_poly")
        if hd.get("green_poly_px") is not None:
            tee, fwd, right, ppy = M.frame(hd)
            dd = (np.asarray(hd["green_poly_px"], float) - tee) / ppy
            gp = np.column_stack([dd @ fwd, dd @ right])
        self.gpoly = None if gp is None else np.asarray(gp, float)
        if self.gpoly is None:
            self.ongreen = np.zeros(self.lie.shape, bool)
        else:
            self.ongreen = Path(self.gpoly).contains_points(
                np.column_stack([R.AA.ravel(), R.LL.ravel()])).reshape(self.lie.shape)
        C = M.CODE
        rk = np.full(self.lie.shape, 2, np.int8)                         # sand, trees, unverified: dry, ball stops
        rk[(self.lie == C["fairway"]) | (self.lie == C["first_cut"])] = 0
        rk[self.lie == C["rough"]] = 1
        rk[self.lie == C["water"]] = 3
        rk[self.lie == C["ob"]] = 4
        if lost:
            rk[self.lie == C["native"]] = 4
        self.rk = np.ascontiguousarray(rk)
        self.term = (self.dist < cfg["anchor_yds"]) | self.ongreen       # the anchor: the table as it is
        # which lie class's DP-minus-table difference a cell takes (first cut: a blend)
        self.sel = np.ones(self.lie.shape, np.int8)
        self.sel[self.lie == C["fairway"]] = 0
        self.sel[self.lie == C["sand"]] = 2
        self.sel[self.lie == C["first_cut"]] = 3
        self._edges()

    def idx(self, a, l):
        ia = np.clip(np.rint((np.asarray(a) - self.A0) / self.res).astype(np.int64), 0, self.na - 1)
        il = np.clip(np.rint((np.asarray(l) - self.L0) / self.res).astype(np.int64), 0, self.nl - 1)
        return ia, il

    def table(self, lc, d):
        return self.M.table(LC[lc] if isinstance(lc, int) else lc, d, self.P)

    def _edges(self):
        """Dry cells within 2 yds of a drop-rule penalty cell (where a relief reference point can be), and for each
        the cells back on the line from the hole through it."""
        pen = self.rk == 3
        self.edge = np.zeros(0, np.int64)
        if not pen.any():
            return
        near = ndimage.binary_dilation(pen, iterations=int(round(2.0 / self.res))) & (self.rk <= 2)
        ia, il = np.nonzero(near)
        a, l = self.R.a[ia], self.R.l[il]
        d = np.maximum(np.hypot(self.green[0] - a, self.green[1] - l), 1e-6)
        ua, ul = (self.green[0] - a) / d, (self.green[1] - l) / d
        t = np.asarray(self.cfg["back_on_line"], float)
        pa, pl = a[:, None] - t[None, :] * ua[:, None], l[:, None] - t[None, :] * ul[:, None]
        ok = (pa >= self.A0) & (pa <= self.R.a[-1]) & (pl >= self.L0) & (pl <= self.R.l[-1])
        ja, jl = self.idx(pa, pl)
        ok &= self.rk[ja, jl] <= 2
        self.edge = ia * self.nl + il
        self.back = np.where(ok, ja * self.nl + jl, -1)


class HoleSolve:
    """The DP on one Ground: V by lie class on a node grid, held as the difference from the engine's table."""

    def __init__(self, G, bag, cal=None, cfg=CONFIG, verbose=False):
        self.G, self.bag, self.cfg, self.cal = G, bag, cfg, cal
        g = cfg["grid_yds"]
        m = cfg["node_margin"]
        a_hi = min(G.R.a[-1], G.green[0] + m[1])
        l_lo = max(G.L0, min(-m[2], G.green[1] - m[3]))
        l_hi = min(G.R.l[-1], max(m[2], G.green[1] + m[3]))
        self.ga = np.arange(m[0], a_hi + 1e-6, g)
        self.gl = np.arange(np.ceil(l_lo / g) * g, l_hi + 1e-6, g)
        nga, ngl = len(self.ga), len(self.gl)
        NA, NL = np.meshgrid(self.ga, self.gl, indexing="ij")
        self.nd = np.hypot(G.green[0] - NA, G.green[1] - NL)
        ia, il = G.idx(NA, NL)
        term = G.term[ia, il]
        # which nodes are solved per lie class: rough everywhere; fairway / sand where such a cell is within a node
        r = int(round(g / G.res))
        fw = ndimage.maximum_filter((G.sel == 0) | (G.sel == 3), size=2 * r + 1)[ia, il]
        sa = ndimage.maximum_filter(G.sel == 2, size=2 * r + 1)[ia, il]
        self.active = np.stack([fw & ~term, ~term, sa & ~term])
        self.delta = np.zeros((3, nga, ngl), np.float32)
        self.Tn = np.stack([G.table(i, self.nd) for i in range(3)])
        # bilinear weights of every raster cell on the node grid
        fa = np.clip((G.R.a - self.ga[0]) / g, 0, nga - 1 - 1e-6)
        fl = np.clip((G.R.l - self.gl[0]) / g, 0, ngl - 1 - 1e-6)
        self._i0, self._wa = np.floor(fa).astype(np.int64), (fa - np.floor(fa)).astype(np.float32)
        self._j0, self._wl = np.floor(fl).astype(np.int64), (fl - np.floor(fl)).astype(np.float32)
        # states
        st = []
        for lc in range(3):
            i, j = np.nonzero(self.active[lc])
            st.append(np.column_stack([np.full(len(i), lc), i, j]))
        st = np.concatenate(st)
        d = self.nd[st[:, 1], st[:, 2]]
        o = np.argsort(d, kind="stable")
        self.st, self.sd = st[o], d[o]
        self.sa_, self.sl_ = f32(self.ga[self.st[:, 1]]), f32(self.gl[self.st[:, 2]])
        self.th0 = f32(np.arctan2(G.green[1] - self.sl_, G.green[0] - self.sa_))
        self.slc = np.ascontiguousarray(self.st[:, 0], np.int32)
        self.mask = self.club_mask(self.slc, self.sd)
        self.calv = f32(self.cal_of(self.slc, self.sd))
        ang = cfg["angles"]
        self.ang = np.radians(np.arange(ang[0], ang[1] + 1e-9, ang[2])).astype(np.float32)
        n = len(self.st)
        self.V = f32(self.Tn[self.st[:, 0], self.st[:, 1], self.st[:, 2]])
        self.bclub = np.full(n, -1, np.int32)
        self.bang = np.zeros(n, np.float32)
        self.evc = np.zeros((n, len(bag.names)), np.float32)
        self.angc = np.zeros((n, len(bag.names)), np.float32)
        self.refresh()
        self.log = []
        self.verbose = verbose

    # ---- pieces
    def club_mask(self, lc, d):
        st = self.bag.stock[lc]                                           # [n][nclub]
        d = np.asarray(d, float)[:, None]
        ok = self.bag.allowed[lc] & (st <= d + self.cfg["club_over"]) & (st >= np.minimum(self.cfg["club_min_frac"] * d, 100.0))
        none = ~ok.any(1)                                                 # nothing fits: the shortest club
        ok[none, len(self.bag.names) - 1] = True
        return np.ascontiguousarray((ok * (1 << np.arange(ok.shape[1]))).sum(1), np.uint32)

    def cal_of(self, lc, d):
        if self.cal is None:
            return np.zeros(len(np.atleast_1d(d)))
        lc, d = np.atleast_1d(lc), np.atleast_1d(d)
        out = np.zeros(len(d))
        for i in range(3):
            m = lc == i
            out[m] = np.interp(d[m], self.cal["d"], self.cal["c"][i])
        return out

    def _interp(self, D, rows=slice(None), cols=slice(None)):
        i0, j0 = self._i0[rows, None], self._j0[None, cols]
        wa, wl = self._wa[rows, None], self._wl[None, cols]
        return ((1 - wa) * ((1 - wl) * D[i0, j0] + wl * D[i0, j0 + 1])
                + wa * ((1 - wl) * D[i0 + 1, j0] + wl * D[i0 + 1, j0 + 1]))

    def cell_delta(self, sel, term, interp=None):
        """DP minus table for the cells of a raster (sel = lie class per cell, 3 = first cut)."""
        I = interp or self._interp
        D = self.delta.copy()
        D[0][~self.active[0]] = D[1][~self.active[0]]                    # no fairway / sand state there: rough's
        D[2][~self.active[2]] = D[1][~self.active[2]]
        I0, I1, I2 = I(D[0]), I(D[1]), I(D[2])
        fc = self.G.P["first_cut"]
        dl = np.where(sel == 0, I0, np.where(sel == 2, I2, np.where(sel == 3, I0 + fc * (I1 - I0), I1)))
        return np.where(term, 0.0, dl)

    def refresh(self, nodes=None):
        """Cell and drop values from the node differences. nodes = (i, j) of the nodes that changed: only the cells
        whose interpolation uses them are recomputed."""
        G = self.G
        rows = cols = slice(None)
        if nodes is not None and len(nodes[0]):
            g = self.cfg["grid_yds"]
            i0, i1, j0, j1 = nodes[0].min() - 1, nodes[0].max() + 1, nodes[1].min() - 1, nodes[1].max() + 1
            r0 = 0 if i0 <= 0 else int(np.searchsorted(G.R.a, self.ga[i0] - 1e-6))
            r1 = G.na if i1 >= len(self.ga) - 1 else int(np.searchsorted(G.R.a, self.ga[i1] + 1e-6, side="right"))
            c0 = 0 if j0 <= 0 else int(np.searchsorted(G.R.l, self.gl[j0] - 1e-6))
            c1 = G.nl if j1 >= len(self.gl) - 1 else int(np.searchsorted(G.R.l, self.gl[j1] + 1e-6, side="right"))
            rows, cols = slice(r0, r1), slice(c0, c1)
            dl = self.cell_delta(G.sel[rows, cols], G.term[rows, cols], lambda D: self._interp(D, rows, cols))
            self.cellv[rows, cols] = G.S[rows, cols] + dl
        else:
            self.cellv = f32(G.S + self.cell_delta(G.sel, G.term))
        self.dropv = self.cellv.copy()
        if len(G.edge):
            flat = self.cellv.ravel()
            b = np.where(G.back >= 0, flat[np.maximum(G.back, 0)], np.inf).min(1)
            self.dropv.ravel()[G.edge] = np.minimum(flat[G.edge], b)

    def _backup(self, sl, mask=None):
        G, B = self.G, self.bag
        n = sl.stop - sl.start
        v = np.zeros(n, np.float32)
        mask = self.mask if mask is None else mask
        K().hs_backup(_p(G.rk), _p(self.cellv), _p(self.dropv), G.na, G.nl, G.A0, G.L0, G.res, G.P["rough_roll"],
                      len(B.names), B.car.shape[2], _p(B.car), _p(B.dev), _p(B.roll),
                      len(self.ang), _p(self.ang), self.cfg["angle_stride"],
                      n, _p(self.sa_[sl]), _p(self.sl_[sl]), _p(self.th0[sl]), _p(self.slc[sl]), _p(mask[sl]),
                      _p(self.calv[sl]), _p(self.V[sl]), _p(v), _p(self.bclub[sl]), _p(self.bang[sl]),
                      _p(self.evc[sl]), _p(self.angc[sl]))
        return v

    def solve(self):
        t0 = time.time()
        band = self.cfg["band_yds"]
        edges = np.searchsorted(self.sd, np.arange(self.sd.min(), self.sd.max() + band, band))
        edges = np.unique(np.concatenate([[0], edges, [len(self.sd)]]))
        mask = None
        for sweep in range(self.cfg["max_sweeps"]):
            ts = time.time()
            if sweep == 1 or (sweep and worst < self.cfg["narrow_after"]):
                # after the first (nearest-first) sweep the values are nearly final: later sweeps re-search only
                # the clubs that were within narrow_margin of the best from each state (every direction again);
                # a narrowed sweep that still moves a value by narrow_after is followed by a full one
                best = self.evc.min(1, keepdims=True)
                keep = self.evc <= best + self.cfg["narrow_margin"]
                mask = np.ascontiguousarray((keep * (1 << np.arange(keep.shape[1]))).sum(1), np.uint32) & self.mask
                mask = np.where(mask == 0, self.mask, mask).astype(np.uint32)
            else:
                mask = None
            worst = 0.0
            for a, b in zip(edges[:-1], edges[1:]):
                sl = slice(int(a), int(b))
                v = self._backup(sl, mask)
                worst = max(worst, float(np.abs(v - self.V[sl]).max()))
                self.V[sl] = v
                s = self.st[sl]
                self.delta[s[:, 0], s[:, 1], s[:, 2]] = v - self.Tn[s[:, 0], s[:, 1], s[:, 2]]
                self.refresh((s[:, 1], s[:, 2]))
            self.log.append(dict(sweep=sweep + 1, max_change=round(worst, 5), secs=round(time.time() - ts, 2)))
            if self.verbose:
                print("   sweep", self.log[-1], flush=True)
            if worst < self.cfg["tol"]:
                break
        self.secs = time.time() - t0
        return self

    # ---- reading the solution
    def node_value(self, lc):
        """V on the node grid for a lie class (nan where not a state)."""
        out = np.full(self.nd.shape, np.nan)
        m = self.st[:, 0] == lc
        out[self.st[m, 1], self.st[m, 2]] = self.V[m]
        return out

    def value_at(self, a, l, lie):
        """Strokes to hole out for a ball at rest at (a, l): the raster's own lie if lie is None."""
        ia, il = self.G.idx(a, l)
        if lie is None:
            return float(self.cellv[ia, il])
        lc = LC.index(lie)
        d = float(np.hypot(self.G.green[0] - a, self.G.green[1] - l))
        D = self.delta.copy()
        D[0][~self.active[0]] = D[1][~self.active[0]]
        D[2][~self.active[2]] = D[1][~self.active[2]]
        g = self.cfg["grid_yds"]
        fa = np.clip((a - self.ga[0]) / g, 0, len(self.ga) - 1 - 1e-6)
        fl = np.clip((l - self.gl[0]) / g, 0, len(self.gl) - 1 - 1e-6)
        i, j, wa, wl = int(fa), int(fl), fa - int(fa), fl - int(fl)
        dl = ((1 - wa) * ((1 - wl) * D[lc, i, j] + wl * D[lc, i, j + 1])
              + wa * ((1 - wl) * D[lc, i + 1, j] + wl * D[lc, i + 1, j + 1]))
        return float(self.G.table(lc, d) + dl)

    def query(self, a, l, lie, clubs=None, all_clubs=False):
        """Every offered club's best direction from (a, l) in `lie`: list of dicts, best first.
        strokes include the calibration term of this spot, so the best row equals V here."""
        G, B = self.G, self.bag
        lc = LC.index(lie)
        d = float(np.hypot(G.green[0] - a, G.green[1] - l))
        sa, sl_ = f32([a]), f32([l])
        th0 = f32([np.arctan2(G.green[1] - l, G.green[0] - a)])
        slc = np.array([lc], np.int32)
        mask = self.club_mask(slc, [d])
        if all_clubs:
            mask = np.array([int((B.allowed[lc] * (1 << np.arange(len(B.names)))).sum())], np.uint32)
        if clubs:
            mask = np.array([sum(1 << B.names.index(c) for c in clubs)], np.uint32)
        cal = f32(self.cal_of(slc, [d]))
        vself = f32([self.value_at(a, l, lie)])
        v, bc, ba = np.zeros(1, np.float32), np.zeros(1, np.int32), np.zeros(1, np.float32)
        evc, angc = np.zeros((1, len(B.names)), np.float32), np.zeros((1, len(B.names)), np.float32)
        K().hs_backup(_p(G.rk), _p(self.cellv), _p(self.dropv), G.na, G.nl, G.A0, G.L0, G.res, G.P["rough_roll"],
                      len(B.names), B.car.shape[2], _p(B.car), _p(B.dev), _p(B.roll), len(self.ang), _p(self.ang), 1,
                      1, _p(sa), _p(sl_), _p(th0), _p(slc), _p(mask), _p(cal), _p(vself), _p(v), _p(bc), _p(ba),
                      _p(evc), _p(angc))
        rows = []
        for c, nm in enumerate(B.names):
            if not (int(mask[0]) >> c) & 1 or evc[0, c] > 1e30:
                continue
            th = float(th0[0] + angc[0, c])
            st = float(B.stock[lc, c])
            ta, tl = a + st * np.cos(th), l + st * np.sin(th)
            sh = self.shares(a, l, lie, nm, th)
            rows.append(dict(club=nm, strokes=round(float(evc[0, c] + cal[0]), 4), ang=round(float(np.degrees(angc[0, c])), 1),
                             stock=round(st, 1), target=[round(float(ta), 1), round(float(tl), 1)],
                             leave=round(float(np.hypot(G.green[0] - ta, G.green[1] - tl)), 1), **sh))
        rows.sort(key=lambda r: r["strokes"])
        return dict(d=round(d, 1), lie=lie, value=round(float(v[0]), 4), cal=round(float(cal[0]), 4), rows=rows)

    def swings(self, a0, l0, lie, club, th):
        """numpy copy of the kernel's swing loop for one club and direction: finish (a, l), kind, value per ball
        (nan = ball gone). Used for the outcome shares and to test the kernel."""
        G, B = self.G, self.bag
        lc, c = LC.index(lie), B.names.index(club)
        car, dev, roll = (x[lc, c].astype(np.float32) for x in (B.car, B.dev, B.roll))
        a0, l0 = np.float32(a0), np.float32(l0)
        ua, ul = np.float32(np.cos(np.float32(th))), np.float32(np.sin(np.float32(th)))
        a, l = a0 + car * ua - dev * ul, l0 + car * ul + dev * ua
        n = np.hypot(a - a0, l - l0)
        fa = np.where(n > 1e-6, (a - a0) / np.maximum(n, 1e-9), ua).astype(np.float32)
        fl = np.where(n > 1e-6, (l - l0) / np.maximum(n, 1e-9), ul).astype(np.float32)
        rr = np.float32(G.P["rough_roll"])
        k = G.rk[G.idx(a, l)]
        la, ll = a.copy(), l.copy()
        left = roll.copy()
        left = np.where(k == 1, left * rr, left)
        left = np.where(k >= 2, np.float32(0), left)
        while (left > 1e-6).any():
            mv = left > 1e-6
            st = np.minimum(left, np.float32(2)) * mv
            a, l = a + fa * st, l + fl * st
            left = left - st
            nk = G.rk[G.idx(a, l)]
            left = np.where(mv & (nk == 1) & (k == 0), left * rr, left)
            left = np.where(mv & (nk >= 2), np.float32(0), left)
            k = np.where(mv, nk, k)
        ia, il = G.idx(a, l)
        v = self.cellv[ia, il].astype(float)
        v[k == 4] = np.nan
        vself = self.value_at(float(a0), float(l0), lie)
        da, dl_ = np.full(len(a), np.nan), np.full(len(a), np.nan)
        for i in np.nonzero(k == 3)[0]:
            nn = np.float32(np.hypot(a[i] - a0, l[i] - l0))
            t = nn - np.float32(1)
            while True:
                if t <= 0:
                    v[i] = 1.0 + vself
                    da[i], dl_[i] = a0, l0
                    break
                qa, ql = a0 + fa[i] * t, l0 + fl[i] * t
                q = G.idx(qa, ql)
                if G.rk[q] <= 2:
                    v[i] = 1.0 + float(self.dropv[q])
                    da[i], dl_[i] = qa, ql
                    break
                t -= np.float32(1)
        return dict(a=a, l=l, kind=k, v=v, drop_a=da, drop_l=dl_, land_a=la, land_l=ll, car=car)

    def shares(self, a0, l0, lie, club, th):
        G = self.G
        s = self.swings(a0, l0, lie, club, th)
        ia, il = G.idx(s["a"], s["l"])
        on = G.ongreen[ia, il] & (s["kind"] <= 2)
        code = G.lie[ia, il]
        C = G.M.CODE
        return dict(green=round(float(on.mean()), 3), penalty=round(float((s["kind"] >= 3).mean()), 3),
                    sand=round(float(((code == C["sand"]) & ~on).mean()), 3),
                    trees=round(float((code == C["recovery"]).mean()), 3),
                    fairway=round(float((((code == C["fairway"]) | (code == C["first_cut"])) & ~on).mean()), 3))

    def tee_values(self, R, S_tab, lost_marker=None):
        """The engine's tee-shot value raster with the DP's values: S + (DP - table) on dry cells; penalty cells one
        stroke + the DP's drop value at the point where the ball crossed the edge on the tee line."""
        G, M = self.G, self.G.M
        C = M.CODE
        sel = np.ones(R.lie.shape, np.int8)
        sel[R.lie == C["fairway"]] = 0
        sel[R.lie == C["sand"]] = 2
        sel[R.lie == C["first_cut"]] = 3
        g = self.cfg["grid_yds"]
        fa = np.clip((R.a - self.ga[0]) / g, 0, len(self.ga) - 1 - 1e-6)
        fl = np.clip((R.l - self.gl[0]) / g, 0, len(self.gl) - 1 - 1e-6)
        i0, wa = np.floor(fa).astype(np.int64)[:, None], (fa - np.floor(fa))[:, None]
        j0, wl = np.floor(fl).astype(np.int64)[None, :], (fl - np.floor(fl))[None, :]

        def interp(D):
            return ((1 - wa) * ((1 - wl) * D[i0, j0] + wl * D[i0, j0 + 1])
                    + wa * ((1 - wl) * D[i0 + 1, j0] + wl * D[i0 + 1, j0 + 1]))
        ja, jl = G.idx(R.AA, R.LL)
        term = G.term[ja, jl]
        S = np.asarray(S_tab, float) + self.cell_delta(sel, term, interp)
        w = np.argwhere(R.lie == C["water"])
        if len(w):
            a, l = R.a[w[:, 0]], R.l[w[:, 1]]
            r = np.hypot(a, l)
            found = np.zeros(len(w), bool)
            ea, el = a.copy(), l.copy()
            for k in np.arange(1, 121, 1.0):                             # model.Raster._water_entry, keeping the point
                s = np.maximum(r - k, 0) / np.maximum(r, 1e-9)
                pa, pl = a * s, l * s
                new = (R.lie_at(pa, pl) != C["water"]) & ~found
                ea[new], el[new] = pa[new], pl[new]
                found |= new
                if found.all():
                    break
            qa, ql = G.idx(ea, el)
            ok = found & (G.rk[qa, ql] <= 2)
            val = np.asarray(S_tab, float)[w[:, 0], w[:, 1]]
            val[ok] = 1.0 + self.dropv[qa[ok], ql[ok]]
            S[w[:, 0], w[:, 1]] = val
        keep = (R.lie == C["ob"]) | (np.asarray(S_tab) < 0)              # OB and lost-ball markers: the engine's
        S[keep] = np.asarray(S_tab, float)[keep]
        return S


# ------------------------------------------------------------------------------------------------ world
class World:
    def __init__(self, slug="gateway_national", which="truth", tall="drop", cfg=CONFIG):
        import v2_course as vc
        self.vc, self.slug, self.which, self.tall, self.cfg = vc, slug, which, tall, cfg
        self.course, self.meta, self.M, self.D = vc.activate(slug, which, tall_grass="lost" if tall == "lost" else None)
        self.P = self.M.central(temp_f=cfg["temp_f"])
        self.bag = Bag(self.M, self.P, cfg)
        self._cal = None
        self._eng = {}

    # ---- rasters
    def big_raster(self, hd):
        """The hole's lie raster out past the green (the engine's stops 430 yds out); untraced ground = rough."""
        M = self.M
        R0 = M.Raster(hd)
        keep = (M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH)
        try:
            M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH = int(R0.green[0] + 70), -170, 170, 1e9
            Rb = M.Raster(hd)
            origin = (float(M.A0), float(M.L0))
            na, nl = len(Rb.a), len(Rb.l)

            def idx(a, l, A0=origin[0], L0=origin[1]):
                ia = np.clip(np.rint((np.asarray(a) - A0) / M.RES).astype(np.int32), 0, na - 1)
                il = np.clip(np.rint((np.asarray(l) - L0) / M.RES).astype(np.int32), 0, nl - 1)
                return ia, il
            Rb.idx = idx
            Rb.lie_at = lambda a, l: Rb.lie[idx(a, l)]
            Rb._blocked()
        finally:
            M.A1, M.L0, M.L1, M.CHECKED_HALF_WIDTH = keep
        return R0, Rb, origin

    def flat_raster(self):
        """The calibration hole: a straight fairway, rough either side, a round green; no trouble."""
        M, f = self.M, self.cfg["flat"]
        length, hw, rad = f["length"], f["half_fairway"], f["green_radius"]
        A0, L0 = -10.0, -120.0
        a = np.arange(A0, length + 60 + M.RES / 2, M.RES)
        l = np.arange(L0, 120 + M.RES / 2, M.RES)
        R = object.__new__(M.Raster)
        R.a, R.l = a, l
        R.AA, R.LL = np.meshgrid(a, l, indexing="ij")
        R.green = np.array([length, 0.0])
        R.dist = np.hypot(R.AA - length, R.LL)
        lie = np.zeros(R.AA.shape, np.int8)
        lie[(np.abs(R.LL) <= hw) & (R.AA < length - rad)] = M.CODE["fairway"]
        lie[R.dist <= rad] = M.CODE["fairway"]
        R.lie = lie
        R.native_depth = np.zeros(lie.shape)
        R.entry_dist = R.dist.copy()
        R.blocked = np.zeros(lie.shape, bool)
        th = np.linspace(0, 2 * np.pi, 90)
        R.hd = dict(green_poly=np.column_stack([length + rad * np.cos(th), rad * np.sin(th)]))
        return R, (A0, L0)

    def flat_ground(self):
        R, origin = self.flat_raster()
        return Ground(self.M, R, self.P, self.cfg["flat"]["length"], origin, cfg=self.cfg)

    # ---- calibration
    def calibration(self, bag=None):
        """c(lie, d): what one shot from a trouble-free spot must cost beyond the model's own best shot for the
        table to be its own fixed point:  c = table(lie, d) - min over shots of E[1 + table(finish)]  on the flat
        hole. Added to every state's Bellman step, so that on trouble-free ground the DP returns the table."""
        if self._cal is not None and bag is None:
            return self._cal
        bag = bag or self.bag
        G = self.flat_ground()
        f = self.cfg["flat"]
        hs = HoleSolve(G, bag, cal=None, cfg=self.cfg)                   # delta = 0: cell values = the table
        d = np.arange(self.cfg["anchor_yds"], f["length"] - 20 + 1e-6, self.cfg["cal_step"])
        lat = f["rough_lateral"]
        c = np.zeros((3, len(d)))
        one = np.zeros((3, len(d)))
        for lc in range(3):
            l0 = np.full(len(d), lat if lc == 1 else 0.0)
            a0 = f["length"] - np.sqrt(np.maximum(d ** 2 - l0 ** 2, 0.0))
            n = len(d)
            slc = np.full(n, lc, np.int32)
            th0 = f32(np.arctan2(-l0, f["length"] - a0))
            mask = hs.club_mask(slc, d)
            T = G.table(lc, d)
            v = np.zeros(n, np.float32)
            bc, ba = np.zeros(n, np.int32), np.zeros(n, np.float32)
            K().hs_backup(_p(G.rk), _p(hs.cellv), _p(hs.dropv), G.na, G.nl, G.A0, G.L0, G.res, G.P["rough_roll"],
                          len(bag.names), bag.car.shape[2], _p(bag.car), _p(bag.dev), _p(bag.roll),
                          len(hs.ang), _p(hs.ang), 1, n, _p(f32(a0)), _p(f32(l0)), _p(th0), _p(slc), _p(mask),
                          _p(f32(np.zeros(n))), _p(f32(T)), _p(v), _p(bc), _p(ba), None, None)
            one[lc] = v
            c[lc] = T - v
        cal = dict(d=d, c=c, one_step=one, table=np.stack([G.table(i, d) for i in range(3)]))
        if bag is self.bag:
            self._cal = cal
        return cal

    # ---- holes
    def ground(self, h):
        hd = self.M.HOLES[h]
        R0, Rb, origin = self.big_raster(hd)
        G = Ground(self.M, Rb, self.P, hd["length"], origin, lost=self.tall == "lost", cfg=self.cfg)
        return R0, G

    def solve_hole(self, h, cal=None, bag=None, verbose=False):
        R0, G = self.ground(h)
        hs = HoleSolve(G, bag or self.bag, cal=cal, cfg=self.cfg, verbose=verbose).solve()
        hs.R0 = R0
        hs.hole = h
        return hs

    # ---- the tee shot: the engine's own two-stage central-world solve (opt/solve2.py) on a given value raster
    def tee_solve(self, h, R, S, clubs=None, n1=3000, n2=16000, seed1=7, seed2=77, half=10.0):
        M, D = self.M, self.D
        hd = M.HOLES[h]
        if "z" not in self._eng:
            self._eng["z"] = (M.draws_z(n1, seed1), M.draws_z(n2, seed2))
        z1, z2 = self._eng["z"]
        res = {}
        for c in (clubs or M.REAL_CLUBS):
            ev, _ = M.ev_curve(R, S, hd, c, self.P, z1, D.AIMS)
            r = D.robust_aim(D.AIMS, ev)
            aims = np.arange(r["aim"] - half, r["aim"] + half + 0.01, 0.5)
            ev2, (a, l, lie, s) = M.ev_curve(R, S, hd, c, self.P, z2, aims)
            r2 = D.robust_aim(aims, ev2, lo=max(-D.AIM_LIMIT, aims[0]), hi=min(D.AIM_LIMIT, aims[-1]))
            j = int(np.argmin(np.abs(aims - r2["aim"])))
            res[c] = dict(aim=r2["aim"], ev=float(r2["ev"]), s=1.0 + np.asarray(s)[:, j], a=a[:, j], l=l[:, j],
                          lie=lie[:, j])
        o = sorted(res, key=lambda c: res[c]["ev"])
        dd = res[o[1]]["s"] - res[o[0]]["s"]
        return dict(pick=o[0], runner=o[1], aim=res[o[0]]["aim"], ev=res[o[0]]["ev"],
                    margin=float(res[o[1]]["ev"] - res[o[0]]["ev"]), se=float(dd.std(ddof=1) / np.sqrt(len(dd))),
                    order=o, clubs={c: dict(aim=res[c]["aim"], ev=round(res[c]["ev"], 4)) for c in o}, raw=res)
