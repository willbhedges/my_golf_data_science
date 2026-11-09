"""package.pads_on_course: lidar pads on buildings / well outside the course outline are not tee candidates."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util

spec = importlib.util.spec_from_file_location("plat_package_pads", os.path.join(os.path.dirname(os.path.abspath(__file__)), "package.py"))
pk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pk)


def sq(lon, lat, d):
    return {"type": "Polygon", "coordinates": [[[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d], [lon - d, lat + d], [lon - d, lat - d]]]}


FC = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"leisure": "golf_course"}, "geometry": sq(-100.0, 40.0, 0.005)},
    {"type": "Feature", "properties": {"building": "house"}, "geometry": sq(-100.0052, 40.0, 0.0001)},
    {"type": "Feature", "properties": {"building": "yes"}, "geometry": sq(-100.002, 40.002, 0.0001)}]}


def pad(lon, lat):
    return dict(id=f"lidar:{lon},{lat}", centroid=(lat, lon), coords=[])


def test_drops_roof_and_far_outside_keeps_course_and_edge():
    pads = [pad(-100.0, 40.0),            # on the course
            pad(-100.0052, 40.0),         # a house roof just outside the outline (Crow Canyon 16)
            pad(-100.002, 40.002),        # a building inside the outline (clubhouse roof)
            pad(-100.00508, 40.003),      # 7 m outside a sloppy outline: still a tee candidate
            pad(-100.01, 40.0)]           # 400 m outside
    keep, n = pk.pads_on_course(pads, FC)
    assert [p["id"] for p in keep] == [pads[0]["id"], pads[3]["id"]] and n == 3


def test_no_outline_no_buildings_keeps_everything():
    pads = [pad(-100.0, 40.0), pad(-101.0, 41.0)]
    assert pk.pads_on_course(pads, {"features": []}) == (pads, 0)


def test_pad_far_to_the_side_of_mapped_tees_is_dropped():
    """Kittansett 10: the boxes are mapped; a pad 70 yds to the side is not a tee, one 60 yds straight back is."""
    feats = [{"type": "Feature", "properties": {"golf": "tee"}, "geometry": sq(-100.0 + i * 0.01, 40.0, 0.00005)} for i in range(9)]
    feats.append({"type": "Feature", "properties": {"golf": "hole", "ref": "1"},
                  "geometry": {"type": "LineString", "coordinates": [[-100.0, 40.0], [-100.0, 40.003]]}})
    fc = {"features": feats}
    side = pad(-100.00075, 40.0)          # ~70 yds west of the box
    back = pad(-100.0, 39.9995)           # ~60 yds straight back of the hole line
    near = pad(-100.0002, 40.0001)        # ~20 yds from the box
    keep, n = pk.pads_on_course([side, back, near], fc)
    assert [p["id"] for p in keep] == [back["id"], near["id"]] and n == 1
