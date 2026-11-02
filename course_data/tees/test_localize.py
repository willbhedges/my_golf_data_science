"""Synthetic tests for the tee-set localizer v2 (python -m pytest -q course_data/tees/test_localize.py)."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import localize as LZ  # noqa: E402
from test_place_tee import F, box, ll, straight_hole  # noqa: E402


def d_green(r, length=400):
    x, y = F.fwd(r["lat"], r["lon"])
    return math.hypot(x, y - length)


def cand(cx, cy, source, p=None, tid=None, w=10, h=20):
    b = box(cx, cy, w=w, h=h, tid=tid)
    return dict(b, source=source, p=LZ.SOURCE_P.get(source, 0.7) if p is None else p)


def test_merge_osm_and_detections_into_one_pad():
    c = [cand(0, 0, "osm", tid="o1"), cand(2, 1, "segment", p=0.7, tid="s1"), cand(1, -1, "lidar", tid="l1"),
         cand(0, 60, "segment", p=0.7, tid="s2")]
    m = LZ.merge_candidates(c)
    assert len(m) == 2
    big = next(x for x in m if x["id"] == "o1")
    assert set(big["sources"]) == {"osm", "segment", "lidar"} and big["p"] > 0.99
    assert next(x for x in m if x["id"] == "s2")["p"] == 0.7


def test_two_osm_boxes_never_merge():
    m = LZ.merge_candidates([cand(0, 0, "osm", tid="a"), cand(0, 5, "osm", tid="b")])
    assert len(m) == 2


def test_sets_back_to_front_with_uncertainty():
    line = straight_hole(400)
    pads = LZ.merge_candidates([cand(0, -30, "osm", tid="gold"), cand(2, 0, "osm", tid="black"),
                                cand(-3, 40, "osm", tid="white"), cand(0, 90, "osm", tid="rust")])
    out = LZ.localize_hole(line, None, pads, (), {"Gold": 430, "Black": 400, "White": 360, "Rust": 310})
    assert [out[s]["tee_id"] for s in ("Gold", "Black", "White", "Rust")] == ["gold", "black", "white", "rust"]
    for s, y in (("Gold", 430), ("Black", 400), ("White", 360), ("Rust", 310)):
        assert abs(d_green(out[s]) - y) < 1.5
        assert out[s]["order_ok"] and out[s]["p_assign"] > 0.9 and 0 < out[s]["sigma_yd"] < 8


def test_detected_pad_beats_walkback_and_is_found_without_osm():
    line = straight_hole(400)
    pads = LZ.merge_candidates([cand(12, -8, "segment", p=0.8, tid="seg")])
    out = LZ.localize_hole(line, None, pads, (), {"Back": 405})
    assert out["Back"]["tee_id"] == "seg" and out["Back"]["method"] == "segment_pad"
    assert abs(d_green(out["Back"]) - 405) < 2


def test_no_pad_walks_back_with_large_sigma():
    out = LZ.localize_hole(straight_hole(400), None, [], (), {"Back": 450})
    assert out["Back"]["method"] == "walkback" and out["Back"]["sigma_yd"] >= 10
    assert abs(d_green(out["Back"]) - 450) < 1


def test_ambiguous_pads_raise_sigma_and_list_alternatives():
    line = straight_hole(400)
    pads = LZ.merge_candidates([cand(-20, 0, "lidar", tid="L"), cand(20, 0, "lidar", tid="R")])
    out = LZ.localize_hole(line, None, pads, (), {"Back": 400})
    r = out["Back"]
    assert r["p_assign"] < 0.7 and r["sigma_lat_yd"] > 10
    assert {a["tee_id"] for a in r["alternatives"][:2]} == {"L", "R"}


def test_localize_course_shape():
    lines = {"1": straight_hole(400)}
    pads = LZ.gather(osm_tees=[box(0, 0, tid="b")])
    res = LZ.positions(lines, [], {"1": {"Black": 400}}, pads)
    t = res["holes"]["1"]["tees"]["Black"]
    assert res["schema"] == "tees/positions" and {"lat", "lon", "method", "sigma_yd", "p_assign"} <= set(t)
    assert t["tee_id"] == "b" and t["localizer"] == LZ.VERSION
    assert ll(0, 0)  # frame helper sanity


def test_osm_box_within_card_tolerance_beats_exact_lidar_pad():
    """Library QA: a set's own OSM box within card_tol_yd of the card wins over an unmapped pad that fits exactly."""
    line = straight_hole(400)
    pads = LZ.merge_candidates([cand(0, 12, "osm", tid="box", w=10, h=6), cand(25, 0, "lidar", tid="pad", w=4, h=4)])
    out = LZ.localize_hole(line, None, pads, (), {"Back": 400})
    assert out["Back"]["tee_id"] == "box" and out["Back"]["error_yd"] <= 10
    out = LZ.localize_hole(line, None, pads, (), {"Back": 400}, params=dict(osm_tol_w=1.0))
    assert out["Back"]["tee_id"] == "pad"


