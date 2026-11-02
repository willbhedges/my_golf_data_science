"""False water on paths / roads / bare ground and piped OSM streams (water_filter.py).

    python3 -m pytest -q course_data/vision_any/test_water_filter.py

Synthetic grids first; then the mapper-labelled cases (course_data/mapper/{rivercut,gustin,la_nickell}: the
agents' 'erase water' polygons on cart paths / a road / a piped stream), run on the committed rasters and
packages when they are in the checkout (skipped otherwise). The labelled cases are checks, not training data:
the thresholds are physical (NAIP NIR / NDVI of pavement vs open water, DTM channel depth).
"""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import water_filter as WF                 # noqa: E402

TURF = (0.10, 0.12, 0.08, 0.50)           # R, G, B, NIR (0..1): mown grass
POND = (0.08, 0.10, 0.09, 0.05)           # open water: dark NIR
PAVE = (0.36, 0.38, 0.36, 0.42)           # asphalt / concrete: NIR as bright as the visible bands
CREEK_BANK = (0.08, 0.12, 0.07, 0.45)     # vegetated creek corridor


def grid(H=200, W=300):
    img = np.zeros((H, W, 4), np.float32)
    img[:] = TURF
    return img


def paved_of(*imgs):
    class S:
        pass
    s = S()
    s.naip = [(2022 - i, im) for i, im in enumerate(imgs)]
    s.H, s.W = imgs[0].shape[:2]
    return WF.paved_mask(s)


def road_d_of(mask_line, half):
    from scipy import ndimage
    return (ndimage.distance_transform_edt(~mask_line) - half).astype(np.float32)


# --------------------------------------------------------------------------- tags
def test_is_piped_tags():
    assert WF.is_piped(dict(waterway="stream", tunnel="yes", layer="-1"))
    assert WF.is_piped(dict(waterway="stream", tunnel="culvert"))
    assert WF.is_piped(dict(waterway="ditch", covered="yes"))
    assert WF.is_piped(dict(waterway="drain", location="underground"))
    assert not WF.is_piped(dict(waterway="stream"))
    assert not WF.is_piped(dict(waterway="stream", tunnel="no"))


def test_road_half_width():
    assert WF.road_half_m(dict(golf="cartpath")) == WF.CARTPATH_HALF
    assert WF.road_half_m(dict(highway="path", golf="cartpath")) == WF.CARTPATH_HALF
    assert WF.road_half_m(dict(highway="footway")) == 1.5
    assert WF.road_half_m(dict(highway="secondary")) == 7.5
    assert WF.road_half_m(dict(highway="service", width="8")) == 4.0
    assert WF.road_half_m(dict(highway="proposed")) is None
    assert WF.road_half_m(dict(waterway="stream")) is None


def test_paved_signature():
    img = grid(20, 20)
    img[:10] = PAVE
    img[10:15] = POND
    p = paved_of(img, img)
    assert p[:10].all() and not p[10:].any()
    img2 = img.copy()
    img2[:5] = POND                       # dark in one year: not paved in every year
    p = paved_of(img, img2)
    assert not p[:5].any() and p[5:10].all()


# --------------------------------------------------------------------------- components
def scene():
    """A pond, a 4 m x 150 m paved cart-path strip, and a vegetated creek corridor the path crosses."""
    img = grid()
    water = np.zeros(img.shape[:2], bool)
    img[20:60, 20:70] = POND
    water[20:60, 20:70] = True
    img[100:104, 40:190] = PAVE                         # cart path (paved)
    water[100:104, 40:190] = True                       # ... called water by NDWI
    img[60:200, 240:250] = CREEK_BANK                    # creek corridor (vegetated), N-S
    water[60:200, 240:250] = True
    img[150:154, 200:290] = PAVE                         # a second path crossing the creek corridor
    line = np.zeros(water.shape, bool)
    line[101:103, 40:190] = True
    line[151:153, 200:290] = True
    return img, water, line


