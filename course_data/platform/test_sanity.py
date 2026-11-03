"""sanity.py guards (review-found pipeline errors) + package.py's use of the card consensus. Synthetic OSM."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import package as pk  # noqa: E402
import sanity  # noqa: E402

LON0, LAT0 = -94.6, 38.9
KX = math.cos(math.radians(LAT0)) * 111320 / 0.9144
KY = 111320 / 0.9144


def ll(x, y):
    """yards east / north of the origin -> [lon, lat]"""
    return [LON0 + x / KX, LAT0 + y / KY]


def poly(cx, cy, r=8, **props):
    ring = [ll(cx - r, cy - r), ll(cx + r, cy - r), ll(cx + r, cy + r), ll(cx - r, cy + r), ll(cx - r, cy - r)]
    return dict(type="Feature", geometry=dict(type="Polygon", coordinates=[ring]), properties=props)


def line(pts, **props):
    return dict(type="Feature", geometry=dict(type="LineString", coordinates=[ll(*p) for p in pts]), properties=props)


def tee_at(fc_tp, ref, s, x, y, method="walkback"):
    lon, lat = ll(x, y)
    fc_tp["holes"].setdefault(ref, {"tees": {}})["tees"][s] = dict(lon=lon, lat=lat, method=method)


def yards_of(r):
    return ((r["lon"] - LON0) * KX, (r["lat"] - LAT0) * KY)


# ----------------------------------------------------------------------------- practice tees (Ironhorse 1)
def test_practice_tees_dropped_by_name_and_range_area():
    fc = dict(features=[
        poly(0, 0, golf="tee", osm_id=1, name="Driving Range Tee Box (Turf)"),
        poly(500, 0, golf="tee", osm_id=2),                            # inside the range polygon
        poly(500, 0, r=60, golf="driving_range", osm_id=3),
        poly(0, 300, golf="tee", osm_id=4, name="Tee 1"),
        poly(0, 400, golf="tee", osm_id=5, description="practice putting"),
    ])
    out, dropped = sanity.drop_practice_tees(fc)
    assert sorted(dropped) == [1, 2, 5]
    assert [f["properties"]["osm_id"] for f in out["features"] if f["properties"].get("golf") == "tee"] == [4]


# ----------------------------------------------------------------------------- neighbour's hole ways (Pevely)
def test_neighbour_course_hole_ways_dropped():
    feats = [line([(i * 100, 0), (i * 100, 400)], golf="hole", ref=str(i + 1), osm_id=100 + i, inside_course=True)
             for i in range(18)]
    feats += [line([(i * 100, 2000), (i * 100, 2400)], golf="hole", ref=str(i + 1), osm_id=200 + i,
                   inside_course=False) for i in (0, 8, 9, 17)]
    out, dropped = sanity.select_hole_ways(dict(features=feats))
    assert sorted(dropped) == [200, 208, 209, 217]
    assert len([f for f in out["features"] if f["properties"]["golf"] == "hole"]) == 18
    # no duplicates and <= 18 ways: untouched
    same, d2 = sanity.select_hole_ways(dict(features=feats[:18]))
    assert d2 == [] and len(same["features"]) == 18


def test_supplement_hole_ways_replace_osm_by_ref_and_are_never_dropped():
    # Creekmoor 10 (qa_rebuild.md): live OSM and the supplement both carry refs 1-18; the ref-10 way's midpoint is
    # outside the course boundary (inside_course False) and the duplicate refs dropped both copies
    osm = [line([(i * 100, 0), (i * 100, 400)], golf="hole", ref=str(i + 1), osm_id=100 + i,
                inside_course=(i != 9)) for i in range(18)]
    hand = [line([(i * 100, 0), (i * 100, 410)], golf="hole", ref=str(i + 1), osm_id=100 + i, src="hand",
                 inside_course=(i != 9)) for i in range(18)]
    out, notes = sanity.clean_osm(dict(features=osm + hand))
    holes = [f for f in out["features"] if f["properties"]["golf"] == "hole"]
    assert len(holes) == 18 and all(f["properties"].get("src") == "hand" for f in holes)
    assert any("osm_supplement" in n for n in notes) and not any("neighbouring" in n for n in notes)
    # a hand way outside the boundary survives even when the neighbour filter runs
    extra = [line([(0, 2000), (0, 2400)], golf="hole", ref="1", osm_id=900, inside_course=False)]
    out, dropped = sanity.select_hole_ways(dict(features=hand + extra))
    assert dropped == [900] and any(f["properties"]["ref"] == "10" for f in out["features"])


# ----------------------------------------------------------------------------- hole lines inside the boundary (Hodge 10)
NOTCH = [(0, 0), (1000, 0), (1000, 1000), (600, 1000), (600, 600), (400, 600), (400, 1000), (0, 1000), (0, 0)]


def _fcm():
    sys.path.insert(0, os.path.dirname(HERE))
    import fetch_course
    return fetch_course


def _summarised(feats, ring=NOTCH):
    fcm = _fcm()
    fc = dict(type="FeatureCollection", features=feats)
    fcm.summarise(fc, None, [], [[ll(*p) for p in ring]])
    return fc


def test_dogleg_round_a_boundary_notch_is_inside():
    """Hodge Park 10: every vertex inside, the vertex mean in a notch of the boundary (maintenance yard)."""
    fcm = _fcm()
    wrap = [(370, 950), (370, 570), (630, 570), (630, 950)]                 # mean (500, 760): in the notch
    assert not fcm.point_in_ring(fcm.rep_point(line(wrap)["geometry"]), [ll(*p) for p in NOTCH])
    cut = [(380, 950), (500, 560), (620, 950)]                              # cuts through the notch, ends inside
    out = [(1200, 100), (1200, 500)]                                       # a neighbour's hole
    stray = [(950, 100), (1300, 100), (1300, 700)]                         # only the tee end inside
    fc = _summarised([line(wrap, golf="hole", ref="10", osm_id=1), line(cut, golf="hole", ref="11", osm_id=2),
                      line(out, golf="hole", ref="12", osm_id=3), line(stray, golf="hole", ref="13", osm_id=4),
                      poly(500, 800, golf="green", osm_id=5)])
    p = {f["properties"]["osm_id"]: f["properties"] for f in fc["features"]}
    assert p[1]["inside_course"] is True and p[1]["inside_frac"] == 1.0
    assert p[2]["inside_course"] is True and p[2]["inside_frac"] < 0.6    # in by both end stretches
    assert p[3]["inside_course"] is False and p[3]["inside_frac"] == 0.0
    assert p[4]["inside_course"] is False
    assert p[5]["inside_course"] is False                                  # polygons: unchanged (vertex mean)


def _course18(ten_inside=True, ten_frac=None):
    """18 holes of this course (tee box at the start, green at the end), hole 10 a dogleg."""
    feats = []
    for i in range(18):
        x = i * 100
        pts = [(x, 0), (x, 200), (x + 40, 400)] if i == 9 else [(x, 0), (x, 400)]
        pr = dict(golf="hole", ref=str(i + 1), osm_id=100 + i, inside_course=(ten_inside if i == 9 else True))
        if i == 9 and ten_frac is not None:
            pr["inside_frac"] = ten_frac
        feats.append(line(pts, **pr))
        feats.append(poly(pts[-1][0], pts[-1][1] + 5, r=12, golf="green", osm_id=300 + i))
        feats.append(poly(x, -5, r=5, golf="tee", osm_id=400 + i))
    return feats


def test_duplicate_ref_keeps_this_courses_way_not_neither():
    """Hodge Park 10: this course's 10 flagged outside (old vertex-mean rule) + a neighbour's 10 -> both used to go."""
    nb = [line([(5000, 0), (5000, 380)], golf="hole", ref="10", osm_id=898574075, inside_course=False),
          poly(5000, 385, r=12, golf="green", osm_id=999, inside_course=False)]
    out, dropped = sanity.select_hole_ways(dict(features=_course18(ten_inside=False) + nb))
    ten = [f for f in out["features"] if f["properties"].get("golf") == "hole" and f["properties"]["ref"] == "10"]
    assert dropped == [898574075]
    assert [f["properties"]["osm_id"] for f in ten] == [109] and ten[0]["properties"]["inside_course"] is True
    # both copies inside: the one with more of its length inside wins (and is connected)
    feats = _course18(ten_frac=0.95) + [line([(900, 2000), (900, 2400)], golf="hole", ref="10", osm_id=777,
                                             inside_course=True, inside_frac=0.62)]
    out, dropped = sanity.select_hole_ways(dict(features=feats))
    assert dropped == [777]
    # a neighbour's duplicate with no tie to this course's greens / tees still goes when ours is flagged outside
    # and unconnected too: both are dropped (nothing says either is ours)
    lone = [line([(0, 3000), (0, 3400)], golf="hole", ref="1", osm_id=801, inside_course=False),
            line([(0, 5000), (0, 5400)], golf="hole", ref="1", osm_id=802, inside_course=False)]
    out, dropped = sanity.select_hole_ways(dict(features=_course18()[3:] + lone))
    assert sorted(dropped) == [801, 802]


HODGE = os.path.join(os.path.dirname(HERE), "packages", "hodge_park", "raw")
HODGE_SUP = os.path.join(os.path.dirname(HERE), "library", "hodge_park", "osm_supplement.geojson")


def test_hodge_park_hole_10_survives_summarise_and_clean_osm():
    import json
    import pytest
    if not (os.path.exists(os.path.join(HODGE, "osm.geojson")) and os.path.exists(os.path.join(HODGE, "course.json"))):
        pytest.skip("hodge_park raw OSM not in this checkout")
    fcm = _fcm()
    fc = json.load(open(os.path.join(HODGE, "osm.geojson")))
    course = json.load(open(os.path.join(HODGE, "course.json")))
    for f in fc["features"]:
        f["properties"].pop("inside_course", None)
    fcm.summarise(fc, None, [], fcm.outer_rings(course["boundary"]))
    by = {f["properties"].get("osm_id"): f["properties"] for f in fc["features"]}
    assert by[1565676856]["inside_course"] is True and by[898574075]["inside_course"] is False
    out, notes = sanity.clean_osm(fc, names=["Hodge Park Golf Course"])
    holes = {f["properties"]["osm_id"]: f["properties"]["ref"] for f in out["features"]
             if f["properties"].get("golf") == "hole"}
    assert holes.get(1565676856) == "10" and 898574075 not in holes
    assert sorted(int(r) for r in holes.values()) == list(range(1, 19))
    # the hand supplement (rv14) still wins by ref
    if os.path.exists(HODGE_SUP):
        sup = json.load(open(HODGE_SUP))["features"]
        for i, f in enumerate(sup):
            f["properties"].update(src="hand", osm_id=-(i + 1), osm_type="hand")
        fc2 = json.load(open(os.path.join(HODGE, "osm.geojson")))
        fc2["features"] += sup
        for f in fc2["features"]:
            f["properties"].pop("inside_course", None)
        fc2, _ = sanity.supplement_hole_ways(fc2)
        fcm.summarise(fc2, None, [], fcm.outer_rings(course["boundary"]))
        out2, _ = sanity.clean_osm(fc2, names=["Hodge Park Golf Course"])
        ten = [f["properties"] for f in out2["features"] if f["properties"].get("golf") == "hole"
               and f["properties"]["ref"] == "10"]
        assert len(ten) == 1 and ten[0]["src"] == "hand" and ten[0]["inside_course"] is True


# ----------------------------------------------------------------------------- tee guards
def _hole_fc(extra=()):
    # hole 1: line start (0, 0) -> green at (0, 340); a road behind it at y = -30, another green at y = -60
    return dict(features=[line([(0, 0), (0, 340)], golf="hole", ref="1"),
                          poly(0, 345, r=12, golf="green", osm_id=11)] + list(extra))


def test_back_tee_walked_forward_is_capped_and_checked():
    """Lake Shawnee page 4: a 339-yd par 4 made a 148-yd par 3 by walking the tee 190 yds up the line."""
    fc = _hole_fc()
    tp = dict(holes={})
    tee_at(tp, "1", "Blue", 0, 192)
    tee_at(tp, "1", "Red", 0, 230)
    notes = sanity.guard_tees(tp, fc)
    blue, red = tp["holes"]["1"]["tees"]["Blue"], tp["holes"]["1"]["tees"]["Red"]
    assert blue["method"] == "walkback_capped" and abs(yards_of(blue)[1]) < 1 and blue["check"]
    assert red["check"] and red["method"] == "walkback"                  # flagged, not moved
    assert len(notes) == 2


def test_forward_sets_are_left_alone():
    fc = _hole_fc([poly(0, -10, golf="tee", osm_id=20)])
    tp = dict(holes={})
    tee_at(tp, "1", "Black", 0, -5, method="tee_axis")
    tee_at(tp, "1", "Red", 0, 150)                                     # a real forward tee
    assert sanity.guard_tees(tp, fc) == []
    assert "check" not in tp["holes"]["1"]["tees"]["Red"]


def test_walkback_capped_before_green_road_building():
    """St Andrews 16 (onto the 15th green), Colbert 1 (car park), The Falls (road / houses)."""
    for obstacle in (poly(0, -40, r=10, golf="green", osm_id=15),
                     poly(0, -40, r=10, amenity="parking", osm_id=16),
                     poly(0, -40, r=10, building="yes", osm_id=17),
                     line([(-200, -35), (200, -35)], highway="residential", osm_id=18)):
        fc = _hole_fc([obstacle])
        tp = dict(holes={})
        tee_at(tp, "1", "Black", 0, -60)
        tee_at(tp, "1", "Red", 0, 100, method="tee_centroid")           # a second set on the hole
        notes = sanity.guard_tees(tp, fc)
        r = tp["holes"]["1"]["tees"]["Black"]
        y = yards_of(r)[1]
        assert r["method"] == "walkback_capped" and r["check"] and notes, obstacle["properties"]
        assert -30 < y <= 0, (obstacle["properties"], y)


def test_capped_walkback_then_another_walkback_set_no_keyerror():
    """us60 batch (Harbour Town, Memorial Park, Seneca, Theodore Wirth, Harding Park): the obstacle cap
    overwrote the back-tee key `back` with a distance, so the next walk-back set hit alongs[17.0] -> KeyError."""
    fc = _hole_fc([poly(0, -40, r=10, building="yes", osm_id=17)])
    tp = dict(holes={})
    tee_at(tp, "1", "Black", 0, -60)                                   # capped by the building
    tee_at(tp, "1", "Blue", 0, -10)                                    # a second walk-back set after it
    tee_at(tp, "1", "White", 0, 40)
    sanity.guard_tees(tp, fc)
    tees = tp["holes"]["1"]["tees"]
    assert tees["Black"]["method"] == "walkback_capped"
    assert "check" not in tees["White"] and tees["White"]["method"] == "walkback"


def test_cart_path_does_not_cap():
    fc = _hole_fc([line([(-200, -20), (200, -20)], highway="service", golf="cartpath", osm_id=19)])
    tp = dict(holes={})
    tee_at(tp, "1", "Black", 0, -30)
    assert sanity.guard_tees(tp, fc) == []


# ----------------------------------------------------------------------------- routed holes
def test_routed_hole_on_used_green_is_reassigned_or_rejected():
    """Ironhorse 18 was routed to hole 4's green (1607 yds as a par 5); an unused green fits the card."""
    fc = dict(features=[line([(0, 0), (0, 500)], golf="hole", ref="4")])
    res = dict(holes={"18": dict(tee_ll=ll(1000, 0), green_ll=ll(0, 505), green_id="osm:way/4", par=4,
                                 card_yards=[475, 434], flags=[], status="ok")})
    greens = [dict(id="osm:way/4", ll=ll(0, 505)), dict(id="osm:way/97", ll=ll(1000, 472))]
    notes = sanity.guard_routed(res, fc, ["18"], greens)
    h = res["holes"]["18"]
    assert h["green_id"] == "osm:way/97" and h["status"] == "check" and notes
    # no unused green fits: flagged, and the absurd length rejects the hole
    res = dict(holes={"18": dict(tee_ll=ll(1600, 0), green_ll=ll(0, 505), green_id="osm:way/4", par=5,
                                 card_yards=[475], flags=[], status="ok")})
    sanity.guard_routed(res, fc, ["18"], greens[:1])
    h = res["holes"]["18"]
    assert h["status"] == "rejected" and "green_ll" not in h


