import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import budget_causes as BC  # noqa: E402


def row(hole, auto, **cfg):
    """auto / configs as (match, regret)."""
    c = {"auto": dict(match=auto[0], regret=auto[1])}
    for L in BC.LAYERS:
        c[f"+{L}"] = dict(match=auto[0], regret=auto[1])
        c[f"-{L}"] = dict(match=True, regret=0.0)
    for g in BC.GROUPS:
        c[f"+{g}"] = dict(match=auto[0], regret=auto[1])
    for k, v in cfg.items():
        c[k.replace("plus_", "+").replace("minus_", "-")] = dict(match=v[0], regret=v[1])
    return dict(hole=hole, configs=c)


def test_one_cause_per_miss_largest_recovery_wins():
    r = row("1", (False, 0.30), plus_tees=(True, 0.25), plus_long_grass=(True, 0.02))
    assert BC.cause_of(r)[0] == "long_grass"
    r = row("2", (False, 0.10), plus_trees=(False, 0.03))          # no fixer, but recovers > half of the regret
    assert BC.cause_of(r)[0] == "trees"
    r = row("3", (False, 0.10), minus_fairway=(False, 0.08))        # nothing fixes it; the auto fairway breaks truth
    assert BC.cause_of(r)[0] == "fairway (-layer)"
    r = row("4", (False, 0.10), plus_hazards=(True, 0.0))
    assert BC.cause_of(r)[0] == "interaction"
    assert BC.cause_of(row("5", (False, 0.10)))[0] == "unexplained"
    assert BC.cause_of(row("6", (True, 0.002)))[0] == "no layer"


def test_summary_adds_up_and_counts_near_ties():
    rows = [("a", row("1", (False, 0.30), plus_tees=(True, 0.0))),
            ("a", row("2", (False, 0.004), plus_trees=(True, 0.0))),
            ("a", row("3", (True, 0.01), plus_long_grass=(True, 0.0))),
            ("national_kc", row("1", (False, 1.0)))]
    S = BC.summarise([x for x in rows if x[0] not in BC.SKIP])
    assert S["n"] == 3 and S["match"] == 1
    assert S["near_tie"] == dict(misses=2, under_tie=1, under_cost=1, over_cost=1, regret_over_cost=0.3)
    assert S["match_if_cost_counted"] == 2
    assert sum(v["misses"] for v in S["per_cause"].values()) == 2
    assert abs(sum(v["regret"] for v in S["per_cause"].values()) - S["regret"]) < 1e-9
    assert S["per_cause"]["long_grass"]["misses"] == 0 and S["per_cause"]["long_grass"]["regret"] == 0.01
