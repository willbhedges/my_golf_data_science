"""Unit tests for the scoreboard's regression guards (no simulation; runs in a second).

  python3 -m pytest course_data/qa/test_scoreboard.py -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scoreboard as SB                                  # noqa: E402


def course(same, n=16, fp="abc", aims=None, checks=None):
    aims = aims or {}
    res = {k: dict(pick="Driver", aim=a, check=(checks or {}).get(k, [])) for k, a in aims.items()}
    return dict(course="Spirit Hollow", slug="spirit_hollow", truth_fp=fp,
                summary=dict(same=same, n_truth=n, n=n, checks=0), aim_violations=SB.aim_violations(res, "Spirit Hollow"))


def hist(same, n=16, fp="abc", regression=False):
    return dict(course="spirit_hollow", same=same, n=n, truth_fp=fp, date="2026-10-17 00:00", commit="x",
                regression=regression)


def test_drop_of_one_hole_passes():
    fails, _ = SB.guards([course(9)], [hist(10)])
    assert not fails


def test_drop_of_two_holes_fails():
    fails, _ = SB.guards([course(8)], [hist(10)])
    assert fails and "dropped by 2" in fails[0]


def test_baseline_skips_regressed_rows():
    fails, _ = SB.guards([course(8)], [hist(9), hist(6, regression=True)])
    assert not fails


def test_truth_change_resets_baseline():
    fails, notes = SB.guards([course(5, fp="new")], [hist(10)])
    assert not fails and "baseline reset" in notes[0]


def test_aim_over_40_without_check_fails():
    c = course(10, aims={"1": -42.5, "2": -40.0, "3": 55.0}, checks={"3": ["aim +55 rejected"]})
    fails, _ = SB.guards([c], [hist(10)])
    assert len(fails) == 1 and "1:" in fails[0]


def test_agree_and_regret():
    p = dict(pick="4-wood", tie=False, runner="2-wood")
    tr = dict(pick="2-wood", tie=True, runner="4-wood", ev={"2-wood": 4.00, "4-wood": 4.004, "Driver": 4.1})
    assert SB.agree(p, tr) == (False, True)
    assert SB.regret(p, tr) == 0.004
    assert SB.agree(dict(pick="Driver", tie=True, runner="2-wood"), dict(pick="2-wood", tie=False)) == (False, True)
