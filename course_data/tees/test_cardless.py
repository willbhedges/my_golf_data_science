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
    card = CL.infer_card(holes, tees, params=dict(line_start=False), S=3)
    sets = list(card["tee_sets"].values())
    assert list(card["tee_sets"]) == ["Back", "2nd", "3rd"]
    # each set stands 0.9 of the way back in its 8-yd box (cards measure from near the back edge): +3.2 yds
    assert all(abs(a - (b + 3.2)) <= 1.5 for a, b in zip(sets[0]["yards"], lengths))
    assert all(abs(a - (0.93 * b + 3.2)) <= 1.5 for a, b in zip(sets[1]["yards"], lengths))
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
