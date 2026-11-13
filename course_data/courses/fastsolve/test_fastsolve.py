"""fastsolve reproduces the v2 engine: small samples, < 2 minutes on 4 cores.

  python3 -m pytest -q course_data/courses/fastsolve/test_fastsolve.py
  python3 course_data/courses/fastsolve/test_fastsolve.py check gateway_national truth     (one course, verbose)

Each course is checked in its own process (the engine binds one course per process: v2_course.activate). In that
process the engine's own functions (kept by fast.install as F.slow_ev_curve / F.slow_raster) and the kernels run on
the same inputs, and the results must be EQUAL (==), which is stronger than the brief's tolerances (same club, aim
within 1 yd, EV within 0.003): the kernel repeats the engine's arithmetic in the same order. The full-size
comparison (every hole, 16,000-swing refine, 3 temperatures x 0 / 5 / 10 mph x 4 directions, prior draws, the
engine's own seed noise) is equiv.py; its table is in README.md.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COURSES = os.path.dirname(HERE)
AIM_TOL, EV_TOL = 1.0, 0.003                     # the brief's tolerances (reported; the assertions are exact)

# (slug, which, holes for the wind cells [None = every tee shot], holes for the prior draws)
CASES = {
    "gateway_national": ("truth", None, [8, 10, 16]),
    "eagle_knoll": ("truth", [1, 9, 14, 15, 18], [14]),
}


def _setup(slug, which):
    for p in (COURSES, HERE):
        if p not in sys.path:
            sys.path.insert(0, p)
    import v2_course as vc
    course, meta, M, D = vc.activate(slug, which)
    import wind_grid as WG
    WG.osm_bearings = lambda: {}
    import wind_grid_v2 as WG2
    if getattr(D, "_aim_limit", None):
        L = float(D._aim_limit)
        WG2.AIMS = np.arange(-(L + 35.0), L + 35.0 + 1e-9, 0.5)
    import fast
    return vc, M, D, WG2, fast


def _same(a, b):
    return json.dumps(a, sort_keys=True, default=float) == json.dumps(b, sort_keys=True, default=float)


def _cell_diff(r0, r1):
    """(same pick, max |aim diff|, max |ev diff|) of two solve() results."""
    da = max(abs(r0["clubs"][c]["aim"] - r1["clubs"][c]["aim"]) for c in r0["clubs"])
    de = max(abs(r0["clubs"][c]["ev"] - r1["clubs"][c]["ev"]) for c in r0["clubs"])
    return r0["pick"] == r1["pick"], da, de


def check(slug, which, wind_holes=None, bayes_holes=(), n1=600, n2=2000, draws=2, n_bayes=800, verbose=True):
    """Engine vs kernels in this process. Returns the list of mismatches (empty = equivalent)."""
    vc, M, D, WG2, fast = _setup(slug, which)
    say = print if verbose else (lambda *a, **k: None)
    bad = []
    t_slow = t_fast = 0.0
    # ---- engine first (unpatched), then the same calls after fast.install()
    holes = list(M.HOLES) if wind_holes is None else [h for h in M.HOLES if h in wind_holes]
    cells = [(50.0, 0, 0), (35.0, 10, 90), (65.0, 5, 180)]

    def wind_pass():
        WG2.N = n1
        solve = vc.refined_solver(M, D, WG2, n2)
        z = M.draws_z(n1, 31)
        out = {}
        for h in holes:
            hd = M.HOLES[h]
            R = M.Raster(hd)
            for T, sp, rel in (cells if h in holes[:4] else cells[:2]):
                P = M.central(temp_f=T)
                S = R.strokes(P, hd["length"])
                out[(h, T, sp, rel)] = solve(h, P, R, S, z, sp, rel)
        return out

    def bayes_pass():
        out = {}
        for h in bayes_holes:
            r = D.bayes(h, draws, n_bayes)
            r["shares"] = D.shares_at(h, D.central(h), r["pick"], r["aim"], n=4000)
            out[h] = r
        return out

    t = time.time()
    w0, b0 = wind_pass(), bayes_pass()
    t_slow = time.time() - t
    F = fast.install(M, D)
    assert F.mode in ("plain", "lidar"), "the kernel does not cover this engine configuration"
    assert M.Raster is F.fast_raster and F.fast_raster is not F.slow_raster
    t = time.time()
    w1, b1 = wind_pass(), bayes_pass()
    t_fast = time.time() - t
    worst_a = worst_e = 0.0
    for k in w0:
        same_pick, da, de = _cell_diff(w0[k], w1[k])
        worst_a, worst_e = max(worst_a, da), max(worst_e, de)
        if not _same(w0[k], w1[k]):
            bad.append(f"wind cell {k}: pick {'same' if same_pick else 'DIFFERENT'}, aim diff {da:g}, ev diff {de:.2e}")
    for h in b0:
        if not _same(b0[h], b1[h]):
            keys = [k for k in b0[h] if not _same(b0[h][k], b1[h][k])]
            bad.append(f"bayes hole {h}: fields differ: {keys}")
    say(f"{slug}: {len(w0)} refined wind cells on {len(holes)} holes, bayes on {list(b0)}: "
        f"engine {t_slow:.1f}s, fastsolve {t_fast:.1f}s; max |aim diff| {worst_a:g}, max |ev diff| {worst_e:.1e}")

    # ---- the pieces, on the first holes: raster (base map and a jittered prior-draw map), every ball of a curve
    for h in holes[:2]:
        hd = M.HOLES[h]
        for seed in (None, 20261114):
            Rs, Rf = F.slow_raster(hd, seed), F.fast_raster(hd, seed)
            for k in ("lie", "dist", "green", "native_depth", "entry_dist", "blocked", "a", "l"):
                if not np.array_equal(getattr(Rs, k), getattr(Rf, k)):
                    bad.append(f"raster hole {h} seed {seed}: {k} differs in "
                               f"{int((np.asarray(getattr(Rs, k)) != np.asarray(getattr(Rf, k))).sum())} cells")
        P = M.central(temp_f=50.0)
        S = Rs.strokes(P, hd["length"])
        if not np.array_equal(S, Rf.strokes(P, hd["length"])):
            bad.append(f"strokes raster hole {h} differs")
        z = M.draws_z(500, 31)
        aims = WG2.AIMS[::4]
        for c in (M.ALL_CLUBS[0], M.ALL_CLUBS[-2]):
            for wind in (None, WG2.wind_hook(c, 10, 300)):
                e0, (a0, l0, lie0, s0) = F.slow_ev_curve(Rs, S, hd, c, P, z, aims, wind=wind)
                e1, (a1, l1, lie1, s1) = F.ev_curve(Rf, S, hd, c, P, z, aims, wind=wind)
                ok = (np.array_equal(e0, e1) and np.array_equal(a0, np.asarray(a1)) and np.array_equal(l0, np.asarray(l1))
                      and np.array_equal(lie0, np.asarray(lie1)) and np.array_equal(s0, np.asarray(s1)))
                if not ok:
                    bad.append(f"ev_curve hole {h} {c} {'wind' if wind else 'calm'}: max |ev diff| "
                               f"{np.abs(e0 - e1).max():.2e}, {int((lie0 != np.asarray(lie1)).sum())} balls on another lie")
    for b in bad:
        say("  MISMATCH", b)
    say(f"{slug}: {'EQUIVALENT (every compared number equal)' if not bad else str(len(bad)) + ' MISMATCHES'}")
    return bad


# ------------------------------------------------------------------------------------------------ pytest
def _run(slug):
    which, wh, bh = CASES[slug]
    return subprocess.Popen([sys.executable, os.path.abspath(__file__), "check", slug, which,
                             json.dumps(dict(wind_holes=wh, bayes_holes=bh))],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


_PROCS = {}


def _result(slug):
    if not _PROCS:                                  # both courses at once: the wall time is the slower one
        for s in CASES:
            _PROCS[s] = _run(s)
    p = _PROCS[slug]
    if not hasattr(p, "_out"):
        p._out = p.communicate()[0]
    return p.returncode, p._out


def test_fill_matches_matplotlib_point_in_path():
    """fs_fill == matplotlib.path.Path.contains_points, including points exactly on edges and vertices."""
    from matplotlib.path import Path
    sys.path.insert(0, HERE)
    import fast
    L = fast.lib()
    rng = np.random.default_rng(3)
    gx, gy = np.meshgrid(np.arange(0, 60, 0.5), np.arange(0, 40, 0.5), indexing="ij")
    pts = np.ascontiguousarray(np.column_stack([gx.ravel(), gy.ravel()]))
    polys = [np.array([[10, 5], [50, 5], [50, 30], [30, 12.5], [10, 30]], float),            # on-grid vertices and edges
             np.array([[5, 5], [20, 5], [20, 20], [5, 20], [5, 5]], float),                  # closed ring
             np.array([[0, 0], [60, 40], [60, 0], [0, 40]], float)]                          # self-crossing
    for _ in range(40):
        n = int(rng.integers(3, 60))
        ang = np.sort(rng.uniform(0, 2 * np.pi, n))
        r = rng.uniform(3, 20, n)
        polys.append(np.column_stack([30 + r * np.cos(ang), 20 + r * np.sin(ang)]) + rng.normal(0, 1.5, (n, 2)))
    for poly in polys:
        want = Path(poly).contains_points(pts)
        for nt in (1, 4):
            got = np.zeros(len(pts), np.int8)
            p = np.ascontiguousarray(poly)
            L.fs_fill(pts.ctypes.data_as(fast.c_dp), len(pts), p.ctypes.data_as(fast.c_dp), len(p), 0.0, 0.0, 1,
                      got.ctypes.data_as(fast.c_i8p), nt)
            assert np.array_equal(got.astype(bool), want), (len(poly), int((got.astype(bool) != want).sum()))


def test_gateway_national_back_equals_engine():
    rc, out = _result("gateway_national")
    print(out)
    assert rc == 0, out[-3000:]


def test_eagle_knoll_back_equals_engine():
    rc, out = _result("eagle_knoll")
    print(out)
    assert rc == 0, out[-3000:]


def test_runner_refuses_the_course_folder():
    p = subprocess.run([sys.executable, os.path.join(HERE, "run.py"), "solve", "--slug", "gateway_national",
                        "--out", os.path.join(COURSES, "gateway_national", "truth", "v2")],
                       capture_output=True, text=True)
    assert p.returncode != 0 and "refusing" in (p.stderr + p.stdout)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "check":
        kw = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        kw["wind_holes"] = kw.get("wind_holes")
        sys.exit(1 if check(sys.argv[2], sys.argv[3], **kw) else 0)
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q", os.path.abspath(__file__)]))
