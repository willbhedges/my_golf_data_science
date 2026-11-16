# Notes from the perception / hole-inference side (fast path)

## Requests to the fetch / imagery side

None open. The perception scene reads only what the fetch stage already writes: `imagery/naip_rgb.tif`,
`imagery/naip_nir.tif` (0.6 m, NAIP CRS), `imagery/dem.tif` (1 m UTM), `canopy/chm_meta.tif`, `raw/course.json`,
`raw/osm.geojson` (non-golf OSM buildings / roads are used as a negative mask).

## The segment U-Net

`fastscene.py` uses our own U-Net (`course_data/segment/models/golfseg_own/`, imported from Actions run 38987845450
on 2026-11-16 with the user's approval) through the torch-free forward pass `fastc/perception/unet.py`, and falls
back to the LightGBM pixel classifier (`fastscene_model/`) when `FASTSCENE_UNET=0` or the file is missing. The
ariadgolf weights have no licence grant and are not in the repository.

Held-out object metrics (perception/evaluate.py, the 9 blind-loop tier A / B courses outside both models'
training data; `fastscene_model/eval/`):

| element | U-Net (golfseg_own) P / R | pixel classifier P / R |
|---|---|---|
| hole greens | 0.93 / 0.85 | 0.94 / 0.62 |
| tee complexes | 0.84 / 0.70 | 0.90 / 0.58 |
| fairways | 0.93 / 0.79 | 0.85 / 0.60 |
| bunkers | 0.85 / 0.90 | 0.88 / 0.54 |
| water | 0.45 / 0.44 | 0.45 / 0.44 |

## Gate for courses routed on detections (fast.py)

Every hole whose green or tee came from the detector is flagged (`gate.json` confirm, `confirm_scene.json`
questions, least certain first). A course is shown only when it has min margin >= 4, no virtual hole, passes the
existing gates and has at most 3 flagged holes (status `confirm`). Otherwise it is blocked with the reason.

## Detection benchmark on simulated-unmapped courses (2026-11-16, perception agent)

Sets (`heldout.py`; packages in `cache/heldout/`, not committed): **TEST** = 40 courses never tuned on: the 9
blind-loop tier A / B courses (`cache/packages/b20_*`; Pheasant Ridge IA dropped: its OSM id is in the U-Net's
training index, so the old "9 held-out" table above included one training course) + the 31 generalize
validation-set test courses. **VAL** (all choices) = 30 generalize validation-set train courses. **TRAIN** (object
models) = 35 perception pool courses outside VAL / TEST and the U-Net index. Simulated unmapped: the detector
never reads OSM golf features (course outline + non-golf OSM buildings / roads only), NAIP year = newest covering
year (no OSM year scoring; the b20 packages kept their scored year). Scoring = perception/evaluate.py (object
level, pooled over eligible courses). U-Net probabilities are cached per course and variant (`perc_bench.py`).

Per-class precision / recall, object level:

| step | set | hole greens | tee complexes | fairways | bunkers | water |
|---|---|---|---|---|---|---|
| baseline (U-Net d0, perception models, NIR water rule) | TEST 40 | 0.911 / 0.790 | 0.811 / 0.758 | 0.916 / 0.757 | 0.844 / 0.831 | 0.442 / 0.350 |
| baseline | VAL 30 | 0.894 / 0.924 | 0.857 / 0.855 | 0.953 / 0.868 | 0.838 / 0.916 | 0.791 / 0.398 |
| + water from the U-Net (seeded by the NIR rule, U-Net veto on rule blobs) | VAL 30 | = | = | = | = | 0.931 / 0.516 |
| + water from the U-Net | TEST 40 | = | = | = | = | **0.649 / 0.498** |
| VAL re-based on all 51 VAL courses (water as above) | VAL 51 | 0.918 / 0.862 | 0.822 / 0.782 | 0.936 / 0.799 | 0.854 / 0.893 | 0.839 / 0.538 |
| + second-stage object models, cross-fitted (2 VAL folds) | VAL 51 | 0.918 / 0.894 | 0.823 / 0.823 | = | = | = |
| + second-stage object models (final: TRAIN + VAL) | TEST 40 | **0.916 / 0.831** | **0.818 / 0.806** | = | = | = |
| tried, not kept: green blob split at distance-transform necks (700 m2) | VAL 51 | 0.917 / 0.863 | = | = | = | = |
| tried, not kept: detections kept within 40 m of the outline (not 25) | VAL 51 | = | 0.819 / 0.783 | 0.934 / 0.799 | = | 0.825 / 0.547 |

| seg thresholds for our U-Net: fairway 0.5 -> 0.3, bunker 0.5 -> 0.4 (VAL: fairways 0.936 / 0.799 -> 0.916 / 0.838) | TEST 40 | 0.915 / 0.832 | 0.818 / 0.806 | 0.871 / 0.807 | 0.839 / 0.835 | 0.649 / 0.498 |
| + **multi-year NAIP fusion** (U-Net probabilities averaged over the package year + 2 other NAIP years) | TEST 40 | **0.928 / 0.891** | **0.848 / 0.832** | **0.876 / 0.838** | **0.928 / 0.878** | **0.637 / 0.502** |
| tried, not kept: 3-view TTA (identity, flip, rot90) on 12 VAL courses | VAL 12 | 0.925 / 0.925 (d0 0.925 / 0.934) | 0.890 / 0.815 (0.870 / 0.820) | 0.972 / 0.898 (0.958 / 0.889) | 0.820 / 0.909 (0.813 / 0.904) | = |
| multi-year on the same 12 VAL courses | VAL 12 | 0.943 / 0.951 | 0.914 / 0.815 | 0.971 / 0.877 | 0.892 / 0.951 | 0.889 / 0.473 |
| tile stride 448 instead of 384 (speed), 12 VAL courses | VAL 12 | 0.934 / 0.934 | 0.877 / 0.815 | 0.966 / 0.881 | 0.814 / 0.903 | 0.909 / 0.462 |
| tried, not kept: tile 384 / stride 352 | VAL 12 | 0.921 / 0.925 | 0.858 / 0.820 | 0.953 / 0.885 | 0.818 / 0.903 | 0.907 / 0.451 |

Totals TEST 40, before -> now (P / R): hole greens 0.911 / 0.790 -> 0.928 / 0.891; tee complexes 0.811 / 0.758 ->
0.848 / 0.832; tee boxes 0.756 / 0.681 -> 0.827 / 0.739; fairways 0.916 / 0.757 -> 0.876 / 0.838; bunkers
0.844 / 0.831 -> 0.928 / 0.878; water 0.442 / 0.350 -> 0.637 / 0.502.

**Detector version for routing: the commit that adds this line, probs variant `d0+yall`** (perc_bench: the package
year + every cached extra year; on TEST computed with stride 384, production uses 448, equal on VAL). Single-year
equivalent: `d0` (same commit).

Multi-year (default, `FASTSCENE_YEARS=2`; 0 = one year): fastscene.build fetches the 2 newest other NAIP years
(coverage > 0.9, >= 2012) once through `fast_imagery.fetch_years` into `imagery/years/<year>/` at 0.6 m (3-8 MB a
year) and averages the U-Net probabilities. Cost: 3 U-Net passes instead of 1 (stride 448 takes back ~30 %), plus
the year fetch (10-30 s, cached). Different flights / seasons separate greens from fairways differently; the gain
is largest on bunkers and tees (precision) and greens (recall).

For routing (NOTES_ROUTING.md asks), measured on TEST 40 with d0+yall:
* tee complexes serving two hole starts (a p >= 0.5 complex within 30 m of >= 2 OSM starts): 29 of 963 complexes,
  63 of 737 starts. Changing the box -> complex clustering (merge 70 -> 40 / 0 m, gap 10 -> 6 m) does not change
  it on VAL (43 / 42 / 42 / 43 merged): those boxes touch, so splitting needs the hole axis (routing side), not the
  clustering. Not fixed.
* practice greens: 77 OSM practice greens; 15 detected and called practice, 15 called hole (false hole greens),
  the rest not detected as greens or "uncertain". The green model has a practice class (98 practice rows in
  training); more practice examples would be the lever. Not fixed beyond that.

Second-stage object models (`perc_objects.py`, `fastscene_model/objects_unet/`, default; `FASTSCENE_OBJECTS2=0`
restores perception's models): green / tee box / tee complex HistGradientBoosting models trained on OUR U-Net's
candidates (perception's were trained on the ariadgolf model's) of TRAIN (35) + VAL (51), labels from OSM through
perception/evaluate.py. Extra candidate features: the five U-Net classes inside the candidate and in a 3-25 m ring
(fairway / bunker around a green), NIR / green-band std inside, NDVI / brightness / NIR contrast with the ring,
canopy max inside and tree fraction in the ring, DEM plane-fit residual, plane slope, relief against the ring,
distance to the nearest fairway centreline end. Used only when the scene comes from the U-Net.

Water (perc_objects.install_water, default `FASTSCENE_WATER=unet`): pixels with U-Net p_water >= 0.5 (or NIR-rule
pixels with p_water >= 0.25), opened, holes filled; a U-Net component is kept only if it holds pixels of the
NIR rule's own water, and a rule component is dropped when its mean p_water < 0.05 (tree shadows / dark roofs the
rule takes for ponds). Alone, the U-Net water class finds more ponds (VAL recall 0.77) but adds bright false
ponds (precision 0.34); `FASTSCENE_WATER=rule` restores the old detector.
