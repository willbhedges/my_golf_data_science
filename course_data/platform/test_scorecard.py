"""Offline tests: scorecard parsing and tee-set choice (python -m pytest -q course_data/platform)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scorecard as scm  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
BLACK = [391, 507, 148, 532, 384, 408, 154, 383, 365, 502, 338, 186, 409, 393, 145, 378, 445, 521]
PAR = [4, 5, 3, 5, 4, 4, 3, 4, 4, 5, 4, 3, 4, 4, 3, 4, 4, 5]


def test_golfify_next_data():
    card, fac = scm.parse_golfify(open(os.path.join(FIX, "golfify_spirit_hollow.json")).read())
    assert fac["state"] == "Iowa"
    assert list(card["tee_sets"]) == ["Gold", "Black", "White", "Rust"]
    b = card["tee_sets"]["Black"]
    assert b["yards"] == BLACK and b["total"] == 6589 and b["rating"] == 71.4 and b["slope"] == 124
    assert card["par"] == PAR
    assert card["tee_sets"]["Rust"]["colour"] == "red"          # golfify colour differs from the name


def test_column_table_text():
    card = scm.parse_text(open(os.path.join(FIX, "golfify_text_table.txt")).read())
    assert card["tee_sets"]["Black"]["yards"] == BLACK
    assert card["par"] == PAR
    assert len(card["tee_sets"]) == 4


def test_hole_by_hole_page():
    card = scm.parse_text(open(os.path.join(FIX, "club_hole_by_hole.txt")).read())
    sets = card["tee_sets"]
    assert len(sets) == 4 and sets["Tee 2"]["yards"] == BLACK
    assert card["par"] == PAR
    assert "back" in sets["Tee 1"]["aliases"] and "forward" in sets["Tee 4"]["aliases"]


def test_row_table_with_totals():
    front = BLACK[:9]
    back = BLACK[9:]
    text = ("Hole 1 2 3 4 5 6 7 8 9 Out 10 11 12 13 14 15 16 17 18 In Tot\n"
            f"Blue Tees {' '.join(map(str, front))} {sum(front)} {' '.join(map(str, back))} {sum(back)} {sum(BLACK)}\n"
            f"Par {' '.join(map(str, PAR[:9]))} 36 {' '.join(map(str, PAR[9:]))} 36 72\n"
            "Handicap 3 11 9 13 15 1 17 5 7 8 12 14 2 4 18 16 10 6\n")
    card = scm.parse_text(text)
    assert card["tee_sets"]["Blue Tees"]["yards"] == BLACK
    assert card["par"] == PAR
    assert card["handicap"][0] == 3


def test_totals_must_add_up():
    nums = BLACK[:9] + [999] + BLACK[9:] + [sum(BLACK[9:]), sum(BLACK)]
    assert scm._strip_totals(nums) is None


def test_choose_tee_set():
    card = scm.normalise(json.load(open(os.path.join(FIX, "spirit_hollow_scorecard.json"))))
    assert scm.choose_tee_set(card, "black")[0] == "Black"
    assert scm.choose_tee_set(card, "blue") == ("Black", "alias")      # tees/scorecard.json alias list
    assert scm.choose_tee_set(card, "back")[0] == "Gold"
    assert scm.choose_tee_set(card, "forward")[0] == "Rust"
    name, why = scm.choose_tee_set(card, "purple")
    assert name is None and "not on the card" in why
    assert scm.choose_tee_set(card, None)[0] == "Gold"
    hole = scm.per_hole(card, "Black", ["1", "3", "18"])
    assert hole["1"] == dict(yards=391, par=4, hcp=3) and hole["18"]["yards"] == 521


def test_card_from_request_yardages():
    card = scm.card_from_yardages({"1": 400, "2": 150}, {"1": 4, "2": 3}, name="White")
    assert card["tee_sets"]["White"]["yards"] == [400, 150] and card["par"] == [4, 3]
    assert scm.choose_tee_set(card, "white")[0] == "White"


def test_normalise_holes_shape():
    card = {"tee_sets": {"white": {"holes": {"2": {"par": 3, "yards": 160}, "1": {"par": 4, "yards": 401}}}},
            "aliases": {"middle": "white"}}
    n = scm.normalise(card)
    assert n["tee_sets"]["white"]["yards"] == [401, 160]
    assert n["par"] == [4, 3]
    assert scm.choose_tee_set(n, "middle") == ("white", "alias")


def test_plausible():
    card, _ = scm.parse_golfify(open(os.path.join(FIX, "golfify_spirit_hollow.json")).read())
    lengths = {str(i + 1): y for i, y in enumerate([426, 528, 183, 566, 468, 445, 165, 431, 383,
                                                    575, 352, 210, 480, 467, 158, 434, 496, 579])}
    assert scm.plausible(card, 18, lengths)
    nine = scm.card_from_yardages(BLACK[:9])
    assert not scm.plausible(nine, 18) and scm.plausible(nine, 9)
    assert scm.plausible(card, 9)                                  # 18-hole card on a 9-hole loop: allowed
    assert not scm.plausible(card, 18, {k: v * 2 for k, v in lengths.items()})


def test_golfify_slugs():
    s = scm.golfify_slugs("Spirit Hollow Golf Course", "Burlington")
    assert s[0] == "spirit-hollow-golf-course"
    assert "spirit-hollow-golf-course-burlington" in s


def test_duplicate_set_names_are_folded():
    """QA P6 (Veenker): golfify gives 'Gold' and 'Gold (Gold)' (its other rating); 'Pink (Pink)' alone is renamed."""
    y = [400] * 18
    card = scm.normalise(dict(tee_sets={
        "Blue": dict(yards=y, total=7200, rating=71.5, slope=131),
        "Gold": dict(yards=y, total=6114, rating=69.1, slope=122),
        "Gold (Gold)": dict(yards=y, total=6086, rating=75.4, slope=132),
        "Pink (Pink)": dict(yards=y, total=5000, rating=70.0, slope=118),
        "Blue (Men)": dict(yards=y, total=7200, rating=71.5, slope=131),
        "Red": dict(yards=y, total=5295, rating=65.8, slope=112),
        "Red #2": dict(yards=y, total=5295, rating=71.5, slope=117)}))
    sets = card["tee_sets"]
    assert set(sets) == {"Blue", "Gold", "Pink", "Blue (Men)", "Red"}
    assert sets["Red"]["alt_ratings"][0]["slope"] == 117
    assert sets["Gold"]["rating"] == 69.1 and sets["Gold"]["alt_ratings"][0]["rating"] == 75.4
    assert scm.choose_tee_set(card, "pink (pink)")[0] == "Pink"
