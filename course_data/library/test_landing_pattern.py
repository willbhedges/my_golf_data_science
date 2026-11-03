"""The landing oval a library page draws (landing_pattern + the course_page.PAGE_PATCHES polygon code)."""
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course_page as cp                         # noqa: E402
import landing_pattern as LP                     # noqa: E402

TEMPLATE = os.path.join(os.path.dirname(HERE), "courses", "wind_page_template_course.html")


def _driver_like(n=20000, seed=3):
    """v2-like driver finishes on a hole: lateral sigma 17.5, carry sigma 8.75 about 275, 12 % slight (92-95 %) and
    2 % heavy (65-85 %) mishits, 25 +/- 25 % roll, 30 % of it once in rough (|lat| > 17), none into trees right
    (lat > 30)."""
    r = np.random.default_rng(seed)
    lat = 17.5 * r.standard_normal(n)
    a = 275 + 8.75 * r.standard_normal(n)
    u = r.random(n)
    a = np.where(u < 0.12, 275 * (0.92 + 0.03 * r.random(n)), a)
    a = np.where((u >= 0.12) & (u < 0.14), 275 * (0.65 + 0.2 * r.random(n)), a)
    roll = 25 * (1 + 0.25 * (2 * r.random(n) - 1))
    roll = np.where(np.abs(lat) > 17, 0.3 * roll, roll)
    roll = np.where(lat > 30, 0.0, roll)
    return a + roll, lat


def _eigen_cloud(a, l):
    """spirit_hollow/v2/build_page_v2.cloud's recipe (the old drawing)."""
    xy = np.c_[a, l]
    mu = np.median(xy, axis=0)
    _, vec = np.linalg.eigh(np.cov((xy - mu).T))
    half = [0.5 * float(np.subtract(*np.percentile((xy - mu) @ vec[:, i], [97.5, 2.5]))) for i in (1, 0)]
    return half, vec[:, 1], vec[:, 0]


def _extent(A, B, u, w):
    t = np.linspace(0, 2 * np.pi, 721)
    p = np.outer(np.cos(t) * A, u) + np.outer(np.sin(t) * B, w)
    return p[:, 1].max(), p[:, 0].max()          # lateral, depth half-extents


def test_pattern_is_wider_than_long_with_a_short_tail():
    a, l = _driver_like()
    p = LP.pattern(a, l)
    assert abs(p["left"] - 34.0) < 1.5 and abs(p["right"] - 34.0) < 1.5
    assert p["long"] < 27 and p["short"] > p["long"] + 6           # mishits and rough stop short, never long
    assert (p["long"] + p["short"]) / (p["left"] + p["right"]) < 0.88
    assert abs(p["tilt"]) < 0.1


def test_old_eigen_recipe_draws_it_rounder():
    """The bug: the one-sided tail inflates the depth variance until it rivals the lateral one, so the eigen axes
    turn (here ~25 degrees) and the symmetric half-range draws the long side as deep as the short side."""
    a, l = _driver_like()
    (A, B), u, w = _eigen_cloud(a, l)
    lat, dep = _extent(A, B, u, w)
    p = LP.pattern(a, l)
    new_ratio = (p["long"] + p["short"]) / (p["left"] + p["right"])
    assert dep / lat > 0.9 and dep / lat > new_ratio + 0.05
    assert np.degrees(np.arctan2(abs(u[0]), abs(u[1]))) > 10      # the drawn major axis is off the lateral
    assert dep > p["long"] + 5                    # the old oval reaches well past the longest 2.5 % of drives


def test_tilt_slice_short():
    r = np.random.default_rng(5)
    l = 17.5 * r.standard_normal(20000)
    a = 280 + 8.0 * r.standard_normal(20000) - 0.2 * l       # misses right come up short
    p = LP.pattern(a, l)
    assert abs(p["tilt"] + 0.2) < 0.02
    assert abs(p["short"] - p["long"]) < 1.5               # the tilt is taken out before the depth extents
    pts = np.array(LP.outline(p, n=4))                     # t = 0, 90, 180, 270 degrees
    assert np.allclose(pts[0], (p["along"] + p["long"], p["lat"]))
    assert np.allclose(pts[1], (p["along"] + p["tilt"] * p["right"], p["lat"] + p["right"]))
    assert np.allclose(pts[2], (p["along"] - p["short"], p["lat"]))