def test_length_reason_limits():
    assert sanity.length_reason(1607, 5, [475]) and sanity.length_reason(300, 3, [])
    assert sanity.length_reason(470, 4, [475]) is None and sanity.length_reason(690, 5, []) is None


# ----------------------------------------------------------------------------- renumbering (Swope)
def test_renumber_swope_front_nine():
    card_pars = [4, 4, 4, 4, 5, 3, 4, 3, 5]
    card_yds = [380, 400, 330, 368, 451, 170, 360, 150, 520]
    # OSM way for card hole i is ref osm_of[i]
    osm_of = [1, 2, 8, 9, 6, 7, 3, 4, 5]
    feats = []
    for i, r in enumerate(osm_of):
        L = card_yds[i] - 5
        feats.append(line([(i * 150, 0), (i * 150, L)], golf="hole", ref=str(r), par=str(card_pars[i])))
    card = dict(par=card_pars, tee_sets={"Blue": dict(yards=card_yds)})
    fc2, mapping = sanity.renumber_holes(dict(features=feats), card)
    assert mapping == {"8": "3", "9": "4", "6": "5", "7": "6", "3": "7", "4": "8", "5": "9"}
    refs = [f["properties"]["ref"] for f in fc2["features"]]
    assert refs == [str(i + 1) for i in range(9)]
    # already in card order: nothing changes
    same, m2 = sanity.renumber_holes(fc2, card)
    assert m2 == {}


