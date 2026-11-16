"""A shared on-disk cache of raster blocks for the fast path's remote COG reads (NAIP items, Meta canopy tiles), so a
re-run under another slug, the second course of a 36-hole club or a neighbouring course reads no bytes again.

  read(key, opener, window)            -> (array (count, h, w), meta): the window (row_off, col_off, height, width)
                                          of the dataset `opener()` opens, assembled from 512 x 512 virtual blocks;
                                          missing blocks come from ONE GDAL read of their bounding window (GDAL does
                                          the HTTP range requests and the decoding), cached losslessly (zlib)
  meta(key, opener)                    -> {shape, count, dtype, transform, crs, nodata} of the dataset (cached too)
  prune()                              -> keep the cache under its cap (oldest-used blocks go first)

key names the dataset and resolution (e.g. "naip/<item id>/ovr1"): never the signed URL. Blocks are written by a
background thread after the read returns (the build never waits on the disk). Root: $FASTPATH_TILE_CACHE, default
<fastpath cache>/tiles; cap $FASTPATH_TILE_CACHE_MB (default 1024 MB), checked at most once a minute.
"""
import atexit
import hashlib
import json
import os
import threading
import time
import zlib
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VB = 512                                    # virtual block edge (NAIP COG tiles are 512 x 512)
_ROOT = []
_W = ThreadPoolExecutor(2)
_LOCK = threading.Lock()
_LAST_PRUNE = [0.0]
atexit.register(lambda: _W.shutdown(wait=True))


def root():
    if not _ROOT:
        base = os.environ.get("FASTPATH_CACHE") or os.path.join(HERE, "cache")
        _ROOT.append(os.environ.get("FASTPATH_TILE_CACHE") or os.path.join(base, "tiles"))
    return _ROOT[0]


def cap_bytes():
    return int(float(os.environ.get("FASTPATH_TILE_CACHE_MB", "1024")) * 1e6)


def enabled():
    return os.environ.get("FASTPATH_TILE_CACHE", "") != "off"


def _dir(key):
    h = hashlib.sha1(key.encode()).hexdigest()[:20]
    return os.path.join(root(), h[:2], h)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, path)


def meta(key, opener):
    """the dataset's grid, from the cache or from opener() (one open)"""
    p = os.path.join(_dir(key), "meta.json")
    try:
        with open(p) as fh:
            m = json.load(fh)
        m["shape"] = tuple(m["shape"])
        return m
    except (OSError, ValueError):
        pass
    with opener() as src:
        m = _meta_of(src)
    if enabled():
        _write(p, json.dumps(dict(m, key=key)).encode())
    return m


def _meta_of(src):
    t = src.transform
    return dict(shape=(src.height, src.width), count=src.count, dtype=str(src.dtypes[0]),
                transform=[t.a, t.b, t.c, t.d, t.e, t.f], crs=src.crs.to_wkt(), nodata=src.nodata)


def _load(path, shape, dtype):
    try:
        with open(path, "rb") as fh:
            raw = zlib.decompress(fh.read())
        a = np.frombuffer(raw, dtype=dtype)
        if a.size != int(np.prod(shape)):
            return None
        try:
            os.utime(path)                  # last use, for the eviction order
        except OSError:
            pass
        return a.reshape(shape)
    except (OSError, zlib.error, ValueError):
        return None


def read(key, opener, window, m=None):
    """-> (array (count, h, w) of the window, meta). window = (row_off, col_off, height, width), clipped to the
    dataset by the caller. Equal to opener().read(window=...) (lossless blocks)."""
    from rasterio.windows import Window
    r0, c0, h, w = (int(x) for x in window)
    m = m or meta(key, opener)
    H, W = m["shape"]
    if not (0 <= r0 and 0 <= c0 and h >= 0 and w >= 0 and r0 + h <= H and c0 + w <= W):
        raise ValueError(f"tilecache.read: window {window} outside {m['shape']}")
    count, dt = m["count"], np.dtype(m["dtype"])
    out = np.empty((count, h, w), dt)
    if h == 0 or w == 0:
        return out, m
    d = _dir(key)
    br = range(r0 // VB, (r0 + h - 1) // VB + 1)
    bc = range(c0 // VB, (c0 + w - 1) // VB + 1)

    def bshape(i, j):
        return count, min(VB, H - i * VB), min(VB, W - j * VB)
    blocks, miss = {}, []
    for i in br:
        for j in bc:
            b = _load(os.path.join(d, f"{i}_{j}.z"), bshape(i, j), dt) if enabled() else None
            if b is None:
                miss.append((i, j))
            else:
                blocks[i, j] = b
    if miss:
        i0, i1 = min(i for i, _ in miss), max(i for i, _ in miss)
        j0, j1 = min(j for _, j in miss), max(j for _, j in miss)
        R0, C0 = i0 * VB, j0 * VB
        R1, C1 = min((i1 + 1) * VB, H), min((j1 + 1) * VB, W)
        with opener() as src:
            a = src.read(window=Window(C0, R0, C1 - C0, R1 - R0))
        new = {}
        for i, j in miss:
            b = a[:, i * VB - R0:min((i + 1) * VB, H) - R0, j * VB - C0:min((j + 1) * VB, W) - C0]
            blocks[i, j] = b
            new[i, j] = b
        if enabled():
            _W.submit(_store, d, {k: np.ascontiguousarray(v) for k, v in new.items()})
    for (i, j), b in blocks.items():
        rs, cs = i * VB, j * VB
        a0, a1 = max(r0, rs), min(r0 + h, rs + b.shape[1])
        b0, b1 = max(c0, cs), min(c0 + w, cs + b.shape[2])
        out[:, a0 - r0:a1 - r0, b0 - c0:b1 - c0] = b[:, a0 - rs:a1 - rs, b0 - cs:b1 - cs]
    return out, m


def _store(d, new):
    for (i, j), b in new.items():
        try:
            _write(os.path.join(d, f"{i}_{j}.z"), zlib.compress(b.tobytes(), 1))
        except OSError:
            return
    prune()


def usage():
    """[(atime-ish mtime, size, path)] of every block file"""
    out = []
    r = root()
    if not os.path.isdir(r):
        return out
    for dp, _, fs in os.walk(r):
        for f in fs:
            if f.endswith((".z", ".tif")):        # blocks; dem/<request>/dem.tif (fast_imagery.fetch_dem_cached)
                p = os.path.join(dp, f)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                out.append((st.st_mtime, st.st_size, p))
    return out


def prune(force=False):
    """delete the least recently used blocks until the cache is under its cap -> bytes kept"""
    with _LOCK:
        if not force and time.time() - _LAST_PRUNE[0] < 60:
            return None
        _LAST_PRUNE[0] = time.time()
    files = sorted(usage())
    total = sum(s for _, s, _ in files)
    cap = cap_bytes()
    for _, s, p in files:
        if total <= cap:
            break
        try:
            os.remove(p)
            total -= s
        except OSError:
            pass
    return total
