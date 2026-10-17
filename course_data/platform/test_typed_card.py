"""Offline tests for typed_card.py (golfer-typed yardages / pars)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import routing as R  # noqa: E402
from typed_card import parse_typed_card  # noqa: E402

Y18 = [391, 175, 520, 402, 365, 148, 430, 510, 388, 405, 160, 545, 372, 410, 190, 498, 355, 420]
P18 = [4, 3, 5, 4, 4, 3, 4, 5, 4, 4, 3, 5, 4, 4, 3, 5, 4, 4]


def codes(issues, level="error"):
    return [i["code"] for i in issues if i["level"] == level]


def test_plain_list_and_routing_reads_it():
    card, iss = parse_typed_card(" ".join(map(str, Y18)), pars=",".join(map(str, P18)), tee="White")
    assert card and not codes(iss), iss
    n, pars, yards = R.card_holes(card)
    assert n == 18 and pars == P18 and [y[0] for y in yards] == Y18


def test_separators_and_subtotals():
    out, inn = sum(Y18[:9]), sum(Y18[9:])
    txt = ", ".join(map(str, Y18[:9])) + f" OUT {out}\n" + " / ".join(map(str, Y18[9:])) + f" IN {inn} {out + inn}"
    card, iss = parse_typed_card(txt)
    assert card and card["tee_sets"]["Typed"]["yards"] == Y18 and not codes(iss), iss


def test_pairs_any_order():
    txt = "  ".join(f"{i + 1}: {y}" for i, y in reversed(list(enumerate(Y18[:9]))))
    card, iss = parse_typed_card(txt)
    assert card and card["tee_sets"]["Typed"]["yards"] == Y18[:9]


def test_errors():
    _, iss = parse_typed_card(" ".join(map(str, Y18[:17])))
    assert "count" in codes(iss)
    _, iss = parse_typed_card(" ".join(map(str, Y18[:3] + [3912] + Y18[5:])))
    assert "joined" in codes(iss) and iss[-1]["hole"] == 4
    _, iss = parse_typed_card(" ".join(map(str, Y18)), pars=" ".join(map(str, P18[:17] + [7])))
    assert "par_range" in codes(iss)
    _, iss = parse_typed_card(" ".join(map(str, Y18)), pars=" ".join(map(str, P18[:9])))
    assert "par_count" in codes(iss)
    _, iss = parse_typed_card("391 17S 520 402 365 148 430 510 388")
    assert "not_a_number" in codes(iss)
    _, iss = parse_typed_card(" ".join(map(str, Y18)), total=sum(Y18) + 10)
    assert "total" in codes(iss)
    _, iss = parse_typed_card(" ".join(["400"] * 27))
    assert "too_many_holes" in codes(iss)


def test_warnings_and_digit_string_pars():
    y = list(Y18)
    y[1] = 375                                     # a par 3 typed as 375
    card, iss = parse_typed_card(" ".join(map(str, y)), pars="".join(map(str, P18)))
    assert card and card["par"] == P18 and "par_fit" in codes(iss, "warning")


def test_metres():
    card, _ = parse_typed_card(" ".join(str(int(y * 0.9144)) for y in Y18), unit="m")
    assert all(abs(a - b) <= 2 for a, b in zip(card["tee_sets"]["Typed"]["yards"], Y18))