# ----------------------------------------------------------------------------- card consensus in package.py
def _ground(lengths):
    return {str(i + 1): dict(line=y, tees=[y]) for i, y in enumerate(lengths)}


def test_consensus_card_rejects_scrambled_and_needs_ground():
    true = [400, 380, 170, 520, 410, 360, 190, 540, 430] * 2
    scr = true[:1] + true[10:18] + true[9:]                              # Eagle Bend golfify: 2-9 are 11-18
    scr = [y + (25 if i in range(1, 9) else 0) for i, y in enumerate(scr)]
    pars = [4, 4, 3, 5, 4, 4, 3, 5, 4] * 2
    web = [dict(source="golfify", card=dict(par=pars, tee_sets={"Blue": dict(yards=scr)}), url="g"),
           dict(source="opengolfapi", card=dict(par=pars, tee_sets={"Blue": dict(yards=true)}), url="o")]
    card, info = pk.consensus_card(web, _ground(true))
    assert info["kind"] == "opengolfapi" and card["tee_sets"]["Blue"]["yards"] == true
    assert any("scrambled" in f for f in info["consensus"]["flags"])
    assert pk.consensus_card(web, _ground(true[:4])) is None             # too little ground: choose_card


def test_consensus_converts_metres(tmp_path):
    true = [400, 380, 170, 520, 410, 360, 190, 540, 430] * 2
    m = [round(y * 0.9144) for y in true]
    pars = [4, 4, 3, 5, 4, 4, 3, 5, 4] * 2
    web = [dict(source="allsquare", card=dict(par=pars, tee_sets={"Blue": dict(yards=m)}), url="a")]
    card, info = pk.consensus_card(web, _ground(true))
    assert abs(card["tee_sets"]["Blue"]["yards"][0] - 400) <= 1
    assert any("metres" in f for f in info["consensus"]["flags"])


