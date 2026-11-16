# fastc/perception: the fast path's perception, hole-inference and solve hot loops in C

`kernel.c` is compiled on first use (`gcc -O3 -march=native -ffp-contract=off -fopenmp -shared -fPIC`, cached as
`_build/kernel_<source hash>.so`, `FASTPERC_SO=<file>` loads a prebuilt one) and loaded with ctypes by
`fastperc.py`. Every kernel keeps its numpy / scipy / LightGBM / Python reference, and a test compares the two
(`test_fastperc.py`, `fastpath/test_solve_c.py`). `GOLF_FASTC=0` switches every hook back to the reference.

Orchestration, HTTP, file I/O, raster reprojection (rasterio / GDAL), shapely geometry and the GEMMs (OpenBLAS)
stay as they are. They are already native code or wait on the network, so C would add risk without saving time.

| kernel | replaces | used by | check | time (4 CPUs, same box) |
|---|---|---|---|---|
| `fp_features` | `fastscene.features_py` (38 NAIP / canopy / DEM planes: separable Gaussians, local std, gradients) | the pixel classifier | within 2e-4 x range (seen: 1.2e-5) | Yorba Linda 3.8 -> 1.0 s |
| `fp_gbm_blocked` | LightGBM `Booster.predict` (multiclass, numerical splits) | the pixel classifier | max \|dp\| 0 (bit-exact) | Yorba Linda (0.71 M px) 4.7 -> 1.9 s |
| `fp_grey_disk` | `scipy.ndimage.grey_opening(footprint=disk)` | `tees/lidar_pads.py` (perception tee pads and the package build) | exact | 2.0 -> 0.4 s per call |
| `fp_comp_stats` | perception `geo.comp_stats` (per-label NaN-safe means) | every perception detector | bit-exact | 0.72 -> 0.006 s per call |
| `fp_label8` | `scipy.ndimage.label` (3 x 3) | not wired in (scipy is faster) | exact | 0.008 vs 0.021 s |
| `fp_im2col`, `fp_bias_act`, `fp_maxpool3s2`, `fp_up2`, `fp_conv3x3` | numpy primitives of the U-Net forward pass (`unet.py`) | `fastscene.unet_probs` | bit-exact without the direct convs; with them within 6e-7 relative (argmax identical) | 512 px tile 1.16 -> 0.52 s |
| `fa_conv`, `fa_stem_patch`, `fa_maxpool`, `fa_upcat` (`amx.c`) | the whole U-Net forward pass on Intel AMX: bf16 tiles, float32 sums, NHWC, implicit GEMM (no im2col), bias / residual / ReLU fused | `fastscene.unet_net` when the CPU has AMX | not exact (bf16): mean \|dp\| 6e-4, argmax 99.9 % on NAIP tiles; held-out 40 within 0.5 points | 512 px tile 0.76 -> 0.08-0.10 s (4 threads), 1.58 -> 0.13 s (1 thread) |
| `fc_conv`, `fc_maxpool`, `fc_upcat` (`conv32.c`) | the same pass in float32 (GCC vector extensions: AVX-512 / AVX2 / NEON), register-blocked implicit GEMM, fused epilogue | `fastscene.unet_net` without AMX | within 1e-4 x max \|logit\| (FMA, other sum order); cached probabilities differ by at most 1/255 | 512 px tile 1.58 -> 0.68 s (1 thread) |
| `fp_roll` | the roll-out loop of `mozingo/tee_strategy.simulate` on the lie raster | `fastpath/solve.py` through `solve_c.py` | identical arrays (every hole x club x 3 aims of 2 courses); decision.json identical on 3 courses | solve 4.4-4.9 -> 1.1-1.5 s |
| `fp_dist_to_rings` | `structure/scene.py _dist_to_rings` | the structure solver's scene (package build) | exact | small on the courses measured |

Whole-stage effect, Yorba Linda: the scene build with the pixel classifier went from 23.3 to 11.8 s with
byte-identical scene.json. The U-Net scene build takes 42 s (U-Net 32 s for 40 tiles, perceive 6.2 s, grid 1.5 s).
The U-Net step was 62 s until `OMP_WAIT_POLICY=PASSIVE`: libgomp's spinning threads were stealing the OpenBLAS
cores.

## unet.py: the segment U-Net without torch

`fastscene.unet_net` picks the pass at run time (`FASTPERC_IMPL=auto`): `unet_amx.AmxUNet` when /proc/cpuinfo has
amx_tile / amx_bf16 / avx512_bf16, `amx.c` compiles, the kernel grants the tile state (`arch_prctl(ARCH_REQ_XCOMP_PERM,
XTILEDATA)`) and a 32-term self-check product is right; else `unet_fast.FastUNet` (`conv32.c`); else `unet.py` with
the C primitives. `FASTPERC_IMPL=amx|fp32|c|ref` forces one (`ref`: numpy + OpenBLAS), `GOLF_FASTC=0` means `ref`.
The AMX pass needs the tile width to be a multiple of 512 (production: 512) and falls back to float32 otherwise.

