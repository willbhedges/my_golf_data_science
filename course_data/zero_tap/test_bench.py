"""Scorer self-checks: the OSM truth written as a result is fully right; known corruptions get the right failure type.

  python -m pytest course_data/zero_tap/test_bench.py -q
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench as B  # noqa: E402


def _oracle(t):
    return dict(schema="zero_tap_result/1", slug=t["slug"], certain=True, confidence=1.0,
                holes=[dict(number=h["ref"], par=h["par"], green_ll=h["green_ll"], tee_ll=h["tee_ll"]) for h in t["holes"]])


def _t18():
    for r in B.courses("dev"):
        if r["kind"] == 18:
            return B.truth(r["slug"])


def test_oracle_right():
    t = _t18()
    s = B.score_course(_oracle(t), t)
    assert s["course_ok"] and s["number"] == 18 and s["primary"] is None


def test_nine_swap():
    t = _t18()
    r = _oracle(t)
    for h in r["holes"]:
        h["number"] = (h["number"] + 8) % 18 + 1
    s = B.score_course(r, t)
    assert s["primary"] == "nine_swap" and s["formed"] == 18 and s["number"] == 0


def test_start_hole():
    t = _t18()
    r = _oracle(t)
    for h in r["holes"]:
        h["number"] = h["number"] % 18 + 1
    assert B.score_course(r, t)["primary"] == "start_hole"


def test_pairing_and_par():
    t = _t18()
    r = _oracle(t)
    a, b = r["holes"][2], r["holes"][7]
    a["tee_ll"], b["tee_ll"] = b["tee_ll"], a["tee_ll"]
    s = B.score_course(r, t)
    assert s["primary"] == "pairing" and s["fails"]["pairing"] == 2
    r2 = _oracle(t)
    r2["holes"][0]["par"] = 9
    assert B.score_course(r2, t)["primary"] == "par"


def test_missing():
    t = _t18()
    r = _oracle(t)
    r["holes"] = r["holes"][:17]
    s = B.score_course(r, t)
    assert s["primary"] == "count" and not s["course_ok"]


def test_none():
    t = _t18()
    assert B.score_course(None, t)["primary"] == "no_result"
    assert B.score_course(copy.deepcopy(dict(error="x")), t)["primary"] == "no_result"
