"""fastsolve: the v2 tee-shot engine's hot loops in C, used ALONGSIDE the engine (nothing in it is edited).

    import v2_course as vc
    course, meta, M, D = vc.activate(slug, which)       # the engine, as always
    import fast
    F = fast.install(M, D)                              # THIS PROCESS only: M.ev_curve and M.Raster -> C kernels

After install() every engine entry point (decide.bayes / ladder / sensitivities / width_sweep, wind_grid_v2.solve,
v2_course.refined_solver, ...) runs unchanged Python on top of the compiled loops, so the outputs keep the engine's
formats by construction. fast.bayes() is decide.bayes with the two half-sums taken inside the kernel (the engine
materialises a swings x aims matrix per club and draw for them).

What is compiled (kernel.c, gcc -O3 -march=native -ffp-contract=off -fopenmp, loaded with ctypes):
  fs_ev           model.ev_curve: landing -> roll-out along the flight line (2-yd steps, slower in rough, stops in
                  hazards) -> strokes raster lookup, summed per aim; with v2_course's lidar flight-through-crowns
                  check when the course has it (Eagle Knoll)
  fs_fill         the zone polygons painted into the lie raster (matplotlib's point-in-path arithmetic)
  fs_water_entry  Raster._water_entry, fs_blocked: Raster._blocked
See README.md for the profile, the equivalence tests and the benchmarks.
"""
import ctypes
import hashlib
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "kernel.c")
CFLAGS = ["-O3", "-march=native", "-ffp-contract=off", "-fopenmp", "-fPIC", "-shared"]
if os.environ.get("FASTSOLVE_CFLAGS"):                # experiments only (README "Rejected: fast-math"): e.g. "-Ofast"
    CFLAGS = [c for c in CFLAGS if c != "-ffp-contract=off"] + os.environ["FASTSOLVE_CFLAGS"].split()
THREADS = int(os.environ.get("FASTSOLVE_THREADS", "0") or 0)        # 0 = every core

_LIB = None
c_dp = ctypes.POINTER(ctypes.c_double)
c_fp = ctypes.POINTER(ctypes.c_float)
c_i8p = ctypes.POINTER(ctypes.c_int8)
c_u8p = ctypes.POINTER(ctypes.c_uint8)


class Strokes(ctypes.Structure):
    _fields_ = ([("nd", ctypes.c_int)] + [(k, c_dp) for k in ("DIST", "T_fw", "T_ro", "T_sa", "T_rec")]
                + [("long_slope", ctypes.c_double)] + [(k, ctypes.c_int) for k in ("am", "broadie", "v1")]
                + [(k, ctypes.c_double) for k in (
                    "am_off", "am_slope", "m_rough", "m_sand", "first_cut", "trees", "one_m_trees", "tree_restricted",
                    "punch_adv", "punch_fail", "lost_edge", "lost_deep", "lost_ramp", "block_sev", "sd", "unverified")]
                + [("green_putting", ctypes.c_int), ("nputt", ctypes.c_int), ("PUTT_FT", c_dp), ("PUTT_TOUR", c_dp)]
                + [(k, ctypes.c_double * 3) for k in ("SY", "SF", "SR", "SS")]
                + [(k, ctypes.c_double) for k in ("gap_r", "gap_s", "mult_r", "mult_s", "mult_fc", "putt_off")])


class Lidar(ctypes.Structure):
    _fields_ = [("nf", ctypes.c_int), ("F", c_dp), ("y", c_dp), ("seg", c_dp), ("stepf", ctypes.c_double), ("min_along", ctypes.c_double),
                ("top", c_fp), ("base", c_fp), ("nga", ctypes.c_int), ("ngl", ctypes.c_int),
                ("ga0", ctypes.c_double), ("gl0", ctypes.c_double), ("inv_c", ctypes.c_double),
                ("tmax", ctypes.c_double), ("has_drop", ctypes.c_int), ("dg", c_dp), ("nda", ctypes.c_int),
                ("ndl", ctypes.c_int), ("da0", ctypes.c_double), ("dl0", ctypes.c_double),
                ("inv_d", ctypes.c_double), ("dmin", ctypes.c_double), ("need", c_fp)]


