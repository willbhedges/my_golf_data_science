"""course_page.py publish gate, no-card labels and the calm-day note (library QA 2026-11-03).

* world_woods: 16 holes, par 64 vs a par-72 card, resolved to "Cabot Citrus Farms" 2.9 km from `near` with match
  score 0.38 -> was "needs confirm"; must be "blocked" (page kept on disk, off the index list).
* tpc_louisiana: no card -> golfers saw "osm_back" and par-3 badges "176 on the card".
* st_andrews_op 15 Blue: the calm-day pick's note (4-wood stats) showed under the forecast play (Long iron).
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course_page as cp  # noqa: E402

TEMPLATE = os.path.join(os.path.dirname(HERE), "courses", "wind_page_template_course.html")


def _pkg(n=18, pars=None, card_n=18, card_par=None, score=1.6, center=(-82.4786, 28.6856), card=True):
    pars = pars or ([4] * n)
    holes = {str(i + 1): dict(par=p) for i, p in enumerate(pars)}
    osm = {"type": "way", "id": 1}
    ts = {}
    if card:
        cp_ = card_par or [4] * card_n
        ts["Black"] = dict(yards=[400] * card_n, par=cp_, total=400 * card_n)
    else:
        ts["osm_back"] = dict(yards=None, par=None, total=None)
    return dict(holes=holes, tee_sets=ts, tee_set="Black" if card else "osm_back",
                course=dict(name="X", osm=osm, center=list(center),
                            candidates=[dict(name="X", osm=osm, score=score)]))


def _cfg(card=True):
    return dict(tees="Black" if card else "osm_back")


# ------------------------------------------------------------------------------------------------ publish gate
def test_world_woods_is_blocked():
    pkg = _pkg(n=16, pars=[4] * 16, score=0.3833, center=(-82.47864195, 28.6855849))
    b = cp.publish_gate(pkg, _cfg(), near="28.6650,-82.4600")
    assert len(b) == 3, b
    assert b[0].startswith("16 holes built, the card has 18")
    assert b[1].startswith("built pars sum to 64, the card's to 72")
    assert b[2].startswith("resolved to 'X' 2.9 km from the request's near point with match score 0.38")


def test_good_page_is_not_blocked():
    assert cp.publish_gate(_pkg(), _cfg(), near=None) == []
    # a low score next to the near point is fine (a short OSM name), and so is a far course with a strong match
    assert cp.publish_gate(_pkg(score=0.38, center=(-82.46, 28.666)), _cfg(), near="28.6650,-82.4600") == []
    assert cp.publish_gate(_pkg(score=1.79), _cfg(), near="28.6650,-82.4600") == []
    # par within 2 of the card (a card / OSM disagreement on one hole) is a CHECK, not a block
    pars = [4] * 17 + [5]
    assert cp.publish_gate(_pkg(pars=pars), _cfg(), near=None) == []


def test_par_off_by_more_than_two_blocks():
    pars = [4] * 15 + [5, 5, 5]                    # 75 vs 72
    b = cp.publish_gate(_pkg(pars=pars), _cfg(), near=None)
    assert b == ["built pars sum to 75, the card's to 72 (more than 2 apart): holes or pars are wrong"]


def test_nine_hole_card_and_no_card_counts():
    assert cp.publish_gate(_pkg(n=9, card_n=9), _cfg(), near=None) == []
    assert cp.publish_gate(_pkg(n=18, card=False), _cfg(card=False), near=None) == []
    assert cp.publish_gate(_pkg(n=9, card=False), _cfg(card=False), near=None) == []
    b = cp.publish_gate(_pkg(n=27, card=False), _cfg(card=False), near=None)
    assert b and b[0].startswith("27 holes built with no card (expected 18 or 9)")
    b = cp.publish_gate(_pkg(n=3, card=False), _cfg(card=False), near=None)
    assert b and b[0].startswith("3 holes built with no card")


def test_resolve_check_skipped_without_coordinates():
    pkg = _pkg(score=0.2)
    assert cp.publish_gate(pkg, _cfg(), near=None) == []
    assert cp.publish_gate(pkg, _cfg(), near="1 Main St, Town, FL") == []
    assert cp.request_near({"near": "28.6650,-82.4600"}) == "28.6650,-82.4600"
    assert cp.request_near({"near": "28.6650,-82.4600", "osm": "way/1"}) is None     # the request named the course
    assert cp.request_near({"near": [28.665, -82.46]}) == "28.665,-82.46"


# TPC Sawgrass (tpc_sawgrass/qa_rebuild.md): the Stadium holes renumbered onto Dye's Valley's card; 18 holes and
# the par total equal, so only the routing shows it: green n -> tee n+1 walked 237-1,546 yds.
SAWGRASS_GAPS = [996, 1195, 940, 865, 743, 160, 993, 612, 610, 1178, 1061, 1546, 808, 1179, 534, 283, 237]


def _routed(pkg, gaps, lat=30.19, lon=-81.39):
    """Lay the package's holes out so green n -> tee n+1 walks gaps[n-1] yds (each hole 400 yds north-south)."""
    ky, kx = 111320 / 0.9144, math.cos(math.radians(lat)) * 111320 / 0.9144
    x = y = 0.0
    for i in range(1, len(pkg["holes"]) + 1):
        h = pkg["holes"][str(i)]
        h["tee_ll"] = [lon + x / kx, lat + y / ky]
        y += 400 if i % 2 else -400
        h["green_ll"] = [lon + x / kx, lat + y / ky]
        x += gaps[i - 1] if i - 1 < len(gaps) else 0
    return pkg


