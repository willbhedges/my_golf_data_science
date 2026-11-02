"""library/wide_aims.py: the wide-aim CHECK on library pages (any printed tee-shot aim past +/-40 yds)."""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wide_aims as W  # noqa: E402

TEMPS = [45.0, 55.0, 65.0]
SPEEDS = [0, 5, 10]
DIRS = list(range(0, 360, 30))


def _cell(aims, drift=0.0, ev=None):
    """{club: [aim, ev, zlo, zhi, carry, total, width, drift]} (the page's compact grid cell)."""
    ev = ev or {"Driver": 4.0, "4-wood": 4.1, "Hybrid ~235 (not in bag)": 3.0}
    width = {"Driver": 70, "4-wood": 54, "Hybrid ~235 (not in bag)": 48}
    return {c: [aims.get(c, 0.0), ev[c], aims.get(c, 0.0) - 1, aims.get(c, 0.0) + 1, 250, 270, width[c],
                drift if c == "Driver" else 0.0] for c in ev}


def _hole(calm_aim=None, wind_aim=None, wind_drift=0.0, calm_pick="Driver", key="6"):
    """A tee hole whose grids say Driver on the line in calm air; every wind cell has Driver at wind_aim (if given)
    with that drift."""
    g = {}
    for T in TEMPS:
        cells = {"0_0": _cell({"Driver": 0.0})}
        for sp in SPEEDS[1:]:
            for d in DIRS:
                cells[f"{sp}_{d}"] = _cell({"Driver": 0.0 if wind_aim is None else wind_aim}, wind_drift)
        g[f"{T:g}"] = cells
    h = dict(kind="tee", key=key, bearing=90.0, grids={"0": g})
    if calm_aim is not None:
        h["calm"] = dict(pick=calm_pick, aim=calm_aim, tie=False, temp=55.0)
    return h


def _page(holes, fc=None, alt=None):
    return dict(base_set="Gold", temps=TEMPS, speeds=SPEEDS, days=["2026-11-07"], holes=holes,
                forecast=fc if fc is not None else [dict(date="2026-11-07", hour=9, mph=8.0, dir=200, temp=52.0),
                                                     dict(date="2026-11-09", hour=9, mph=8.0, dir=200, temp=52.0)],
                **({"alt": alt} if alt else {}))


def test_same_rule_and_words_as_product_decide():
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "product"))
    import decide
    assert W.GUARD_AIM == decide.GUARD_AIM
    for club, aim in [("4-wood", -60.0), ("Driver", 58.5), ("2-wood", 52.5), ("Driver", 40.0), ("Driver", -40.0),
                      ("Driver", 12.5), ("Driver", 40.5)]:
        assert W.wide_aim_flags(club, aim) == decide.wide_aim_flags(club, aim)
    assert W.wide_aim_flags("4-wood", -60.0) == [
        "4-wood aim -60 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): "
        "confirm the line on the map"]


def test_calm_book_aim_past_40_is_a_check():
    # Gustin Gold 6: the note's book line is 4-wood 60 yds left, printed with no CHECK before
    h = _hole(calm_aim=-60.0)
    assert W.flags(h, _page([h])) == W.wide_aim_flags("Driver", -60.0)
    h = _hole(calm_aim=58.5)                                  # Sycamore Ridge 18
    assert W.flags(h, _page([h])) == W.wide_aim_flags("Driver", 58.5)


def test_on_the_bound_or_inside_is_no_check():
    for a in (-40.0, 40.0, 12.0, 0.0):
        h = _hole(calm_aim=a)
        assert W.flags(h, _page([h])) == []


def test_forecast_aim_past_40_on_a_widened_line_is_a_check():
    # no book pick: the forecast wind pick is Driver +55 finishing 50 right, the wider bound
    h = _hole(wind_aim=55.0, wind_drift=-5.0)
    f = W.flags(h, _page([h]))
    assert len(f) == 1 and f[0].startswith("Driver aim +55 yds is more than 40 yds right")


def test_crosswind_compensation_is_not_a_wide_aim():
    # aim 46 into the wind, drift -20: the line is 26 right, inside the v2 bound (shifted by the drift)
    h = _hole(wind_aim=46.0, wind_drift=-20.0)
    assert W.flags(h, _page([h])) == []


def test_forecast_outside_the_event_days_is_ignored():
    h = _hole(wind_aim=55.0)
    assert W.flags(h, _page([h]))
    fc = [dict(date="2026-11-09", hour=9, mph=8.0, dir=200, temp=52.0)]
    assert W.flags(h, _page([h], fc=fc)) == []


def test_light_wind_keeps_the_book_aim_shifted_by_the_wind():
    # the page keeps the calm book pick (bayes) when the wind does not change the quick pick: book aim + wind change
    h = _hole(calm_aim=-45.0)
    rows = W.printed(h, _page([h]))
    assert [r[0] for r in rows][:1] == ["calm-day book"]
    fc = [r for r in rows if r[0].startswith("forecast")]
    assert fc and all(r[1] == "Driver" and r[2] == pytest.approx(-45.0) for r in fc)


def test_both_sides_and_alt_sets():
    a = _hole(calm_aim=-60.0, key="6")
    b = _hole(calm_aim=10.0, key="7")
    c = _hole(calm_aim=60.0, key="2")
    D = _page([a, b], alt={"Blue": [c]})
    pf = W.page_flags(D)
    assert set(pf) == {"Gold", "Blue"} and set(pf["Gold"]) == {"6"} and set(pf["Blue"]) == {"2"}
    reasons, where = pf["Blue"]["2"]
    assert reasons == W.wide_aim_flags("Driver", 60.0) and "calm-day" in where


def test_landing_extent_covers_the_wide_oval_only():
    h = _hole(calm_aim=-60.0)
    D = _page([h])
    left, right = W.landing_extent(h, D)
    assert left >= 60 + 35 and right == pytest.approx(10.0)         # Driver 95% width 70: half 35, + pad
    assert W.landing_extent(_hole(calm_aim=-20.0), D) is None
