"""review_fixes.py: the review.json schema variants -> one set of course-page request keys."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import review_fixes as rf  # noqa: E402


def _w(p, d):
    p.write_text(json.dumps(d))


def test_variants(tmp_path):
    f = tmp_path / "x"
    f.mkdir()
    _w(f / "review.json", {"course_review/1": {
        "slug": "x", "card": {"set": {"Gold": [400] * 18}, "par": [4] * 18},
        "course_notes": ["Fix: rebuild with request 'scorecard', tees ['Gold', 'Black']."],
        "holes": [{"n": 1, "verdict": "OK"},
                  {"n": 2, "verdict": "bad", "fix": {"tee_ll": {"Web": [38.1, -94.2]}, "yards": 590}},
                  {"n": 3, "verdict": "bad", "fix": {"yards": {"Black": 399}, "par": 3, "green_ll": [38.0, -94.0]}},
                  {"n": 4, "verdict": "bad", "fix": {"par": 4, "yards": 362, "yards_by_set": {"Gold": 362, "Blue": 344}}},
                  {"n": 5, "verdict": "bad", "fix": {"renumber_as": 18, "tee_ll": {"Blue": [1, 2]}}}]}})
    _w(f / "card_golfify.json", {"schema": "scorecard/1", "tee_sets": {"Gold": {"yards": [400] * 18}}})
    _w(f / "card_review.json", {"schema": "scorecard/1", "tee_sets": {"Gold": {"yards": [401] * 18}}})
    (f / "osm_supplement.geojson").write_text('{"type": "FeatureCollection", "features": []}')
    r = rf.library_request(str(f), str(tmp_path))
    assert r["scorecard"] == "x/card_review.json" and r["osm_supplement"] == "x/osm_supplement.geojson"
    assert r["tees"] == ["Gold", "Black"]
    assert r["tee_overrides"] == {"2": {"Web": [38.1, -94.2]}, "18": {"Blue": [1, 2]}}   # hole 5 -> card 18
    assert r["yardage_overrides"] == {"2": {"Web": 590}, "3": {"Black": 399}, "4": {"Gold": 362, "Blue": 344}}
    assert r["par_overrides"] == {"3": 3, "4": 4}
    assert r["green_overrides"] == {"3": [38.0, -94.0]}
    assert r["hole_renumber"] == {"5": {"to": 18, "near_ll": [1, 2]}}
    assert "review_not_applied" not in r


def test_bare_body_hint_and_merge(tmp_path):
    f = tmp_path / "y"
    f.mkdir()
    _w(f / "review.json", {"slug": "y", "page_set_should_be": "Black, Blue",
                           "summary": {"rebuild_hint": {"yardages": "430 386", "pars": "4 4", "tees": "Championship"}},
                           "holes": {"9": {"fix": {"tee_ll": {"osm_back": [38.0, -92.8]}}}}})
    r = rf.library_request(str(f), str(tmp_path))
    assert r["yardages"] == [430, 386] and r["pars"] == [4, 4] and r["tees"] == ["Championship"]
    assert r["tee_overrides"] == {"9": {"osm_back": [38.0, -92.8]}}
    q = rf.merge({"name": "Y", "tees": ["White"]}, str(f), str(tmp_path))
    assert q["tees"] == ["White"] and q["yardages"] == [430, 386]          # the request's own keys win
    assert rf.merge({"name": "Y", "library_fixes": False}, str(f), str(tmp_path)) == {"name": "Y", "library_fixes": False}
    assert rf.merge({"name": "Z"}, str(tmp_path / "missing"), str(tmp_path)) == {"name": "Z"}


def test_renumber_rekeys_fixes(tmp_path):
    """Page-numbered fixes move to the card number; the renumbered hole wins a clash; a card-numbered
    supplement with ignore_osm_holes sends no hole_renumber (its ways are already renumbered)."""
    f = tmp_path / "r"
    f.mkdir()
    body = {"renumber": {"page_to_card": {"1": 10, "10": 1, "2": 2}}, "card": {"King": [400] * 18},
            "holes": [{"n": 1, "fix": {"tee_ll": {"King": [41.0, -93.0]}, "par": 4}},
                      {"n": 10, "fix": {"card_hole": 1, "par": 5, "yards": {"King": 553}}},
                      {"n": 3, "fix": {"renumber_as": 4, "yards": 300}},
                      {"n": 4, "fix": {"yards": 999}}]}
    _w(f / "review.json", {"course_review/1": body})
    r = rf.library_request(str(f), str(tmp_path))
    assert r["par_overrides"] == {"10": 4, "1": 5}
    assert r["tee_overrides"] == {"10": {"King": [41.0, -93.0]}}
    assert r["yardage_overrides"] == {"1": {"King": 553}, "4": {"*": 300}}       # page 4's own fix dropped
    assert r["hole_renumber"] == {"1": {"to": 10, "near_ll": [41.0, -93.0]}, "10": 1, "3": 4}
    assert any("hole 4" in s for s in r["review_not_applied"])
    body["rebuild_advice"] = "request ignore_osm_holes: true"
    _w(f / "review.json", {"course_review/1": body})
    (f / "osm_supplement.geojson").write_text('{"type": "FeatureCollection", "features": []}')
    r = rf.library_request(str(f), str(tmp_path))
    assert r["ignore_osm_holes"] is True and "hole_renumber" not in r and r["par_overrides"] == {"10": 4, "1": 5}


def test_bare_yards_keyed_to_the_named_set(tmp_path):
    """The Falls / Weaver Ridge (qa_rebuild.md): a bare fix "yards" never goes to "*" on a multi-set rebuild (it
    landed on the solved set, Blue / Black). It goes to the set tee_ll names; with several named sets, to those
    whose review card value it is; with none named, "*" only when the rebuild has one set; else dropped + noted."""
    f = tmp_path / "f"
    f.mkdir()
    card = {"set": {"Gold": [390] * 18, "Blue": [379] * 18}}
    _w(f / "review.json", {"course_review/1": {"card": card, "page_set_should_be": "Blue, White", "holes": [
        {"n": 2, "fix": {"tee_ll": {"Gold": [38.79, -90.72]}, "yards": 390}},
        {"n": 12, "fix": {"tee_ll": {"Gold": [1, 2], "Blue": [1, 3]}, "yards": 379}},
        {"n": 13, "fix": {"tee_ll": {"Gold": [1, 2], "Blue": [1, 3]}, "yards": 240}},
        {"n": 5, "fix": {"yards": 387, "par": 4}},
        {"n": 6, "notes": "Blue on the back box; the card is short", "fix": {"yards": 401}}]}})
    r = rf.library_request(str(f), str(tmp_path))
    assert r["yardage_overrides"] == {"2": {"Gold": 390}, "12": {"Blue": 379}, "6": {"Blue": 401}}
    assert r["par_overrides"] == {"5": 4}
    assert sum("bare yards" in s for s in r["review_not_applied"]) == 2       # 13 (which set?) and 5 (no set)
    _w(f / "review.json", {"course_review/1": {"holes": [{"n": 5, "fix": {"yards": 387}}]}})
    _w(f / "package.json", {"tee_sets": {"osm_back": {"yards": None}}})       # the last build had no card: one set
    assert rf.library_request(str(f), str(tmp_path))["yardage_overrides"] == {"5": {"*": 387}}