# ----------------------------------------------------------------------------- hole refs (us60 finish failures)
def _ways(refs, x0=0):
    return [line([(x0 + i * 50, 0), (x0 + i * 50, 300)], golf="hole", ref=r, osm_id=1000 + x0 + i)
            for i, r in enumerate(refs)]


def _refs(fc):
    return sorted((f["properties"]["ref"] for f in fc["features"] if f["properties"].get("golf") == "hole"),
                  key=lambda r: (len(r), r))


def test_hole_refs_named_course_group_kept_and_renumbered():
    """Bethpage ("Black - 13", v2 hole_number crashed on int()), Pinehurst ("1 - #2" beside plain 1..27 + tee_boxes)."""
    fc = dict(features=_ways([f"Black - {i}" for i in range(1, 19)]) + _ways([f"Red - {i}" for i in range(1, 19)], 5000))
    out, notes = sanity.clean_osm(fc, names=["Bethpage Black Course", "Bethpage State Park"])
    assert _refs(out) == [str(i) for i in range(1, 19)]
    assert all(f["properties"]["ref_osm"].startswith("Black") for f in out["features"])
    assert any("black" in n for n in notes) and any("Red - 1" in n for n in notes)
    fc = dict(features=_ways([str(i) for i in range(1, 28)]) + _ways([f"{i} - #2" for i in range(1, 19)], 5000)
              + _ways(["tee_boxes"], 9000))
    out, _ = sanity.clean_osm(fc, names=["Pinehurst No. 2"])
    assert _refs(out) == [str(i) for i in range(1, 19)]
    assert {f["properties"]["ref_osm"] for f in out["features"]} == {f"{i} - #2" for i in range(1, 19)}


