"""tilecache.read / fast_imagery._warp_cached == reading / warping the dataset itself; pruning keeps the cap.
python3 -m pytest -q course_data/platform/fastpath/test_tilecache.py   (local rasters only, no network)"""
import os
import sys
import time

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


@pytest.fixture()
def tc(tmp_path, monkeypatch):
    monkeypatch.setenv("FASTPATH_TILE_CACHE", str(tmp_path / "tiles"))
    import tilecache
    monkeypatch.setattr(tilecache, "_ROOT", [])
    tilecache._LAST_PRUNE[0] = 0.0
    return tilecache


def _raster(path, h=1300, w=1100, count=3, dtype="uint8", crs="EPSG:26915", origin=(500000.0, 4700000.0), res=0.6):
    import rasterio
    rng = np.random.default_rng(0)
    a = rng.integers(0, 256, (count, h, w)).astype(dtype)
    a[:, :40] = 0
    tr = rasterio.transform.from_origin(origin[0], origin[1], res, res)
    with rasterio.open(path, "w", driver="GTiff", height=h, width=w, count=count, dtype=dtype, crs=crs, transform=tr,
                       tiled=True, blockxsize=512, blockysize=512, compress="deflate") as d:
        d.write(a)
    return a, tr


def _drain(tc):
    tc._W.shutdown(wait=True)
    from concurrent.futures import ThreadPoolExecutor
    tc._W = ThreadPoolExecutor(2)


def test_read_equal_and_cached(tc, tmp_path):
    import rasterio
    p = str(tmp_path / "a.tif")
    a, _ = _raster(p)
    opened = []

    def opener():
        opened.append(1)
        return rasterio.open(p)
    for win in ((0, 0, 1300, 1100), (17, 511, 600, 2), (1299, 1099, 1, 1), (500, 500, 30, 30), (0, 0, 0, 5)):
        got, m = tc.read("t/a", opener, win)
        r, c, h, w = win
        assert np.array_equal(got, a[:, r:r + h, c:c + w])
    _drain(tc)
    n = len(opened)
    got, _ = tc.read("t/a", opener, (3, 700, 1200, 390))
    assert np.array_equal(got, a[:, 3:1203, 700:1090]) and len(opened) == n      # all blocks from disk
    with pytest.raises(ValueError):
        tc.read("t/a", opener, (1200, 0, 200, 10))


def test_corrupt_block_is_refetched(tc, tmp_path):
    import rasterio
    p = str(tmp_path / "b.tif")
    a, _ = _raster(p, h=600, w=600)
    tc.read("t/b", lambda: rasterio.open(p), (0, 0, 600, 600))
    _drain(tc)
    blocks = [f for _, _, f in tc.usage()]
    assert blocks
    with open(blocks[0], "wb") as fh:
        fh.write(b"garbage")
    got, _ = tc.read("t/b", lambda: rasterio.open(p), (0, 0, 600, 600))
    assert np.array_equal(got, a)


def test_prune_keeps_cap(tc, tmp_path, monkeypatch):
    import rasterio
    p = str(tmp_path / "c.tif")
    _raster(p)
    tc.read("t/c", lambda: rasterio.open(p), (0, 0, 1300, 1100))
    _drain(tc)
    files = tc.usage()
    total = sum(s for _, s, _ in files)
    for _, _, f in files[:3]:
        os.utime(f, (time.time() - 3600, time.time() - 3600))
    monkeypatch.setenv("FASTPATH_TILE_CACHE_MB", str(total / 2e6))
    kept = tc.prune(force=True)
    assert kept <= total / 2 and sum(s for _, s, _ in tc.usage()) == kept
    assert not any(os.path.exists(f) for _, _, f in files[:3])          # the least recently used go first


@pytest.mark.parametrize("dst_crs,how", [("EPSG:26915", "average"), ("EPSG:32615", "bilinear"), ("EPSG:3857", "bilinear")])
def test_warp_cached_equals_dataset_warp(tc, tmp_path, dst_crs, how):
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject, transform_bounds
    import fast_imagery as fim
    p = str(tmp_path / "d.tif")
    _raster(p, count=4)
    rs = getattr(Resampling, how)
    with rasterio.open(p) as src:
        b = transform_bounds(src.crs, dst_crs, *src.bounds)
    res = 2.4 if how == "average" else 1.0
    x0, y1 = b[0] + 60, b[3] - 45
    W, H = int((b[2] - b[0] - 150) / res), int((b[3] - b[1] - 120) / res)
    tr = rasterio.transform.from_origin(x0, y1, res, res)
    ref = np.zeros((4, H, W), np.uint8)
    with rasterio.open(p) as src:
        reproject(rasterio.band(src, [1, 2, 3, 4]), ref, src_nodata=0, dst_transform=tr, dst_crs=dst_crs, dst_nodata=0,
                  resampling=rs)
    m = tc.meta("t/d", lambda: rasterio.open(p))
    got = fim._warp_cached("t/d", lambda: rasterio.open(p), m, tr, rasterio.crs.CRS.from_string(dst_crs), (4, H, W), 0, rs)
    assert np.array_equal(got, ref)