def lib():
    """Compile kernel.c once per source / flags / machine into _build/ and load it."""
    global _LIB
    if _LIB is not None:
        return _LIB
    cc = os.environ.get("CC", "gcc")
    try:
        cpu = subprocess.run([cc, "-march=native", "-Q", "--help=target"], capture_output=True, text=True).stdout
        cpu = next((ln for ln in cpu.splitlines() if "-march=" in ln), "")
    except Exception:                                  # noqa: BLE001
        cpu = ""
    tag = hashlib.sha1((open(SRC).read() + " ".join(CFLAGS) + cpu).encode()).hexdigest()[:12]
    bdir = os.environ.get("FASTSOLVE_BUILD") or os.path.join(HERE, "_build")
    os.makedirs(bdir, exist_ok=True)
    so = os.path.join(bdir, f"kernel_{tag}.so")
    if not os.path.exists(so):
        tmp = so + f".{os.getpid()}.tmp"
        subprocess.run([cc] + CFLAGS + ["-o", tmp, SRC, "-lm"], check=True)
        os.replace(tmp, so)
    L = ctypes.CDLL(so)
    d, i = ctypes.c_double, ctypes.c_int
    L.fs_ev.argtypes = [c_i8p, c_dp, i, i, d, d, d, c_dp, c_dp, c_dp, i, c_dp, i, d, i, i, ctypes.POINTER(Lidar),
                        c_dp, c_dp, c_dp, c_dp, c_dp, c_dp, c_i8p, c_dp, i, c_i8p]
    L.fs_ev.restype = None
    L.fs_fill.argtypes = [c_dp, ctypes.c_long, c_dp, i, d, d, ctypes.c_int8, c_i8p, i]
    L.fs_fill.restype = None
    L.fs_water_entry.argtypes = [c_i8p, i, i, d, d, d, d, d, c_dp, i]
    L.fs_water_entry.restype = None
    L.fs_blocked.argtypes = [c_i8p, c_dp, i, i, d, d, d, d, d, d, d, c_u8p, i]
    L.fs_blocked.restype = None
    L.fs_strokes.argtypes = [ctypes.POINTER(Strokes), c_i8p, c_dp, c_dp, c_dp, c_u8p, c_u8p, ctypes.c_long, c_dp, i]
    L.fs_strokes.restype = None
    L.fs_max_threads.restype = i
    L.fs_selfcheck.restype = i
    L.fs_simd.restype = i
    L.hypot_inline = bool(L.fs_selfcheck())      # the written-out hypot is used only when it equals this libm's
    L.simd = bool(L.fs_simd()) and os.environ.get("FASTSOLVE_SIMD", "1") != "0"
    _LIB = L
    return L


def nthreads():
    return THREADS or lib().fs_max_threads()


def _p(a, t):
    return a.ctypes.data_as(t)


def _f64(a):
    return np.ascontiguousarray(a, dtype=np.float64)


# ------------------------------------------------------------------------------------------------ raster
_GEO = {}


def _geometry(M, hd):
    """The per-hole grid geometry that does not depend on the map draw (cached per tee / line / green)."""
    tee, fwd, right, ppy = M.frame(hd)
    key = (tuple(tee), tuple(fwd), tuple(right), float(ppy), tuple(np.asarray(hd["green"], float)),
           M.A0, M.A1, M.L0, M.L1, M.RES)
    g = _GEO.get(key)
    if g is None:
        a = np.arange(M.A0, M.A1 + M.RES / 2, M.RES)
        l = np.arange(M.L0, M.L1 + M.RES / 2, M.RES)
        AA, LL = np.meshgrid(a, l, indexing="ij")
        pts = np.ascontiguousarray(tee + (AA.ravel()[:, None] * fwd + LL.ravel()[:, None] * right) * ppy)
        gv = np.asarray(hd["green"], float) - tee
        green = np.array([gv @ fwd / ppy, gv @ right / ppy])
        dist = np.hypot(AA - green[0], LL - green[1])
        assert np.array_equal(a, M.A0 + np.arange(len(a)) * M.RES) and np.array_equal(l, M.L0 + np.arange(len(l)) * M.RES)
        assert (1.0 / M.RES) * M.RES == 1.0 and np.log2(M.RES) == int(np.log2(M.RES)), "RES must be a power of two"
        g = dict(a=a, l=l, AA=AA, LL=LL, pts=pts, green=green, dist=dist,
                 pts_frame=np.ascontiguousarray(np.column_stack([AA.ravel(), LL.ravel()])))
        if len(_GEO) > 64:
            _GEO.clear()
        _GEO[key] = g
    return g, tee, fwd, right, ppy


