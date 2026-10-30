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
