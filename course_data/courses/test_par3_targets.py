"""Expected-strokes par-3 target box (course_data/courses/par3_targets.py; Eagle Knoll OPTIMIZE.md section 13).

  python3 -m pytest -q course_data/courses/test_par3_targets.py
"""
import json
import os
import re
import sys
import types

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import par3_targets as P3                                   # noqa: E402

EK = os.path.join(HERE, "eagle_knoll")


def _fake_bw():
    """A stand-in for spirit_hollow/build_wind_page: one par 3 on a straight north line, 1 px per yd."""
    bw = types.ModuleType("bw")
    bw.course = types.SimpleNamespace(PAR3={6: dict(tee=(0.0, 200.0), flag=(0.0, 62.0), center=138.0,
                                                    plays_like_delta=-13.0)})

    def frame(tee, flag, center):
        tee, flag = np.array(tee, float), np.array(flag, float)
        f = (flag - tee) / np.linalg.norm(flag - tee)
        return tee, f, np.array([-f[1], f[0]]), np.linalg.norm(flag - tee) / center
    bw.frame = frame
    bw.par3_hole = lambda h: dict(kind="par3", boxes={"-1": dict(poly=[], play=138.0, lo=137, hi=139)})
    bw.par3_sets = lambda h, opts, grid: {o["name"]: dict(center=o["yards"], boxes={}, plays={}) for o in opts}
    return bw


T = {"sets": {"Back": {"6": dict(
    boxes={str(m): dict(aim=[0.5, -4.0], lat=[-1.5, 2.5], dep=[-6.0, -2.0]) for m in (-1, 0, 1, 2, 3)},
    clubs={"sat": dict(pick="GW", runner="PW", tie=False, margin=0.4),
           "sun": dict(pick="GW", runner="PW", tie=True, margin=0.004)})}}}


def _install(tmp_path, bw):
    p = tmp_path / "t.json"
    p.write_text(json.dumps(T))
    P3.install({"par3_targets": str(p)}, bw, "Back")


def test_off_without_config():
    bw = _fake_bw()
    h0, s0 = bw.par3_hole, bw.par3_sets
    P3.install({}, bw, "Back")
    assert bw.par3_hole is h0 and bw.par3_sets is s0


def test_box_is_the_solved_aim_not_the_centre(tmp_path):
    bw = _fake_bw()
    _install(tmp_path, bw)
    d = bw.par3_hole(6)
    b = d["boxes"]["-1"]
    assert b["play"] == pytest.approx(138 - 4.0)
    assert (b["lo"], b["hi"]) == (pytest.approx(132.0), pytest.approx(136.0))
    ys = sorted(p[1] for p in b["poly"])           # north = up the page: 200 - along
    assert ys[0] == pytest.approx(200 - 136.0) and ys[-1] == pytest.approx(200 - 132.0)
    xs = sorted(p[0] for p in b["poly"])           # heading north, right = +x... frame right = (-f1, f0) = (1, 0)
    assert xs[0] == pytest.approx(-1.5) and xs[-1] == pytest.approx(2.5)
    assert "GW" in d["p3club"] and "tie with PW" in d["p3club"]


def test_page_number_is_the_carry_to_the_aim(tmp_path):
    """The template: play = box.play x plays[cell] / center x tmul. With the scaled plays it equals the plays-like
    distance to the AIM (incl. elevation), and the elevation chip is dz exactly."""
    sys.path.insert(0, os.path.join(ROOT, "spirit_hollow"))
    wg = types.ModuleType("wind_grid")
    wg.plays_like = lambda dist, speed, rel: dist * (1 + 0.01 * speed * np.cos(np.radians(rel)))
    sys.modules["wind_grid"] = wg
    bw = _fake_bw()
    _install(tmp_path, bw)
    grid = {"par3": {"6": {"0_0": 0, "10_0": 0, "10_180": 0}}}
    out = bw.par3_sets(6, [dict(name="Back", yards=138)], grid)
    S = out["Back"]
    A = 138 - 4.0
    for cell in grid["par3"]["6"]:
        sp, rel = [int(x) for x in cell.split("_")]
        play = P3.page_play(S["boxes"]["-1"]["play"], S["plays"][cell], S["center"], 1.0)
        assert play == pytest.approx(wg.plays_like(A, sp, rel) - 13.0)
    calmP = S["plays"]["0_0"] / S["center"]
    eY = S["boxes"]["-1"]["play"] * calmP - S["boxes"]["-1"]["play"]
    assert eY == pytest.approx(-13.0)