def make_raster(M, slow_cls):
    """A Raster subclass whose __init__ is model.Raster.__init__ (+ v2_course's checked_extra wrapper) on the C
    kernels: same attributes, same values."""
    from scipy import ndimage
    L = lib()
    CODE = M.CODE

    class FastRaster(slow_cls):
        def __init__(self, hd, jitter_seed=None, jitter_yds=2.5):
            nt = nthreads()
            self.hd = hd
            g, tee, fwd, right, ppy = _geometry(M, hd)
            self.a, self.l = g["a"], g["l"]
            AA, LL = g["AA"], g["LL"]
            shape = AA.shape
            lie = np.zeros(shape[0] * shape[1], np.int8)
            rng = np.random.default_rng(jitter_seed) if jitter_seed is not None else None
            for name, poly in hd["zones"]:
                poly = _f64(poly)
                dx = dy = 0.0
                if rng is not None:
                    dx, dy = rng.normal(0, jitter_yds * ppy / 1.414, 2)
                L.fs_fill(_p(g["pts"], c_dp), len(lie), _p(poly, c_dp), len(poly), float(dx), float(dy), CODE[name],
                          _p(lie, c_i8p), nt)
            lie = lie.reshape(shape)
            lie[(lie == CODE["rough"]) & (np.abs(LL) > M.CHECKED_HALF_WIDTH)] = CODE["unverified"]
            self.lie = lie
            self.green = g["green"]
            self.dist = g["dist"]
            self.AA, self.LL = AA, LL
            nat = lie == CODE["native"]
            self.native_depth = (ndimage.distance_transform_edt(nat) * M.RES if nat.any()
                                 else np.zeros(shape, np.float64))
            self._water_entry()
            rings = hd.get("checked_extra_px") if getattr(slow_cls, "_checked_extra", False) else None
            if rings:                                    # v2_course.install_checked_extra
                inside = np.zeros(lie.size, np.int8)
                for r in rings:
                    d = (np.asarray(r, float) - tee) / ppy
                    ring = _f64(np.column_stack([d @ fwd, d @ right]))
                    L.fs_fill(_p(g["pts_frame"], c_dp), lie.size, _p(ring, c_dp), len(ring), 0.0, 0.0, 1,
                              _p(inside, c_i8p), nt)
                m = inside.reshape(shape).astype(bool) & (lie == CODE["unverified"])
                if m.any():
                    lie[m] = CODE["rough"]
            self._blocked()

        def _water_entry(self):
            self.entry_dist = self.dist.copy()
            if not (self.lie == CODE["water"]).any():
                return
            L.fs_water_entry(_p(self.lie, c_i8p), self.lie.shape[0], self.lie.shape[1], float(M.A0), float(M.L0),
                             float(M.RES), float(self.green[0]), float(self.green[1]), _p(self.entry_dist, c_dp),
                             nthreads())

        def _blocked(self, near=10.0, far=60.0, step=5.0):
            if (near, far, step) != (10.0, 60.0, 5.0):
                return slow_cls._blocked(self, near, far, step)
            blk = np.zeros(self.lie.shape, np.uint8)
            L.fs_blocked(_p(self.lie, c_i8p), _p(self.dist, c_dp), self.lie.shape[0], self.lie.shape[1], float(M.A0),
                         float(M.L0), float(M.RES), float(M.A1), float(M.L1), float(self.green[0]),
                         float(self.green[1]), _p(blk, c_u8p), nthreads())
            self.blocked = blk.astype(bool)

    sq = slow_cls.strokes.__qualname__
    green_wrapped = sq == "install_green_putting.<locals>.strokes"
    if (sq == "Raster.strokes" or green_wrapped) and os.environ.get("FASTSOLVE_STROKES", "1") != "0":
        tabs = [_f64(M.DIST)] + [_f64(M.TOUR[k]) for k in ("fairway", "rough", "sand", "recovery")]

        def strokes(self, P, length):
            """model.Raster.strokes (+ the green-putting wrapper of v2_course) in C: fs_strokes."""
            import v2_course as vc
            p = Strokes()
            p.nd = len(tabs[0])
            p.DIST, p.T_fw, p.T_ro, p.T_sa, p.T_rec = (_p(t, c_dp) for t in tabs)
            p.long_slope = float(M.LONG_SLOPE)
            am = P["table"] == "am"
            v1 = bool(P.get("v1_penalties"))
            p.am, p.broadie, p.v1 = int(am), int(bool(P.get("broadie_recovery"))), int(v1)
            if am:
                p.am_off, p.am_slope, p.m_rough, p.m_sand = P["am_off"], P["am_slope"], P["m_rough"], P["m_sand"]
            p.first_cut, p.trees, p.one_m_trees = P["first_cut"], P["trees"], 1 - P["trees"]
            p.tree_restricted = 0.0 if v1 else P["tree_restricted"]
            if not p.broadie:
                p.punch_adv, p.punch_fail = P["punch_adv"], P["punch_fail"]
            p.lost_deep = P["lost_deep"]
            if not v1:
                p.lost_edge, p.lost_ramp = P["lost_edge"], P["lost_ramp"]
                p.sd = 1.0 + M.tee_value(length, P)
            p.block_sev = P.get("block_sev", 0)
            p.unverified = 0.0 if v1 else M.UNVERIFIED_TREES
            keep = []
            green = None
            if green_wrapped:
                p.green_putting = 1
                off = float(M._engine_opts["green_putting"].get("am_putt_off", 0.10))
                ft, pt = _f64(vc.PUTT_FT), _f64(vc.PUTT_TOUR)
                keep += [ft, pt]
                p.nputt, p.PUTT_FT, p.PUTT_TOUR = len(ft), _p(ft, c_dp), _p(pt, c_dp)
                st = vc.SHORT_TOUR
                p.SY, p.SF = (ctypes.c_double * 3)(*vc.SHORT_YDS), (ctypes.c_double * 3)(*st["fairway"])
                p.SR, p.SS = (ctypes.c_double * 3)(*st["rough"]), (ctypes.c_double * 3)(*st["sand"])
                p.gap_r = st["rough"][-1] - st["fairway"][-1]
                p.gap_s = st["sand"][-1] - st["fairway"][-1]
                tab_am = P.get("table") == "am"
                p.mult_r = 1.0 if not tab_am else P["m_rough"]
                p.mult_s = 1.0 if not tab_am else P["m_sand"]
                p.mult_fc = p.mult_r * P["first_cut"]
                p.putt_off = off if tab_am else 0.0
                gp = self.hd.get("green_poly")
                tee, fwd, right, ppy = M.frame(self.hd)
                if self.hd.get("green_poly_px") is not None:
                    dd = (np.asarray(self.hd["green_poly_px"], float) - tee) / ppy
                    gp = np.column_stack([dd @ fwd, dd @ right])
                if gp is not None:
                    gp = _f64(gp)
                    g = _geometry(M, self.hd)[0]
                    green = np.zeros(self.lie.size, np.uint8)
                    L.fs_fill(_p(g["pts_frame"], c_dp), green.size, _p(gp, c_dp), len(gp), 0.0, 0.0, 1,
                              _p(green, c_i8p), nthreads())
            lie = np.ascontiguousarray(self.lie, np.int8)
            blk = np.ascontiguousarray(self.blocked).view(np.uint8)
            nd_, en = _f64(self.native_depth), _f64(self.entry_dist)
            S = np.empty(self.lie.shape, np.float64)
            L.fs_strokes(ctypes.byref(p), _p(lie, c_i8p), _p(_f64(self.dist), c_dp), _p(nd_, c_dp), _p(en, c_dp),
                         _p(blk, c_u8p), _p(green, c_u8p) if green is not None else None, lie.size, _p(S, c_dp),
                         nthreads())
            return S
        FastRaster.strokes = strokes
        FastRaster._fast_strokes = True

    FastRaster.__name__ = "FastRaster"
    FastRaster._fast = True
    return FastRaster