def _template_code():
    if not os.path.exists(TEMPLATE):
        pytest.skip("course_data/courses/wind_page_template_course.html not in this checkout")
    html = open(TEMPLATE).read()
    m = re.search(r"<script>(.*const D = /\*__DATA__\*/null;?)(.*?)</script>", html, re.S)
    return m.group(2) if m else html


def _js_pattern(cl, width):
    """The patched page code's landing polygon for one cloud, in (along, lat) yds (tee at 0, line straight up)."""
    code, missed = cp.patch_code(_template_code())
    assert not missed
    i = code.index("if(cl){ const sc")
    j = code.index("pattern = `<polygon", i)
    js = ("const P = (h, p) => [p[0], p[1]];\n"
          "const at = (h, along, lat) => [h.tee[0]+(along*h.f[0]+lat*h.r[0])*h.ppy, h.tee[1]+(along*h.f[1]+lat*h.r[1])*h.ppy];\n"
          "const h = {tee: [0, 0], f: [0, -1], r: [1, 0], ppy: 1, s: 1};\n"
          f"const cl = {json.dumps(cl)}; const best = {{total: 300, width: {width}, drift: 0, kick: 0}};\n"
          "const B = 0, aimC = 0, cA = cl.dA, cL = cl.dL; let pattern;\n"
          + code[i:j] + "\nconsole.log(JSON.stringify(pts)); }")
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-800:]
    xy = np.array([[float(v) for v in q.split(",")] for q in json.loads(out.stdout)])
    return np.c_[-xy[:, 1], xy[:, 0]]                          # pixels (x right, y down) -> (along, lat)


def test_page_draws_the_tee_frame_pattern():
    if not shutil.which("node"):
        pytest.skip("no node")
    p = dict(along=0.0, lat=0.0, long=22.0, short=38.0, left=35.0, right=37.0, tilt=-0.1)
    cl = dict(dA=-10.0, dL=1.0, A=30.0, B=36.0, u=[1.0, 0.0], w=[0.0, 1.0], width=70.0,
              **{k: p[k] for k in ("long", "short", "left", "right", "tilt")})
    got = _js_pattern(cl, 70.0)
    want = np.array(LP.outline(dict(p, along=290.0, lat=1.0), n=48))
    assert np.allclose(got, want, atol=1e-6)
    # in wind the page scales the pattern by the wind width / calm width, the shape kept
    got2 = _js_pattern(cl, 77.0)
    assert np.allclose(got2[:, 1].max() - 1.0, 37.0 * 1.1, atol=1e-6)
    assert got[:, 0].min() == pytest.approx(290.0 - 38.0 - 0.1 * 0.0, abs=0.5)


def test_old_cloud_still_draws_without_the_shape():
    """A cloud without the shape fields (tournament pages, old builds) keeps the eigen-ellipse drawing."""
    if not shutil.which("node"):
        pytest.skip("no node")
    cl = dict(dA=0.0, dL=0.0, A=35.0, B=20.0, u=[0.0, 1.0], w=[-1.0, 0.0], width=70.0)
    got = _js_pattern(cl, 70.0)
    assert got[:, 1].max() == pytest.approx(35.0, abs=1e-6)
    assert got[:, 0].max() - 300 == pytest.approx(20.0, abs=0.1)


# ------------------------------------------------------------------------------------- the Aim Caddie app
APP = os.path.join(os.path.dirname(HERE), "app")


def _node(js):
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-800:]
    return json.loads(out.stdout)


