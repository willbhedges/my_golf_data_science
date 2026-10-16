"""Offline tests for the product fixes (QA REPORT.md 5): one tee-line rule, the absurd-aim guard, lie mapping
at package load.  python3 -m pytest -q course_data/product"""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import importlib.util                               # noqa: E402

# platform/ also has a package.py: load the product's under its own name (pytest runs both in one process)
_spec = importlib.util.spec_from_file_location("product_package_under_test", os.path.join(HERE, "package.py"))
PK = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = PK
_spec.loader.exec_module(PK)
import decide                                       # noqa: E402

t = decide.t
PPY, TX, TY = 3.4, 460.0, 1900.0


@pytest.fixture(autouse=True)
def _restore_model():
    """decide.set_prior_means / bind change tee_strategy's globals: put them back for the other test files."""
    import copy
    names = ("CLUBS", "IRONS", "TREE_SEVERITY", "NATIVE_LOST", "MISHIT_RATE", "HCP_BASELINE", "HOLES")
    saved = {n: copy.deepcopy(getattr(t, n)) for n in names}
    yield
    for n, v in saved.items():
        setattr(t, n, v)


def px(x, along):
    return (TX + PPY * x, TY - PPY * along)


def rect(x0, x1, a0, a1):
    return [px(x0, a0), px(x1, a0), px(x1, a1), px(x0, a1)]


def hole(zones):
    return dict(par=4, length=420, tee=(TX, TY), dot270=px(0, 270), green=px(0, 420), zones=zones,
                aim_min=-60, aim_max=60, play_line=[px(0, 0), px(0, 420)])


def run_quick(holes, k):
    decide.bind(holes)
    t.HOLES = holes
    return decide.quick_hole(k, n=600)


def test_guard_rejects_aim_into_another_hole():
    """A wide fairway 75-130 yds right (another hole) and water across this hole's landing area: the model's
    unconstrained best aim is over there; the guard must flag CHECK and print an aim within 40 yds."""
    zones = [("fairway", rect(-25, 25, 120, 200)), ("fairway", rect(75, 130, 150, 420)),
             ("water", rect(-60, 25, 230, 330)), ("fairway", rect(-15, 15, 340, 420))]
    r = run_quick({1: hole(zones)}, 1)
    assert r["check"], r
    assert abs(r["aim"]) <= decide.GUARD_AIM and not decide.aim_problems(1, r["pick"], r["aim"])
    raw = [v["raw_aim"] for v in r["clubs"].values()]
    assert max(abs(a) for a in raw) > decide.GUARD_AIM                 # the guard did change something


def test_guard_no_printable_aim():
    """Water across every aim within 40 yds: no printable aim; the hole is CHECK and says so."""
    import book
    zones = [("fairway", rect(-25, 25, 120, 200)), ("fairway", rect(75, 130, 150, 420)),
             ("water", rect(-60, 60, 230, 330)), ("fairway", rect(-15, 15, 340, 420))]
    holes = {1: hole(zones)}
    r = run_quick(holes, 1)
    assert any(c.startswith("no printable") for c in r["check"])
    _, aim_at = book.notes_and_aims(holes, {}, {1: r}, {})
    assert aim_at[1].startswith("CHECK: no safe aim")


def test_guard_quiet_on_a_normal_hole():
    zones = [("fairway", rect(-18, 18, 150, 420)), ("recovery", rect(-90, -35, 100, 420)),
             ("recovery", rect(35, 90, 100, 420))]
    r = run_quick({1: hole(zones)}, 1)
    assert r["check"] == [] and abs(r["aim"]) <= 15
    assert not decide.aim_problems(1, r["pick"], r["aim"])


def test_aim_problems_reasons():
    zones = [("fairway", rect(-18, 18, 150, 420)), ("water", rect(20, 60, 200, 320))]
    decide.bind({1: hole(zones)})
    assert decide.aim_problems(1, "Driver", 0.0) == []
    assert any("water" in p for p in decide.aim_problems(1, "Driver", 30.0))
    assert any("more than 40" in p for p in decide.aim_problems(1, "Driver", 45.0))
    h = hole(zones)
    h["play_line"] = [px(-80, 0), px(-80, 420)]                        # line of play far left
    decide.bind({1: h})
    assert any("line of play" in p for p in decide.aim_problems(1, "Driver", 0.0))


def test_book_prints_check():
    import book
    zones = [("fairway", rect(-25, 25, 120, 200)), ("fairway", rect(75, 130, 150, 420)),
             ("water", rect(-60, 60, 230, 330)), ("fairway", rect(-15, 15, 340, 420))]
    holes = {1: hole(zones)}
    r = run_quick(holes, 1)
    notes, aim_at = book.notes_and_aims(holes, {}, {1: r}, {})
    assert notes[1].startswith("CHECK THE MAP") and aim_at[1].startswith("CHECK")


