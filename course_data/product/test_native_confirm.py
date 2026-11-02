"""Tests for the golfer native-side confirm tap (product/native_confirm.py) and its apply_answers hook.

    python3 -m pytest -q course_data/product/test_native_confirm.py

Synthetic holes only (a straight corridor frame, a 30-yd fairway): no course data is read.
"""
import copy
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import native_confirm as NC  # noqa: E402

M = NC.M
TEE, AIM = [-95.3, 38.9], [-95.3, 38.9 + 250 * 0.9144 / 110574.0]   # due north, 250 yds


def _fj():
    fr = M.corridor_frame(TEE, AIM, 1.0)
    return dict(ref="1", par=4, tee_ll=TEE, aim_ll=AIM, frame=fr.to_json())


def _ring(fj, xy):
    return [[float(x), float(y)] for x, y in M.xy_to_ll(fj, xy)]


def _box(x0, x1, a0, a1):
    return [(x0, a0), (x1, a0), (x1, a1), (x0, a1)]


def _hole(fj, native=()):
    zs = [dict(lie="fairway", poly=_ring(fj, _box(-15, 15, 100, 430)), src="osm")]
    for x0, x1 in native:
        zs.append(dict(lie="native", poly=_ring(fj, _box(x0, x1, 150, 350)), src="agent:mapper"))
    return dict(ref="1", par=4, tee_ll=TEE, aim_ll=AIM, green_ll=AIM, zones_ll=zs)


def _native_xy(fj, h, src=None):
    out = []
    for z in h["zones_ll"]:
        if z["lie"] == "native" and (src is None or z.get("src") == src):
            out.append(M.ll_to_xy(fj, z["poly"]))
    return out


def test_answers_round_trip():
    for a in NC.ANSWERS:
        assert NC.answer_of(NC.sides_of(a)) == a
    assert NC.sides_of("both") == {"L": True, "R": True}
    with pytest.raises(ValueError):
        NC.sides_of("left-ish")


def test_native_left_beyond_10_yds_of_fairway():
    fj = _fj()
    h = _hole(fj)
    NC.apply_answer(h, {"frame": fj, "widths": {}}, "L")
    nat = _native_xy(fj, h, NC.SRC)
    assert nat, "native added"
    xy = np.vstack(nat)
    assert xy[:, 0].max() <= -15 - NC.MIN_BEYOND + 0.5          # beyond 10 yds of the fairway's left edge
    assert xy[:, 0].min() >= -NC.REACH - 0.5
    assert xy[:, 1].min() >= NC.A0 - 0.5 and xy[:, 1].max() <= NC.A1 + 0.5
    assert h["verification"]["native_sides"]["answer"] == "L"


def test_width_from_the_mappers_native_edge():
    fj = _fj()
    h = _hole(fj, native=[(-60, -33)])                          # mapper's native 18 yds off the fairway (left)
    assert NC.rough_width(fj, h, "L") == pytest.approx(18, abs=1.0)
    assert NC.rough_width(fj, h, "R") is None
    NC.apply_answer(h, {"frame": fj, "widths": {"L": NC.rough_width(fj, h, "L")}}, "both")
    L = np.vstack([p for p in _native_xy(fj, h, NC.SRC) if p[:, 0].mean() < 0])
    R = np.vstack([p for p in _native_xy(fj, h, NC.SRC) if p[:, 0].mean() > 0])
    assert L[:, 0].max() <= -15 - 18 + 0.5                      # left at the measured rough width
    assert R[:, 0].min() >= 15 + NC.MIN_BEYOND - 0.5            # right: the 10-yd default
    assert NC.beyond_width(40) == NC.MAX_BEYOND and NC.beyond_width(3) == NC.MIN_BEYOND


def test_none_removes_native_on_that_side_only():
    fj = _fj()
    h = _hole(fj, native=[(-60, -30), (25, 60)])
    d = NC.apply_answer(h, {"frame": fj, "widths": {}}, "L")    # native left, none right
    assert d["R"] < 0
    rest = _native_xy(fj, h)
    assert all(p[:, 0].max() <= 0.5 for p in rest)             # nothing native right of the tee line any more
    assert any(z.get("src") == "agent:mapper" for z in h["zones_ll"] if z["lie"] == "native")   # left kept
    h2 = _hole(fj, native=[(-60, -30), (25, 60)])
    NC.apply_answer(h2, {"frame": fj, "widths": {}}, "none")
    assert not _native_xy(fj, h2)


