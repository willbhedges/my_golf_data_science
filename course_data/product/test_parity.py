"""Decision-parity fixes in the product loader (package.py) + the parity harness (parity.py).

  python3 -m pytest -q course_data/product/test_parity.py
"""
import copy
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import package as PK                                # noqa: E402

CD = os.path.dirname(HERE)
SH = os.path.join(CD, "packages", "spirit_hollow", "package.json")
HAND = os.path.join(CD, "spirit_hollow", "hand_zones_ll.json")
SQ = lambda x0, y0, x1, y1: [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]      # noqa: E731


def lie_at(zones, pt):
    from matplotlib.path import Path
    lie = "rough"
    for n, p in zones:
        if Path(np.asarray(p, float)).contains_point(pt):
            lie = n
    return lie


def test_given_order_kept_and_precedence_sorted():
    zones = [("fairway", SQ(0, 0, 10, 10)), ("recovery", SQ(5, 5, 15, 15)), ("rough", SQ(6, 6, 8, 8))]
    given = PK.order_zones(zones, "given")
    assert [n for n, _ in given] == ["fairway", "recovery", "rough"]
    assert lie_at(given, (7, 7)) == "rough"                 # the correction patch wins where it was drawn
    assert lie_at(given, (9, 9)) == "recovery"              # traced trees over the traced fairway
    prec = PK.order_zones(zones, None)
    assert [n for n, _ in prec] == ["recovery", "rough", "fairway"]


def test_rough_is_not_a_noop_in_precedence_mode():
    zones = PK.order_zones([("rough", SQ(0, 0, 4, 4)), ("native", SQ(0, 0, 10, 10))])
    assert lie_at(zones, (2, 2)) == "rough"


def test_first_cut_band_only_replaces_rough():
    zones = [("fairway", SQ(100, 100, 200, 400)), ("recovery", SQ(195, 150, 260, 200))]
    band = PK.first_cut_band(zones, yds=8)
    assert band and all(n == "first_cut_band" for n, _ in band)
    z = PK.order_zones(band + zones)
    assert lie_at(z, (150, 300)) == "fairway"
    assert lie_at(z, (100 - 4 * PK.PPY, 300)) == "first_cut"        # 4 yds outside the fairway
    assert lie_at(z, (100 - 12 * PK.PPY, 300)) == "rough"            # 12 yds outside
    assert lie_at(z, (205, 175)) == "recovery"                        # trees beside the fairway still win
    assert PK.first_cut_band(zones + [("first_cut", SQ(0, 0, 1, 1))], yds=8) == []
    assert PK.first_cut_band(zones, yds=0) == []


@pytest.fixture(scope="module")
def sh():
    if not os.path.exists(SH):
        pytest.skip("no Spirit Hollow package")
    return json.load(open(SH))


def _load(pkg, tmp_path, tees="Black"):
    p = tmp_path / "package.json"
    p.write_text(json.dumps(pkg))
    return PK.load(str(p), tees)


def test_load_honours_zone_order_given(sh, tmp_path):
    pkg = copy.deepcopy(sh)
    h = pkg["holes"]["4"]
    zs = h["zones_ll"]
    fw = next(z for z in zs if z["lie"] == "fairway")
    h["zones_ll"] = [fw] + [z for z in zs if z is not fw and z["lie"] == "recovery"][:1]
    h["zones_ll"] = [h["zones_ll"][-1], fw] if len(h["zones_ll"]) > 1 else h["zones_ll"]
    C = _load(pkg, tmp_path)
    assert [n for n, _ in C.holes[4]["zones"]][-1] == "fairway"     # precedence: fairway over trees
    h["zone_order"] = "given"
    h["zones_ll"] = h["zones_ll"][::-1]
    C = _load(pkg, tmp_path)
    assert [n for n, _ in C.holes[4]["zones"]][0] == "fairway"      # given: as listed


def test_given_line_kept(sh, tmp_path):
    pkg = copy.deepcopy(sh)
    t = pkg["holes"]["4"]["tees"]["Black"]
    C0 = _load(pkg, tmp_path)
    b0 = C0.bearings[4]
    fr = PK.R.Frame(t["tee_ll"], C0.frames[4]["aim_ll"], ppy=1.0, tee_px=(0.0, 0.0), proj="enu")
    t["aim_ll"] = [float(v) for v in fr.yds_to_ll([[60.0, -250.0]])[0]]     # 13.5 deg right of the rule's line
    C1 = _load(pkg, tmp_path)
    assert abs(C1.bearings[4] - b0) < 0.5                           # the landing rule ignores a package aim_ll
    t["aim_rule"] = "app"
    C2 = _load(pkg, tmp_path)
    assert abs(((C2.bearings[4] - b0 + 180) % 360 - 180) - 13.5) < 1.0


def test_elevation_follows_the_tee(sh, tmp_path):
    if not PK.dem_path(sh, SH):
        pytest.skip("no DEM on disk")
    pkg = copy.deepcopy(sh)
    C0 = _load(pkg, tmp_path)
    stored = PK._elev(pkg["holes"]["14"]["tees"]["Black"]["elevation"], PK.conditions_of(pkg))
    assert C0.holes[14]["elev"]["Driver"] == stored["Driver"]        # same line -> the stored table
    t = pkg["holes"]["14"]["tees"]["Black"]
    fr = PK.R.Frame(t["tee_ll"], C0.frames[14]["aim_ll"], ppy=1.0, tee_px=(0.0, 0.0), proj="enu")
    t["tee_ll"] = [float(v) for v in fr.yds_to_ll([[0.0, -40.0]])[0]]   # 40 yds up the line
    C1 = _load(pkg, tmp_path)
    assert C1.holes[14]["elev"]["Driver"] != stored["Driver"]


def test_soft_conditions():
    e = {"adjustments": {"clubs": {"Driver": dict(carry_delta_yds=12.0, roll_factor=2.4, lateral_kick_yds=-9.0)}}}
    assert PK._elev(e, "soft")["Driver"] == (12.0, 1.3, 0.0)
    assert PK._elev(e, "normal")["Driver"] == (12.0, 2.0, -9.0)


def test_parity_mapping_reproduces_hand_lies(sh):
    """Hand inputs mapped into the product frame give the hand's lies (the 'all hand' row checks the mapping)."""
    import parity as PA
    hand = json.load(open(HAND))
    course = PA.load_hand_course()
    C, _ = PA.product_course(SH, "Black", hand)
    for k, hk in ((4, "4"), (11, "11")):
        hd = course.HOLES[PA.course_key(hk)]
        geo = PA.ShotGeo(hand["holes"][hk])
        fr = PK.R.Frame.from_json(C.frames[k])
        H = PA.hand_in_product(hd, geo, fr)
        v = PA.variant(C.holes[k], H, PA.FACTORS)
        ht, hf, hr, hp = PA.frame_vectors(hd)
        A, L = np.meshgrid(np.arange(150, 320, 7.0), np.arange(-50, 51, 7.0))
        hpx = ht + (A.ravel()[:, None] * hf + L.ravel()[:, None] * hr) * hp
        ppx = fr.ll_to_px(geo.px_to_ll(hpx))
        agree = (PA.lie_grid(hd, hpx) == PA.lie_grid(v, ppx)).mean()
        assert agree > 0.99, (k, agree)
        # the mapped tee line: same bearing, ground scale of the app's 270 dot
        assert np.allclose(v["tee"], fr.ll_to_px(geo.px_to_ll([hd["tee"]]))[0])