def test_app_library_draws_the_record_pattern():
    """lib_play.js lpPattern: a record's V.pat row is drawn as landing_pattern.outline at the landing point."""
    if not shutil.which("node"):
        pytest.skip("no node")
    src = open(os.path.join(APP, "lib_play.js")).read()
    snippet = src[src.index("const LP_FALLBACK"):src.index("function lpDraw")]
    row = [-11.5, -0.5, 22.4, 27.8, 35.6, 35.8, 0.165]
    r = dict(total=298.0, aim=-8.5, drift=1.5)
    got = np.array(_node(snippet + f"\nconsole.log(JSON.stringify(lpPattern({{pat: {{'0': {json.dumps(row)}}}}}, 0, {json.dumps(r)})));"))
    p = dict(along=298.0 - 11.5, lat=-8.5 + 1.5 - 0.5, long=22.4, short=27.8, left=35.6, right=35.8, tilt=0.165)
    assert np.allclose(got, np.array(LP.outline(p, n=48)), atol=1e-9)
    # no pattern for this club: the generic oval (60 x 28) at the landing point
    fb = np.array(_node(snippet + f"\nconsole.log(JSON.stringify(lpPattern({{}}, 3, {json.dumps(r)})));"))
    assert fb[:, 1].max() == pytest.approx(-7.0 + 30) and fb[:, 0].max() == pytest.approx(298 + 14)


def test_app_course_draws_the_cloud_pattern():
    """app_template.html patternAt (app / Spirit Hollow clouds with the tee-frame shape) = landing_pattern.outline."""
    if not shutil.which("node"):
        pytest.skip("no node")
    src = open(os.path.join(APP, "app_template.html")).read()
    snippet = src[src.index("function patternAt"):src.index("function renderHole")]
    p = dict(along=0.0, lat=0.0, long=20.0, short=30.0, left=33.0, right=36.0, tilt=-0.05)
    js = (snippet + f"\nconst p = {json.dumps(p)}; const o = [];"
          "for (let k = 0; k < 48; k++) o.push(patternAt(p, k / 48 * 2 * Math.PI, 1.1, 280, 4));"
          "console.log(JSON.stringify(o));")
    got = np.array(_node(js))
    want = np.array(LP.outline(dict(p, along=280.0, lat=4.0), n=48, scale=1.1))
    assert np.allclose(got, want, atol=1e-9)
    assert "patternAt(cl, a, sc, landA, landL)" in src and "ov.pattern" in src


def test_library_record_patterns():
    sys.path.insert(0, APP)
    import build_library_play as BL
    clubs = ["Driver", "4-wood", "Long iron"]
    new = {"Driver": dict(dA=-10, dL=0.5, A=30, B=36, u=[1, 0], w=[0, 1], width=70, long=22, short=38, left=35,
                          right=37, tilt=-0.1)}
    assert BL.tee_patterns({"cloud": new}, None, clubs) == {"0": [-10.0, 0.5, 22.0, 38.0, 35.0, 37.0, -0.1]}
    old = {"Driver": dict(dA=-10, dL=0.5, A=35, B=33, u=[0.5, 0.86], w=[-0.86, 0.5], width=70)}
    cache = {"4-wood": [-5, 0, 18, 26, 27, 28, 0.02], "Hybrid": [0] * 7}
    assert BL.tee_patterns({"cloud": old}, cache, clubs) == {"1": [-5.0, 0.0, 18.0, 26.0, 27.0, 28.0, 0.02]}
    assert BL.tee_patterns({"cloud": old}, None, clubs) is None


def test_check_card_crop_pattern():
    """build_app.crop_pattern: the hole's cloud in a verify crop's pixels (tee line up, s px per yd, target = aim pt)."""
    sys.path.insert(0, APP)
    try:
        import build_app as BA
        from verify import CROP
    except Exception as e:                       # noqa: BLE001
        pytest.skip(f"build_app not importable here: {e}")
    cl = dict(long=20.0, short=30.0, left=35.0, right=35.0, tilt=0.0, off=[12.0, -1.0])
    holes = [dict(no=4, variants={"Blue": {"cloud": {"Driver": cl}}})]
    pat = BA.crop_pattern(dict(hole=4, type="hazard"), dict(target=[150.0, 150.0], pick="Driver"), holes, "Blue")
    s = CROP["landing"]["s"]
    xy = np.array(pat)
    assert xy[:, 0].max() == pytest.approx(150 + (-1 + 35) * s, abs=0.1)
    assert xy[:, 1].min() == pytest.approx(150 - (12 + 20) * s, abs=0.1)       # long = up the picture
    assert BA.crop_pattern(dict(hole=4, type="hazard"), dict(target=[1, 1], pick="4-wood"), holes, "Blue") is None
