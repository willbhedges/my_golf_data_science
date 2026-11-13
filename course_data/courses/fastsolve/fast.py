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
THREADS = int(os.environ.get("FASTSOLVE_THREADS", "0") or 0)        # 0 = every core

_LIB = None
c_dp = ctypes.POINTER(ctypes.c_double)
c_fp = ctypes.POINTER(ctypes.c_float)
c_i8p = ctypes.POINTER(ctypes.c_int8)
c_u8p = ctypes.POINTER(ctypes.c_uint8)


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
                        c_dp, c_dp, c_dp, c_dp, c_dp, c_i8p, c_dp, i]
    L.fs_ev.restype = None
    L.fs_fill.argtypes = [c_dp, ctypes.c_long, c_dp, i, d, d, ctypes.c_int8, c_i8p, i]
    L.fs_fill.restype = None
    L.fs_water_entry.argtypes = [c_i8p, i, i, d, d, d, d, d, c_dp, i]
    L.fs_water_entry.restype = None
    L.fs_blocked.argtypes = [c_i8p, c_dp, i, i, d, d, d, d, d, d, d, c_u8p, i]
    L.fs_blocked.restype = None
    L.fs_max_threads.restype = i
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

    FastRaster.__name__ = "FastRaster"
    FastRaster._fast = True
    return FastRaster


# ------------------------------------------------------------------------------------------------ EV kernel
class _Shots:
    """The (a, l, lie, s) tuple of model.ev_curve, computed only when somebody unpacks it."""

    def __init__(self, fn):
        self._fn, self._v = fn, None

    def _get(self):
        if self._v is None:
            self._v = self._fn()
        return self._v

    def __iter__(self):
        return iter(self._get())

    def __getitem__(self, i):
        return self._get()[i]

    def __len__(self):
        return 4


class Fast:
    """Handle returned by install(): the engine's original functions (slow_*) and the fast ones."""

    def __init__(self, M, D):
        self.M, self.D = M, D
        self.slow_ev_curve = M.ev_curve
        self.slow_raster = M.Raster
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
        """-> (sumA, sumB, sum_all[, (a, l, lie, s)]) of the strokes-after-the-tee-shot over the swings, per aim."""
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
        sa, sb, st = np.empty(m), np.empty(m), np.empty(m)
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
                _p(sa, c_dp), _p(sb, c_dp), _p(st, c_dp), *po, threads or nthreads())
        self.calls += 1
        if full:
            return sa, sb, st, (oa, ol, olie, os_)
        return sa, sb, st

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
        _, _, st = self.sums(R, S, hd, club, P, z, aims, wind)
        ev = 1.0 + st / n
        return ev, _Shots(lambda: self.sums(R, S, hd, club, P, z, aims, wind, full=True)[3])


def install(M, D=None, raster=True):
    """Point this process's engine at the C kernels. Returns the Fast handle (F.slow_ev_curve / F.slow_raster are the
    engine's own, for A/B). Idempotent."""
    F = getattr(M, "_fastsolve", None)
    if F is not None:
        return F
    F = Fast(M, D)
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
    M.ev_curve, M.Raster = F.slow_ev_curve, F.slow_raster
    M._fastsolve = None