def test_card_beyond_the_box_leaves_it_along_the_axis():
    """ERROR_BUDGET.md tees: an OSM box drawn short of the back tee. Card 15 yds behind the box's back edge -> the
    point leaves the box by 15 - beyond_free_yd; a gap within beyond_free_yd stays clamped to the box."""
    line = straight_hole(400)
    pads = LZ.merge_candidates([cand(0, 0, "osm", tid="box", w=10, h=10)])     # box spans 395..405 yds
    far = LZ.localize_hole(line, None, pads, (), {"Back": 420})["Back"]
    assert far["tee_id"] == "box"
    assert abs(d_green(far) - (420 - LZ.PARAMS["beyond_free_yd"])) < 1.0
    near = LZ.localize_hole(line, None, pads, (), {"Back": 408})["Back"]
    assert abs(d_green(near) - 405) < 1.0
    old = LZ.localize_hole(line, None, pads, (), {"Back": 420}, params=dict(beyond_max_yd=0.0))["Back"]
    assert abs(d_green(old) - 405) < 1.0


def test_tagged_box_point_at_card_yardage_not_centroid():
    line = straight_hole(400)
    boxes = [box(0, 0, w=10, h=20, tid="t1"), box(0, -60, w=10, h=10, tid="t2")]      # 390..410 and 455..465
    lat, lon, tid, dist = LZ.tagged_point(line, None, boxes, 407)
    assert tid == "t1" and abs(d_green(dict(lat=lat, lon=lon)) - 407) < 1.0 and abs(dist - 407) < 1.0
    lat, lon, tid, dist = LZ.tagged_point(line, None, boxes, 475)           # nearest-to-card box, 10 beyond its back
    assert tid == "t2" and abs(dist - (475 - LZ.PARAMS["beyond_free_yd"])) < 1.0
    assert LZ.tagged_point(line, None, boxes, None) is None


def test_tag_far_off_card_loses_to_untagged_box_on_card():
    """sycamore_ridge 1: the black tag sits two boxes forward (42 yds short); an untagged box fits the card."""
    line = straight_hole(400)
    tagged = [box(0, 30, w=10, h=10, tid="tag")]                     # 365..375 from the green
    on_card = [box(0, 0, w=10, h=10, tid="u1"), box(0, 60, w=10, h=10, tid="u2")]   # 395..405, 335..345
    lat, lon, tid, dist, how = LZ.card_checked_point(line, None, tagged, on_card, 407)
    assert (tid, how) == ("u1", "card_box") and abs(dist - 405) < 1.0      # 2 yds beyond the box: clamped to its back
    # the untagged box must itself fit the card (within untagged_card_yd), else the tag stays
    lat, lon, tid, dist, how = LZ.card_checked_point(line, None, tagged, [box(0, 0, w=10, h=10, tid="u")], 413)
    assert (tid, how) == ("tag", "tagged")
    # a tag within tag_off_card_yd of the card keeps its box even with a perfect untagged box
    lat, lon, tid, dist, how = LZ.card_checked_point(line, None, [box(0, 15, w=10, h=10, tid="tag")], on_card, 400)
    assert (tid, how) == ("tag", "tagged")
    assert LZ.card_checked_point(line, None, tagged, [], 407)[2:] == LZ.tagged_point(line, None, tagged, 407)[2:] + ("tagged",)