def test_side_prior_rules():
    assert NC.side_prior("native: edit 0") > 0.7
    assert NC.side_prior("none: woods") <= 0.1
    assert NC.side_prior("none: woods", other_native=True) <= 0.1            # woods stay unlikely
    assert NC.side_prior("none: smooth mown rough") == pytest.approx(0.25)
    assert NC.side_prior("none: smooth mown rough", other_native=True) >= 0.4   # one-sided verdict is suspect
    assert NC.side_prior("none: 2023 coarser beyond -40 (uncertain)") == pytest.approx(0.4)
    assert NC.side_prior(None, has_edit=True, edit_conf="high") == pytest.approx(0.9)
    assert NC.side_prior(None) == pytest.approx(0.3)


def test_priors_from_verdicts():
    fj = _fj()
    pk = dict(holes={"1": _hole(fj)})
    pri = NC.priors({"holes": {"1": {"long_grass": {"L": "native: edit 0", "R": "none: smooth mown rough"}}}},
                    None, {"1": fj}, pk)
    assert pri["1"]["L"]["p"] > 0.7 and pri["1"]["R"]["p"] >= 0.4
    s = sum(NC.state_p(pri["1"], a) for a in NC.ANSWERS)
    assert s == pytest.approx(1.0)


class FakeDecider:
    """Plan = Driver unless the hole has golfer/agent native on the left within the window -> 3-wood."""

    def __init__(self, fj):
        self.fj = fj
        self.calls = 0

    def __call__(self, pkgs):
        self.calls += 1
        out = {}
        for name, pk in pkgs.items():
            out[name] = {}
            for r, h in pk["holes"].items():
                left = any(p[:, 0].mean() < 0 for p in _native_xy(self.fj[r], h))
                out[name][r] = dict(pick="3-wood" if left and r != "3" else "Driver", aim=0.0, ev=4.0)
        self._p = out
        return out

    def regret(self, name, ref, plan):
        return 0.0 if plan["pick"] == self._p[name][ref]["pick"] else 0.08


def test_select_asks_only_where_the_plan_changes_and_caps():
    fj = _fj()
    frames = {r: dict(_fj(), ref=r) for r in ("1", "2", "3")}
    pk = dict(holes={r: dict(_hole(fj), ref=r) for r in frames})
    lg = {"1": {"L": "none: smooth mown rough (uncertain)", "R": "none: woods"},
          "2": {"L": "none: woods", "R": "none: woods"},
          "3": {"L": "none: smooth mown rough", "R": "none: smooth mown rough"}}
    pri = NC.priors({"holes": {r: {"long_grass": v} for r, v in lg.items()}}, None, frames, pk)
    D = FakeDecider(frames)
    qs = NC.select(pk, frames, pri, D, cap=1)
    by = {q["hole"]: q for q in qs}
    assert D.calls == 1                                      # every state of every hole in one batch
    assert not by["3"]["changes"]                            # left native never changes hole 3's plan
    assert by["1"]["value"] > by["2"]["value"] > 0           # the uncertain side is worth more than woods
    assert [q["hole"] for q in qs if q["asked"]] == ["1"]    # cap 1
    assert by["1"]["plans"]["L"].startswith("3-wood")
    items = NC.items_for_review(qs)
    assert len(items) == 1 and items[0]["type"] == "native" and items[0]["answers"] == list(NC.ANSWERS)


def test_apply_answers_hook():
    import apply_answers as AA
    fj = _fj()
    pkg = dict(tee_set="Blue", holes={"1": _hole(fj, native=[(25, 60)])})
    item = dict(id="native_1", type="native", hole="1", frame=fj["frame"], widths={"L": 10.0, "R": 10.0})
    review = dict(tee_set="Blue", items=[item], holes={"1": {}})
    out, changed, warn = AA.apply(pkg, review, {"answers": [{"id": "native_1", "answer": "L"}]}, log=lambda *a: None)
    assert changed == {"1": ["native_1"]}
    h = out["holes"]["1"]
    xs = [p[:, 0].mean() for p in _native_xy(fj, h)]
    assert xs and all(x < 0 for x in xs)
    assert pkg["holes"]["1"]["zones_ll"][-1]["src"] == "agent:mapper"     # input untouched