# ------------------------------------------------------------------------------------------------ EV kernel
class _LazyArr:
    """One of model.ev_curve's (a, l, lie, s) arrays (swings x aims), filled by a second kernel pass only if it is
    used. decide.bayes only ever takes three means of `1.0 + s` (all swings, first half, second half): those come
    from the sums the first pass already made, in the engine's summation order, so no matrix is built."""

    def __init__(self, owner, i):
        self._o, self._i = owner, i

    def _arr(self):
        return self._o.full()[self._i]

    def __array__(self, dtype=None, copy=None):
        a = self._arr()
        return a if dtype is None else a.astype(dtype)

    def __getitem__(self, k):
        return self._arr()[k]

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._arr(), name)

    def __add__(self, other):
        if self._i == 3 and isinstance(other, float) and other == 1.0:
            return _LazyV(self._o)
        return self._arr() + other

    __radd__ = __add__

    def __sub__(self, other):
        return self._arr() - other

    def __mul__(self, other):
        return self._arr() * other

    __rmul__ = __mul__

    def __eq__(self, other):
        return self._arr() == other

    __hash__ = None


class _LazyV:
    """`1.0 + sv` of decide.bayes."""

    def __init__(self, owner):
        self._o = owner

    def _arr(self):
        return 1.0 + self._o.full()[3]

    def mean(self, axis=None, *a, **kw):
        if axis == 0 and not a and not kw:
            return self._o.v_all / self._o.n
        return self._arr().mean(axis, *a, **kw)

    def __getitem__(self, k):
        o = self._o
        if isinstance(k, slice) and k.step is None and 0 < o.ksplit < o.n:
            if k.start is None and k.stop == o.ksplit:
                return _Half(o.vA, o.ksplit)
            if k.start == o.ksplit and k.stop is None:
                return _Half(o.vB, o.n - o.ksplit)
        return self._arr()[k]

    def __array__(self, dtype=None, copy=None):
        return self._arr()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._arr(), name)


