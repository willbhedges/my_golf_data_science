"""Offline tests: card consensus on reviewed library courses' saved cards (fixtures/cards_consensus.json:
the build's golfify / OpenGolfAPI cards, AllSquare pages parsed from course_data/research/web, the reviewers'
typed cards, and the OSM ground from each package.json)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import card_consensus as cc  # noqa: E402
import scorecard as scm  # noqa: E402

FX = json.load(open(os.path.join(HERE, "fixtures", "cards_consensus.json")))
WEB = os.path.join(HERE, "..", "research", "web")


def run(course, kinds=None):
    d = FX[course]
    cards = [(x["kind"], x["card"], x["url"]) for x in d["cards"] if kinds is None or x["kind"] in kinds]
    return cc.consensus(cards, d["ground"])


def changed(r):
    return {(c["hole"], c["set"]): c["chosen"] for c in r["changes"]}


def test_finkbine_stale_card_fixed_on_the_ground():
    # golfify / AllSquare Black 7017 is the pre-2021 card; the club's current card fits the OSM tees (review.md)
    r = run("finkbine", {"golfify", "allsquare", "opengolfapi"})
    assert r["base"] == "golfify"
    ch = changed(r)
    assert ch[(1, "Black")] == 375 and ch[(10, "Black")] == 410
    assert r["card"]["tee_sets"]["Black"]["yards"][0] == 375


def test_harvester_par3_and_yardage_holes():
    r = run("harvester", {"golfify", "allsquare", "opengolfapi"})
    ch = changed(r)
    assert ch[(14, "Black")] == 180          # golfify 230 has no tee; the OSM back box is at 176
    assert ch[(13, "Black")] == 418          # ground 409-414, golfify 390
    assert (16, "Red") not in ch and not any(s == "Red" for _, s in ch)   # OpenGolfAPI Red is another set


def test_eagle_bend_scrambled_golfify_loses_to_the_ground():
    r = run("eagle_bend", {"golfify", "opengolfapi"})
    assert r["base"] == "opengolfapi"
    assert any("stale or scrambled" in f and f.startswith("golfify") for f in r["flags"])
    assert not any(c["source"] == "golfify" for c in r["changes"])


def test_weaver_ridge_swapped_set_names():
    r = run("weaver_ridge", {"opengolfapi"})
    assert any("set names swapped" in f for f in r["flags"])
    black = r["card"]["tee_sets"]["Black"]["yards"]
    review = scm.normalise(next(x["card"] for x in FX["weaver_ridge"]["cards"] if x["kind"] == "review"))
    rb = review["tee_sets"]["Black"]["yards"]
    assert sum(abs(a - b) <= 10 for a, b in zip(black, rb)) >= 14          # rows now under the right name


def test_tpc_deere_run_card_typed_in_metres():
    r = run("tpc_deere_run", {"review"})
    assert any("in metres" in f for f in r["flags"])
    assert abs(r["card"]["tee_sets"]["Gold"]["total"] - 7268) <= 5


def test_metres_vetoed_by_an_agreeing_card():
    # Painted Hills: OpenGolfAPI lists only White (0.93 x the back-tee ground) but equals golfify White
    r = run("painted_hills")
    assert not any("metres" in f for f in r["flags"])
    assert r["base"] == "golfify"


def test_good_cards_left_alone():
    for course in ("creekmoor", "st_andrews_op", "la_nickell", "falcon_ridge", "old_kinderhook"):
        r = run(course, {"golfify", "allsquare", "opengolfapi"})
        assert len(r["changes"]) <= 1, (course, r["changes"])
        assert r["base"] in ("golfify", "opengolfapi")


def test_allsquare_page_yards_from_json():
    p = os.path.join(WEB, "rv02_cards", "07.html")
    if not os.path.exists(p):
        return
    card, info = scm.parse_allsquare(open(p).read())
    assert info["state"] == "IA" and info["name"] == "Finkbine Golf Course"
    assert card["tee_sets"]["Black"]["total"] == 7017            # the page table shows 6417 (metres)
    assert card["par"][:3] == [4, 5, 4]
    ok, _ = scm.page_matches(info, "Finkbine Golf Course", "IA", "Iowa City")
    assert ok


def test_allsquare_wrong_state_rejected():
    p = os.path.join(WEB, "rv09_cards", "08.html")             # 'Sycamore Ridge' in Goodview VA, not Spring Hill KS
    if not os.path.exists(p):
        return
    card, info = scm.parse_allsquare(open(p).read())
    ok, why = scm.page_matches(info, "Sycamore Ridge Golf Club", "KS", "Spring Hill")
    assert not ok and "state" in why


def test_metres_to_yards():
    assert scm.metres_to_yards(379) == 414 and scm.metres_to_yards(6417) == 7018


def test_derived_urls():
    u = scm.derived_card_urls("Harvester Golf Club", "IA", "Rhodes")
    assert "https://www.golfify.io/courses/the-harvester-golf-club" in u["golfify"][:3]
    u = scm.derived_card_urls("St. Andrews Golf Course", "KS", "Overland Park")
    assert "https://www.golfify.io/courses/st-andrews-golf-club-overland-park" in u["golfify"]
    u = scm.derived_card_urls("A.L. Gustin Jr. Golf Course", "MO", "Columbia")
    assert "https://www.allsquaregolf.com/golf-courses/missouri/a-l-gustin-golf-course" in u["allsquare"][:2]
    assert scm.name_similarity("L A Nickell Golf Course", "L.A. Nickell Golf Course") == 1.0