def test_path_strip_removed_pond_and_creek_kept():
    img, water, line = scene()
    paved = paved_of(img, img)
    out, rep = WF.false_water(water, paved, road_d_of(line, 1.5), None)
    assert out[20:60, 20:70].all(), "pond kept"
    assert not out[100:104, 40:190].any(), "cart-path strip removed"
    assert out[60:150, 240:250].all() and out[154:200, 240:250].all(), "creek corridor kept"
    assert not out[150:154, 240:250].any(), "the paved path cells across the corridor removed"
    assert {r["reason"] for r in rep} >= {"road", "cells"}


def test_unmapped_paved_strip_needs_flat_ground():
    img, water, _ = scene()
    paved = paved_of(img, img)
    flat = np.zeros(water.shape, np.float32)
    out, rep = WF.false_water(water, paved, None, flat)
    assert not out[100:104, 40:190].any() and any(r["reason"] == "strip" for r in rep)
    chan = flat.copy()
    chan[98:106, 40:190] = -1.0                         # the strip lies in a 1 m channel: keep it
    out, _ = WF.false_water(water, paved, None, chan)
    assert out[100:104, 40:190].all()
    assert out[20:60, 20:70].all()


def test_raised_bare_blob_removed_flat_one_kept():
    img = grid()
    water = np.zeros(img.shape[:2], bool)
    img[50:90, 50:100] = PAVE                           # 40 x 50 m bright bare patch (wide: not a strip)
    water[50:90, 50:100] = True
    paved = paved_of(img, img)
    dtm = np.zeros(water.shape, np.float32)
    out, _ = WF.false_water(water, paved, None, dtm)
    assert out[50:90, 50:100].all(), "flat and wide: not judged"
    dtm[50:90, 50:100] = 0.6                            # stands 0.6 m above its surroundings
    out, rep = WF.false_water(water, paved, None, dtm)
    assert not out[50:90, 50:100].any() and rep[0]["reason"] == "raised"


def test_osm_water_never_removed():
    img, water, line = scene()
    keep = np.zeros(water.shape, bool)
    keep[100:104, 40:190] = True                        # OSM says this strip is water: keep it
    out, _ = WF.false_water(water, paved_of(img, img), road_d_of(line, 1.5), np.zeros(water.shape), keep=keep)
    assert out[100:104, 40:190].all()


def test_dark_strip_along_path_kept():
    """A narrow dark (open water) channel next to a path stays: the path rules need pavement."""
    img = grid()
    water = np.zeros(img.shape[:2], bool)
    img[100:104, 40:190] = POND
    water[100:104, 40:190] = True
    line = np.zeros(water.shape, bool)
    line[106, 40:190] = True
    out, rep = WF.false_water(water, paved_of(img, img), road_d_of(line, 1.5), np.zeros(water.shape))
    assert out[100:104, 40:190].all() and not rep


# --------------------------------------------------------------------------- piped streams
def _dem(tmp_path, z):
    import rasterio
    from affine import Affine
    p = str(tmp_path / "dem.tif")
    with rasterio.open(p, "w", driver="GTiff", height=z.shape[0], width=z.shape[1], count=1, dtype="float32",
                       crs="EPSG:32615", transform=Affine(1.0, 0, 500000.0, 0, -1.0, 4300000.0)) as d:
        d.write(z.astype(np.float32), 1)
    return p


def _ll(xy):
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:32615", "EPSG:4326", always_xy=True)
    xy = np.asarray(xy, float)
    lon, lat = t.transform(500000.0 + xy[:, 0], 4300000.0 - xy[:, 1])
    return [[float(a), float(b)] for a, b in zip(lon, lat)]


def _fc(stream_props, with_pond=False):
    # fairway: x 50..150, y 80..120 (pixel metres); stream runs N-S at x 100 from y 0 to 200
    fw = _ll([(50, 80), (150, 80), (150, 120), (50, 120), (50, 80)])
    st = _ll([(100, 0), (100, 200)])
    feats = [dict(type="Feature", properties=dict(golf="fairway"), geometry=dict(type="Polygon", coordinates=[fw])),
             dict(type="Feature", properties=dict(waterway="stream", **stream_props),
                  geometry=dict(type="LineString", coordinates=st))]
    if with_pond:
        pond = _ll([(80, 105), (120, 105), (120, 140), (80, 140), (80, 105)])
        feats.append(dict(type="Feature", properties=dict(natural="water"),
                          geometry=dict(type="Polygon", coordinates=[pond])))
    return dict(type="FeatureCollection", features=feats)


