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
    assert RC.score(a, b)[ref] < same[ref] - 0.1


def test_single_model_scores_a_routing_alone():
    a = _course("A")
    p = RC.score(a)
    assert set(p) == {h["ref"] for h in a["route"]["hole_features"]} and all(0.0 <= v <= 1.0 for v in p.values())


def test_card_corroboration_counts_other_sources_only():
    import route_conf as RC
    y = [400, 150, 520, 380, 410, 170, 390, 505, 360]
    card = dict(tee_sets={"Blue": dict(yards=y), "Red": dict(yards=[v - 60 for v in y])})
    same = dict(source="golfify", card=card)
    other = dict(source="opengolfapi", card=dict(tee_sets={"Back": dict(yards=[v + 5 for v in y])}))
    wrong = dict(source="allsquare", card=dict(tee_sets={"Back": dict(yards=y[::-1])}))
    assert RC.card_corroboration(card, [same]) == 0
    assert RC.card_corroboration(card, [same, dict(source="allsquare", card=card)]) == 1   # same numbers, other site
    assert RC.card_corroboration(card, [same, dict(source="golfify", card=card)]) == 0
    assert RC.card_corroboration(card, [same, other, wrong]) == 1
    assert RC.verified(dict(p_id={"1": 0.99, "2": 0.9}), card, [same, other]) == (["1"], 1)
    assert RC.verified(dict(p_id={"1": 0.99}), card, [same, wrong]) == ([], 0)


def test_verified_joint_needs_lines_margin_and_a_second_card():
    import route_conf as RC
    y = [400, 150, 520, 380, 410, 170, 390, 505, 360]
    card = dict(tee_sets={"Blue": dict(yards=y)})
    web = [dict(source="golfify", card=card), dict(source="allsquare", card=card)]
    fs = [dict(properties=dict(golf="hole", ref=str(i + 1), margin=m)) for i, m in enumerate([9.0, 3.9, 4.0])]
    lines = dict(mode="unnumbered OSM hole lines ordered", n_virtual=0)
    assert RC.verified_joint(fs, lines, card, web) == (["1", "3"], 1)
    assert RC.verified_joint(fs, lines, card, web[:1]) == ([], 0)
    assert RC.verified_joint(fs, dict(n_virtual=0), card, web) == ([], 1)              # greens and tees only
    assert RC.verified_joint(fs, dict(lines, n_virtual=1), card, web) == ([], 1)