def test_template_formula_unchanged():
    """par3_targets relies on the template's solvePar3 number; fail loudly if that formula changes."""
    html = open(os.path.join(HERE, "wind_page_template_course.html")).read()
    assert re.search(r"play:\s*b\.play\s*\*\s*plays\s*/\s*S3\.center\s*\*\s*tmul", html)


def test_eagle_knoll_switched_on_with_every_par3():
    cfg = json.load(open(os.path.join(EK, "config.json")))
    T = P3.load(cfg)
    assert T is not None
    for s in ("Back", "Eagle", "Middle"):
        for h in ("2", "6", "12", "16"):
            t = T["sets"][s][h]
            for m in ("-1", "0", "1", "2", "3"):
                b = t["boxes"][m]
                assert b["lat"][0] <= b["aim"][0] <= b["lat"][1] and b["dep"][0] <= b["aim"][1] <= b["dep"][1]
                assert b["lat"][1] - b["lat"][0] >= 4 - 1e-9 and b["dep"][1] - b["dep"][0] >= 4 - 1e-9
            g, se = t["gain_vs_centre"]
            assert g > -2 * se                       # the solved aim is never worse than the centre


def test_other_courses_keep_decade():
    import glob
    for p in glob.glob(os.path.join(HERE, "*", "config.json")):
        if os.path.basename(os.path.dirname(p)) not in ("eagle_knoll", "gateway_national"):   # switched on per course
            assert "par3_targets" not in json.load(open(p)), p


def test_club_line_per_set_and_hidden(monkeypatch):
    """by_set[set].p3club carries each set's own club; config par3_club_hide blanks it (Gateway Tips 14)."""
    import types
    import par3_targets as PT
    t = {"clubs": {"sat": {"pick": "4-iron", "runner": "5-iron"}}, "boxes": {m: {"lat": [-2, 2], "dep": [-3, 1], "aim": [0, -1]}
                                                                         for m in ("-1", "0", "1", "2", "3")}}
    T = {"sets": {"Back": {"14": dict(t, clubs={"sat": {"pick": "5-iron", "runner": "6-iron"}})}, "The Tips": {"14": t}}}
    BW = types.SimpleNamespace()
    BW.course = types.SimpleNamespace(PAR3={14: {"tee": (0.0, 0.0), "flag": (0.0, -10.0), "center": 200.0}})
    BW.frame = lambda tee, flag, center: (np.zeros(2), np.array([0.0, -1.0]), np.array([1.0, 0.0]), 1.0)
    BW.par3_hole = lambda h: {}
    BW.par3_sets = lambda h, opts, grid: {o["name"]: {} for o in opts}
    monkeypatch.setattr(PT, "load", lambda cfg: T)
    PT.install({"par3_targets": "x", "par3_club_hide": {"The Tips": [14]}}, BW, "Back")
    monkeypatch.setitem(sys.modules, "wind_grid", types.SimpleNamespace(plays_like=lambda A, sp, d: A))
    out = BW.par3_sets(14, [{"name": "Back", "yards": 200}, {"name": "The Tips", "yards": 240}], {"par3": {"14": {"0_0": 0}}})
    assert out["Back"]["p3club"] == "Sat: 5-iron" and out["The Tips"]["p3club"] == ""
    assert BW.par3_hole(14)["p3club"] == "Sat: 5-iron"