def _poly_m(geoms):
    from pyproj import Transformer
    from shapely.ops import transform, unary_union
    t = Transformer.from_crs("EPSG:4326", "EPSG:32615", always_xy=True)
    g = unary_union([transform(t.transform, q) for q in geoms])
    return transform(lambda x, y: (np.asarray(x) - 500000.0, 4300000.0 - np.asarray(y)), g)


def test_stream_across_fairway_without_channel_is_piped(tmp_path):
    z = np.zeros((200, 200))
    z[:80, 97:104] = -1.0                                # a real channel north and south of the fairway
    z[120:, 97:104] = -1.0
    geoms, rep = WF.piped_streams(_fc({}), _dem(tmp_path, z))
    assert rep["crossing_m"] >= 30
    g = _poly_m(geoms)
    from shapely.geometry import Point
    assert g.contains(Point(100, 100)), "the fairway crossing is piped"
    assert not g.contains(Point(100, 40)) and not g.contains(Point(100, 170)), "the open channel stays water"


def test_stream_across_fairway_with_channel_stays(tmp_path):
    z = np.zeros((200, 200))
    z[:, 97:104] = -1.0                                  # the channel continues through the fairway
    geoms, rep = WF.piped_streams(_fc({}), _dem(tmp_path, z))
    assert not geoms and rep["crossing_m"] == 0


def test_tunnel_tag_is_piped_without_dem_and_pond_kept():
    geoms, rep = WF.piped_streams(_fc(dict(tunnel="culvert"), with_pond=True), None)
    assert rep["tagged"] == 1
    g = _poly_m(geoms)
    from shapely.geometry import Point
    assert g.contains(Point(100, 40)) and g.contains(Point(100, 95))
    assert not g.contains(Point(100, 120)), "the OSM pond the culvert feeds stays water"


def test_tunnel_tag_with_dem_keeps_open_channel_at_the_mouth(tmp_path):
    z = np.zeros((200, 200))
    z[:60, 97:104] = -1.0                                # open ditch north of the culvert: stays water
    geoms, rep = WF.piped_streams(_fc(dict(tunnel="culvert")), _dem(tmp_path, z))
    g = _poly_m(geoms)
    from shapely.geometry import Point
    assert rep["tagged"] == 1 and rep["tagged_m"] >= 100
    assert g.contains(Point(100, 100)) and g.contains(Point(100, 150))
    assert not g.contains(Point(100, 30))


def test_subtract_from_hole_splits_zone():
    from shapely.geometry import box
    h = dict(zones_ll=[dict(lie="water", src="osm", poly=[[0, 0], [10, 0], [10, 1], [0, 1]]),
                       dict(lie="fairway", src="osm", poly=[[0, 0], [10, 0], [10, 1], [0, 1]])])
    n = WF.subtract_from_hole(h, [box(4, -1, 6, 2)])
    assert n == 1
    w = [z for z in h["zones_ll"] if z["lie"] == "water"]
    assert len(w) == 2 and all(z.get("piped_cut") for z in w)
    assert sum(1 for z in h["zones_ll"] if z["lie"] == "fairway") == 1


# --------------------------------------------------------------------------- mapper-labelled cases
CASES = ("rivercut", "gustin", "la_nickell")


def _have(slug):
    return (os.path.exists(os.path.join(HERE, slug, "raw", "meta.json"))
            and os.path.exists(os.path.join(ROOT, "course_data", "packages", slug, "package.json"))
            and os.path.exists(os.path.join(ROOT, "course_data", "mapper", slug, "agent_zones.geojson")))


