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
    assert r["tee_overrides"] == {"2": {"Web": [38.1, -94.2]}}                 # renumbered hole 5 skipped
    assert r["yardage_overrides"] == {"2": {"*": 590}, "3": {"Black": 399}, "4": {"Gold": 362, "Blue": 344}}
    assert r["par_overrides"] == {"3": 3, "4": 4}
    assert len(r["review_not_applied"]) == 2


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