def test_hole_refs_practice_and_lettered_nines_dropped_plain_kept():
    """Old Works ("Practice 1..3" beside 1..18), Neshanic Valley (1..18 + A1 / L1 / M1 / R1 / P1 nines)."""
    fc = dict(features=_ways([str(i) for i in range(1, 19)] + ["Practice 1", "Practice 2", "Practice 3"]))
    out, notes = sanity.clean_osm(fc, names=["Old Works Golf Course"])
    assert _refs(out) == [str(i) for i in range(1, 19)] and notes
    fc = dict(features=_ways([str(i) for i in range(1, 19)]) + _ways([f"{c}{i}" for c in "ALMR" for i in range(1, 10)],
                                                                      5000))
    out, _ = sanity.clean_osm(fc, names=["Neshanic Valley Golf Course"])
    assert _refs(out) == [str(i) for i in range(1, 19)]


def test_hole_refs_only_qualified_largest_group_and_plain_untouched():
    fc = dict(features=_ways([f"Hole {i}" for i in range(1, 19)]))
    out, _ = sanity.clean_osm(fc, names=["Somewhere"])
    assert _refs(out) == [str(i) for i in range(1, 19)]
    plain = dict(features=_ways([str(i) for i in range(1, 19)]))
    same, notes = sanity.normalize_hole_refs(plain, ["X"])
    assert same is plain and notes == []
    assert sanity.parse_hole_ref("tee_boxes") is None
    assert sanity.parse_hole_ref("Monument 3") == (("monument",), 3)