@pytest.fixture(scope="module")
def filtered():
    """{slug: (S, erase mask, vision water before, after, OSM water mask)} for the labelled courses present.
    (gustin: the mapper erased a creek corridor stretch where the cart path runs in it; only the paved path cells
    are paved, the vegetated corridor is kept by design, hence the lower share.)"""
    import layers as L
    import run_any as RA
    from shapely.geometry import Polygon, shape
    out = {}
    for slug in CASES:
        if not _have(slug):
            continue
        cdir = RA.course_dir_for(slug)
        S = L.Stack.load(slug, cdir)
        fc = json.load(open(os.path.join(cdir, "osm.geojson")))
        M, _ = L.osm_masks(S, fc)
        pkg = json.load(open(os.path.join(ROOT, "course_data", "packages", slug, "package.json")))
        vz = [Polygon(z["poly"]).buffer(0) for h in pkg["holes"].values() for z in h["zones_ll"]
              if z["lie"] == "water" and str(z.get("src", "")).startswith("vision")]
        W = S.rasterize(vz) & ~M["water"]
        az = json.load(open(os.path.join(ROOT, "course_data", "mapper", slug, "agent_zones.geojson")))
        E = S.rasterize([shape(f["geometry"]) for f in az["features"]
                         if f["properties"]["op"] == "erase" and f["properties"]["lie"] == "water"])
        W2, _ = WF.clean_grid(S, fc, W, keep=M["water"])
        out[slug] = (S, E, W, W2, M["water"])
    if not out:
        pytest.skip("no labelled course rasters in this checkout")
    return out


@pytest.mark.parametrize("slug,share", [("rivercut", 0.75), ("la_nickell", 0.75), ("gustin", 0.2)])
def test_mapper_erased_water_is_removed(filtered, slug, share):
    if slug not in filtered:
        pytest.skip(f"{slug} rasters not in the checkout")
    S, E, W, W2, _ = filtered[slug]
    before = (W & E).sum()
    removed = (W & E & ~W2).sum()
    assert before > 300
    assert removed >= share * before, f"{slug}: removed {removed} of {before} m2 the mapper erased"


def test_labelled_courses_keep_unpaved_water(filtered):
    """Vegetated creek corridors stay: on gustin (creek corridors + a road) >= 95 % of the vision water that is not
    bright-and-bare in every NAIP year and not within 15 m of an OSM road / path is kept."""
    if "gustin" not in filtered:
        pytest.skip("gustin rasters not in the checkout")
    S, E, W, W2, _ = filtered["gustin"]
    fc = json.load(open(os.path.join(ROOT, "course_data", "packages", "gustin", "raw", "osm.geojson")))
    un = W & ~WF.paved_mask(S) & (WF.road_distance(S, WF.road_lines(fc)) > 15)
    assert un.sum() > 10000
    assert (W2 & un).sum() >= 0.95 * un.sum()


def test_rivercut_hole14_tunnel_stream_piped():
    if not os.path.exists(os.path.join(ROOT, "course_data", "packages", "rivercut", "raw", "osm.geojson")):
        pytest.skip("rivercut package not in the checkout")
    from shapely.geometry import shape
    from shapely.ops import unary_union
    osm = json.load(open(os.path.join(ROOT, "course_data", "packages", "rivercut", "raw", "osm.geojson")))
    dem = os.path.join(ROOT, "course_data", "packages", "rivercut", "imagery", "dem.tif")
    geoms, rep = WF.piped_streams(osm, dem)
    assert rep["tagged"] >= 1
    az = json.load(open(os.path.join(ROOT, "course_data", "mapper", "rivercut", "agent_zones.geojson")))
    e = [shape(f["geometry"]) for f in az["features"] if f["properties"]["hole"] == "14"
         and f["properties"]["op"] == "erase" and "OSM stream" in f["properties"].get("evidence", "")]
    assert e and unary_union(geoms).intersects(e[0])
    ponds = [shape(f["geometry"]) for f in osm["features"] if f["geometry"]["type"] == "Polygon"
             and (f["properties"].get("natural") == "water" or f["properties"].get("golf") == "water_hazard")]
    assert unary_union(geoms).intersection(unary_union(ponds)).area < 1e-12, "OSM ponds untouched"


