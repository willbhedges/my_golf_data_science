"""Contract tests for every auto-built course package (QA, course_data/qa/).

  python3 -m pytest course_data/qa/test_contracts.py -q            # all packages on disk
  QA_PACKAGE=spirit_hollow python3 -m pytest course_data/qa/test_contracts.py -q

Checks, per ARCHITECTURE.md (sections 3.5 / 3.8 and the platform package contract):
  schema    every hole has par, tee, green, bearing, zones with known lie names, provenance
  geometry  tee -> green length within 15% of the card; green inside the course boundary (+25 yds);
            tee not inside a hazard; zones are valid simple polygons (>= 3 vertices, finite, non-zero area)
  model     mozingo/tee_strategy.best_aim runs on every hole (Driver, 1,000 swings) without error and
            returns a finite EV
"""
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packages as P                                     # noqa: E402

WANT = os.environ.get("QA_PACKAGE")
PKGS = [p for p in P.find_packages() if not WANT or WANT in p.slug or WANT in p.path]
HOLES = [(pk, ref) for pk in PKGS for ref in pk.holes]
LEN_TOL = 0.15
BOUNDARY_SLACK_YD = 25


def hid(x):
    return f"{x[0].id}-{x[1]}" if isinstance(x, tuple) else x.id


# ----------------------------------------------------------------------------- package level
@pytest.mark.parametrize("pk", PKGS, ids=hid)
def test_package_loads(pk):
    assert not pk.errors, pk.errors
    assert pk.holes, "no holes"


@pytest.mark.parametrize("pk", PKGS, ids=hid)
def test_hole_count(pk):
    refs = sorted(pk.holes, key=lambda r: (len(r), r))
    base = {r.rstrip("BF") for r in refs}
    assert len(base) in (9, 18), f"{len(base)} holes: {refs}"
    missing = [str(i) for i in range(1, len(base) + 1) if str(i) not in base]
    assert not missing, f"missing refs {missing}"


@pytest.mark.parametrize("pk", PKGS, ids=hid)
def test_course_identity(pk):
    c = pk.course or {}
    assert c.get("name"), "course name missing"


# ----------------------------------------------------------------------------- schema per hole
@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_schema(hole):
    pk, ref = hole
    q = pk.holes[ref]
    bad = []
    if q.par not in (3, 4, 5, 6):
        bad.append(f"par={q.par!r}")
    if not q.tee_ll:
        bad.append("no tee (lon/lat)")
    if not q.green_ll:
        bad.append("no green (lon/lat)")
    if q.bearing is None or not (0 <= float(q.bearing) < 360):
        bad.append(f"bearing={q.bearing!r}")
    if not q.zones_ll and q.par and q.par > 3:
        bad.append("no zones")
    unknown = sorted({str(lie) for lie, _ in q.zones_ll} - P.KNOWN_LIES)
    if unknown:
        bad.append(f"unknown zone names {unknown}")
    if not q.provenance:
        bad.append("no provenance")
    else:
        for k in ("tee", "green"):
            if k not in q.provenance:
                bad.append(f"provenance lacks '{k}'")
    if q.card is None:
        bad.append("no scorecard yardage for the tee set")
    assert not bad, "; ".join(bad)


