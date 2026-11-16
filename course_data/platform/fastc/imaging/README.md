# fastc/imaging: the fetch stage's imagery kernels in C

The fast path (`platform/fastpath/fast.py`) fetches, for one course: the OSM features, a scorecard, NAIP (4 years
scored, one read), the 3DEP DEM and the Meta canopy height. This folder holds the part of that work that is
compute and was numpy: `kernel.c` (gcc -O3 -march=native -ffp-contract=off -fopenmp, built on first use into
`_build/`, loaded with ctypes by `fastimg.py`; `FASTIMG_SO=<file>` loads a prebuilt one). Every kernel keeps its
numpy reference, and the callers fall back to it when the library cannot be built.

| kernel | replaces (numpy) | used by | equality | Yorba Linda-sized timing, C vs numpy |
|---|---|---|---|---|
| `fi_paste_u8` | the mosaic paste of `rasterio.merge` 'first' / `naip_years.read_year`'s `np.where` | `fast_imagery.read_window`, `read_year_ovr` | exact | 4 x 4607 x 900 into 4607 x 1565: 11-14 ms vs 101-107 ms (x 8-10) |
| `fi_metrics` | `naip_years.metrics` (the NAIP year score's statistics) | `fast_imagery` year scoring via `fastimg.score_array` | exact (same dict) | 2.4 m (1152 x 392): 5.4 vs 47 ms (x 8.7); 0.6 m: 70 vs 676 ms (x 9.7) |
| `fi_chm_merge`, `fi_chm_quantize` | `canopy.fetch`'s merge and uint8 quantisation | `canopy.fetch` | exact | 2900 x 1000: 4-8 vs 30 ms; 8 vs 15 ms |

`python3 bench.py` prints the table's timings; `python3 -m pytest -q test_fastimg.py` checks equality (synthetic
scenes incl. the < 200 px turf fallback, empty / one-pixel / even-odd cases, and the cached NAIP products at 2.4 and
0.6 m).

How `fi_metrics` is exact: the NDVI of a uint8 (NIR, red) pair is one of 65536 float32 values, computed with
numpy's own float32 formula `(n - r) / max(n + r, 1)`; the kernel sorts those once at load and takes every NDVI
median from a 65536-bin histogram walked in that order (numpy's median: the middle value, or the float32 mean of
the two middle ones). Excess green `2G - R - B` is an integer in [-510, 510] and the turf RGB / blue haze values are
uint8, so their medians and numpy's 'linear' 2nd percentile come from histograms too. Per-green medians use a
quickselect. No `-ffast-math`, no FMA contraction.

## What is not here, and why

Measured on Yorba Linda (cold, `bench.py --fetch-only` in the session scratchpad), the fetch stage takes about
7-10 s wall for about 6 s of process CPU, and almost all of that CPU is already C inside libraries: zlib inflating
NAIP / canopy tiles and libjpeg encoding the NAIP COGs (GDAL), GDAL's warper, Pillow. The numpy work these kernels
replace was about 0.2 s of it. The wall time is network: the link here is capped around 14-16 MB/s with 0.4-0.9 s
to a first byte, so the fetch was made faster by downloading less and waiting less, not by computing faster (see
`fastpath/fast_imagery.py` and `fast.py`):

- the year scoring reads the COG overview at 2.4 m instead of full resolution (155 -> 13 MB);
- the chosen year is read as one block-aligned window per item with `GDAL_NUM_THREADS` (99 -> 35 MB, bit-identical);
- the NAIP STAC search and its SAS token run at once, from the national-index point, while the course outline is
  resolved; the scoring reads start before the OSM turf is in; the card sources run at once;
- the NAIP COGs are JPEG-encoded once, on all cores (2.2 -> 0.5 s).

HTTP, TIFF parsing, decoding and file orchestration stay in Python / GDAL: C buys nothing there (the decoders are
already C, the rest is waiting on the network), and a hand-written TIFF reader would only add risk.