def test_holes_out_of_order_block():
    b = cp.publish_gate(_routed(_pkg(), SAWGRASS_GAPS), _cfg(), near=None)
    assert len(b) == 1 and b[0].startswith("holes out of order:") and "1546 yds" in b[0]
    # four walks over 500 (Memorial Park, renumbered onto a mixed card): blocked too
    b = cp.publish_gate(_routed(_pkg(), [65, 447, 405, 101, 72, 47, 130, 54, 177, 48, 87, 449, 265, 709, 516, 508,
                                         617]), _cfg(), near=None)
    assert b and b[0].startswith("holes out of order")


def test_long_walks_of_good_pages_pass():
    for gaps in ([69, 143, 39, 157, 140, 74, 114, 51, 672, 147, 73, 284, 58, 130, 96, 135, 73],     # buffalo_ridge
                 [177, 88, 66, 71, 100, 649, 545, 82, 105, 116, 153, 60, 110, 52, 104, 47, 80],     # hawktree
                 [100] * 14 + [600, 700, 790]):
        assert cp.publish_gate(_routed(_pkg(), gaps), _cfg(), near=None) == [], gaps
    # only consecutive holes that both have coordinates are judged
    pkg = _routed(_pkg(), SAWGRASS_GAPS)
    for h in pkg["holes"].values():
        h.pop("green_ll")
    assert cp.publish_gate(pkg, _cfg(), near=None) == []
    pkg = _routed(_pkg(), SAWGRASS_GAPS)
    assert [r for r, _ in cp.routing_gaps(dict(holes={k: v for k, v in pkg["holes"].items() if k != "5"}))] == \
        [1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]


