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


TEE_SETS = [(pk, ref, ts) for pk in PKGS if pk.kind == "package.json" for ref in pk.holes
            for ts in (pk.holes[ref].tee_sets or {})]


@pytest.mark.parametrize("pk", [p for p in PKGS if p.kind == "package.json"], ids=hid)
def test_package_header(pk):
    """package/1 header: schema, course name/slug/state/boundary, tee_set, tee_sets, sources, stages."""
    r, bad = pk.raw, []
    if r.get("schema") != "course_package/1":
        bad.append(f"schema={r.get('schema')!r} (ARCHITECTURE 9.2 says course_package/1)")
    c = r.get("course") or {}
    for k in ("name", "slug", "state", "boundary", "bbox"):
        if not c.get(k):
            bad.append(f"course.{k} missing")
    if not pk.tee_set:
        bad.append("tee_set missing")
    if not isinstance(r.get("tee_sets"), dict) or not r.get("tee_sets"):
        bad.append("tee_sets missing")
    for k in ("sources", "stages", "built"):
        if not r.get(k):
            bad.append(f"{k} missing")
    rel = os.path.relpath(pk.path, P.CD).replace(os.sep, "/")
    if not rel.startswith("packages/") and "standin" not in rel:
        bad.append(f"location {rel} (ARCHITECTURE 9.2: packages/<slug>/package.json)")
    assert not bad, "; ".join(bad)


@pytest.mark.parametrize("hole", [(pk, ref) for pk in PKGS if pk.kind == "package.json" for ref in pk.holes], ids=hid)
def test_package_hole_fields(hole):
    """package/1 per-hole fields the product and wind page read (9.2): yards per set, tees per set,
    exposure, confidence, zone src."""
    pk, ref = hole
    h = pk.holes[ref].raw
    bad = []
    if not isinstance(h.get("yards"), dict):
        bad.append("yards{set: yds} missing")
    if not isinstance(h.get("tees"), dict) or not h.get("tees"):
        bad.append("tees{set: {...}} missing")
    if "exposure" not in h:
        bad.append("exposure missing (wind page needs it)")
    if not isinstance(h.get("confidence"), dict) or "score" not in h.get("confidence", {}):
        bad.append("confidence.score missing")
    for k in ("tee_ll", "aim_ll", "green_ll", "bearing_deg", "length"):
        if h.get(k) is None:
            bad.append(f"{k} missing")
    if not h.get("green_polygon_ll") and h.get("par") == 3:
        bad.append("green_polygon_ll missing")
    zs = h.get("zones_ll")
    if zs is None:
        bad.append("zones_ll missing (ARCHITECTURE 9.1-1: WGS84 zones are required)")
    elif not all(isinstance(z, dict) and z.get("lie") and z.get("poly") and z.get("src") for z in zs):
        bad.append("zones_ll entries are not {lie, poly, src, p} dicts with src")
    assert not bad, "; ".join(bad)


@pytest.mark.parametrize("hole", [(pk, ref) for pk in PKGS if pk.kind == "package.json" for ref in pk.holes], ids=hid)
def test_zones_match_zones_ll(hole):
    """`zones` (yard frame) must be `zones_ll` reframed (9.1-1: zones is derived by reframe()): same lies in the
    same order, and the landing grid gets the same lie from both."""
    pk, ref = hole
    q = pk.holes[ref]
    if not q.zones_yard:
        pytest.skip("no zones_ll + yard zones pair")
    a = [lie for lie, _ in q.zones_ll]
    b = [lie for lie, _ in q.zones_yard]
    assert sorted(a) == sorted(b), f"lies differ: zones_ll {len(a)} vs zones {len(b)}"
    from matplotlib.path import Path
    R = P._render()
    yfr = R.Frame(q.tee_ll, q.aim_ll, ppy=1.0, tee_px=(0, 0), proj="utm")
    al, la = np.meshgrid(np.arange(100, 400, 10.0), np.arange(-60, 61, 10.0))
    xy = np.c_[la.ravel(), -al.ravel()]
    ll = yfr.px_to_ll(xy)

    def lies(zs, pts):
        out = np.array(["rough"] * len(pts), dtype=object)
        for lie, poly in zs:
            out[Path(np.asarray(poly, float)[:, :2]).contains_points(pts)] = lie
        return out
    agree = float(np.mean(lies(q.zones_ll, ll) == lies(q.zones_yard, xy)))
    assert agree >= 0.98, f"zones vs zones_ll agree on only {agree:.0%} of the 100-400 yd grid"


@pytest.mark.parametrize("tset", TEE_SETS, ids=lambda x: f"{x[0].id}-{x[1]}-{x[2]}")
def test_every_tee_set(tset):
    """Each tee set's entry: tee_ll, aim_ll, bearing_deg, card yards, and the tee->green length along the
    hole line within 15% of that set's card yardage; tee not in a hazard."""
    pk, ref, ts = tset
    q = pk.holes[ref]
    e = q.tee_sets[ts]
    bad = []
    tll, all_ = P._ll(e.get("tee_ll")), P._ll(e.get("aim_ll"))
    if not tll:
        bad.append("no tee_ll")
    if not all_:
        bad.append("no aim_ll")
    if e.get("bearing_deg") is None:
        bad.append("no bearing_deg")
    card = e.get("card_yards") or P._ci(q.raw.get("yards"), ts)
    if not card:
        bad.append("no card yards")
    if tll and card and q.green_ll:
        L = P.dist_yd(tll, q.green_ll)
        if q.hole_line_ll and len(q.hole_line_ll) > 2:
            L = P.path_yd([tll] + [p[:2] for p in q.hole_line_ll[1:-1]] + [q.green_ll])
        if abs(L - card) / card > LEN_TOL:
            bad.append(f"length {L:.0f} vs card {card} ({(L - card) / card:+.0%})")
    if tll:
        lie = P.lie_at_ll(q, tll)
        if lie in P.PENAL:
            bad.append(f"tee in '{lie}'")
    assert not bad, "; ".join(bad)


@pytest.mark.parametrize("pk", PKGS, ids=hid)
def test_model_understands_lies(pk):
    """Every zone name a package uses must be scorable by tee_strategy (BASELINE + _lie_mixture) as-is;
    ARCHITECTURE 9.1-4 allows 'green' and 'ob_boundary' in packages, so the model or every consumer must map them."""
    import tee_strategy as t
    names = sorted({lie for q in pk.holes.values() for lie, _ in q.zones_ll})
    bad = []
    for n in names:
        try:
            v = t.expected_strokes(n, np.array([150.0]))
            assert np.isfinite(v).all()
        except Exception as e:                                     # noqa: BLE001
            bad.append(f"{n}: {type(e).__name__}: {e}")
    assert not bad, "tee_strategy cannot score " + "; ".join(bad)


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
