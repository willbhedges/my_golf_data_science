"""Offline unit tests for tees/cardless.py (synthetic geometry, no data files)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardless as CL  # noqa: E402
import eval_cardless as E  # noqa: E402

LAT0, LON0 = 40.0, -90.0
YD = 0.9144
DLAT = 1.0 / 111320.0 * YD                     # degrees per yard north
DLON = DLAT / math.cos(math.radians(LAT0))


def ll(x, y):
    """(x east, y north) yards -> (lat, lon)."""
    return (LAT0 + y * DLAT, LON0 + x * DLON)


def box(x0, y_front, y_back, w=8):
    return [ll(x0 - w, y_front), ll(x0 + w, y_front), ll(x0 + w, y_back), ll(x0 - w, y_back), ll(x0 - w, y_front)]


def straight_hole(ref, x0, length):
    """Hole played north -> south: tee at y = length, green centre at y = 0."""
    return dict(ref=ref, line=[ll(x0, length), ll(x0, 0)], green=ll(x0, 0), green_r_yd=15)


def test_measure_and_slots():
    h = straight_hole(1, 0, 400)
    bx = CL.measure_boxes(h, [dict(id="a", coords=box(0, 395, 405)), dict(id="b", coords=box(0, 340, 380)),
                              dict(id="c", coords=box(12, 397, 403))])
    assert len(bx) == 2                          # a and c (side by side) merge
    assert abs(bx[0]["d_back"] - 405) < 1 and abs(bx[1]["len"] - 40) < 1
    sl = CL.slots(bx, dict(long_yd=30, slot_f=0.25, short_a=0.5))
    assert len(sl) == 3 and abs(sl[0] - 400) < 1 and abs(sl[1] - 370) < 1 and abs(sl[2] - 350) < 1


def test_dogleg_measured_along_line():
    h = dict(ref=1, line=[ll(0, 300), ll(0, 100), ll(150, 100)], green=ll(150, 100))
    bx = CL.measure_boxes(h, [dict(id="a", coords=box(0, 298, 302, w=3))])
    assert abs(bx[0]["d_centroid"] - 350) < 2   # 200 down + 150 across, not the 250 straight line


def test_hole_dp_shares_and_orders():
    r = [1.0, 0.93, 0.86, 0.78]
    P = dict(CL.PARAMS, off_cost=1000.0)
    _, ys = CL._hole_dp([(400.0, 400.0), (340.0, 340.0)], r, 400.0, P)
    assert ys == sorted(ys, reverse=True) and ys[0] == 400.0 and set(ys) <= {400.0, 340.0}
    P = dict(CL.PARAMS, off_cost=0.0)
    _, ys = CL._hole_dp([(400.0, 400.0)], r, 400.0, P)
    assert abs(ys[3] - 312) < 1                  # forward set off the box, at r * back
    P = dict(CL.PARAMS, off_cost=1000.0)
    _, ys = CL._hole_dp([(380.0, 400.0), (300.0, 330.0)], r, 400.0, P)
    assert ys[0] == 400.0 and abs(ys[1] - 380.0) < 1e-6 and 300 <= ys[2] <= 330 and ys[3] <= ys[2]


def test_par_dp_respects_course_prior():
    probs = [[0.1, 0.8, 0.1]] * 18
    probs[0] = probs[1] = probs[2] = probs[3] = [0.9, 0.1, 0.0]
    probs[4] = probs[5] = probs[6] = [0.0, 0.2, 0.8]
    probs[7] = [0.0, 0.55, 0.45]
    pars = CL.infer_pars(probs, dict(par_prior=None))
    assert pars[:4] == [3, 3, 3, 3] and pars[4:7] == [5, 5, 5]
    assert 70 <= sum(pars) <= 72


def test_infer_card_end_to_end():
    lengths = [400, 180, 520, 380, 420, 160, 540, 350, 410] * 2
    holes, tees = [], []
    for i, L in enumerate(lengths):
        x0 = i * 200.0
        holes.append(straight_hole(i + 1, x0, L))
        for k, f in enumerate((1.0, 0.93, 0.85)):          # three boxes per hole
            y = L * f
            tees.append(dict(id=f"t{i}_{k}", coords=box(x0, y - 4, y + 4)))
    card = CL.infer_card(holes, tees, params=dict(line_start=False, second_mode="dp"), S=3)
    sets = list(card["tee_sets"].values())
    assert list(card["tee_sets"]) == ["Back", "2nd", "3rd"]
    # each set stands 0.9 of the way back in its 8-yd box (cards measure from near the back edge): +3.2 yds
    assert all(abs(a - (b + 3.2)) <= 1.5 for a, b in zip(sets[0]["yards"], lengths))
    assert all(abs(a - (0.93 * b + 3.2)) <= 1.5 for a, b in zip(sets[1]["yards"], lengths))   # v1: the DP's 2nd set
    assert card["par"][:3] == [4, 3, 5]
    assert sets[0]["total"] > sets[1]["total"] > sets[2]["total"]


def test_clean_sets_drops_duplicates_and_combos():
    card = dict(tee_sets={"Blue": dict(yards=[400, 200, 500]), "Web": dict(yards=[400, 180, 500]),
                          "White": dict(yards=[370, 180, 470]), "Blue2": dict(yards=[400, 200, 500]),
                          "Red": dict(yards=[300, 140, 420]), "Kids": dict(yards=[100, 60, 150])})
    names = [n for n, _ in E.clean_sets(card, 3)]
    assert names == ["Blue", "White", "Red"]


def test_match_sets():
    pairs = E.match_sets([[400] * 18, [300] * 18], [[410] * 18, [370] * 18, [300] * 18])
    assert pairs == [(0, 0), (1, 2)]


# ----------------------------------------------------------------------------- v2: box assignment, hybrid, 2nd set
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures_cardless_backbox.json")


def test_far_box_nearer_another_start_is_reassigned():
    # hole 1 north -> south from y=400 at x=0; hole 2 starts at (60, 520). A box at (20, 500) is 100 behind hole 1's
    # start but nearer hole 2's start: it is hole 2's box.
    h1 = straight_hole(1, 0, 400)
    h2 = dict(ref=2, line=[ll(60, 520), ll(60, 900)], green=ll(60, 900), green_r_yd=15)
    lines = {"1#0": [tuple(p) for p in h1["line"]], "2#1": [tuple(p) for p in h2["line"]]}
    t = dict(id="far", coords=box(20, 496, 504, w=4), source="osm")
    near = dict(id="near", coords=box(0, 396, 404, w=4), source="osm")
    out = CL.reassign_far_boxes(lines, {"1#0": [t, near], "2#1": []})
    assert [b["id"] for b in out["1#0"]] == ["near"]
    assert [b["id"] for b in out["2#1"]] == ["far"]
    out = CL.reassign_far_boxes(lines, {"1#0": [dict(t, coords=box(0, 446, 454, w=4))], "2#1": []})
    assert len(out["1#0"]) == 1                              # far behind but nearest its own start: stays


def test_anchor_boxes_and_second_set():
    bx = [dict(d_front=440, d_back=450, source="osm"), dict(d_front=400, d_back=410, source="osm"),
          dict(d_front=405, d_back=415, source="lidar"), dict(d_front=360, d_back=372, source="osm")]
    kept = CL.anchor_boxes(bx, 400.0, dict(anchor_behind_yd=45.0, anchor_pad_behind_yd=10.0))
    assert [b["d_back"] for b in kept] == [410, 372]          # 50 behind (box) and 15 behind (pad) dropped
    model = dict(gap2=dict(bw=50, par={"4": 20}, bins={"4:8": 22}))
    assert CL.gap2(4, 410, model) == 22 and CL.gap2(4, 300, model) == 20
    # target 410 - 22 = 388: a box at 405-410 is 17 off (> second_snap 15): stays at the target
    assert CL.second_set(410.0, 4, [dict(d_front=405, d_back=410)], model) == 388
    # a box at 372-380 is 8 off: snapped to its back edge
    assert CL.second_set(410.0, 4, [dict(d_front=405, d_back=410), dict(d_front=372, d_back=380)], model) == 380


def test_cardblind_backbox_cases_fixed():
    """The five card-blind holes where v1 put Back 47-112 yds behind the OSM way's start (platform/CARDBLIND.md):
    hot_springs_arlington 5 / 10, pine_dunes 18, spirit_hollow 4, veenker 18."""
    import json
    with open(FIX) as fh:
        cases = json.load(fh)["cases"]
    assert len(cases) == 5
    for c in cases:
        holes = [dict(h, line=[tuple(p) for p in h["line"]], green=tuple(h["green"])) for h in c["holes"]]
        i = [h["ref"] for h in holes].index(c["hole"])
        v1 = CL.infer_card(holes, c["tees"], c["pads"], params=E.V1_PARAMS)
        hy = CL.infer_card(holes, c["tees"], c["pads"], anchored=True)
        assert v1["tee_sets"]["Back"]["yards"][i] > c["ref_back_yd"] + 30, c["slug"]
        assert abs(hy["tee_sets"]["Back"]["yards"][i] - c["ref_back_yd"]) <= 12, (c["slug"], c["hole"])
        assert hy["tee_sets"]["2nd"]["yards"][i] < hy["tee_sets"]["Back"]["yards"][i]
