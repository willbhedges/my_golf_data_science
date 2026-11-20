"""Fast path: the extra publish gate and the lie raster."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast
import importlib.util as _ilu
# fastpath/solve.py under its own module name: a plain `import solve` would register it as sys.modules["solve"] and
# shadow zero_tap/joint/solve.py, which route_scene imports as `solve` (pytest runs every platform test in one process)
_spec = _ilu.spec_from_file_location("fastpath_solve", os.path.join(os.path.dirname(os.path.abspath(__file__)), "solve.py"))
solve = sys.modules.get("fastpath_solve") or _ilu.module_from_spec(_spec)
sys.modules["fastpath_solve"] = solve
if not hasattr(solve, "raster_lie_at"):
    _spec.loader.exec_module(solve)


def hole(green, card, meas):
    return dict(green_ll=green, yards={"Blue": card}, tees={"Blue": dict(measured_yards=meas)})


def test_gate_blocks_a_shared_green_and_a_card_that_does_not_fit():
    ok = {str(i + 1): hole([-100 + i * 0.005, 40.0], 400, 398) for i in range(18)}
    assert fast.extra_gate(dict(tee_set="Blue", holes=ok)) == []
    dup = dict(ok, **{"12": hole([-100.00002, 40.0], 395, 395)})
    assert any("1 and 12 share a green" in r for r in fast.extra_gate(dict(tee_set="Blue", holes=dup)))
    one = dict(ok, **{"5": hole(ok["5"]["green_ll"], 350, 265)})          # one card error: shown, flagged elsewhere
    assert fast.extra_gate(dict(tee_set="Blue", holes=one)) == []
    three = dict(ok, **{k: hole(ok[k]["green_ll"], 400, 300) for k in ("9", "10", "11")})
    assert any("does not fit the map on 3 holes" in r for r in fast.extra_gate(dict(tee_set="Blue", holes=three)))


def test_lie_raster_matches_the_polygon_order():
    h = dict(zones=[("fairway", [(0, 0), (100, 0), (100, 300), (0, 300)]), ("water", [(40, 100), (60, 100), (60, 140), (40, 140)])])
    pts = np.array([[50, 50], [50, 120], [150, 50], [-5, 10], [99, 299]], float)
    assert list(solve.raster_lie_at(h, pts)) == ["fairway", "water", "rough", "rough", "fairway"]


def test_unnumbered_hole_lines_are_detected_only_when_refs_are_missing():
    import route_joint

    def way(ref=None):
        pr = {"golf": "hole"}
        if ref:
            pr["ref"] = ref
        return {"type": "Feature", "properties": pr, "geometry": {"type": "LineString", "coordinates": [[-100, 40], [-100, 40.003]]}}
    assert len(route_joint.unnumbered_lines({"features": [way() for _ in range(18)]}, 18)) == 18      # Brookhaven CC
    assert route_joint.unnumbered_lines({"features": [way(str(i + 1)) for i in range(18)]}, 18) is None  # numbered: OSM's own
    assert route_joint.unnumbered_lines({"features": [way() for _ in range(6)]}, 18) is None           # too few lines


def test_vintage_fallback_helpers(tmp_path):
    import fastscene as FS
    assert FS.hole_greens(dict(summary=dict(greens_hole=4))) == 4
    assert FS.hole_greens(dict(greens=[dict(kind="hole"), dict(kind="practice")])) == 1
    raw = tmp_path / "raw"
    raw.mkdir()
    card = dict(par=[4] * 9, tee_sets=dict(B=dict(yards=[350] * 9)))
    (raw / "scorecard_web.json").write_text(json.dumps(dict(cards=[dict(source="golfify", card=card)])))
    assert FS.package_holes(str(tmp_path)) == 9                   # the card production would pick
    assert FS.package_holes(str(tmp_path / "missing")) == 18
    assert FS.vintage_on() or os.environ.get(FS.VINTAGE_ENV) == "0"     # default on


def _fake_vintages(monkeypatch, tmp_path, counts, own=2023, cues=None):
    """fastscene.vintage_fallback on stubbed imagery: counts {year: hole greens} per single-vintage scene"""
    import numpy as np
    import fastscene as FS
    import fast_imagery as fim
    (tmp_path / "imagery").mkdir(exist_ok=True)
    (tmp_path / "imagery" / "georef.json").write_text(json.dumps(dict(imagery=dict(year=own) if own else {})))
    cur = {}

    class St:
        def __init__(s):
            s.a = dict(seg=np.zeros((len(FS.SEG_ORDER), 4, 4), np.uint8))
            s.meta = dict(grid=dict(crs="EPSG:32616", transform=[1, 0, 0, 0, -1, 0]))

    def unet_probs(pkg_dir, st, uw, keep, naip=None, **k):
        cur["y"] = (own or 0) if naip is None else int(naip[0].split(os.sep)[-2])
        return np.zeros((6, 4, 4), np.float32)

    def perceive(st, **k):
        n = counts[cur["y"]]
        return dict(summary=dict(greens_hole=n), greens=[dict(kind="hole", centroid=[-90, 40])] * n), None
    monkeypatch.setattr(FS, "grid_stack", lambda *a, **k: St())
    monkeypatch.setattr(FS, "unet_probs", unet_probs)
    monkeypatch.setattr(FS, "perceive", perceive)
    monkeypatch.setattr(FS, "osm_negative_mask", lambda *a, **k: np.zeros((4, 4), bool))
    monkeypatch.setattr(FS, "course_mask", lambda *a, **k: np.ones((4, 4), bool))
    monkeypatch.setattr(fim, "fetch_years", lambda img, k: sorted(y for y in counts if y and y != own))
    if cues is not None:
        monkeypatch.setattr(FS, "green_cues", cues)
    return FS


def test_vintage_fallback_review_cases(monkeypatch, tmp_path):
    import numpy as np
    dead = lambda *a: dict(turf=0.5, rough=0.1, rough_ring=0.5)          # noqa: E731
    keep = np.ones((4, 4), bool)
    # the newest flight wins: no "possibly closed" warning
    FS = _fake_vintages(monkeypatch, tmp_path, {2023: 12, 2021: 4, 2019: 3, 2017: 2}, cues=dead)
    sc = FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=3)), "w", keep, 18)[0]
    assert sc["fastscene_vintage"]["chosen"] == 2023 and not sc.get("warnings")
    # one or two greens more than the mean is not enough (margin 3 on 18 holes)
    FS = _fake_vintages(monkeypatch, tmp_path, {2023: 5, 2021: 4, 2019: 3, 2017: 2}, cues=dead)
    assert FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=3)), "w", keep, 18) is None
    # an old winner with dead recent turf warns; a cue failure keeps the vintage without the warning
    FS = _fake_vintages(monkeypatch, tmp_path, {2023: 2, 2021: 3, 2019: 4, 2017: 15}, cues=dead)
    sc = FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=2)), "w", keep, 18)[0]
    assert sc["fastscene_vintage"]["chosen"] == 2017 and FS.OUTDATED_WARNING in sc["warnings"][0]

    def boom(*a):
        raise KeyError("crs")
    FS = _fake_vintages(monkeypatch, tmp_path, {2023: 2, 2021: 3, 2019: 4, 2017: 15}, cues=boom)
    sc = FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=2)), "w", keep, 18)[0]
    assert sc["fastscene_vintage"]["chosen"] == 2017 and not sc.get("warnings") and "cue_err" in sc["fastscene_vintage"]
    # missing cues are no evidence of dead turf
    FS = _fake_vintages(monkeypatch, tmp_path, {2023: 2, 2021: 3, 2019: 4, 2017: 15}, cues=lambda *a: {})
    sc = FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=2)), "w", keep, 18)[0]
    assert not sc.get("warnings")
    # unknown package year: no warning
    FS = _fake_vintages(monkeypatch, tmp_path, {0: 12, 2021: 4, 2019: 3, 2017: 2}, own=None, cues=dead)
    sc = FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=3)), "w", keep, 18)[0]
    assert not sc.get("warnings")
    # counts above n are no better than n: the newer flight that reaches n wins
    FS = _fake_vintages(monkeypatch, tmp_path, {2023: 18, 2021: 25, 2019: 3, 2017: 2}, cues=dead)
    sc = FS.vintage_fallback(str(tmp_path), dict(summary=dict(greens_hole=3)), "w", keep, 18)[0]
    assert sc["fastscene_vintage"]["chosen"] == 2023


def test_package_holes_nine_dup(tmp_path):
    import fastscene as FS
    raw = tmp_path / "raw"
    raw.mkdir()
    y9 = [350, 510, 160, 380, 400, 170, 520, 390, 410]
    card = dict(par=[4] * 18, tee_sets=dict(B=dict(yards=y9 + [v + 5 for v in y9])))   # the nine twice
    (raw / "scorecard_web.json").write_text(json.dumps(dict(cards=[dict(source="golfify", card=card)])))
    few = dict(greens=[dict(kind="hole", p_hole=0.9)] * 9)
    many = dict(greens=[dict(kind="hole", p_hole=0.9)] * 18)
    assert FS.package_holes(str(tmp_path), few) == 9 and FS.package_holes(str(tmp_path), many) == 18


def test_fastpath_solve_does_not_shadow_the_joint_solver():
    # zero_tap/joint/solve.py is imported as `solve` by route_scene; fastpath/solve.py must not take that name
    m = sys.modules.get("solve")
    assert m is None or not hasattr(m, "raster_lie_at")