def test_title_names_the_kept_course():
    w = ["multi-course facility: 2 courses' hole ways in one outline (by hole way names: stadium 18, valley 18); "
         "kept 'stadium' (named in the request)"]
    assert cp.page_name(dict(course=dict(name="TPC Sawgrass"), warnings=w), dict(name="TPC Sawgrass Stadium")) \
        == "TPC Sawgrass Stadium"
    w2 = ["multi-course facility: 2 courses' hole ways in one outline (by hole way names: Pinnacle Course 18, "
          "Monument Course 18); kept 'Monument Course' (named in the request), 18 ways"]
    assert cp.page_name(dict(course=dict(name="Troon North Golf Club"), warnings=w2), dict(name="Troon North Monument")) \
        == "Troon North Monument"
    # no request name with the kept course in it: the OSM name + the kept group
    assert cp.page_name(dict(course=dict(name="Troon North Golf Club"), warnings=w2), dict(name="Troon North")) \
        == "Troon North Golf Club Monument Course"
    # the kept course already in the OSM name, or a single course: the OSM name
    w3 = ["hole refs: kept the '2' holes (named in the request) (18 ways, refs as plain numbers)"]
    assert cp.page_name(dict(course=dict(name="Pinehurst No. 2"), warnings=w3), dict(name="Pinehurst No 2")) \
        == "Pinehurst No. 2"
    assert cp.page_name(dict(course=dict(name="Annbriar Golf Course"), warnings=[]), dict(name="Annbriar")) \
        == "Annbriar Golf Course"


def _status(tmp_path, slug, status="needs confirm", page=True):
    d = tmp_path / slug
    d.mkdir()
    if page:
        (d / "page.html").write_text("<html></html>")
    st = dict(slug=slug, name=slug, city="T", state="FL", status=status, reasons=["r"], check_holes=[], tee_sets=[],
              solved_sets=["Black"], page=f"{slug}/page.html" if page else None, page_bytes=10, qa_report=None,
              center=[0, 0], osm="way/1", holes=18, days=[], weather="forecast", built="2026-11-03T00:00Z")
    (d / "status.json").write_text(json.dumps(st))
    return st


def test_index_keeps_blocked_pages_off_the_list(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "HERE", str(tmp_path))
    monkeypatch.setattr(cp, "TOURNAMENT", str(tmp_path / "no_courses"))
    monkeypatch.setattr(cp, "ROOT", str(tmp_path))
    _status(tmp_path, "good")
    _status(tmp_path, "bad", status="blocked")
    cp.index()
    idx = json.load(open(tmp_path / "index.json"))
    assert [r["slug"] for r in idx["courses"]] == ["good"]
    assert [r["slug"] for r in idx["blocked"]] == ["bad"] and idx["blocked"][0]["reasons"] == ["r"]
    assert idx["counts"]["blocked"] == 1
    assert (tmp_path / "bad" / "page.html").exists()              # the files are kept


def test_regate_flips_only_bad_pages(tmp_path, monkeypatch):
    monkeypatch.setattr(cp, "HERE", str(tmp_path))
    monkeypatch.setattr(cp, "ROOT", str(tmp_path))
    for slug, pkg in (("good", _pkg()), ("bad", _pkg(n=16))):
        _status(tmp_path, slug)
        (tmp_path / slug / "package.json").write_text(json.dumps(pkg))
        (tmp_path / slug / "config.json").write_text(json.dumps(_cfg()))
    _status(tmp_path, "failed_one", status="failed", page=False)
    flips = cp.regate(apply=False)
    assert [f[0] for f in flips] == ["bad"]
    assert json.load(open(tmp_path / "bad" / "status.json"))["status"] == "needs confirm"      # dry run
    cp.regate(apply=True)
    st = json.load(open(tmp_path / "bad" / "status.json"))
    assert st["status"] == "blocked" and st["reasons"][0].startswith("16 holes built") and st["reasons"][-1] == "r"
    assert st["page"] == "bad/page.html" and (tmp_path / "bad" / "page.html").exists()
    assert json.load(open(tmp_path / "good" / "status.json"))["status"] == "needs confirm"
    assert cp.regate(apply=False) == []                                       # idempotent


# ------------------------------------------------------------------------------------------------ no-card labels
def _page_data():
    return dict(base_set="osm_back", sets=["osm_back"], colors={"osm_back": "#111"}, set_totals={"osm_back": None},
                sub="Waggaman, LA · automatic page: NEEDS CONFIRM · osm_back · Driver 275/300",
                foot_extra="Solved tee sets: osm_back. See qa_report.md",
                holes=[dict(key="1", base_set="osm_back", tee_name="osm_back tee",
                            note="Driver ... Auto-map CHECK: yardage: no card yardage for osm_back; par: no card par",
                            tee_opts=[])])