def _ll_package(lies):
    """A one-hole package/1 in WGS84 with the given zone lies (straight hole north from the tee)."""
    lat, lon = 40.76, -91.14
    yd = 0.9144 / 111320
    k = 1 / np.cos(np.radians(lat))

    def ll(x, a):
        return [lon + x * yd * k, lat + a * yd]

    def box(x0, x1, a0, a1):
        return [ll(x0, a0), ll(x1, a0), ll(x1, a1), ll(x0, a1)]
    zl = [dict(lie=lie, poly=box(*b), src="osm:course_boundary" if lie == "ob_boundary" else "osm", p=1.0)
          for lie, b in lies]
    h = dict(ref="1", par=4, length=400, yards={"Black": 400}, tee_ll=ll(0, 0), aim_ll=ll(0, 100),
             green_ll=ll(0, 400), hole_line_ll=[ll(0, -5), ll(0, 200), ll(0, 400)],
             tees={"Black": dict(tee_ll=ll(0, 0), aim_ll=ll(0, 100), card_yards=400)}, zones_ll=zl)
    return {"schema": "course_package/1", "course": {"name": "Test", "slug": "test", "center": [lon, lat]},
            "tee_set": "Black", "tee_sets": {"Black": {"aliases": []}}, "holes": {"1": h}}


def test_green_and_ob_boundary_mapped_at_load(tmp_path):
    """QA A1: 'green' and 'ob_boundary' (allowed in zones_ll) are mapped when the package is loaded, so
    tee_strategy (unchanged) scores every lie."""
    pkg = _ll_package([("fairway", (-20, 20, 150, 380)), ("green", (-12, 12, 385, 415)),
                       ("ob_boundary", (60, 120, 0, 450)), ("tee", (-5, 5, -5, 5))])
    p = tmp_path / "package.json"
    p.write_text(json.dumps(pkg))
    C = PK.load(str(p), "Black")
    lies = {z for z, _ in C.holes[1]["zones"]}
    assert lies <= PK.MODEL_LIES and {"fairway", "ob"} <= lies
    decide.bind(C.holes)
    t.HOLES = C.holes
    for aim in (0.0, 80.0):
        _, lie, _, strokes = t.simulate(1, "Driver", aim, n=400, z=decide._z(400, 1))
        assert np.isfinite(strokes).all()


def test_tee_line_matches_platform_rule(tmp_path):
    """One rule: the product's tee line is platform/tee_line.aim_point (the package's aim_ll rule)."""
    pkg = _ll_package([("fairway", (-20, 20, 150, 380))])
    p = tmp_path / "package.json"
    p.write_text(json.dumps(pkg))
    C = PK.load(str(p), "Black")
    h = pkg["holes"]["1"]
    aim, how = PK._tee_line_mod().aim_point(h["tee_ll"], h["hole_line_ll"], h["green_ll"], 400, 4)
    assert C.frames[1]["aim"] == how == "landing"
    assert np.allclose(C.frames[1]["aim_ll"], aim, atol=1e-9)
    # straight 400-yd hole: min(250, 62% of 400 = 248) yds up the tee line
    d = (aim[1] - h["tee_ll"][1]) * 111320 / 0.9144
    assert d == pytest.approx(248, abs=0.5)


@pytest.mark.parametrize("slug,tees", [("spirit_hollow", "Black"), ("veenker", None), ("mozingo_lake", None)])
def test_real_packages_line_of_play_near_tee_line(slug, tees):
    """On the committed packages the hole line crosses 250 yds (or the short-hole cap) within 30 yds of the
    tee line on every tee hole: aims are read against a line over the landing area (QA R1)."""
    path = os.path.join(CD, "packages", slug, "package.json")
    if not os.path.exists(path):
        pytest.skip("package not built")
    C = PK.load(path, tees)
    bad = []
    for k, hd in C.holes.items():
        line = hd.get("play_line")
        if not line or C.frames[k]["aim"] != "landing":
            continue
        rel = (np.asarray(line, float) - (TX, TY)) / PPY
        along, lat = -rel[:, 1], rel[:, 0]
        want = min(250, 0.62 * hd["length"])
        x = np.interp(want * 0.98, along, lat) if np.all(np.diff(along) > 0) else None
        if x is not None and abs(x) > 30:
            bad.append((k, round(float(x))))
    assert not bad, bad