# ----------------------------------------------------------------------------- geometry
@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_length_vs_card(hole):
    pk, ref = hole
    q = pk.holes[ref]
    if q.card is None or not q.tee_ll or not q.green_ll:
        pytest.skip("no card or no tee/green")
    if q.hole_line_ll and len(q.hole_line_ll) >= 2:
        pts = [q.tee_ll] + [p[:2] for p in q.hole_line_ll[1:-1]] + [q.green_ll]
        L, how = P.path_yd(pts), "along the hole line"
    else:
        L, how = P.dist_yd(q.tee_ll, q.green_ll), "straight"
    err = (L - float(q.card)) / float(q.card)
    assert abs(err) <= LEN_TOL, f"tee->green {L:.0f} yds ({how}) vs card {q.card} ({err:+.0%})"


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_green_inside_course(hole):
    from shapely.geometry import Point
    pk, ref = hole
    q = pk.holes[ref]
    b = course_boundary(pk)
    if b is None:
        pytest.skip("no course boundary available")
    if not q.green_ll:
        pytest.fail("no green")
    d = b.distance(Point(q.green_ll)) * 111320 / P.YD          # deg -> yds (rough, fine for slack test)
    assert d <= BOUNDARY_SLACK_YD, f"green {q.green_ll} is {d:.0f} yds outside the course boundary"


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_tee_inside_course(hole):
    from shapely.geometry import Point
    pk, ref = hole
    q = pk.holes[ref]
    b = course_boundary(pk)
    if b is None or not q.tee_ll:
        pytest.skip("no boundary / tee")
    d = b.distance(Point(q.tee_ll)) * 111320 / P.YD
    assert d <= BOUNDARY_SLACK_YD, f"tee {q.tee_ll} is {d:.0f} yds outside the course boundary"


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_tee_not_in_hazard(hole):
    pk, ref = hole
    q = pk.holes[ref]
    if not q.tee_ll:
        pytest.fail("no tee")
    lie = P.lie_at_ll(q, q.tee_ll)
    assert lie not in P.PENAL, f"tee {q.tee_ll} sits in '{lie}'"


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_green_not_in_hazard(hole):
    pk, ref = hole
    q = pk.holes[ref]
    if not q.green_ll:
        pytest.fail("no green")
    lie = P.lie_at_ll(q, q.green_ll)
    assert lie not in P.PENAL - {"sand"}, f"green centre {q.green_ll} sits in '{lie}'"


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_zones_valid_simple(hole):
    from shapely.geometry import LinearRing, Polygon
    pk, ref = hole
    q = pk.holes[ref]
    bad = []
    for i, (lie, poly) in enumerate(q.zones_ll):
        a = np.asarray(poly, float)
        if a.ndim != 2 or len(a) < 3 or not np.isfinite(a).all():
            bad.append(f"#{i} {lie}: {len(a)} vertices / non-finite")
            continue
        a = a[:, :2]
        if np.allclose(a[0], a[-1]) and len(a) > 3:
            a = a[:-1]
        try:
            ring = LinearRing(a)
            pg = Polygon(a)
        except Exception as e:                                     # noqa: BLE001
            bad.append(f"#{i} {lie}: {e}")
            continue
        if pg.area == 0:
            bad.append(f"#{i} {lie}: zero area")
        elif not ring.is_simple or not pg.is_valid:
            from shapely.validation import explain_validity
            bad.append(f"#{i} {lie}: {explain_validity(pg)}")
    assert not bad, f"{len(bad)}/{len(q.zones_ll)} bad zones: " + "; ".join(bad[:6])


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_bearing_points_at_green(hole):
    """The tee line (bearing) should point roughly at the hole: within 60 deg of tee->green
    (dog-legs aim at the first leg)."""
    pk, ref = hole
    q = pk.holes[ref]
    if q.bearing is None or not q.tee_ll or not q.green_ll:
        pytest.skip("no bearing")
    b2 = P.bearing_deg(q.tee_ll, q.green_ll)
    d = abs((float(q.bearing) - b2 + 180) % 360 - 180)
    lim = 20 if q.par == 3 else 60
    assert d <= lim, f"bearing {q.bearing:.0f} vs tee->green {b2:.0f} ({d:.0f} deg)"


# ----------------------------------------------------------------------------- the model runs
_Z = None


@pytest.mark.parametrize("hole", HOLES, ids=hid)
def test_tee_strategy_runs(hole):
    global _Z
    import tee_strategy as t
    pk, ref = hole
    q = pk.holes[ref]
    assert q.model is not None, "package could not be turned into a model hole"
    if _Z is None:
        rng = np.random.default_rng(3)
        _Z = np.vstack([rng.standard_normal((2, 1000)), rng.random((2, 1000))])
    saved = t.HOLES
    t.HOLES = {ref: q.model}
    try:
        r = t.best_aim(ref, "Driver", z=_Z)
    finally:
        t.HOLES = saved
    assert r is not None and math.isfinite(r["ev"]), r
    assert 1.5 < r["ev"] < 8, f"EV {r['ev']:.2f} out of range"


_BOUND = {}


def course_boundary(pk):
    if pk.id not in _BOUND:
        _BOUND[pk.id] = P.course_boundary(pk)
    return _BOUND[pk.id]
