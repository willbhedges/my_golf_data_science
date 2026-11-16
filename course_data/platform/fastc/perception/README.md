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
| `fp_roll` | the roll-out loop of `mozingo/tee_strategy.simulate` on the lie raster | `fastpath/solve.py` through `solve_c.py` | identical arrays (every hole x club x 3 aims of 2 courses); decision.json identical on 3 courses | solve 4.4-4.9 -> 1.1-1.5 s |
| `fp_dist_to_rings` | `structure/scene.py _dist_to_rings` | the structure solver's scene (package build) | exact | small on the courses measured |

Whole-stage effect, Yorba Linda: the scene build with the pixel classifier went from 23.3 to 11.8 s with
byte-identical scene.json. The U-Net scene build takes 42 s (U-Net 32 s for 40 tiles, perceive 6.2 s, grid 1.5 s).
The U-Net step was 62 s until `OMP_WAIT_POLICY=PASSIVE`: libgomp's spinning threads were stealing the OpenBLAS
cores.

## unet.py: the segment U-Net without torch

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
* The U-Net GEMMs are OpenBLAS. 40 tiles x 63 GFLOP run at about 80 GFLOP/s effective against a 313 GFLOP/s SGEMM
  peak on this box. The rest is im2col memory traffic and small matrices.
