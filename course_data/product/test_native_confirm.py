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


def _along_cover(polys, side):
    """Along slices (10 yds) where the golfer band has any area on that side."""
    from shapely.geometry import box
    from shapely.ops import unary_union
    g = unary_union([M._poly(p) for p in polys]).buffer(0)
    out = set()
    for a in range(int(NC.A0), int(NC.A1), 10):
        bx = box(-NC.REACH, a, 0, a + 10) if side == "L" else box(0, a, NC.REACH, a + 10)
        if g.intersection(bx).area > 5:
            out.add(a)
    return out


def test_yes_well_out_keeps_mapper_islands_and_fills_only_bare_stretches():
    """Mariah Hills: native as islands 25+ yds out. "Yes, well out" keeps them and adds the band only where
    nothing is drawn within ISLAND_NEAR yds of the fairway on that side; a plain "yes" bands the whole side."""
    fj = _fj()
    h = _hole(fj)
    h["zones_ll"].append(dict(lie="native", poly=_ring(fj, _box(-60, -42, 200, 280)), src="agent:mapper"))   # 27 yds out
    h0 = copy.deepcopy(h)
    NC.apply_answer(h, {"frame": fj, "widths": {}}, "L", out="L")
    gol = _native_xy(fj, h, NC.SRC)
    cov = _along_cover(gol, "L")
    assert not cov & set(range(200, 280, 10))                  # no 10-yd band beside the island
    assert {130, 150, 290, 380} <= cov                         # bare stretches still get the band
    assert any(z.get("src") == "agent:mapper" for z in h["zones_ll"] if z["lie"] == "native")   # island kept
    assert h["verification"]["native_sides"]["out"] == "L"
    NC.apply_answer(h0, {"frame": fj, "widths": {}}, "L")      # plain yes: the band beside the island too
    assert set(range(200, 280, 10)) <= _along_cover(_native_xy(fj, h0, NC.SRC), "L")
    assert NC.island_sides("R") == {"L": False, "R": True} and NC.island_sides(None) == {"L": False, "R": False}
    assert NC.island_sides(None, mode="always") == {"L": True, "R": True}


def test_far_native_does_not_block_the_band():
    fj = _fj()
    h = _hole(fj)
    h["zones_ll"].append(dict(lie="native", poly=_ring(fj, _box(-65, -58, 150, 350)), src="agent:mapper"))   # 43+ yds out
    NC.apply_answer(h, {"frame": fj, "widths": {}}, "L", out="L")
    cov = _along_cover(_native_xy(fj, h, NC.SRC), "L")
    assert set(range(150, 350, 10)) <= cov


def test_right_island_does_not_block_left():
    fj = _fj()
    h = _hole(fj)
    h["zones_ll"].append(dict(lie="native", poly=_ring(fj, _box(42, 60, 150, 350)), src="agent:mapper"))
    NC.apply_answer(h, {"frame": fj, "widths": {}}, "both", out="both")
    gol = _native_xy(fj, h, NC.SRC)
    assert set(range(150, 350, 10)) <= _along_cover(gol, "L")
    assert not _along_cover(gol, "R") & set(range(150, 350, 10))


def test_bare_stretches_helper():
    fj = _fj()
    h = _hole(fj)
    h["zones_ll"].append(dict(lie="native", poly=_ring(fj, _box(-60, -42, 200, 280)), src="agent:mapper"))
    cov = NC.covered_along(fj, h, "L")
    assert [c[0] for c in cov] == list(range(200, 280, 10))
    assert all(c[2] == pytest.approx(42, abs=0.5) for c in cov)          # the island's inner edge
    assert NC.covered_along(fj, h, "R") == []


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


def test_reapply_redoes_native_after_rebuild():
    import apply_answers as AA
    fj = _fj()
    pkg = dict(tee_set="Blue", holes={"1": _hole(fj, native=[(25, 60)])})
    item = dict(id="native_1", type="native", hole="1", frame=fj["frame"], widths={"L": 10.0, "R": 10.0})
    review = dict(tee_set="Blue", items=[item], holes={"1": {}})
    corr = []
    AA.apply(pkg, review, {"answers": [{"id": "native_1", "answer": "L"}]}, log=lambda *a: None, corrections_out=corr)
    assert corr and corr[0]["kind"] == "native" and corr[0]["answer"] == "L"
    rebuilt = dict(tee_set="Blue", holes={"1": _hole(fj, native=[(25, 60)])})      # a fresh package build
    r = AA.reapply(rebuilt, {"items": corr}, log=lambda *a: None)
    assert r["applied"] == 1 and not r["skipped"]
    xs = [p[:, 0].mean() for p in _native_xy(fj, rebuilt["holes"]["1"])]
    assert xs and all(x < 0 for x in xs)                                           # right native gone, left added
    assert rebuilt["holes"]["1"]["verification"]["native_sides"]["answer"] == "L"