class _Half:
    def __init__(self, s, n):
        self._s, self._n = s, n

    def mean(self, axis=None):
        if axis != 0:
            raise NotImplementedError("fastsolve: only mean(0) of a half of the swings is kept")
        return self._s / self._n


class _Call:
    """One ev_curve call: the sums, and the full arrays on demand."""

    def __init__(self, F, args, n, ksplit, sums):
        self.F, self.args, self.n, self.ksplit = F, args, n, ksplit
        self.sum_all, self.vA, self.vB, self.v_all = sums
        self._full = None

    def full(self):
        if self._full is None:
            self._full = self.F.sums(*self.args, ksplit=self.ksplit, full=True)[4]
        return self._full


class Fast:
    """Handle returned by install(): the engine's original functions (slow_*) and the fast ones."""

    def __init__(self, M, D):
        self.M, self.D = M, D
        self.slow_ev_curve = M.ev_curve
        self.slow_raster = M.Raster
        self.slow_finish = M.finish
        self.mode = None
        self.calls = 0

    # -- what the engine has installed, and whether the kernel covers it
    def _check(self):
        M = self.M
        ev = self.slow_ev_curve
        ok = M.shots.__module__ == "model" and M.finish.__module__ == "model"
        init = self.slow_raster.__init__.__qualname__
        ok_r = init in ("Raster.__init__", "install_checked_extra.<locals>.init")
        if ev.__module__ == "model" and ev.__name__ == "ev_curve":
            mode = "plain"
        elif getattr(ev, "_lidar_stop", False):
            mode = "lidar"
        else:
            mode = None                                  # e.g. the legacy constant-height flight check: not ported
        return (mode if ok else None), ok_r

    def sums(self, R, S, hd, club, P, z, aims, wind=None, ksplit=None, full=False, threads=None):
        """-> (sum_all, vA, vB, v_all[, (a, l, lie, s)]) per aim: sums over the swings of S (strokes after the tee
        shot) and of 1.0 + S (all swings, swings [0, ksplit), swings [ksplit, n)); see kernel.c fs_ev."""
        M = self.M
        L = lib()
        car, dev, roll = M.shots(hd, club, P, z, wind)
        car, dev, roll = _f64(car), _f64(dev), _f64(roll)
        aims = _f64(aims)
        n, m = len(car), len(aims)
        lid = None
        keep = []
        if self.mode == "lidar":
            lid = self._lidar(hd, club, car, n, keep)
        lie = R.lie
        if lie.dtype != np.int8 or not lie.flags.c_contiguous:
            lie = np.ascontiguousarray(lie, np.int8)
        S = _f64(S)
        pad = None
        if L.simd and not full:
            pad = getattr(R, "_lie_pad", None)        # the lie raster + 3 readable bytes (32-bit gathers)
            if pad is None or pad[1] is not R.lie or not np.array_equal(pad[0][:lie.size], lie.ravel()):
                buf = np.zeros(lie.size + 8, np.int8)
                buf[:lie.size] = lie.ravel()
                pad = (buf, R.lie)
                try:
                    R._lie_pad = pad
                except Exception:                    # noqa: BLE001
                    pass
            pad = pad[0]
        st, sa, sb, vt = np.empty(m), np.empty(m), np.empty(m), np.empty(m)
        if full:
            oa, ol, os_ = np.empty((n, m)), np.empty((n, m)), np.empty((n, m))
            olie = np.empty((n, m), np.int8)
            po = (_p(oa, c_dp), _p(ol, c_dp), _p(olie, c_i8p), _p(os_, c_dp))
        else:
            po = (None, None, None, None)
        L.fs_ev(_p(lie, c_i8p), _p(S, c_dp), lie.shape[0], lie.shape[1], float(M.A0), float(M.L0), 1.0 / M.RES,
                _p(car, c_dp), _p(dev, c_dp), _p(roll, c_dp), n, _p(aims, c_dp), m, float(P["rough_roll"]),
                int(bool(P.get("v1_roll", False))), n if ksplit is None else int(ksplit),
                ctypes.byref(lid) if lid is not None else None,
                _p(st, c_dp), _p(sa, c_dp), _p(sb, c_dp), _p(vt, c_dp), *po, threads or nthreads(),
                _p(pad, c_i8p) if pad is not None else None)
        self.calls += 1
        if full:
            return st, sa, sb, vt, (oa, ol, olie, os_)
        return st, sa, sb, vt

    def _lidar(self, hd, club, car, n, keep):
        """The per-call constants of v2_course.lidar_flight_ev_curve, computed exactly as it does."""
        import math
        import v2_course as vc
        M = self.M
        eng = M._engine_opts
        opts = M._lidar_opts
        k = float(opts["k_per_yd"])
        canopy_of, drop_of = eng.get("_canopy_of"), eng.get("_drop_of")
        C = canopy_of(hd) if canopy_of else None
        if C is None or k <= 0:
            return None
        ga, gl, top, base = C
        kind = "wood" if club in M.WOODS else "iron"
        cm = float(np.median(car))
        nst = max(4, int(np.ceil((1.0 - opts["f0"]) * cm / opts["step_yds"])))
        F = np.linspace(opts["f0"], 1.0, nst + 1)[:-1] + 0.5 * (1.0 - opts["f0"]) / nst
        y = vc.flight_heights(F, kind, cm)
        dydx = np.gradient(vc.flight_heights(np.linspace(0, 1, 401), kind, cm), np.linspace(0, cm, 401))
        slope = np.interp(F, np.linspace(0, 1, 401), dydx)
        stepf = (1.0 - opts["f0"]) / nst
        # the engine: (car1 * stepf) * sqrt(1 + sl^2), in that order: the kernel gets both factors
        sq = np.array([math.sqrt(1.0 + sl * sl) for sl in slope])
        G = drop_of(hd) if drop_of else None
        u = np.random.default_rng(int(n) * 7919 + 17).random(n)
        need = np.ascontiguousarray((-np.log1p(-np.minimum(u, 1 - 1e-12)) / k).astype(np.float32))
        top = np.ascontiguousarray(top, np.float32)
        base = np.ascontiguousarray(base, np.float32)
        F, y, sq = _f64(F), _f64(y), _f64(sq)
        lid = Lidar()
        lid.nf, lid.F, lid.y, lid.seg = len(F), _p(F, c_dp), _p(y, c_dp), _p(sq, c_dp)
        lid.min_along = float(opts["min_along"])
        lid.top, lid.base, lid.nga, lid.ngl = _p(top, c_fp), _p(base, c_fp), len(ga), len(gl)
        lid.ga0, lid.gl0, lid.inv_c = float(ga[0]), float(gl[0]), 1.0 / vc.CANOPY_STEP
        lid.tmax = float(top.max())
        keep += [F, y, sq, need, top, base]
        if G is not None:
            dga, dgl, dg = G
            dg = _f64(dg)
            lid.has_drop, lid.dg, lid.nda, lid.ndl = 1, _p(dg, c_dp), len(dga), len(dgl)
            lid.da0, lid.dl0, lid.inv_d = float(dga[0]), float(dgl[0]), 1.0 / vc.DROP_STEP
            lid.dmin = float(dg.min())
            keep.append(dg)
        else:
            lid.has_drop, lid.dmin = 0, 0.0
        lid.need = _p(need, c_fp)
        lid.stepf = float(stepf)
        return lid

    def ev_curve(self, R, S, hd, club, P, z, aims, wind=None):
        """Drop-in for model.ev_curve: (ev per aim, lazy (a, l, lie, s))."""
        if self.mode is None:
            return self.slow_ev_curve(R, S, hd, club, P, z, aims, wind)
        n = z.shape[1]
        k = n // 2
        sums = self.sums(R, S, hd, club, P, z, aims, wind, ksplit=k)
        ev = 1.0 + sums[0] / n
        call = _Call(self, (R, S, hd, club, P, z, aims, wind), n, k, sums)
        return ev, tuple(_LazyArr(call, i) for i in range(4))


