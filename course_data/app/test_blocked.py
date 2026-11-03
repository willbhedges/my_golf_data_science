"""Blocked library pages stay out of the app, judged by each page's own status.json (written with page.html), not
only by library/index.json (rewritten later, in its own commit): build_library_play.library_rows / build(),
build_app.blocked_courses / library().

  python3 -m pytest course_data/app/test_blocked.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_library_play as B  # noqa: E402


def _w(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        json.dump(d, fh)


def _row(slug, status, holes=18, built="2026-11-03T05:14Z", name=None):
    return dict(slug=slug, name=name or slug.title(), city="Town", state="MD", status=status, check_holes=[],
                reasons=[], page=f"course_data/library/{slug}/page.html", holes=holes, built=built, group="library")


def _lib(tmp_path, index, statuses):
    lib = tmp_path / "library"
    _w(str(lib / "index.json"), index)
    for slug, st in statuses.items():
        _w(str(lib / slug / "status.json"), st)
    return str(lib)


def test_stale_index_row_of_a_blocked_page_is_blocked(tmp_path):
    # 2026-11-03: the index still listed the 18-hole build as "needs confirm"; page.html + status.json were the
    # blocked 9-hole South River rebuild
    idx = dict(courses=[_row("qh", "needs confirm"), _row("ok", "auto-OK")], blocked=[])
    lib = _lib(tmp_path, idx, {"qh": dict(_row("qh", "blocked", 9, "2026-11-03T15:03Z", "South River Golf Course")),
                               "ok": _row("ok", "auto-OK")})
    rows, blocked = B.library_rows(None, lib)
    assert [r["slug"] for r in rows] == ["ok"]
    assert [r["slug"] for r in blocked] == ["qh"] and blocked[0]["name"] == "South River Golf Course"


def test_page_rebuilt_after_a_block_is_listed_from_its_status(tmp_path):
    idx = dict(courses=[], blocked=[dict(_row("qh", "blocked", 9, "2026-11-03T15:03Z"))])
    lib = _lib(tmp_path, idx, {"qh": _row("qh", "needs confirm", 18, "2026-11-03T16:14Z")})
    rows, blocked = B.library_rows(None, lib)
    assert blocked == [] and rows[0]["slug"] == "qh" and rows[0]["holes"] == 18 and rows[0]["built"] == "2026-11-03T16:14Z"


def test_rows_without_status_json_keep_the_index(tmp_path):
    t = dict(slug="tour", name="Tour", status="hand-checked", group="tournament", page="x")
    idx = dict(courses=[t, _row("nost", "needs confirm")], blocked=[_row("gone", "blocked")])
    rows, blocked = B.library_rows(None, _lib(tmp_path, idx, {}))
    assert [r["slug"] for r in rows] == ["tour", "nost"] and [r["slug"] for r in blocked] == ["gone"]


def test_blocked_page_never_replaces_an_existing_record(tmp_path, monkeypatch):
    idx = dict(courses=[_row("qh", "needs confirm")], blocked=[])
    lib = _lib(tmp_path, idx, {"qh": _row("qh", "blocked", 9)})
    out = tmp_path / "out"
    good = dict(schema="golf_lib_play/1", id="qh", holes=[{"no": i} for i in range(1, 19)])
    _w(str(out / "qh.json"), good)
    monkeypatch.setattr(B, "LIBDIR", lib)
    called = []
    monkeypatch.setattr(B, "build_one", lambda *a, **k: called.append(a))
    res = B.build(str(out), log=lambda *_: None)
    assert res == {} and called == []
    assert json.load(open(out / "qh.json")) == good


def test_build_one_refuses_a_page_that_is_not_its_row(tmp_path):
    # the hole-count guard: a real 18-hole page under a 9-hole row writes nothing
    import pytest
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="18 holes, its status row 9"):
        B.build_one("eagle_bend", dict(_row("eagle_bend", "needs confirm", 9), city="X"), str(out))
    assert not (out / "eagle_bend.json").exists()


def test_build_app_blocked_courses_reads_status_json(tmp_path, monkeypatch):
    import build_app as A
    idx = dict(courses=[_row("qh", "needs confirm", name="Queenstown Harbor River Course")], blocked=[])
    lib = _lib(tmp_path, idx, {"qh": _row("qh", "blocked", 9, name="South River Golf Course")})
    monkeypatch.setattr(A, "LIBRARY_INDEX", os.path.join(lib, "index.json"))
    held = A.blocked_courses()
    assert held["ids"] == {"qh"} and held["keys"] == {A._norm("South River Golf Course") + "|MD"}