# --------------------------------------------------------------------------- the build paths use it
def test_build_holes_skips_piped_waterways():
    pytest.importorskip("shapely")
    sys.path.insert(0, os.path.join(ROOT, "course_data", "geometry"))
    import build_holes as bh
    assert bh.lie_of(dict(waterway="stream"), "LineString")[0] == "water"
    assert bh.lie_of(dict(waterway="stream", tunnel="yes", layer="-1"), "LineString") is None
    assert bh.lie_of(dict(waterway="ditch", tunnel="culvert"), "LineString") is None
    assert bh.lie_of(dict(natural="water"), "Polygon") == ("water", 0)


def test_osm_layers_drop_piped_streams_and_keep_roads():
    import layers as L
    ln = dict(type="LineString", coordinates=[[-92.3, 38.9], [-92.299, 38.9]])
    fc = dict(type="FeatureCollection", features=[
        dict(type="Feature", properties=dict(waterway="stream"), geometry=ln),
        dict(type="Feature", properties=dict(waterway="stream", tunnel="culvert"), geometry=ln),
        dict(type="Feature", properties=dict(highway="path", golf="cartpath"), geometry=ln),
        dict(type="Feature", properties=dict(highway="secondary"), geometry=ln)])
    Ly = L.osm_layers(fc)
    assert len(Ly["stream"]) == 1
    assert sorted(h for _, h in Ly["_roads"]) == [WF.CARTPATH_HALF, 7.5]


def test_filter_package_on_rivercut():
    """End to end on the committed rivercut package: the mapper's cart-path erasures lose their vision water, the
    hole-14 tunnel stream across the fairway loses its OSM water, other lies are untouched."""
    pp = os.path.join(ROOT, "course_data", "packages", "rivercut", "package.json")
    if not (_have("rivercut") and os.path.exists(pp)):
        pytest.skip("rivercut not in the checkout")
    import copy
    from shapely.geometry import Polygon, shape
    from shapely.ops import unary_union
    pkg = json.load(open(pp))
    new = copy.deepcopy(pkg)
    rep = WF.filter_package(new, slug="rivercut")
    assert rep["piped"]["zones_cut"] >= 1 and rep["vision"]["removed_m2"] > 5000
    az = json.load(open(os.path.join(ROOT, "course_data", "mapper", "rivercut", "agent_zones.geojson")))

    def water(p, h, src=None):
        return unary_union([Polygon(z["poly"]).buffer(0) for z in p["holes"][h]["zones_ll"] if z["lie"] == "water"
                            and (src is None or str(z.get("src", "")).startswith(src))] or [Polygon()])
    for f in az["features"]:
        pr = f["properties"]
        if pr["op"] != "erase" or pr["lie"] != "water":
            continue
        e = shape(f["geometry"])
        before, after = water(pkg, pr["hole"]).intersection(e).area, water(new, pr["hole"]).intersection(e).area
        if "OSM stream" in pr.get("evidence", ""):
            assert after < 0.75 * before, pr["edit"]
        elif "cart path" in pr.get("evidence", ""):
            vb = water(pkg, pr["hole"], "vision").intersection(e).area
            va = water(new, pr["hole"], "vision").intersection(e).area
            assert va <= 0.05 * vb, pr["edit"]
    for k in pkg["holes"]:
        a = [z for z in pkg["holes"][k]["zones_ll"] if z["lie"] != "water"]
        b = [z for z in new["holes"][k]["zones_ll"] if z["lie"] != "water"]
        assert a == b
        osm_ponds_a = [z for z in pkg["holes"][k]["zones_ll"] if z["lie"] == "water" and z.get("src") == "osm"]
        assert len([z for z in new["holes"][k]["zones_ll"] if z["lie"] == "water" and z.get("src") == "osm"]) >= \
            len(osm_ponds_a) - 2
    assert "water_filter" in new["sources"]