def test_verify_native_review_items_have_four_answers():
    import verify as V
    frames = {r: dict(_fj(), ref=r) for r in ("1", "2")}
    fj = frames["1"]
    pk = dict(holes={r: dict(_hole(fj), ref=r) for r in frames})
    lg = {"1": {"L": "none: smooth mown rough (uncertain)", "R": "none: woods"},
          "2": {"L": "none: woods", "R": "none: woods"}}
    pri = NC.priors({"holes": {r: {"long_grass": v} for r, v in lg.items()}}, None, frames, pk)
    items = V.native_review_items(pk, frames, pri, FakeDecider(frames), cap=4)
    assert [it["id"] for it in items] == ["native_1"]                  # woods-only hole 2: below MIN_VOI
    it = items[0]
    assert it["type"] == "native" and it["severity"] == "red"
    assert [o["answer"] for o in it["options"]] == ["L", "R", "both", "none"]
    assert [o["label"] for o in it["options"]] == ["Left", "Right", "Both", "None"]
    L = next(o for o in it["options"] if o["answer"] == "L")
    assert "3-wood" in L["text"] and L["outcome"]["club_changed"]
    N = next(o for o in it["options"] if o["answer"] == "none")
    assert N["text"].startswith("No change")
    import review_page
    d = review_page.page_data(dict(course="X", slug="x", tee_set="Blue", built="t", counts={}, holes={},
                                   items=items, settings={"n": 10}))
    assert d["items"][0]["options"][0]["answer"] == "L" and "frame" not in d["items"][0]


def _band_area(rects):
    return sum((a1 - a0) * abs(x1 - x0) for a0, a1, x0, x1 in rects or [])


def test_band_rects_follow_the_shapely_rule():
    fj = _fj()
    h = _hole(fj)
    h["zones_ll"].append(dict(lie="native", poly=_ring(fj, _box(-60, -42, 200, 280)), src="agent:mapper"))
    spec = NC.band_spec(fj, h, {})
    assert spec["near"]["L"][(200 - 130) // 10] == pytest.approx(42, abs=0.5) and not any(spec["near"]["R"])
    assert spec["fw"]["L"][5] == pytest.approx(15, abs=0.5) and spec["w"]["R"] == NC.MIN_BEYOND
    for out in (None, "L"):
        r = NC.band_rects(spec, "L", out)
        assert r["R"] is None and (out is None or all(not (200 <= a0 < 280) for a0, *_ in r["L"]))
        h2 = copy.deepcopy(h)
        NC.apply_answer(h2, {"frame": fj, "widths": {}}, "L", out)
        shp = sum(M._poly(p).area for p in _native_xy(fj, h2, NC.SRC))
        assert _band_area(r["L"]) == pytest.approx(shp, rel=0.1)
    assert NC.band_rects(spec, "none") == {"L": None, "R": None}


def native_band_fixture():
    """Specs + the Python answers for confirm_engine.js nativeBand (app/test_confirm.js parity)."""
    fj = _fj()
    cases = []
    for name, nat in (("bare", []), ("island_left", [(-60, -42, 200, 280)]), ("far_right", [(58, 65, 150, 350)]),
                      ("near_both", [(-40, -30, 150, 240), (28, 50, 300, 400)])):
        h = _hole(fj)
        for x0, x1, a0, a1 in nat:
            h["zones_ll"].append(dict(lie="native", poly=_ring(fj, _box(x0, x1, a0, a1)), src="agent:mapper"))
        spec = NC.band_spec(fj, h, {"L": 18.0} if name == "near_both" else {})
        cases.append(dict(name=name, spec=spec, rects={a: NC.band_rects(spec, a) for a in NC.ANSWERS},
                          out={o: {a: NC.band_rects(spec, a, o) for a in NC.ANSWERS} for o in ("L", "R", "both")}))
    return dict(schema="native_band_fixture/1", cases=cases)


def test_app_native_band_fixture_is_current():
    import json
    p = os.path.join(os.path.dirname(HERE), "app", "fixtures", "native_band.json")
    want = json.loads(json.dumps(native_band_fixture()))
    if os.environ.get("WRITE_FIXTURES"):
        with open(p, "w") as fh:
            json.dump(want, fh, indent=0)
    assert json.load(open(p)) == want, "regenerate: WRITE_FIXTURES=1 pytest -k native_band_fixture"
