"""Second-shot planner (spirit_hollow/approach): geometry, DECADE box, dispersion, par-5 summaries."""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "spirit_hollow", "approach"))

import geom          # noqa: E402
import plan as P     # noqa: E402
import shots as S    # noqa: E402
from matplotlib.path import Path   # noqa: E402


class FakeRaster:
    """Rough everywhere, water where x < water_x (west = golfer's left when playing north)."""

    def __init__(self, water_x=None):
        self.water_x = water_x

    def lie_id(self, pts):
        pts = np.asarray(pts, float)
        out = np.full(pts.shape[:-1], geom.LIE_ID["rough"], np.int8)
        if self.water_x is not None:
            out[pts[..., 0] < self.water_x] = geom.LIE_ID["water"]
        return out


class FakeHole:
    def __init__(self, r=15.0, n=48):
        a = np.linspace(0, 2 * np.pi, n, endpoint=False)
        self.green = np.c_[r * np.cos(a), r * np.sin(a)]
        self.green_c = np.zeros(2)
        self.green_path = Path(self.green)


def test_enu_round_trip():
    e = geom.ENU([-91.15, 40.76])
    ll = np.array([[-91.149, 40.761], [-91.151, 40.758]])
    assert np.allclose(e.to_ll(e.from_ll(ll)), ll, atol=1e-9)
    # 0.001 deg of latitude is ~121 yds
    assert abs(e.from_ll([[-91.15, 40.761]])[0, 1] - 120.9) < 1.0


def test_right_of_is_golfers_right():
    assert np.allclose(geom.right_of(np.array([0.0, 1.0])), [1.0, 0.0])     # facing north, right = east


def test_decade_base_extends_the_card():
    assert P.decade_base(40) == 3
    assert P.decade_base(150) == 8
    assert P.decade_base(250) == 13
    assert P.decade_base(300) == 15


def test_box_centred_without_trouble():
    h = FakeHole()
    b = P.decade_box(h, FakeRaster(), np.array([0.0, -150.0]))
    assert all(v == "rough" for v in b["haz"].values())
    assert abs(b["aim_ld"][0]) < 0.5 and abs(b["aim_ld"][1]) < 0.5
    assert b["how_lat"] == "fits" and b["how_dep"] == "fits"


def test_water_left_pushes_the_box_right():
    h = FakeHole()
    b = P.decade_box(h, FakeRaster(water_x=-17.0), np.array([0.0, -150.0]))
    assert b["haz"]["left"] == "water" and b["haz"]["right"] == "rough"
    assert b["off"]["left"] == pytest.approx(b["off"]["right"] + 3.0)
    assert b["aim_ld"][0] > 1.0


def test_rough_widens_the_cushions():
    h = FakeHole()
    fw = P.decade_box(h, FakeRaster(), np.array([0.0, -120.0]), "fairway")
    rg = P.decade_box(h, FakeRaster(), np.array([0.0, -120.0]), "rough")
    assert rg["off"]["short"] > fw["off"]["short"] and rg["off"]["left"] > fw["off"]["left"]
    assert np.ptp(rg["lat"]) <= np.ptp(fw["lat"])


def test_wind_modifier_shrinks_the_box():
    h = FakeHole()
    calm = P.decade_box(h, FakeRaster(), np.array([0.0, -150.0]), wind=0)
    windy = P.decade_box(h, FakeRaster(), np.array([0.0, -150.0]), wind=2)
    assert np.ptp(windy["dep"]) < np.ptp(calm["dep"])


def test_small_green_falls_back_to_the_middle():
    h = FakeHole(r=6.0)
    b = P.decade_box(h, FakeRaster(), np.array([0.0, -220.0]))
    assert b["how_lat"] == "split" and abs(b["aim_ld"][0]) < 0.6


def test_clip_to_rect():
    sq = np.array([[0, 0], [10, 0], [10, 10], [0, 10]], float)
    c = P.clip_to_rect(sq, 2, 5, -1, 4)
    assert np.allclose(c.min(axis=0), [2, 0]) and np.allclose(c.max(axis=0), [5, 4])


def test_dispersion_matches_5hcp_proximity():
    z = S.z_draws(100000, 1)
    for d, lo, hi in ((100, 30, 40), (150, 40, 50), (200, 58, 72)):
        sl, sd = S.sigma(d)
        prox_ft = np.hypot(sl * z[1], sd * z[0]).mean() * 3
        assert lo <= prox_ft <= hi, (d, prox_ft)


def test_rough_disperses_more():
    assert S.sigma(150, "rough")[0] > S.sigma(150, "first_cut")[0] > S.sigma(150, "fairway")[0]


def test_short_game_joins_the_long_tables():
    import tee_strategy as t
    for lie in ("fairway", "rough", "sand", "recovery"):
        for d in (20, 40):
            assert S.SHORT[lie][list(S.SHORT_D).index(d)] == pytest.approx(
                float(np.interp(d, t.DIST, t.BASELINE[lie])), abs=1e-9)


def test_putts_monotone():
    ft = np.array([2, 5, 10, 20, 40, 80])
    assert np.all(np.diff(S.putts(ft)) > 0)


def test_go_rule_scans_out():
    rows = [dict(dist=d, lie="fairway", e_go=g, e_lay=l, go_aim=a) for d, g, l, a in
            ((150, 3.3, 3.5, "green"), (160, 3.35, 3.5, "green"), (170, 3.45, 3.5, "20 short, +0"),
             (180, 3.6, 3.5, "green"), (190, 3.4, 3.5, "green"))]
    r = P.go_rule(rows)["fairway"]
    assert r["go_up_to"] == 170 and r["green_box_up_to"] == 160


def test_summarize_par5_families():
    targets = [(20.0, 0.0), (60.0, 0.0), (100.0, 0.0)]
    res = dict(targets=targets, target_xy=np.zeros((3, 2)),
               E_go=np.array([3.6, 3.9, np.nan, np.nan]),
               E_lay=np.array([[3.7, 3.8, 3.9], [3.8, 3.7, 3.85], [np.nan, 3.75, 3.8], [np.nan, np.nan, np.nan]]),
               E_fixed=np.array([np.nan, np.nan, np.nan, 4.2]), dist=np.array([200, 230, 280, 210.0]),
               lies=np.array(["fairway", "fairway", "rough", "recovery"], dtype=object))
    s = P.summarize_par5(res)
    # ball 0 goes at the green; ball 1 goes at the apron (20 short beats the 60 lay-up? 3.8 > 3.7: no)
    assert s["go_better"].tolist() == [True, False, False, False]
    assert s["p_fixed"] == pytest.approx(0.25)
    assert s["fixed"]["L"] == 60.0


@pytest.mark.parametrize("key", [13, "2F"])
def test_real_hole_geometry(key):
    h = geom.Hole(key)
    assert h.lie(h.green_c[None])[0] == "green"
    assert np.linalg.norm(h.green_trilat - h.green_c) < 15
    d_tee = np.linalg.norm(h.tee - h.green_c)
    assert 300 < d_tee < 560
    # ground -> page px -> ground (these holes are drawn on the traced screenshot itself)
    assert not h.hd.get("display")
    back = h.px_to_xy(h.xy_to_px(h.green))
    assert np.allclose(back, h.green, atol=0.05)