# ----------------------------------------------------------------------------- 36-hole facilities (one OSM outline)
def _two_courses(name_a=None, name_b=None, polys=False):
    """Two 18-hole courses in ONE outline, refs 1-18 each, every way inside it: course A west (x -1800..-100),
    course B east (x 3000..4700), holes alternating north / south so green n is by tee n+1. A per-ref pick
    (select_hole_ways) can mix them."""
    feats = []
    for c, (x0, sgn, oid, nm) in enumerate(((-1800, -1, 1000, name_a), (3000, 1, 2000, name_b))):
        for i in range(18):
            x = x0 + i * 100
            y0 = 0 if i % 2 == 0 else 450
            pts = [(x, y0), (x, 450 - y0)]
            pr = dict(golf="hole", ref=str(i + 1), osm_id=oid + i, inside_course=True)
            feats.append(line(pts, **pr))
            feats.append(poly(pts[-1][0], pts[-1][1], r=12, golf="green", osm_id=oid + 100 + i))
            feats.append(poly(pts[0][0], pts[0][1], r=5, golf="tee", osm_id=oid + 200 + i))
        if polys:
            ring = [ll(x0 - 150, -200), ll(x0 + 1850, -200), ll(x0 + 1850, 700), ll(x0 - 150, 700), ll(x0 - 150, -200)]
            feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[ring]),
                              properties=dict(leisure="golf_course", name=nm, osm_id=oid + 900)))
    outer = [ll(-2500, -500), ll(5500, -500), ll(5500, 1000), ll(-2500, 1000), ll(-2500, -500)]
    feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[outer]),
                      properties=dict(leisure="golf_course", osm_id=1)))
    return feats


def _hole_ids(fc):
    return sorted(f["properties"]["osm_id"] for f in fc["features"] if f["properties"].get("golf") == "hole")


def test_36_holes_in_one_outline_named_sub_courses_pick_the_request():
    """Troon North: Monument + Pinnacle inside one club outline; the request names Monument."""
    feats = _two_courses("Monument Course", "Pinnacle Course", polys=True)
    out, notes = sanity.clean_osm(dict(features=feats), names=["Troon North Monument", "Troon North Golf Club"])
    assert _hole_ids(out) == list(range(1000, 1018)), notes
    assert any("Monument" in n for n in notes)
    out, _ = sanity.clean_osm(dict(features=feats), names=["Troon North Pinnacle"])
    assert _hole_ids(out) == list(range(2000, 2018))


def test_36_holes_unnamed_outline_near_point_picks_the_nearest_course():
    """Queenstown Harbor: River + Lakes, 36 plain-numbered hole ways in one unnamed outline: never a per-ref mix;
    the request's near point picks the course whose hole lines are nearest."""
    feats = _two_courses()
    near = ll(3800, 200)[::-1]                           # (lat, lon) by course B
    out, notes = sanity.clean_osm(dict(features=feats), names=["Queenstown Harbor River Course"], near=near)
    assert _hole_ids(out) == list(range(2000, 2018)), notes
    near = ll(-1000, 200)[::-1]
    out, _ = sanity.clean_osm(dict(features=feats), names=["Queenstown Harbor River Course"], near=near)
    assert _hole_ids(out) == list(range(1000, 1018))
    # no near, no names: still one whole course (never a mix), and a CHECK note
    out, notes = sanity.clean_osm(dict(features=feats), names=[])
    assert _hole_ids(out) in (list(range(1000, 1018)), list(range(2000, 2018)))
    assert any("CHECK" in n for n in notes)


def test_split_courses_chains_follow_green_to_next_tee():
    """No sub-course polygons: the holes are grouped by walking green n -> nearest tee n+1, so the two courses
    come out whole even when they interleave by ref."""
    groups = sanity.course_groups(dict(features=_two_courses()))
    assert sorted(sorted(f["properties"]["osm_id"] for f in g["holes"]) for g in groups) == \
        [list(range(1000, 1018)), list(range(2000, 2018))]


def test_one_neighbour_duplicate_is_not_a_facility_split():
    """Hodge Park / Pevely Farms: a few duplicated refs from a neighbour stay select_hole_ways' job."""
    nb = [line([(5000, 0), (5000, 380)], golf="hole", ref="10", osm_id=898574075, inside_course=False)]
    out, notes = sanity.split_courses(dict(features=_course18() + nb), names=["x"])
    assert notes == [] and len(_hole_ids(out)) == 19


FIX = os.path.join(HERE, "fixtures")
QH_RIVER = {814359274, 814359293, 69343493, 69343494, 69343495, 69343496, 69343487, 69343488, 69343489,
            885395002, 885395009, 885395018, 885398042, 885398043, 885398044, 885398045, 885398057, 885398071}


def _fix(name):
    import json
    return json.load(open(os.path.join(FIX, name)))


