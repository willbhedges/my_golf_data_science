"""Tournament wind pages (v2_course.py + wind_page_template_course.html): the dashed landing oval is the model's
tee-frame pattern (course_data/library/landing_pattern.py), not build_page_v2.cloud's covariance-eigen near circle.

  python3 -m pytest -q course_data/courses/test_v2_course_landing.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import types

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
ROOT = os.path.dirname(CD)
TEMPLATE = os.path.join(HERE, "wind_page_template_course.html")
sys.path.insert(0, os.path.join(CD, "library"))
import landing_pattern as LP                     # noqa: E402


def _vc():
    import importlib.util
    spec = importlib.util.spec_from_file_location("v2_course_t", os.path.join(HERE, "v2_course.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _js_pattern(cl, width):
    """The UNPATCHED tournament template's landing polygon for one cloud, in (along, lat) yds."""
    html = open(TEMPLATE).read()
    code = re.search(r"const D = /\*__DATA__\*/null;?(.*?)</script>", html, re.S).group(1)
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
    return np.c_[-xy[:, 1], xy[:, 0]]


@pytest.mark.skipif(not shutil.which("node"), reason="no node")
def test_template_draws_the_tee_frame_pattern():
    p = dict(along=0.0, lat=0.0, long=22.0, short=38.0, left=35.0, right=37.0, tilt=-0.1)
    cl = dict(dA=-10.0, dL=1.0, A=30.0, B=36.0, u=[1.0, 0.0], w=[0.0, 1.0], width=70.0,
              **{k: p[k] for k in ("long", "short", "left", "right", "tilt")})
    got = _js_pattern(cl, 70.0)
    assert np.allclose(got, np.array(LP.outline(dict(p, along=290.0, lat=1.0), n=48)), atol=1e-6)
    assert got[:, 0].max() == pytest.approx(290 + 22, abs=0.5) and got[:, 0].min() == pytest.approx(290 - 38, abs=0.5)
    got2 = _js_pattern(cl, 77.0)                   # wind widens the pattern: same shape, scaled
    assert got2[:, 1].max() - 1.0 == pytest.approx(37.0 * 1.1, abs=1e-6)


@pytest.mark.skipif(not shutil.which("node"), reason="no node")
def test_template_old_cloud_unchanged():
    cl = dict(dA=0.0, dL=0.0, A=35.0, B=20.0, u=[0.0, 1.0], w=[-1.0, 0.0], width=70.0)
    got = _js_pattern(cl, 70.0)
    assert got[:, 1].max() == pytest.approx(35.0, abs=1e-6)
    assert got[:, 0].max() - 300 == pytest.approx(20.0, abs=0.1)


def test_library_patches_do_not_duplicate_the_branch():
    import course_page as cp
    html = open(TEMPLATE).read()
    code, missed = cp.patch_code(html)
    assert not missed
    assert code.count("if(cl.long != null)") == 1


def test_install_swaps_the_cloud_and_can_be_turned_off(monkeypatch):
    vc = _vc()
    BP = types.SimpleNamespace(cloud=lambda h, g, t: "old")
    monkeypatch.setenv("V2_LANDING_PATTERN", "0")
    vc.install_landing_pattern(object(), BP)
    assert BP.cloud(1, {}, 50) == "old"
    monkeypatch.setenv("V2_LANDING_PATTERN", "1")
    vc.install_landing_pattern(object(), BP)
    assert BP._tee_frame_cloud and BP.cloud is not None
    called = {}
    monkeypatch.setattr(LP, "page_cloud", lambda M, h, g, t: called.setdefault("x", (h, t)))
    BP.cloud(9, {}, 50.0)
    assert called["x"] == (9, 50.0)


def test_spirit_hollow_page_code_not_patched():
    """Spirit Hollow's live page is built by spirit_hollow/v2/build_page_v2.py main with its own cloud and template:
    importing v2_course must not touch them (the swap happens only inside v2_course.build_page)."""
    src = open(os.path.join(ROOT, "spirit_hollow", "v2", "build_page_v2.py")).read()
    assert "np.linalg.eigh(np.cov" in src and "landing_pattern" not in src
    vc = _vc()
    assert "build_page_v2" not in sys.modules or not getattr(sys.modules["build_page_v2"], "_tee_frame_cloud", False)
    assert "wind_page_template_course" not in open(os.path.join(ROOT, "spirit_hollow", "build_wind_page.py")).read()
    del vc


EK = os.path.join(HERE, "eagle_knoll", "truth")


@pytest.mark.skipif(not os.path.exists(os.path.join(EK, "v2", "wind_grid.json")), reason="no Eagle Knoll grid")
def test_eagle_knoll_cloud_is_wider_than_long():
    """On the real course module (own process: the engine binds `course`): the new cloud for hole 9's driver is the
    model's tee-frame 95 % finish pattern, a short tail and wider than long; the old eigen recipe was a circle."""
    code = r"""
import json, sys, os
sys.path.insert(0, %r); sys.path.insert(0, %r)
import v2_course as vc
course, meta, M, D = vc.activate("eagle_knoll", "truth")
import build_page_v2 as BP
old = BP.cloud
vc.install_landing_pattern(M, BP)
g = json.load(open(vc.cdir("eagle_knoll", "truth", "v2", "wind_grid.json")))["holes"]["9"]["50"]["0_0"]
g = dict(g, clubs={"Driver": g["clubs"]["Driver"]})
print(json.dumps(dict(old=old(9, g, 50.0)["Driver"], new=BP.cloud(9, g, 50.0)["Driver"])))
""" % (HERE, os.path.join(CD, "library"))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=600)
    assert out.returncode == 0, out.stderr[-1500:]
    r = json.loads(out.stdout.strip().splitlines()[-1])
    new, old = r["new"], r["old"]
    assert new["u"] == [1.0, 0.0] and new["w"] == [0.0, 1.0]
    assert new["short"] > new["long"] + 5                    # mishits and rough stop short, never long
    assert (new["short"] + new["long"]) < 0.92 * (new["left"] + new["right"])
    t = np.linspace(0, 2 * np.pi, 721)
    p = np.outer(np.cos(t) * old["A"], old["u"]) + np.outer(np.sin(t) * old["B"], old["w"])
    assert np.ptp(p[:, 0]) > 0.95 * np.ptp(p[:, 1])           # the old drawing: depth ~ width
