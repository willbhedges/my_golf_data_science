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
    assert set(g) == {("recovery", "left"), ("recovery", "right")}       # vision and OSM are both asked about
    assert g[("recovery", "left")]["p_wrong"] == 0.4 and g[("recovery", "right")]["p_wrong"] == 0.15
    grp = g[("recovery", "left")]
    assert grp["idx"] == [1] and abs(grp["edge"] + 25) < 1 and grp["toward"] == (1.0, 0.0)
    moved = V.shifted(h, fr, [1], grp["toward"], 10.0)
    assert abs(V.to_yd(fr, moved[1]["poly"])[:, 0].max() + 15) < 0.5
    assert len(V.removed(h, [1])) == 2
    assert V.gap_sides(h, fr, {"aim": 0.0}) == []
    h2 = dict(h, zones_ll=h["zones_ll"][:1])
    assert [s for s, _ in V.gap_sides(h2, fr, {"aim": 0.0})] == ["left", "right"]
    h2["verification"] = {"open_left": True}
    h2["zones_ll"] = h["zones_ll"][:1]
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


def test_priors_fairway_cut():
    assert V.tee_prior({"confidence": 0.8}, 0) == pytest.approx(0.2)
    assert V.tee_prior({"confidence": 0.8}, 18) == pytest.approx(0.35)
    assert V.tee_prior({"confidence": 0.9, "method": "walkback"}, 0) == 0.5
    assert V.tee_prior({"confidence": 0.8, "verified": "golfer"}, 30) == 0.0
    h = hole()
    _, fr = V.hole_model(h, "Blue")
    sides, idx = V.fairway_sides(h, fr, {"aim": 0.0})
    assert set(sides) == {"left", "right"} and idx == [0] and abs(sides["left"]["edge"] + 18) < 0.5
    nz = V.fairway_moved(h, fr, idx, "left", 10.0, 0.0)          # 10 yds narrower on the left, inside the corridor
    xa = V.to_yd(fr, nz[0]["poly"])
    mid = (xa[:, 1] > 200) & (xa[:, 1] < 300) & (xa[:, 0] < 0)
    assert np.allclose(xa[mid, 0], -8, atol=0.5) and xa[:, 0].max() == pytest.approx(18, abs=0.5)
    cut = V.cut_polys(h, fr)
    assert cut and all(V.shapely_poly(c).is_valid for c in cut)
    total = sum(V.shapely_poly(c).area for c in cut)
    assert 1500 < total < 4500                                  # a 6-yd ring around the fairway, trees cut out


def _item(i, typ, prelim, er):
    return dict(id=f"{i}-{typ}", hole=str(i), type=typ, tested=True, prelim=prelim, exp_regret=er, max_d_ev=0.0)


def test_assign_severity_budget():
    items = [_item(1, "tee", "red", 0.02), _item(2, "tee", "red", 0.01), _item(3, "hazard", "red", 0.03),
             _item(4, "hazard", "red", 0.006), _item(5, "fairway", "red", 0.02), _item(6, "hazard", "red", 0.001),
             _item(7, "cut", "amber", 0.004), _item(8, "hazard", "amber", 0.0005), _item(9, "hazard", "red", 0.01)]
    b = V.assign_severity(items, red_cards=4)
    sev = {it["id"]: it["severity"] for it in items}
    # cards: tees (0.03), 3 (0.03), 5 (0.02), 9 (0.01) | 4 (0.006) over budget
    assert sev["1-tee"] == sev["2-tee"] == sev["3-hazard"] == sev["5-fairway"] == sev["9-hazard"] == "red"
    assert sev["4-hazard"] == "amber" and items[[i["id"] for i in items].index("4-hazard")]["over_budget"]
    assert sev["6-hazard"] == "green" and sev["7-cut"] == "amber" and sev["8-hazard"] == "green"   # ER floor 0.002
    assert b["red_cards"] == 4 and b["red_candidate_cards"] == 5


