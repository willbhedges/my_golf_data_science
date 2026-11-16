"""route_scene: when perception runs, the candidate merge (OSM wins), confirm questions."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_scene as RS  # noqa: E402


def _f(golf, coords, typ="Polygon", **p):
    return {"type": "Feature", "geometry": {"type": typ, "coordinates": coords}, "properties": dict(golf=golf, **p)}


def _sq(lon, lat, d=0.0002):
    return [[[lon, lat], [lon + d, lat], [lon + d, lat + d], [lon, lat + d], [lon, lat]]]


def test_needs_perception():
    full = {"features": [_f("hole", [[0, 0], [0, 0.003]], "LineString", ref=str(i)) for i in range(1, 10)]}
    assert not RS.needs_perception(full, 9)
    mapped = {"features": [_f("green", _sq(-90 + i * 0.003, 40)) for i in range(9)]
              + [_f("tee", _sq(-90 + i * 0.003, 40.002)) for i in range(9)]}
    assert not RS.needs_perception(mapped, 9)
    assert RS.needs_perception({"features": []}, 18)
    assert RS.needs_perception({"features": mapped["features"][:7]}, 9)


def test_candidates_osm_wins():
    fc = {"features": [_f("green", _sq(-90.0, 40.0)), _f("tee", _sq(-90.0, 40.003))]}
    scene = dict(greens=[dict(id="g1", centroid=[-90.0001, 40.0001], area_m2=400, p=0.9, p_hole=0.9, kind="hole",
                              polygon=_sq(-90.0, 40.0)[0]),
                         dict(id="g2", centroid=[-90.004, 40.0], area_m2=400, p=0.9, p_hole=0.9, kind="hole",
                              polygon=_sq(-90.004, 40.0)[0])],
                 tee_complexes=[dict(id="t1", centroid=[-90.004, 40.003], p=0.8, boxes=[dict(centroid=[-90.004, 40.003])])])
    co, info = RS.candidates(fc, scene, n_holes=2)
    assert info["greens_osm"] == 1 and info["greens_scene"] == 1        # g1 sits on the OSM green: dropped
    assert info["tees_osm"] == 1 and info["tees_scene"] == 1


def test_confirm_questions_order():
    pkg = {"holes": {"1": dict(tee_ll=[0, 0], green_ll=[0, 1], par=4, length=380),
                     "2": dict(tee_ll=[1, 0], green_ll=[1, 1], par=3, length=160),
                     "3": dict(tee_ll=[2, 0], green_ll=[2, 1], par=5, length=520)}}
    q = RS.confirm_questions(pkg, dict(margins=[5.0, 1.0, 9.0], detected_holes=["1", "2"], min_margin=1.0))
    assert [x["hole"] for x in q["questions"]] == ["2", "1"]
