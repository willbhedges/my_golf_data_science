"""Synthetic tests for v2_treeline_handcal (python -m pytest -q course_data/vision_any/test_treeline_handcal.py)."""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import v2_treeline_handcal as H  # noqa: E402


def test_tree_masks_buffer_grows_and_erodes():
    c = np.zeros((60, 60), bool)
    c[20:40, 20:40] = True                                   # 400 m2 clump on a 1 m grid
    m = H.tree_masks(c, 1.0)
    assert m[-1].sum() < m[0].sum() == 400 < m[1].sum() < m[3].sum()


def _per(missing, extra, inter=100.0, edge=10.0):
    return [dict(ref="1", missing=missing, extra=extra, inter=inter, union=inter + missing + extra, edge=edge)]


def test_agg_bias_sign_and_loco_picks_the_other_courses_best():
    a = H.agg(_per(50, 10))
    assert a["bias_yd"] == -4.0 and a["iou"] == round(100 / 160, 3)
    keys = ["2.5_-1", "2.5_1", "2.5_3"]
    R = {c: {"2.5_-1": _per(60, 0), "2.5_1": _per(10, 10), "2.5_3": _per(0, 60)} for c in ("a", "b", "c")}
    R["c"]["2.5_3"] = _per(0, 0)                              # c alone prefers k 3; held out, it gets k 1
    loco, best = H.select(R, list(R))
    assert loco["c"]["chosen"] == "2.5_1" and loco["a"]["chosen"] == "2.5_1" and best == "2.5_1"
    assert set(keys) == set(R["a"])
