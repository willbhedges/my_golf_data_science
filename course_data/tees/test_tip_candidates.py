"""Offline tests for tip_candidates.py and the cardless extra_boxes hook (synthetic geometry)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cardless as CL  # noqa: E402
import tip_candidates as TC  # noqa: E402
from test_cardless import box, straight_hole  # noqa: E402


def test_extra_box_extends_back():
    h = straight_hole(1, 0, 400)
    osm = [dict(id="a", coords=box(0, 380, 395))]
    b0 = CL.tee_complexes([h], osm)[0]
    b1 = CL.tee_complexes([h], osm, extra_boxes=[[dict(id="tip", coords=box(0, 415, 425), source="tip:lidar")]])[0]
    assert len(b1) == len(b0) + 1 and b1[0]["source"] == "tip:lidar" and b1[0]["d_back"] > 420


def test_candidate_rows_behind_only():
    h = straight_hole(1, 0, 400)
    osm = [dict(id="a", coords=box(0, 380, 395))]
    cands = [dict(id="behind", coords=box(0, 410, 420), source="lidar", p=None, area=200),
             dict(id="front", coords=box(0, 340, 350), source="scene", p=0.9, area=200)]
    (top, rows), = TC.candidate_rows([h], osm, cands)
    assert abs(top - 395) < 1 and [r["tee"]["id"] for r in rows] == ["behind"]
    assert len(rows[0]["x"]) == len(TC.FEATURES)
    extra, _ = TC.select_tips([h], osm, cands, model=dict(w=[50.0] + [0.0] * (len(TC.FEATURES) - 1), thr=0.5))
    assert extra[0] and extra[0][0]["source"] == "tip:lidar"