def test_queenstown_harbor_river_course_from_live_osm():
    """Live OSM (2026-11-03): River + Lakes in one unnamed outline; River's 3, 6-9 have no ref, only names
    ('#7 - par 4', 'River # 9 - par 4'). The request 'Queenstown Harbor River Course' keeps River's 18 whole,
    numbered 1-18 (refs from the names), never a per-ref mix of the two courses."""
    out, notes = sanity.clean_osm(_fix("queenstown_harbor_holes.geojson"), names=["Queenstown Harbor River Course"],
                                  near="38.9850,-76.1700")
    holes = [f for f in out["features"] if f["properties"].get("golf") == "hole"]
    assert {f["properties"]["osm_id"] for f in holes} == QH_RIVER, notes
    assert sorted(int(f["properties"]["ref"]) for f in holes) == list(range(1, 19))
    assert any("river" in n for n in notes)


def test_troon_north_monument_from_live_osm():
    fc = _fix("troon_north_holes.geojson")
    for want in ("Monument", "Pinnacle"):
        out, notes = sanity.clean_osm(fc, names=[f"Troon North {want}", "Troon North Golf Club"])
        holes = [f for f in out["features"] if f["properties"].get("golf") == "hole"]
        assert len(holes) == 18 and {f["properties"]["golf:course:name"] for f in holes} == {f"{want} Course"}, notes
        assert sorted(int(f["properties"]["ref"]) for f in holes) == list(range(1, 19))


# ----------------------------------------------------------------------------- nine-hole groups (27-hole facilities)
def _nines(refs=((1, 9), (1, 9), (1, 9)), names=(None, None, None), outlines=None, same_greens=False):
    """Three nines side by side (nine c at x = c*2000 ..), holes alternating north / south so green n is by tee
    n+1; nine c's ways have osm_id 1000*(c+1)+n. refs: each nine's (first, last) number. names: a hole-name word
    per nine ('Red 3'). outlines: a leisure=golf_course name per nine. same_greens: every nine on nine 0's ground
    (a nine-hole course mapped twice)."""
    feats = []
    for c, ((lo, hi), nm) in enumerate(zip(refs, names)):
        x0 = 0 if same_greens else c * 2000
        for i, n in enumerate(range(lo, hi + 1)):
            x = x0 + i * 100
            y0 = 0 if i % 2 == 0 else 450
            pr = dict(golf="hole", ref=str(n), osm_id=1000 * (c + 1) + n, inside_course=True)
            if nm:
                pr["name"] = f"{nm} {n}"
            feats.append(line([(x, y0), (x + (3 if same_greens and c else 0), 450 - y0)], **pr))
        if outlines:
            ring = [ll(x0 - 150, -200), ll(x0 + 1000, -200), ll(x0 + 1000, 700), ll(x0 - 150, 700), ll(x0 - 150, -200)]
            feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[ring]),
                              properties=dict(leisure="golf_course", name=outlines[c], osm_id=900 + c)))
    outer = [ll(-500, -500), ll(6500, -500), ll(6500, 1000), ll(-500, 1000), ll(-500, -500)]
    feats.append(dict(type="Feature", geometry=dict(type="Polygon", coordinates=[outer]),
                      properties=dict(leisure="golf_course", osm_id=1)))
    return feats


def _holes(fc):
    return {f["properties"]["osm_id"]: int(f["properties"]["ref"]) for f in fc["features"]
            if f["properties"].get("golf") == "hole"}


def test_nine_outlines_1_9_and_10_18_combined_into_one_18():
    """Paa-Ko Ridge: outlines '1-9', '10-18', '19-27', refs 1-9 / 10-18 / 10-18: never just one nine; the 1-9 and
    10-18 nines make the 18 when no name decides."""
    feats = _nines(refs=((1, 9), (10, 18), (10, 18)), outlines=("Ridge 1-9", "Ridge 10-18", "Ridge 19-27"))
    out, notes = sanity.clean_osm(dict(features=feats), names=["Ridge Golf Club"])
    h = _holes(out)
    assert sorted(h) == list(range(1001, 1010)) + list(range(2010, 2019)), notes
    assert sorted(h.values()) == list(range(1, 19))
    assert any("CHECK" in n and "1-9" in n and "10-18" in n for n in notes), notes


def test_named_nines_kept_and_second_renumbered_10_18():
    """Hole-name nines (Carillon white / red / blue, refs 1-9 each): the two nines the request names make the 18,
    in the request's order, the second renumbered 10-18."""
    feats = _nines(names=("Red", "White", "Blue"))
    out, notes = sanity.clean_osm(dict(features=feats), names=["Carillon Blue / White"])
    h = _holes(out)
    assert h == {**{3000 + n: n for n in range(1, 10)}, **{2000 + n: n + 9 for n in range(1, 10)}}, notes
    assert any("blue" in n and "white" in n for n in notes)


