"""v2_course engine options and page fixes from the Eagle Knoll optimisation (OPTIMIZE.md, 2026-11-03):
refined wind-grid solve, flight-path trees, extra lay-up clubs, par-3 temperature, par-3 box floor.

  python3 -m pytest -q course_data/courses/test_v2_course_engine.py
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
TEMPLATE = os.path.join(HERE, "wind_page_template_course.html")


def _vc():
    import importlib.util
    spec = importlib.util.spec_from_file_location("v2_course_e", os.path.join(HERE, "v2_course.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


vc = _vc()


def test_flight_heights_shape():
    f = np.linspace(0, 1, 201)
    y = vc.flight_heights(f, "wood", 275.0)
    assert y[0] == pytest.approx(0, abs=1e-9) and y[-1] == pytest.approx(0, abs=1e-6)
    assert y.max() == pytest.approx(vc.APEX_YDS["wood"], rel=1e-3)
    assert f[int(np.argmax(y))] == pytest.approx(vc.APEX_AT, abs=0.01)
    # landing slope = tan(38 deg) in yds per yd of carry
    slope = (y[-2] - y[-1]) / ((f[-1] - f[-2]) * 275.0)
    assert slope == pytest.approx(np.tan(np.radians(vc.LAND_DEG["wood"])), rel=0.08)
    # below 20 yds only in the last ~12 % of a driver's carry
    assert 0.83 < f[(f > 0.6) & (y < 20)][0] < 0.92


class _R:
    """A 1-yd raster with trees in a band 250-262 yds out, x -40..-10 (the corner of a dogleg)."""
    def __init__(self):
        self.tree = lambda a, l: (a >= 250) & (a <= 262) & (l >= -40) & (l <= -10)

    def lie_at(self, a, l):
        return np.where(self.tree(np.asarray(a), np.asarray(l)), 4, 0).astype(np.int8)

    def idx(self, a, l):
        return (np.clip(np.rint(a).astype(int), 0, 499), np.clip(np.rint(l).astype(int) + 100, 0, 199))


def _fake_M(car=290.0):
    M = types.SimpleNamespace(CODE={"recovery": 4}, WOODS=["Driver"])
    M.shots = lambda hd, club, P, z, wind=None: (np.full(z.shape[1], car), np.zeros(z.shape[1]), np.zeros(z.shape[1]))
    M.finish = lambda R, car, lat, roll, rr, v1=False: (np.broadcast_to(car, np.broadcast(car, lat).shape).astype(float),
                                                        np.broadcast_to(lat, np.broadcast(car, lat).shape).astype(float),
                                                        R.lie_at(np.broadcast_to(car, np.broadcast(car, lat).shape), np.broadcast_to(lat, np.broadcast(car, lat).shape)))
    return M


def test_flight_over_the_corner_hits_the_trees():
    M, R = _fake_M(290.0), _R()
    S = np.zeros((500, 200))
    S[250:263, 60:91] = 1.0                          # a tree cell costs a stroke more than open ground
    ev = vc.flight_tree_ev_curve(M, 20.0, 1.0)
    z = np.zeros((5, 400))
    aims = np.array([-28.0, 0.0])                   # -28: the line crosses x -25..-24 at 250-262 yds (below 20 yds)
    e, (a, l, lie, s) = ev(R, S, {}, "Driver", {"rough_roll": 0.3}, z, aims)
    assert e[0] == pytest.approx(2.0) and e[1] == pytest.approx(1.0)
    assert (lie[:, 0] == 4).all() and (a[:, 0] < 263).all()
    # a ravine below the tee: the same flight clears the crowns
    dg = np.zeros((111, 76))
    dg[60:70, :] = 30.0                              # 230-266 yds out is 30 yds below the tee; the landing is level
    deep = (np.arange(-10, 434, 4.0), np.arange(-150, 154, 4.0), dg)
    ev2 = vc.flight_tree_ev_curve(M, 20.0, 1.0, drop_of=lambda hd: deep)
    e2, _ = ev2(R, S, {}, "Driver", {"rough_roll": 0.3}, z, aims)
    assert e2[0] == pytest.approx(1.0)
    # p_hit 0.4: about 40 % stopped, the same swings for every aim
    ev3 = vc.flight_tree_ev_curve(M, 20.0, 0.4)
    e3, _ = ev3(R, S, {}, "Driver", {"rough_roll": 0.3}, np.zeros((5, 4000)), aims)
    assert e3[0] - 1.0 == pytest.approx(0.4, abs=0.03)


def test_flight_check_ignores_the_tee_chute():
    M = _fake_M(290.0)
    R = _R()
    R.tree = lambda a, l: (a >= 40) & (a <= 120)     # woods round the tee: not on the checked map
    ev = vc.flight_tree_ev_curve(M, 20.0, 1.0)
    e, _ = ev(R, np.zeros((500, 200)), {}, "Driver", {"rough_roll": 0.3}, np.zeros((5, 50)), np.array([0.0]))
    assert e[0] == pytest.approx(1.0)


def test_extra_clubs_and_prior_widths():
    CLUBS = {"Driver": (275, 300, 65, 28), "4-wood": (255, 270, 50, 24), "Mid iron": (185, 192, 34, 18),
             "Hybrid ~235 (not in bag)": (235, 248, 45, 22)}
    M = types.SimpleNamespace(CLUBS=dict(CLUBS), ALL_CLUBS=list(CLUBS), REAL_CLUBS=["Driver", "4-wood", "Mid iron"],
                              HYBRID="Hybrid ~235 (not in bag)", HOLES={1: {"elev": {"Mid iron": (-3.0, 0.9, 1.0)}}})
    D = types.SimpleNamespace(prior_draws=lambda s=64, seed=2026, hole=None: [
        dict(width={"Driver": 70.0, "4-wood": 54.0, "Mid iron": 36.0}, c_club={"Mid iron": 2.0}) for _ in range(s)])
    vc.install_engine({"extra_clubs": {"8-iron": [162, 167, 30, 16]}}, M, D)
    assert M.ALL_CLUBS.index("8-iron") == M.ALL_CLUBS.index(M.HYBRID) - 1
    assert "8-iron" in M.REAL_CLUBS and M.CLUBS["8-iron"] == (162.0, 167.0, 30.0, 16.0)
    assert M.HOLES[1]["elev"]["8-iron"] == (-3.0, 0.9, 1.0)
    P = D.prior_draws(4)[0]
    assert P["width"]["8-iron"] == pytest.approx(36.0 * 30 / 34)
    assert P["c_club"]["8-iron"] == 2.0
    vc.install_engine({"extra_clubs": {"8-iron": [1, 1, 1, 1]}}, M, D)    # once per process
    assert M.CLUBS["8-iron"][0] == 162.0


def test_engine_off_switch(monkeypatch):
    M = types.SimpleNamespace(CLUBS={}, ALL_CLUBS=[], REAL_CLUBS=[], HYBRID="h", HOLES={})
    monkeypatch.setenv("V2_ENGINE", "0")
    vc.install_engine({"extra_clubs": {"8-iron": [162, 167, 30, 16]}}, M, types.SimpleNamespace())
    assert M._engine_opts == {} and not M.CLUBS


def test_refined_solver_replaces_aim_and_pick():
    """Stage 2 re-evaluates each club near its coarse aim on fresh swings: a coarse pick made on noise is undone."""
    def curve(club, aims):                      # true EV: 2-wood 0.004 worse than 4-wood, both best at +3
        return 4.0 + 0.0004 * (aims - 3.0) ** 2 + (0.004 if club == "2-wood" else 0.0)
    M = types.SimpleNamespace(HYPOTHETICAL=set(), HOLES={1: {}}, draws_z=lambda n, seed: np.zeros((5, n)),
                              club_numbers=lambda hd, c, P: (250, 15, 12, 6))
    M.ev_curve = lambda R, S, hd, c, P, z, aims, wind=None: (curve(c, aims), None)
    D = types.SimpleNamespace(AIM_LIMIT=40.0)

    def robust_aim(aims, curve_, lo=-40, hi=40):
        i = int(np.argmin(np.where((aims >= lo) & (aims <= hi), curve_, np.inf)))
        return dict(aim=float(aims[i]), ev=float(curve_[i]), window=[float(aims[max(i - 4, 0)]), float(aims[min(i + 4, len(aims) - 1)])],
                    at_bound=False)
    D.robust_aim = robust_aim

    def coarse(h, P, R, S, z, speed, rel):     # a noisy coarse stage that has the 2-wood ahead
        cl = {"4-wood": dict(aim=1.0, ev=4.006, zone=[-1.0, 3.0], at_bound=False),
              "2-wood": dict(aim=5.0, ev=4.003, zone=[3.0, 7.0], at_bound=False)}
        return dict(pick="2-wood", runner="4-wood", margin=0.003, clubs=cl)
    WG2 = types.SimpleNamespace(solve=coarse, wind_hook=lambda c, s, r: None)
    solve = vc.refined_solver(M, D, WG2, 1000)
    r = solve(1, {}, None, None, None, 0, 0)
    assert r["pick"] == "4-wood" and r["runner"] == "2-wood"
    assert r["margin"] == pytest.approx(0.004, abs=1e-9)
    assert r["clubs"]["4-wood"]["aim"] == 3.0 and r["clubs"]["4-wood"]["ev_coarse"] == 4.006
    assert r["clubs"]["2-wood"]["n_refine"] == 1000


def test_floored_par3_box():
    one_line = lambda p: dict(lat=(-0.2, 1.0), dep=(2.0, 2.0), how_lat="fits", how_dep="lo", aim=(0.4, 2.0))
    r = vc.floored_plan(one_line)({})
    assert r["dep"] == (0.0, 4.0) and r["aim"] == (0.4, 2.0)          # drawn 4 yds deep, the target kept
    assert r["lat"][1] - r["lat"][0] == pytest.approx(4.0) and np.mean(r["lat"]) == pytest.approx(0.4)
    wide = vc.floored_plan(lambda p: dict(lat=(-3.0, 3.0), dep=(-5.0, 5.0), aim=(0.0, 0.0)))({})
    assert wide["lat"] == (-3.0, 3.0) and wide["dep"] == (-5.0, 5.0)


def _js_par3(temp, tk):
    html = open(TEMPLATE).read()
    code = re.search(r"const D = /\*__DATA__\*/null;?(.*?)</script>", html, re.S).group(1)
    i = code.index("function solvePar3(h){")
    j = code.index("\nconst P = (h, p)", i)
    js = (f"const D = {{speeds: [0, 5], temp_k: {tk}}}; const st = {{from: 0, mph: 0, set: 'Back'}};\n"
          f"const tempFor = h => {temp}; const windMod = m => 0;\n" + code[i:j] +
          "\nconst h = {bearing: 0, base_set: 'Back', by_set: {Back: {center: 150, plays: {'0_0': 133, '5_0': 140, '5_30': 140}, boxes: {'0': {play: 152}}}}};\n"
          "console.log(JSON.stringify(solvePar3(h)));")
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-800:]
    return json.loads(out.stdout)


@pytest.mark.skipif(not shutil.which("node"), reason="no node")
def test_par3_plays_like_includes_temperature():
    r70 = _js_par3(70, 0.00075)
    assert r70["play"] == pytest.approx(152 * 133 / 150)
    r50 = _js_par3(50, 0.00075)
    assert r50["play"] == pytest.approx(152 * 133 / 150 / (1 - 0.00075 * 20))
    assert 1.9 < r50["play"] - r70["play"] < 2.2                 # ~2 yds longer at 50 F on a 135-yd shot
    assert _js_par3(50, 0)["play"] == pytest.approx(r70["play"])  # pages built without temp_k: unchanged


def test_template_moved_tee_note_and_hazards():
    html = open(TEMPLATE).read()
    assert "if(r.T.back !== 0) note = `The calm-day book" in html
    # golfer request 2026-11-06: no hazard outlines on the photo (h.haz is no longer drawn)
    assert "h.haz" not in html and 'id="adj" min="-60" max="60" step="5"' in html
