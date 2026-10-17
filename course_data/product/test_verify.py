"""Offline tests for the pre-round check (verify.py, apply_answers.py, review_page.py) on a synthetic hole.
python3 -m pytest -q course_data/product/test_verify.py"""
import copy
import json
import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify as V                                  # noqa: E402
import apply_answers as AA                          # noqa: E402
import review_page as RP                            # noqa: E402

t = V.t
LON0, LAT0 = -93.65, 42.03
DLAT = 0.9144 / 111320.0
DLON = DLAT / math.cos(math.radians(LAT0))


def ll(x, along):
    return [LON0 + x * DLON, LAT0 + along * DLAT]


def rect(x0, x1, a0, a1):
    return [ll(x0, a0), ll(x1, a0), ll(x1, a1), ll(x0, a1)]


def hole():
    tee, green = ll(0, 0), ll(0, 400)
    return {"ref": "1", "par": 4, "length": 400, "yards": {"Blue": 400}, "green_ll": green,
            "hole_line_ll": [tee, ll(0, 200), green],
            "tees": {"Blue": {"tee_ll": tee, "aim_ll": ll(0, 250), "card_yards": 400, "measured_yards": 400,
                              "method": "tee_axis", "confidence": 0.8}},
            "tee_ll": tee, "aim_ll": ll(0, 250),
            "zones_ll": [{"lie": "fairway", "poly": rect(-18, 18, 180, 390), "src": "osm", "p": 1.0},
                         {"lie": "recovery", "poly": rect(-60, -25, 200, 320), "src": "vision:lidar_hag", "p": 0.9},
                         {"lie": "recovery", "poly": rect(30, 70, 200, 320), "src": "osm", "p": 1.0}]}


@pytest.fixture(autouse=True)
def _restore_model():
    names = ("CLUBS", "IRONS", "TREE_SEVERITY", "NATIVE_LOST", "MISHIT_RATE", "HCP_BASELINE", "HOLES")
    saved = {n: copy.deepcopy(getattr(t, n)) for n in names}
    yield
    for n, v in saved.items():
        setattr(t, n, v)


def test_hole_model_frame_and_zones():
    hd, fr = V.hole_model(hole(), "Blue")
    assert np.allclose(hd["tee"], V.PK.TEE_PX)
    gx, gy = hd["green"]
    assert abs(gx - 460) < 2 and abs((1900 - gy) / V.PK.PPY - 400) < 1.5
    assert [z[0] for z in hd["zones"]] == ["recovery", "recovery", "fairway"]     # precedence order


def test_groups_shift_remove_gap():
    h = hole()
    _, fr = V.hole_model(h, "Blue")
    g = V.hazard_groups(h, fr, {"aim": 0.0})
    assert list(g) == [("recovery", "left")]                  # the OSM trees on the right are not asked about
    grp = g[("recovery", "left")]
    assert grp["idx"] == [1] and abs(grp["edge"] + 25) < 1 and grp["toward"] == (1.0, 0.0)
    moved = V.shifted(h, fr, [1], grp["toward"], 10.0)
    assert abs(V.to_yd(fr, moved[1]["poly"])[:, 0].max() + 15) < 0.5
    assert len(V.removed(h, [1])) == 2
    assert V.gap_sides(h, fr, {"aim": 0.0}) == []
    h2 = dict(h, zones_ll=h["zones_ll"][:1])
    assert [s for s, _ in V.gap_sides(h2, fr, {"aim": 0.0})] == ["left", "right"]
    h2["verification"] = {"open_left": True}
    assert [s for s, _ in V.gap_sides(h2, fr, {"aim": 0.0})] == ["right"]


def test_base_plan_and_replan_small_n():
    V.decide.set_prior_means()
    z = V.decide._z(300, 1)
    h = hole()
    hd, fr = V.hole_model(h, "Blue")
    base = V.base_plan(hd, z)
    assert base["pick"] in V.decide.clubs_for(V.KEY) and base["runner"] != base["pick"]
    same = V.replan(hd, fr, base, fr, z)                      # unchanged world: no change, no regret
    assert same["pick"] == base["pick"] and abs(same["aim_shift"]) <= 2.5 and same["regret"] < 1e-9


def test_apply_answers_tee_and_hazard():
    h = hole()
    _, fr = V.hole_model(h, "Blue")
    pkg = {"tee_set": "Blue", "holes": {"1": h}}
    review = {"tee_set": "Blue", "built": "x", "holes": {"1": {"frame": fr.to_json(), "base": {"aim": 0}}},
              "items": [{"id": "1-tee", "hole": "1", "type": "tee"},
                        {"id": "1-recovery-left", "hole": "1", "type": "hazard", "zone_idx": [1],
                         "zone_fp": [[round(v, 7) for v in h["zones_ll"][1]["poly"][0]]], "toward": [1.0, 0.0]}]}
    ans = {"answers": [{"id": "1-tee", "answer": "moved", "dx": 0, "dy": -20},
                       {"id": "1-recovery-left", "answer": "absent"}]}
    new, changed, warn = AA.apply(pkg, review, ans)
    tee = new["holes"]["1"]["tees"]["Blue"]["tee_ll"]
    assert abs((tee[1] - LAT0) / DLAT + 20) < 0.3 and new["holes"]["1"]["tee_ll"] == tee
    assert len(new["holes"]["1"]["zones_ll"]) == 2 and changed == {"1": ["1-tee", "1-recovery-left"]}
    assert len(pkg["holes"]["1"]["zones_ll"]) == 3                       # input untouched
    # moved hazard: 10 yds toward the fairway, then verified (no longer asked)
    ans = {"answers": [{"id": "1-recovery-left", "answer": "moved", "shift": 10}]}
    new, _, _ = AA.apply(pkg, review, ans)
    z = new["holes"]["1"]["zones_ll"][1]
    assert abs(V.to_yd(fr, z["poly"])[:, 0].max() + 15) < 0.5 and not V.is_uncertain(z)
    # fingerprint mismatch (package rebuilt): skipped with a warning
    review["items"][1]["zone_fp"] = [[0.0, 0.0]]
    _, changed, warn = AA.apply(pkg, review, {"answers": [{"id": "1-recovery-left", "answer": "absent"}]})
    assert not changed and any("skipped" in w for w in warn)


def test_page_is_self_contained(tmp_path):
    rv = {"course": "Test Golf Course", "slug": "test", "tee_set": "Blue", "built": "2026-10-17T00:00Z",
          "counts": {"red": 1, "amber": 0, "green": 1}, "imagery": {"date": "2023-09-02"}, "settings": {"n": 1500},
          "holes": {"1": {"par": 4, "base": {"pick": "Driver", "aim": -2.5}}},
          "items": [{"id": "1-tee", "hole": "1", "type": "tee", "severity": "red", "question": "Is the Blue tee here?",
                     "detail": "", "options": [{"answer": "confirm", "label": "Looks right", "outcome": None, "text": "No change."}]},
                    {"id": "1-x", "hole": "1", "type": "hazard", "severity": "green", "question": "q", "crop": {"img": "data:"},
                     "options": []}]}
    out = RP.build(rv, str(tmp_path / "index.html"))
    html = open(out).read()
    assert "/*__DATA__*/null" not in html and "fetch(" not in html and "XMLHttpRequest" not in html
    data = json.loads(html.split("const D = ")[1].split(";\nconst KEY")[0])
    assert data["items"][1].get("crop") is None and data["items"][0]["id"] == "1-tee"
    assert "<title>Test Pre-Round Check</title>" in html