smp `Unet` / ResNet-34 / 4 bands / 6 classes, read from a safetensors file. BatchNorm is folded into the
convolutions; each convolution is an im2col plus one SGEMM, except the high-resolution few-channel decoder layers,
which run as direct C convolutions. Weights: `course_data/segment/models/golfseg_own/` (our own model, imported
from Actions run 38987845450 by `.github/workflows/import_golfseg_own.yml`). Inputs are NAIP at the model's
0.6 m; 0.3 m NAIP is averaged down first.

## Not ported (measured, open)

* `platform/routing_v2.solve`, the beam search: about 10 s self time per course where the stage selector routes
  (Down River 23 s package build; Yorba Linda 24 s when one hole is left for it). Its states are numpy arrays with
  argpartition / unique tie order, so a C port that keeps the results identical needs the same tie-breaking.
* `structure/solver.route_dp`: about 4 s on the same courses.
* U-Net (fixed): the OpenBLAS + im2col pass ran 40 tiles x 63 GFLOP at about 80 GFLOP/s effective (decoder.blocks.3.1
  alone, a 1152 x 65536 im2col for 32 outputs, took a third of a tile). It is replaced by `amx.c` / `conv32.c` above.
* Not kept: running the extra NAIP years only on tiles where the first year is uncertain. On the TEST 40 d0
  probabilities only 3-7 % of tiles have no pixel below max p 0.9 / 0.8, so it would save almost nothing.

## U-Net speed: accuracy gate and timings

Gate: perception detection on the TEST 40 (`fastpath/perc_bench_speed.py`, the package year + every cached extra
NAIP year, scored by `perc_bench.evaluate`). The extra-year GeoTIFFs had been deleted to save disk and were fetched
again with `fastpath/heldout_refetch_years.py` (deleted again afterwards, `--clean`). P / R:

| pass, tile stride | hole greens | tee complexes | fairways | bunkers | water |
|---|---|---|---|---|---|
| float32 (OpenBLAS), 384: the cached reference of feae37f33 (re-scored today: same) | 0.928 / 0.891 | 0.848 / 0.832 | 0.876 / 0.838 | 0.928 / 0.878 | 0.637 / 0.502 |
| **AMX bf16, 384** | 0.929 / 0.891 | 0.848 / 0.834 | 0.875 / 0.838 | 0.927 / 0.878 | 0.637 / 0.502 |
| float32 (`conv32.c`, == OpenBLAS within 1/255), 448 = production since feae37f33 | 0.925 / 0.887 | 0.845 / 0.830 | 0.883 / 0.832 | 0.926 / 0.874 | 0.639 / 0.505 |
| **AMX bf16, 448** (production now) | 0.925 / 0.887 | 0.847 / 0.834 | 0.882 / 0.833 | 0.926 / 0.874 | 0.636 / 0.505 |

bf16 against float32 at the same stride moves no class by more than 0.4 points. The 384 -> 448 stride change of
feae37f33 (chosen on VAL, where it was equal) costs up to 0.4 points on TEST (green R, bunker R); that is not new.

Per tile (512 px, real weights), median of repeated runs, box shared with a routing job (load 4-6 on 4 CPUs):

| pass | 4 threads | 1 thread (taskset) |
|---|---|---|
| unet.py + C primitives + OpenBLAS (before) | 0.76 s (lightly loaded), 2.2-2.3 s at load 4-5 | 1.58 s |
| `conv32.c` float32 | 0.37-0.44 s at load 4-5 | 0.68 s |
| `amx.c` bf16 | 0.08-0.11 s | 0.13 s |

Whole scene build (`fastscene.build`, FASTSCENE_YEARS=2: 3 NAIP years), median of 3 runs (old path: 2-3), load 4-6:

| course (tiles a year) | stage | before (`FASTPERC_IMPL=c`) | float32 (`fp32`) | AMX (default here) |
|---|---|---|---|---|
| Remsen (15) | U-Net | 102.0 s | 21.4 s | 8.9 s |
| | total | 105.8 s | 26.4 s | 12.9 s |
| Kittansett (28, 21 hole greens) | U-Net | 139.3 s | 36.1 s | 16.0 s |
| | total | 154.9 s | 51.7 s | 30.7 s (perceive 13.4 s) |

The scene summaries are identical across the three passes. With AMX the U-Net stage is ~0.08 s a tile plus
~1.5 s a year of I/O and reprojection onto the stack grid (`rasterio.reproject`, 6 classes, average); the rest of
the build is perceive (2.3 s Remsen, 13.4 s Kittansett) and the grid (1.4 s). `GOLF_FASTC=0` (numpy reference)
gives the same summary in 128 s on Remsen.

Tried, not kept: softmax + window blend of each tile in C (no measurable gain over numpy, ~1 % of a tile); one
reprojection for all years on the same NAIP grid (the years' grids differ by a pixel or a half-pixel shift on most
courses); extra years only on uncertain tiles (3-7 % of tiles qualify, above).
