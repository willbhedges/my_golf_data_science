import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tee_cases as TC  # noqa: E402


def test_case_order():
    c = TC.case_of
    assert c(4.0, "walkback") == "ok"
    assert c(30.0, "tee_axis", has_set=False) == "wrong set mapping / card"
    assert c(30.0, "tee_axis", auto_card=400, truth_card=420) == "wrong set mapping / card"
    assert c(30.0, "review (snapped 3 yds along OSM tee 7)") == "review tee snap"
    assert c(30.0, "walkback_capped") == "walkback from card"
    assert c(30.0, "lidar_pad_capped") == "lidar / texture pad"
    assert c(30.0, "tee_axis", stage_ran=False) == "no OSM hole way (package tee kept)"
    assert c(30.0, "tee_axis", truth_box=(12.0, 5), tee_id=5) == "no OSM tee at the truth tee"
    assert c(30.0, "tee_axis", truth_box=(0.0, 5), tee_id=5) == "box right, point off"
    assert c(30.0, "tee_axis", truth_box=(0.0, 5), tee_id=6, auto_box=(0.0, 6)) == "wrong box in the complex"
