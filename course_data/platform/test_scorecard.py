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


# ----------------------------------------------------------------------------- Q4 OpenGolfAPI + card checks
def oga(slug):
    return json.load(open(os.path.join(FIX, f"opengolfapi_{slug}.json")))


def test_parse_opengolfapi_veenker():
    card = scm.parse_opengolfapi(oga("veenker")["details"][0])
    sets = card["tee_sets"]
    assert list(sets) == ["Blue", "Gold", "Red"]                 # longest first
    assert all(len(s["yards"]) == 18 and None not in s["yards"] for s in sets.values())
    assert sets["Blue"]["total_stated"] == 6680 and sets["Blue"]["total"] == 6633
    assert sets["Blue"]["rating"] == 71.5 and sets["Blue"]["slope"] == 131
    assert card["par"][:3] == [4, 4, 4] and len(card["handicap"]) == 18
    assert "OpenGolfAPI" in card["attribution"] and card["licence"] == "ODbL-1.0"
    assert any(a.get("rating") for s in sets.values() for a in s.get("alt_ratings", []))   # the other gender


def test_parse_opengolfapi_nine_hole_course_is_not_mozingos_eighteen():
    card = scm.parse_opengolfapi(oga("mozingo_lake")["details"][0])
    assert len(next(iter(card["tee_sets"].values()))["yards"]) == 9
    assert not scm.plausible(card, n_holes=18)


def test_consistency_flags_mixed_card_versions():
    sh = scm.parse_opengolfapi(oga("spirit_hollow")["details"][0])
    chk = scm.consistency(sh)
    assert not chk["ok"] and not chk["sets"]["Gold"]["ok"] and chk["sets"]["Gold"]["diff"] == 7268 - 7550
    assert any("mixed card versions" in f for f in chk["flags"])
    club = scm.normalise(json.load(open(os.path.join(FIX, "spirit_hollow_scorecard.json"))))
    assert scm.consistency(club)["ok"], scm.consistency(club)["flags"]


def test_consistency_order_violation():
    card = scm.card_from_yardages(BLACK, PAR, name="Black")
    short = list(BLACK)
    short[4] = BLACK[4] + 30                                      # the forward set longer on hole 5
    card["tee_sets"]["White"] = dict(colour="white", aliases=[], yards=short, total=sum(short) - 400)
    chk = scm.consistency(card)
    assert chk["order_violations"] and chk["order_violations"][0]["hole"] == 5


def test_choose_card_by_reliability_not_by_fit():
    club = scm.card_from_yardages(BLACK, PAR, name="Black", source="club")
    gfy = scm.card_from_yardages([y + 1 for y in BLACK], PAR, name="Black", source="golfify")
    oga_card = scm.parse_opengolfapi(oga("spirit_hollow")["details"][0])
    kind, card, url, chk = scm.choose_card([("opengolfapi", oga_card, "u3"), ("golfify", gfy, "u2"),
                                            ("club_site", club, "u1")])
    assert kind == "club_site" and url == "u1" and chk["ok"]
    bad = scm.card_from_yardages(BLACK, PAR, name="Black")
    bad["tee_sets"]["Black"]["total_stated"] = sum(BLACK) + 200     # club page with a stale total
    kind, *_ = scm.choose_card([("club_site", bad, "u1"), ("golfify", gfy, "u2")])
    assert kind == "golfify"
    kind, _, _, chk = scm.choose_card([("opengolfapi", oga_card, "u3")])
    assert kind == "opengolfapi" and not chk["ok"]                 # nothing better: used, but flagged


def test_cross_check_matches_sets_by_colour():
    club = scm.normalise(json.load(open(os.path.join(FIX, "spirit_hollow_scorecard.json"))))
    sh = scm.parse_opengolfapi(oga("spirit_hollow")["details"][0])
    cc = scm.cross_check(club, sh)
    assert cc["Gold"]["other_set"] == "Gold" and cc["Gold"]["mae"] > 10 and 2 in cc["Gold"]["holes_over_tol"]
    assert cc["Rust"]["other_set"] == "Red"                        # Rust's colour is red


def test_pick_opengolfapi_candidate():
    cands = oga("veenker")["search"]["courses"]
    c, why = scm.pick_opengolfapi_candidate(cands, "Veenker Memorial Golf Course", "IA", center=[-93.651, 42.038])
    assert c["id"] == "939125f5-e5e5-4c0c-84e3-4271dc5fa4c7"
    assert scm.pick_opengolfapi_candidate(cands, "Veenker Memorial", "MO")[0] is None
    assert scm.pick_opengolfapi_candidate(cands, "Veenker Memorial", "IA", center=[-91.14, 40.76])[0] is None


class _Resp:
    def __init__(self, code, js=None, headers=None):
        self.status_code, self._js, self.headers = code, js, headers or {}

    def json(self):
        return self._js


class _Session:
    """Fake requests.Session: the first search call is rate-limited (429), then fixtures."""

    def __init__(self, fixture):
        self.fx, self.urls = fixture, []

    def get(self, url, timeout=None, headers=None):
        self.urls.append(url)
        assert "User-Agent" in (headers or {})
        if "/search" in url and len(self.urls) == 1:
            return _Resp(429, headers={"Retry-After": "2"})
        if "/search" in url:
            return _Resp(200, self.fx["search"])
        return _Resp(200, self.fx["details"][0])


def test_fetch_opengolfapi_offline(tmp_path):
    sess, sleeps = _Session(oga("veenker")), []
    card, url = scm.fetch_opengolfapi("Veenker Memorial Golf Course", "IA", [-93.651, 42.038], str(tmp_path),
                                      session=sess, sleep=sleeps.append)
    assert card and url.endswith("/api/v1/courses/939125f5-e5e5-4c0c-84e3-4271dc5fa4c7")
    assert len(sess.urls) == 3 and "state=IA" in sess.urls[0]       # 429, retried search, detail
    assert 2.0 in sleeps                                          # honoured Retry-After
    assert all(s <= 60 for s in sleeps)
    assert (tmp_path / "opengolfapi_search.json").exists()
    assert (tmp_path / "opengolfapi_939125f5-e5e5-4c0c-84e3-4271dc5fa4c7.json").exists()
    assert set(card["tee_sets"]) == {"Blue", "Gold", "Red"}
