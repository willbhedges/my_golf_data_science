"""route_conf: the shipped model scores a paired bench course and picks one of the two routings."""
import glob
import gzip
import json
import os

import pytest

import route_conf as RC

ART = os.path.join(os.path.dirname(os.path.dirname(RC.HERE)), "research", "artifacts", "pair_v3", "44817755394", "pair-0")


def _course(arm, i=0):
    f = glob.glob(os.path.join(ART, "bench_%s.json.gz" % arm))
    if not f or not os.path.exists(RC.MODEL):
        pytest.skip("no paired artifacts / model")
    cs = [c for c in json.load(gzip.open(f[0], "rt"))["courses"] if "hole_ok" in c]
    return cs[i]


def test_pick_scores_every_hole_and_keeps_one_routing():
    a = _course("A")
    b = next(c for c in [_course("B", i) for i in range(3)] if c["slug"] == a["slug"])
    pk = RC.pick(a, b)
    refs = {h["ref"] for h in (b if pk["use"] == "b" else a)["route"]["hole_features"]}
    assert pk["use"] in ("a", "b") and set(pk["p"]) == refs
    assert all(0.0 <= v <= 1.0 for v in pk["p"].values()) and 0.0 <= pk["agree"] <= 1.0
    assert (pk["sum_b"] > pk["sum_a"] + RC.PICK_MARGIN) == (pk["use"] == "b")


def test_a_hole_the_other_routing_puts_elsewhere_scores_lower():
    a = _course("A")
    same = RC.score(a, a)
    b = json.loads(json.dumps(a))
    ref = max(same, key=same.get)
    co = b["lines"][ref]["co"]
    b["lines"][ref]["co"] = co[:-1] + [[co[-1][0] + 0.004, co[-1][1] + 0.004]]      # the green about 500 yds away
    assert RC.score(a, b)[ref] < same[ref] - 0.2


def test_single_model_scores_a_routing_alone():
    a = _course("A")
    p = RC.score(a)
    assert set(p) == {h["ref"] for h in a["route"]["hole_features"]} and all(0.0 <= v <= 1.0 for v in p.values())