def test_nines_19_27_numbering_split_and_renumbered():
    """Refs 1-27 on one facility (no repeated ref): grouped into nines by number; 1-9 + 10-18 make the 18 unless
    the request names other nines (then 19-27 is renumbered 10-18)."""
    feats = _nines(refs=((1, 9), (10, 18), (19, 27)), names=("Lakes", "Hills", "Pines"))
    out, notes = sanity.clean_osm(dict(features=feats), names=["Some Golf Club"])
    assert sorted(_holes(out)) == list(range(1001, 1010)) + list(range(2010, 2019)), notes
    out, notes = sanity.clean_osm(dict(features=feats), names=["Some Golf Club Lakes and Pines"])
    h = _holes(out)
    assert h == {**{1000 + n: n for n in range(1, 10)}, **{3000 + n: n - 9 for n in range(19, 28)}}, notes


def test_unnamed_nines_near_point_picks_two():
    feats = _nines()
    near = ll(3000, 200)[::-1]                                  # between nine 1 (x 2000..2800) and nine 2 (4000..)
    out, notes = sanity.clean_osm(dict(features=feats), names=["x"], near=near)
    assert sorted(_holes(out)) == list(range(2001, 2010)) + list(range(3001, 3010)), notes
    assert sorted(_holes(out).values()) == list(range(1, 19))
    out, notes = sanity.clean_osm(dict(features=feats), names=["x"])          # nothing decides: still an 18
    assert len(_holes(out)) == 18 and sorted(_holes(out).values()) == list(range(1, 19))
    assert any("CHECK" in n for n in notes)


def test_nine_mapped_twice_on_the_same_ground_stays_a_nine():
    """A nine-hole course whose holes are mapped twice (same tees / greens: Bobby Jones' reversible nine) is not
    two nines."""
    feats = _nines(refs=((1, 9), (1, 9)), names=(None, None), same_greens=True)
    out, notes = sanity.clean_osm(dict(features=feats), names=["x"])
    assert len(_holes(out)) == 9, notes


def test_unnumbered_hole_ways_dropped_after_a_split_only():
    """Grand National: a short course's ref-less golf=hole ways belong to no kept course; without a split they
    stay (a course's own unnumbered way is select_hole_ways' business)."""
    stray = [line([(6000 + i * 60, 0), (6000 + i * 60, 120)], golf="hole", osm_id=5000 + i, inside_course=True)
             for i in range(5)]
    out, notes = sanity.clean_osm(dict(features=_two_courses() + stray), names=["x"], near=ll(-1000, 200)[::-1])
    assert _hole_ids(out) == list(range(1000, 1018)), notes
    assert any("unnumbered" in n for n in notes)
    out, _ = sanity.clean_osm(dict(features=_course18() + stray), names=["x"])
    assert len(_hole_ids(out)) == 23


def test_paa_ko_ridge_three_nines_from_live_osm():
    """Live OSM (2026-11-03): outlines 'Paa-ko Ridge 1-9' / '10-18' / '19-27', refs 1-9, 10-18, 10-18. Was 9 holes
    (one nine kept as a course); now the 1-9 + 10-18 nines, refs 1-18, one way each."""
    out, notes = sanity.clean_osm(_fix("paa_ko_ridge_holes.geojson"), names=["Paa-Ko Ridge Golf Club"])
    holes = [f for f in out["features"] if f["properties"].get("golf") == "hole"]
    assert sorted(int(f["properties"]["ref"]) for f in holes) == list(range(1, 19)), notes
    ids = {f["properties"]["osm_id"] for f in holes}
    assert 725227273 in ids and 799526077 in ids and 802547647 not in ids        # 1, 10 (10-18), not 10 (19-27)
    assert any("1-9" in n and "10-18" in n and "CHECK" in n for n in notes), notes


def test_grand_national_links_clean_18_from_live_osm():
    """Live OSM: Links 18 (no course name), Lake 18 (golf:course:name=Lake) and 17 ref-less short-course ways.
    The near point keeps the Links 18 and nothing else."""
    out, notes = sanity.clean_osm(_fix("grand_national_holes.geojson"),
                                  names=["Grand National Links Course", "RTJ Grand National Golf"], near="32.706,-85.418")
    holes = [f for f in out["features"] if f["properties"].get("golf") == "hole"]
    assert sorted(int(f["properties"]["ref"]) for f in holes) == list(range(1, 19)), notes
    assert not any(f["properties"].get("golf:course:name") for f in holes)
    assert any("17 unnumbered" in n for n in notes), notes
