"""yardage_book par-3 rule (DECADE edge cushions), tested on synthetic greens and the real ones."""
import itertools

import numpy as np
import pytest
from matplotlib.path import Path

import course as course_mod
import yardage_book as ybmod

STEP_TOL = 0.5      # par3_plan scans the green edge on a 0.25-yd grid


def ellipse(width, depth, n=200, c=(0.0, 0.0)):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [(c[0] + width / 2 * np.cos(x), c[1] + depth / 2 * np.sin(x)) for x in a]


def green(width=20, depth=30, center=150, **haz):
    h = dict(left="rough", right="rough", short="rough", long="rough")
    h.update(haz)
    return dict(center=center, green=ellipse(width, depth), haz=h)


def corners(plan):
    (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
    return [(l0, d0), (l1, d0), (l1, d1), (l0, d1)]


ALL_PAR3 = [("mozingo", k, p) for k, p in ybmod.PAR3.items()] + \
           [("spirit", k, p) for k, p in course_mod.PAR3.items()]


# ---------------------------------------------------------------- tables
def test_modifier_table(yb):
    assert yb.ADD == {"water": 3.0, "ob": 3.0, "trees": 2.0, "native": 2.0, "bunker": 1.0,
                      "rough": 0.0, "runoff": -2.0}
    assert yb.WIND_NOW == 0
    assert set(yb.SEVERITY) == set(yb.ADD)
    assert yb.SEVERITY["water"] == yb.SEVERITY["ob"] > yb.SEVERITY["trees"] == yb.SEVERITY["native"] \
        > yb.SEVERITY["bunker"] > yb.SEVERITY["rough"] > yb.SEVERITY["runoff"]


@pytest.mark.parametrize("dist,exp", [(60, 3), (100, 5), (150, 8), (160, 8), (180, 9), (200, 10),
                                      (250, 13), (30, 3), (300, 13), (152, 8), (178, 9), (224, 11)])
def test_baseline_target(yb, dist, exp):
    assert yb.baseline_target(dist) == exp


def test_baseline_target_tracks_distance_over_20(yb):
    for d in range(60, 251):
        assert abs(yb.baseline_target(d) - d / 20) <= 1.0


# ---------------------------------------------------------------- cushions
@pytest.mark.parametrize("dist", [60, 95, 134, 150, 177, 199, 219, 250])
@pytest.mark.parametrize("kind", list(ybmod.ADD))
def test_cushion_is_target_plus_modifier(yb, dist, kind):
    p = green(center=dist, left=kind, right="rough", short=kind, long="bunker")
    plan = yb.par3_plan(p)
    base = yb.TARGET[int(round(min(max(dist, 60), 250) / 10.0) * 10)]
    assert plan["base"] == base
    assert plan["off"]["left"] == max(base + yb.ADD[kind], 0.0)
    assert plan["off"]["short"] == max(base + yb.ADD[kind], 0.0)
    assert plan["off"]["right"] == base
    assert plan["off"]["long"] == base + 1
    assert plan["sev"]["left"] == yb.SEVERITY[kind]


def test_explicit_modifier_values(yb):
    plan = yb.par3_plan(green(center=200, left="water", right="ob", short="trees", long="runoff"))
    assert plan["off"] == {"left": 13.0, "right": 13.0, "short": 12.0, "long": 8.0}
    plan = yb.par3_plan(green(center=200, left="native", right="bunker", short="rough", long="rough"))
    assert plan["off"] == {"left": 12.0, "right": 11.0, "short": 10.0, "long": 10.0}


def test_wind_adds_to_every_edge(yb, monkeypatch):
    p = green(center=150, left="water", right="bunker", short="rough", long="runoff")
    calm = yb.par3_plan(p)["off"]
    monkeypatch.setattr(yb, "WIND_NOW", yb.WIND["10-20 mph"])
    windy = yb.par3_plan(p)["off"]
    assert {k: windy[k] - calm[k] for k in calm} == {k: 1.0 for k in calm}


def test_cushion_never_negative(yb):
    plan = yb.par3_plan(green(center=60, left="runoff", right="runoff", short="runoff", long="runoff"))
    assert all(v >= 0 for v in plan["off"].values())


# ---------------------------------------------------------------- geometry of the rule
def test_edges_found_on_synthetic_ellipse(yb):
    plan = yb.par3_plan(green(20, 30))
    assert plan["edges_lat"] == pytest.approx((-10, 10), abs=STEP_TOL)
    assert plan["edges_dep"] == pytest.approx((-15, 15), abs=STEP_TOL)


def test_both_fit_both_honoured(yb):
    # 150 yds -> 8 each side; 20 wide has room for 8 + 8, 30 deep for 8 + 9
    plan = yb.par3_plan(green(20, 30, center=150, long="bunker"))
    assert plan["how_lat"] == "fits" and plan["how_dep"] == "fits"
    l, r = plan["edges_lat"]
    f, b = plan["edges_dep"]
    assert plan["lat"] == pytest.approx((l + 8, r - 8))
    assert plan["dep"] == pytest.approx((f + 8, b - 9))
    # the box keeps the full cushion from every edge
    assert plan["lat"][0] - l >= plan["off"]["left"] - 1e-9
    assert r - plan["lat"][1] >= plan["off"]["right"] - 1e-9
    assert plan["dep"][0] - f >= plan["off"]["short"] - 1e-9
    assert b - plan["dep"][1] >= plan["off"]["long"] - 1e-9


SEV_PAIRS = [(a, b) for a, b in itertools.permutations(["water", "trees", "bunker", "rough"], 2)]


@pytest.mark.parametrize("lo,hi", SEV_PAIRS)
def test_lateral_worse_side_keeps_full_cushion(yb, lo, hi):
    # 12 wide at 150 yds: cushions are >= 8 each, so they never both fit
    p = green(12, 30, center=150, left=lo, right=hi)
    plan = yb.par3_plan(p)
    l, r = plan["edges_lat"]
    assert plan["off"]["left"] + plan["off"]["right"] > r - l
    assert plan["lat"][0] == plan["lat"][1] == plan["aim"][0]
    if yb.SEVERITY[lo] > yb.SEVERITY[hi]:
        assert plan["how_lat"] == "lo"
        assert plan["aim"][0] - l == pytest.approx(plan["off"]["left"])
    else:
        assert plan["how_lat"] == "hi"
        assert r - plan["aim"][0] == pytest.approx(plan["off"]["right"])


@pytest.mark.parametrize("short,long", [("water", "trees"), ("trees", "water"), ("water", "bunker"),
                                        ("bunker", "rough"), ("rough", "native")])
def test_depth_worse_side_keeps_full_cushion(yb, short, long):
    p = green(30, 14, center=180, short=short, long=long)
    plan = yb.par3_plan(p)
    f, b = plan["edges_dep"]
    assert plan["off"]["short"] + plan["off"]["long"] > b - f
    assert plan["dep"][0] == plan["dep"][1]
    if yb.SEVERITY[short] > yb.SEVERITY[long]:
        assert plan["how_dep"] == "lo"
        assert plan["aim"][1] - f == pytest.approx(plan["off"]["short"])
    else:
        assert plan["how_dep"] == "hi"
        assert b - plan["aim"][1] == pytest.approx(plan["off"]["long"])


@pytest.mark.parametrize("kind", ["water", "ob", "trees", "native", "bunker", "rough"])
def test_identical_hazards_both_sides_aim_middle(yb, kind):
    # symmetric 12 x 14 ellipse, same hazard all round: nothing fits, aim is dead centre
    p = green(12, 14, center=200, left=kind, right=kind, short=kind, long=kind)
    plan = yb.par3_plan(p)
    assert plan["how_lat"] == "split" and plan["how_dep"] == "split"
    assert plan["aim"] == pytest.approx((0.0, 0.0), abs=STEP_TOL / 2)
    assert plan["lat"][0] == plan["lat"][1] and plan["dep"][0] == plan["dep"][1]


def test_split_is_proportional_to_edge_numbers(yb):
    # same severity (water vs ob) but the 'runoff'-free split uses the two numbers: equal here
    plan = yb.par3_plan(green(12, 30, center=150, left="water", right="ob"))
    assert plan["how_lat"] == "split"
    assert plan["aim"][0] == pytest.approx(0.0, abs=STEP_TOL / 2)
    # trees vs native: same severity, same cushion
    plan = yb.par3_plan(green(12, 30, center=150, left="trees", right="native"))
    assert plan["aim"][0] == pytest.approx(0.0, abs=STEP_TOL / 2)


def test_offset_green_is_handled(yb):
    p = dict(center=150, green=ellipse(20, 30, c=(7.0, -4.0)),
             haz=dict(left="rough", right="rough", short="rough", long="rough"))
    plan = yb.par3_plan(p)
    assert plan["aim"] == pytest.approx((7.0, -4.0), abs=STEP_TOL)


def test_axis_helper_directly(yb):
    assert yb._axis(-10, 10, 3, 4, 0, 0) == (-7, 6, "fits")
    assert yb._axis(-10, 10, 12, 12, 2, 2) == (0, 0, "split")
    assert yb._axis(-10, 10, 12, 10, 3, 2) == (2, 2, "lo")
    assert yb._axis(-10, 10, 12, 10, 1, 2) == (0, 0, "hi")


SYNTH = [green(20, 30), green(20, 30, left="water", right="trees"), green(12, 14, left="water",
         right="water", short="water", long="water"), green(30, 14, short="water", long="trees"),
         green(25, 25, center=220, left="bunker", right="native", short="runoff", long="ob")]


@pytest.mark.parametrize("p", SYNTH)
def test_box_corners_on_synthetic_green(yb, p):
    plan = yb.par3_plan(p)
    assert Path(p["green"]).contains_points(corners(plan)).all()
    assert Path(p["green"]).contains_point(plan["aim"])


@pytest.mark.parametrize("course,hole,p", ALL_PAR3, ids=[f"{c}-{h}" for c, h, _ in ALL_PAR3])
def test_box_corners_on_real_green(yb, course, hole, p):
    plan = yb.par3_plan(p)
    path = Path(p["green"])
    assert path.contains_points(corners(plan)).all()
    assert path.contains_point(plan["aim"])
    (l0, l1), (d0, d1) = plan["lat"], plan["dep"]
    assert l0 <= l1 and d0 <= d1
    # cushions computed from the card for the app's centre number
    assert plan["base"] == yb.baseline_target(p["center"])
    for k, v in p["haz"].items():
        assert plan["off"][k] == max(plan["base"] + yb.ADD[v], 0.0)


@pytest.mark.parametrize("course,hole,p", ALL_PAR3, ids=[f"{c}-{h}" for c, h, _ in ALL_PAR3])
def test_real_green_rule_consistent(yb, course, hole, p):
    plan = yb.par3_plan(p)
    for axis, lo, hi, idx, edges in (("lat", "left", "right", 0, "edges_lat"),
                                     ("dep", "short", "long", 1, "edges_dep")):
        how = plan["how_" + axis]
        e0, e1 = plan[edges]
        z0, z1 = plan[axis]
        if how == "fits":
            assert z0 == pytest.approx(e0 + plan["off"][lo])
            assert z1 == pytest.approx(e1 - plan["off"][hi])
        elif how == "lo":
            assert plan["sev"][lo] > plan["sev"][hi]
            assert z0 == pytest.approx(e0 + plan["off"][lo])
        elif how == "hi":
            assert plan["sev"][hi] > plan["sev"][lo]
            assert z1 == pytest.approx(e1 - plan["off"][hi])
        else:
            assert plan["sev"][lo] == plan["sev"][hi]


def test_mozingo_8_water_short_keeps_cushion(yb):
    # documented in the hole note: too shallow for both, water short wins, box 13 past the front
    plan = yb.par3_plan(yb.PAR3[8])
    assert plan["how_dep"] == "lo"
    assert plan["aim"][1] - plan["edges_dep"][0] == pytest.approx(13.0)