def test_no_card_labels_hide_the_internal_set_name():
    d = _page_data()
    cp.label_no_card(d, "osm_back")
    assert d["no_card"] is True
    # identifiers stay (the app and qa.json key on them); golfers see the label
    assert d["base_set"] == "osm_back" and d["sets"] == ["osm_back"] and d["holes"][0]["base_set"] == "osm_back"
    assert d["set_labels"] == {"osm_back": cp.NO_CARD_SET_LABEL} and d["tee_labels"] == {"osm_back": "Back"}
    txt = json.dumps({k: v for k, v in d.items() if k not in ("base_set", "sets", "colors", "set_totals", "set_labels",
                                                                  "tee_labels")} | {"holes": [
        {k: v for k, v in d["holes"][0].items() if k != "base_set"}]})
    assert "osm_back" not in txt
    assert "Back tees (from the map)" in d["sub"] and d["holes"][0]["tee_name"] == "Back tee"
    assert "on the card" not in txt


def test_has_card():
    assert cp.has_card(_pkg(), _cfg())
    assert not cp.has_card(_pkg(card=False), _cfg(card=False))


def _template_code():
    if not os.path.exists(TEMPLATE):
        pytest.skip("course_data/courses/wind_page_template_course.html not in this checkout")
    html = open(TEMPLATE).read()
    m = re.search(r"<script>(.*const D = /\*__DATA__\*/null;?)(.*?)</script>", html, re.S)
    return m.group(2) if m else html


def test_page_patches_all_apply_to_the_template():
    code = _template_code()
    out, missed = cp.patch_code(code)
    assert missed == [], missed
    assert "SETLBL(" in out and "TEELBL(" in out
    assert 'D.no_card ? "to the middle" : "on the card"' in out
    # the calm-day note is labelled when the forecast play differs
    assert "Calm-day pick" in out[out.index("let note = h.note"):][:600]


def test_patched_code_is_valid_js():
    if not shutil.which("node"):
        pytest.skip("no node")
    code, missed = cp.patch_code(_template_code())
    r = subprocess.run(["node", "--check", "-"], input="const D = {};\n" + code, capture_output=True, text=True)
    if r.returncode and "Unexpected token" in r.stderr and "<" in code[:200]:
        pytest.skip("template script not separable")
    assert r.returncode == 0, r.stderr[-800:]


def _run_note(note, calm, play, back=0):
    """The patched note logic, run in node on one hole."""
    code, _ = cp.patch_code(_template_code())
    i = code.index("let note = h.note")
    j = code.index('document.getElementById("hNote").textContent = note;', i)
    snippet = code[i:j]
    js = ("const D = {tee_labels: {}}; const TEELBL = s => (D.tee_labels || {})[s] || s;\n"
          f"const h = {json.dumps(dict(note=note, base_set='Blue'))}; const r = {json.dumps(dict(pick=play, T=dict(back=back)))};\n"
          f"const calm = {json.dumps(calm)};\n" + snippet + "\nconsole.log(note);")
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def test_calm_note_says_which_club_it_describes():
    if not shutil.which("node"):
        pytest.skip("no node")
    note = "4-wood by 0.025 ± 0.017 strokes over long iron. With 4-wood at 57°F: fairway 7%, trees 14%."
    same = _run_note(note, "4-wood", "4-wood")
    assert same == note
    diff = _run_note(note, "4-wood", "Long iron")
    assert diff.startswith("Calm-day pick (no wind): 4-wood. ") and note in diff
    assert diff.endswith("In this wind the play is Long iron: its numbers are in the club table.")
    assert _run_note("ends in a CHECK", "4-wood", "Long iron").startswith(
        "Calm-day pick (no wind): 4-wood. ends in a CHECK. In this wind")