# ------------------------------------------------------------------------------------------------ swing sets
def sobol_draws(n, seed):
    """model.draws_z's rows (z_lat, z_car, u_mishit, u_frac, u_roll) from a scrambled Sobol sequence instead of
    independent draws: the same marginal distributions, a far more even cover of the 5-D swing space (noise.py)."""
    from scipy.stats import norm, qmc
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        u = qmc.Sobol(5, scramble=True, seed=seed).random(int(n))
    u = np.clip(u, 1e-12, 1 - 1e-12)
    return np.vstack([norm.ppf(u[:, 0]), norm.ppf(u[:, 1]), u[:, 2], u[:, 3], u[:, 4]])


def antithetic_draws(n, seed):
    """Antithetic pairs: n / 2 independent swings and their mirror images (z -> -z, u -> 1 - u)."""
    r = np.random.default_rng(seed)
    h = int(n) // 2
    z, u = r.standard_normal((2, h)), r.random((3, h))
    return np.vstack([np.hstack([z, -z]), np.hstack([u, 1.0 - u])])


def install(M, D=None, raster=True, swings=None):
    """Point this process's engine at the C kernels. Returns the Fast handle (F.slow_ev_curve / F.slow_raster are the
    engine's own, for A/B). Idempotent. swings="sobol" (opt-in, NOT the engine's numbers: see README "Lower-variance
    swings") also replaces model.draws_z by scrambled Sobol points."""
    F = getattr(M, "_fastsolve", None)
    if F is not None:
        return F
    F = Fast(M, D)
    F.slow_draws_z = M.draws_z
    swings = swings or os.environ.get("FASTSOLVE_SWINGS") or None
    if swings == "sobol":
        M.draws_z = sobol_draws
    elif swings == "antithetic":
        M.draws_z = antithetic_draws
    elif swings not in (None, "mc"):
        raise ValueError(f"unknown swing set {swings!r}")
    F.swings = swings or "mc"
    F.mode, ok_r = F._check()
    if F.mode is not None:
        M.ev_curve = F.ev_curve
    F.fast_raster = make_raster(M, F.slow_raster) if (raster and ok_r) else F.slow_raster
    M.Raster = F.fast_raster
    M._fastsolve = F
    return F


def uninstall(M):
    F = getattr(M, "_fastsolve", None)
    if F is None:
        return
    M.ev_curve, M.Raster, M.draws_z = F.slow_ev_curve, F.slow_raster, F.slow_draws_z
    M._fastsolve = None