def test_corrections_survive_rebuild():
    h = hole()
    _, fr = V.hole_model(h, "Blue")
    pkg = {"tee_set": "Blue", "holes": {"1": h}}
    review = {"tee_set": "Blue", "built": "x", "holes": {"1": {"frame": fr.to_json(), "base": {"aim": 0}}},
              "items": [{"id": "1-tee", "hole": "1", "type": "tee"},
                        {"id": "1-recovery-left", "hole": "1", "type": "hazard", "zone_idx": [1],
                         "zone_fp": [[round(v, 7) for v in h["zones_ll"][1]["poly"][0]]], "toward": [1.0, 0.0]},
                        {"id": "1-gap-right", "hole": "1", "type": "gap", "side": "right",
                         "strip_xa": [[25, 200], [65, 200], [65, 330], [25, 330]]}]}
    corr = []
    new, _, _ = AA.apply(pkg, review, {"answers": [{"id": "1-tee", "answer": "moved", "dx": 0, "dy": -20},
                                                   {"id": "1-recovery-left", "answer": "absent"},
                                                   {"id": "1-gap-right", "answer": "present"}]}, corrections_out=corr)
    assert [c["kind"] for c in corr] == ["tee", "zones", "add"]
    rebuilt = copy.deepcopy(pkg)                          # a rebuild: same zones, slightly re-traced
    rebuilt["holes"]["1"]["zones_ll"][1]["poly"] = rect(-61, -24, 199, 321)
    rebuilt["holes"]["1"]["zones_ll"].insert(0, {"lie": "sand", "poly": rect(-5, 5, 330, 340), "src": "osm"})
    res = AA.reapply(rebuilt, {"items": corr}, log=lambda *a: None)
    rh = rebuilt["holes"]["1"]
    assert res["applied"] == 3 and not res["skipped"]
    assert [z["lie"] for z in rh["zones_ll"]] == ["sand", "fairway", "recovery", "recovery"]   # vision trees gone
    assert rh["zones_ll"][-1]["src"] == "golfer:added" and rh["tees"]["Blue"]["tee_ll"] == new["holes"]["1"]["tees"]["Blue"]["tee_ll"]
    AA.reapply(rebuilt, {"items": corr}, log=lambda *a: None)                     # idempotent for adds
    assert len(rebuilt["holes"]["1"]["zones_ll"]) == 4


def test_badges():
    pkg = {"holes": {"1": {}, "2": {"verification": {"2-tee": {"answer": "confirm"}}}, "3": {}}}
    rv = {"items": [{"id": "1-tee", "hole": "1", "severity": "red", "question": "Is the Blue tee here?",
                     "options": [{"samples": [{"text": "Hole 1: Driver -> 4-wood.", "outcome": {"regret": 0.05}}]}]},
                    {"id": "2-tee", "hole": "2", "severity": "red", "question": "q", "options": []}]}
    b = V.badges(pkg, rv)
    assert b["1"]["state"] == "unverified" and "4-wood" in b["1"]["line"]
    assert b["2"]["state"] == "checked" and b["3"]["state"] == "auto" and V.badges(pkg, None) == {}


def test_book_badges_in_notes_and_cover():
    import book
    book.set_badges({"1": {"state": "unverified", "symbol": "!", "line": "Unverified: Is the Blue tee here? If not, X."},
                     "2": {"state": "checked", "symbol": "o", "line": "Map checked by you before the round."}})
    try:
        r = {"pick": "Driver", "runner": "2-wood", "margin": 0.02, "aim": 0.0, "zone": [-5, 5], "tie": False,
             "clubs": {"Driver": {"share": {"fairway": 0.6}, "approach": 120.0}}}
        notes, _ = book.notes_and_aims({}, {}, {1: r, 2: r, 3: r}, {})
        assert notes[1].startswith("⚠ Unverified: Is the Blue tee here?")
        assert notes[2].startswith("◐ Map checked") and not notes[3].startswith(("⚠", "◐"))
        assert "unverified 1" in book.badge_line() and "checked by you 2" in book.badge_line()
    finally:
        book.set_badges({})
