"""Regression tests: greens that are not visible on the package imagery, and the NAIP year choice.

The app's report "par-3 greens are not drawn on some auto-mapped courses" was Wakonda: its package shipped the
newest NAIP flight (2023-09), taken mid-renovation, so the greens of holes 5, 9, 15 and 17 (par 3s 9 and 17)
were bare soil under the OSM outline. Root cause: fetch_imagery took the newest covering year unconditionally and
nothing checked the greens on it. Fix: imagery/naip_years.py scores every year (turf greenness, greens visible,
haze, date, resolution, age) and fetch_imagery --year auto takes the best; package.check_green_visibility flags
any green still not visible. Both tests fail on the old code (no check; latest-year rule)."""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
CD = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(CD, "imagery")]
import package as pk  # noqa: E402
import test_package as tp  # noqa: E402

rasterio = pytest.importorskip("rasterio")
pytest.importorskip("pyproj")
pytest.importorskip("shapely")


def write_imagery(d, holes, bare=(), year=2023):
    """Synthetic NAIP package imagery (naip_rgb.tif, naip_nir.tif, georef.json) over the holes' greens: healthy
    turf everywhere (NDVI ~0.43), bare soil (NDVI ~0) inside the greens of the holes in `bare`."""
    from pyproj import Transformer
    from rasterio.features import rasterize
    from rasterio.transform import from_origin
    from shapely.geometry import Polygon
    from shapely.ops import transform as stx
    os.makedirs(d, exist_ok=True)
    crs = "EPSG:32615"
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    polys = {k: stx(tr.transform, Polygon(h["green_polygon_ll"])) for k, h in holes.items() if h.get("green_polygon_ll")}
    x0, y0, x1, y1 = np.array([p.bounds for p in polys.values()]).T
    x0, y0, x1, y1 = x0.min() - 50, y0.min() - 50, x1.max() + 50, y1.max() + 50
    res = 1.0
    W, H = int((x1 - x0) / res) + 1, int((y1 - y0) / res) + 1
    T = from_origin(x0, y1, res, res)
    rgb = np.zeros((3, H, W), np.uint8)
    rgb[:] = np.array([80, 120, 70], np.uint8)[:, None, None]
    nir = np.full((1, H, W), 200, np.uint8)
    if bare:
        m = rasterize([polys[k] for k in bare], out_shape=(H, W), transform=T).astype(bool)
        for i, v in enumerate((150, 140, 120)):
            rgb[i][m] = v
        nir[0][m] = 150
    prof = dict(driver="GTiff", width=W, height=H, crs=crs, transform=T, dtype="uint8")
    with rasterio.open(os.path.join(d, "naip_rgb.tif"), "w", count=3, **prof) as f:
        f.write(rgb)
    with rasterio.open(os.path.join(d, "naip_nir.tif"), "w", count=1, **prof) as f:
        f.write(nir)
    json.dump(dict(imagery=dict(source="synthetic NAIP", year=year, acquired=[f"{year}-09-02"],
                                files=dict(rgb="naip_rgb.tif", nir="naip_nir.tif"), crs=crs)),
              open(os.path.join(d, "georef.json"), "w"))
    return d


def test_green_not_visible_is_flagged(tmp_path, black):
    """A par-3 green on bare soil gets a confidence flag; the other greens do not."""
    package, _ = black
    holes = {k: dict(h) for k, h in package["holes"].items()}
    par3 = sorted(k for k, h in holes.items() if h["par"] == 3)
    assert par3, "fixture has par 3s"
    bad = par3[0]
    img = write_imagery(str(tmp_path / "imagery"), holes, bare=(bad,))
    imagery, _ = pk.imagery_ref(img)
    stages, warnings = {}, []
    pk.check_green_visibility(holes, img, imagery, stages, warnings)
    assert holes[bad]["green_visibility"]["visible"] is False
    assert all(holes[k]["green_visibility"]["visible"] for k in holes if k != bad)
    assert "NOT visible: holes " + bad in stages["green_visibility"]
    out = pk.reframe(dict(package, holes=holes))
    flags = out["holes"][bad]["confidence"]["flags"]
    assert any("green not visible on the NAIP 2023 imagery" in f for f in flags), flags
    assert not any("green not visible" in f for k in out["holes"] if k != bad for f in out["holes"][k]["confidence"]["flags"])


def test_all_greens_visible_no_flag(tmp_path, black):
    package, _ = black
    holes = {k: dict(h) for k, h in package["holes"].items()}
    img = write_imagery(str(tmp_path / "imagery"), holes)
    stages, warnings = {}, []
    pk.check_green_visibility(holes, img, pk.imagery_ref(img)[0], stages, warnings)
    assert stages["green_visibility"].startswith("ok: 18/18") and not warnings


black = tp.black


def cand(year, ndvi, bare_turf=0.05, greens_bare=0.0, gsd=0.6, dates=None, haze=45.0, cover=1.0):
    return dict(year=year, dates=dates or [f"{year}-08-20"], coverage=cover, gsd_m=gsd, has_nir=True,
                turf_ndvi=ndvi, turf_exg=70.0, bare_turf=bare_turf, greens_bare=greens_bare,
                greens_bare_n=int(round(greens_bare * 18)), greens_n=18, cloud=0.0, haze=haze)


def test_year_choice_skips_a_renovation_flight():
    """Wakonda-like: 2023 (newest, 0.3 m) shows 4 of 18 greens as bare soil and brown turf; 2021 is green."""
    import fetch_imagery as FI
    years = [dict(year=y, items=[], dates=[f"{y}-08-20"], coverage=1.0, gsd_m=0.6 if y < 2023 else 0.3)
             for y in (2017, 2019, 2021, 2023)]
    metrics = {2017: cand(2017, 0.30), 2019: cand(2019, 0.27), 2021: cand(2021, 0.31),
               2023: cand(2023, -0.05, bare_turf=0.87, greens_bare=4 / 18, gsd=0.3)}
    assert FI.latest_covering(years)["year"] == 2023                       # the old rule
    row, rec = FI.choose_year(years, "auto", osm={"features": []}, bbox=(0, 0, 1, 1), current=2023,
                              scorer=lambda y: {k: v for k, v in metrics[y["year"]].items() if k not in ("year", "dates")})
    assert row["year"] == 2021
    assert rec["chosen"] == 2021 and "2021" in rec["reason"] and "replaces 2023" in rec["reason"]
    assert {c["year"] for c in rec["candidates"]} == {2017, 2019, 2021, 2023}


def test_year_choice_keeps_newest_when_it_is_green_and_rules():
    import naip_years as NY
    # newest is as green: keep it (age penalty + resolution); a leaf-off or partial-coverage flight never wins
    best, reason, _ = NY.select([cand(2023, 0.30, gsd=0.3), cand(2021, 0.31),
                                 cand(2019, 0.60, dates=["2019-11-03"]), cand(2017, 0.70, cover=0.6)])
    assert best["year"] == 2023 and "newest" in reason
    # a much greener older year wins over a drought flight
    best, reason, _ = NY.select([cand(2023, 0.19, bare_turf=0.6, gsd=0.3), cand(2021, 0.33)])
    assert best["year"] == 2021


def test_bare_greens_rule():
    import naip_years as NY
    meds = [0.22, 0.21, 0.23, -0.10, 0.20, 0.16, 0.22, None]
    assert NY.bare_greens(meds) == [False, False, False, True, False, False, False, None]
    assert NY.bare_greens([0.02, 0.03, 0.01, 0.02]) == [False] * 4          # a uniformly dull flight: no outlier
