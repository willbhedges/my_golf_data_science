"""app/build_library_play.native_cards: course_page.py's native.json -> the library record's check cards."""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(os.path.dirname(HERE), "app")
sys.path.insert(0, APP)
import build_library_play as B  # noqa: E402

NATIVE = os.path.join(APP, "fixtures", "lib_native", "eagle_bend_native.json")   # a local course_page.py native run


def _page():
    D = B.load_page(os.path.join(HERE, "eagle_bend", "page.html"))
    by = {D["base_set"]: D["holes"]}
    by.update(D.get("alt") or {})
    clubs = []
    for h in D["holes"]:
        if h.get("kind") == "tee":
            for c in h["grids"]["0"][list(h["grids"]["0"])[0]]["0_0"]:
                if c not in clubs:
                    clubs.append(c)
    V_of = {(s, str(h["key"])): dict(tee_ll=None, bearing=h["bearing"]) for s, hs in by.items() for h in hs}
    return D, by, clubs, V_of


def test_cards_from_native_json(tmp_path, monkeypatch):
    os.makedirs(tmp_path / "eagle_bend")
    shutil.copy(NATIVE, tmp_path / "eagle_bend" / "native.json")
    monkeypatch.setattr(B, "LIBDIR", str(tmp_path))
    D, by, clubs, V_of = _page()
    nat = json.load(open(NATIVE))
    tee = {str(k): v for k, v in json.load(open(os.path.join(HERE, "eagle_bend", "package.json")))["holes"].items()}
    for (s, ref), V in V_of.items():
        V["tee_ll"] = ((tee.get(ref) or {}).get("tees") or {}).get(s, {}).get("tee_ll")
    cards = B.native_cards("eagle_bend", by, V_of, D["temps"], clubs)
    assert [str(c["hole"]) for c in cards] == [it["hole"] for it in nat["items"]] and len(cards) <= 4
    for c in cards:
        assert c["type"] == "native" and c["question"] == "Native grass along this hole's landing area?"
        assert [o["label"] for o in c["options"]] == ["Left", "Right", "Both", "None"]
        assert c["tee_set"] == nat["tee_set"]
        h = next(x for x in by[c["tee_set"]] if str(x["key"]) == str(c["hole"]))
        for o in c["options"]:
            if o["outcome"] is None:
                assert o["text"] == "No change to the plan."
                continue
            oc = o["outcome"]
            assert o["text"].startswith("Re-planned: ") and oc["pick"] in clubs
            assert oc["pick"] != h["calm"]["pick"] or abs(oc["aim"] - h["calm"]["aim"]) > B.NATIVE_AIM_TOL
            assert len(oc["wind"]) == 17 and clubs[oc["wind"][0][0]] == oc["pick"]     # calm cell = the re-plan
            assert abs(oc["wind"][0][1] - oc["aim"]) <= 0.5
        # the band: one polygon per side, beyond the tee line on its own side, 130-400 yds out
        for side, sg in (("L", -1), ("R", 1)):
            for poly in c["band"][side]:
                assert all(sg * l > 0 for _, l in poly)
                assert 100 < min(a for a, _ in poly) and max(a for a, _ in poly) < 430
    # answers where the native planner keeps its plan never move the page's plan
    assert any(o["outcome"] is None for c in cards for o in c["options"])


def test_no_native_json_no_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "LIBDIR", str(tmp_path))
    D, by, clubs, V_of = _page()
    assert B.native_cards("eagle_bend", by, V_of, D["temps"], clubs) == []
