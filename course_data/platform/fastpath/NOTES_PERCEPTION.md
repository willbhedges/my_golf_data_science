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

## 2026-11-19: national U-Net fine-tune (golfseg_own_v2), now the default

`detector.py`: `FASTSCENE_UNET_MODEL` = `v2` (default) -> `segment/models/golfseg_own_v2` + second-stage object models
`fastscene_model/objects_unet_v2` + routing fits `route_models/v2/`; `v1` rolls back to golfseg_own + objects_unet +
the routing files at the top of this folder (`FASTSCENE_UNET=<file>` still overrides the weights).

Model (README in the model folder): v1 fine-tuned on 1383 well-mapped OSM courses from 49 lower-48 states + DC
(`segment/train/pick_v2.py` -> `v2_courses.json`, 1500 drawn; `build_dataset.py --courses --quality`; Actions run
44408172242 data, 44417856467 training, 6353 steps on CPU, exported step 3783 = best mean validation IoU).
Excluded from the draw: every validation-set course (train + test), blind20 (TEST-40's b20), the perception
stacks_meta pool, the heldout sets, all 900 TRAIN-BIG manifest courses, and anything within 1.5 km of them
(checked after the build: 0 ids, 0 within 1.5 km). Same input / normalisation as v1, so fastc/perception runs it
unchanged. heldout.py's leak check now reads dataset_index.json and dataset_index_v2.json (sets unchanged:
TEST 40 / VAL 51 / TRAIN 63). Validation IoU on 54 held-out national courses, v1 -> v2: green 0.647 -> 0.689, tee
0.331 -> 0.352, fairway 0.631 -> 0.687, bunker 0.493 -> 0.526, water 0.602 -> 0.747 (mean 0.541 -> 0.600).

The second-stage object models were refitted on v2's candidates the same way objects_unet was (perc_objects fit on
TRAIN + VAL d0 rows; rows in cache/v2root/heldout/rows). v2 has all 63 TRAIN courses (v1's fit had 31; the
missing pool packages were fetched for this). With v1's object models v2 lost tee complexes (0.779 / 0.811).

TEST-40 (production path: AMX, stride 448, d0+yall), P / R; v1 = test_speedgate_amx448 (reproduced exactly):

| element | v1 | v2 (v1 object models) | **v2 (objects_unet_v2, default)** |
|---|---|---|---|
| hole greens | 0.925 / 0.887 | 0.924 / 0.929 | **0.939 / 0.917** |
| tee complexes | 0.847 / 0.834 | 0.779 / 0.811 | **0.941 / 0.765** (F1 0.840 -> 0.843) |
| tee boxes | 0.829 / 0.739 | 0.760 / 0.712 | **0.864 / 0.676** (F1 0.78 = 0.78) |
| fairways | 0.882 / 0.833 | 0.883 / 0.830 | **0.883 / 0.830** |
| bunkers | 0.926 / 0.874 | 0.920 / 0.895 | **0.920 / 0.895** |
| water | 0.636 / 0.505 | 0.736 / 0.482 | **0.736 / 0.482** |

TEST-40 was read twice (before / after the object-model refit; nothing tuned on it). Tee complexes trade recall for
precision (the refitted tee-complex threshold is 0.40 vs 0.325); for routing the lost complexes are the next lever
(NOTES_ROUTING.md). Probabilities: cache/v2root/heldout/probs (perc_bench PERC_PROBS_DIR; PERC_ROWS_DIR for rows).

## 2026-11-20: tee-targeted fine-tune golfseg_own_v3 (opt-in FASTSCENE_UNET_MODEL=v3; v2 stays the default)

Why: the learning curve (v1 130 -> v2 1329 courses) moved green IoU 0.647 -> 0.689 but tee IoU only 0.331 -> 0.352,
and the routing bench recall is weakest on wooded tees (tree cover > 0.5 within 15 m: 79 %), small tees (< 100 m2: 86 %),
par-3 / exec (88 %) and short courses (85 %). v3 fine-tunes v2 with more courses, a tee-label filter and oversampling
of those groups. Expected routing gain was modest (+10-40 bench holes).

Data (`segment/train/pick_v3.py` -> `v3_courses.json`): v2's draw and label filter with the 1500 v2 courses also excluded
(id and 1.5 km, as for every evaluation set and TRAIN-BIG); no per-state cap (with 60 a state only 1021 courses / 26 states
were left): 1510 drawn, 26 states. `build_dataset.py --quality --tee-quality` (tees >= holes, median tee polygon 40-1500 m2,
>= 85 % of tee polygons 15-4000 m2; passed 36 of 40 local heldout courses, the 4 rejects had tees < holes) kept 1404
(`dataset_index_v3.json`, data run 44730428783). Trained on v2's data + these: 2661 training courses.

Tree cover for the wooded-tee weight: a NAIP-only proxy was tried first and is useless per tee (vs Meta CHM >= 3 m
within 15 m: corr 0.25 rule-based, 0.31 logistic; pixel AUC 0.79-0.85), so `segment/train/chm_add.py` warps the Meta / WRI
canopy height COGs (free, CC BY 4.0) onto every training image grid (tree = >= 3 m, the bench's rule; 1.7 s a course,
99.98 % agreement with the package chm_meta.tif).

Training (`train_v2.py`, all new flags default off so the v2 recipe is unchanged): init golfseg_own_v2, lr 1e-4,
`--tee-focus small=2,wood=4,exec=2.5,short=1.5` (tee crop centres on small / wooded tee components, course picks on
par-3 / exec and short courses), `--tee-min 1`, `--select green,tee` (export the checkpoint with the best mean green +
tee validation IoU, chosen before training), `--max-val 120`. Fine-tune from v2 on v2 data + new data rather than new data
alone: keeps what v2 learned, the oversampling only shifts emphasis, and the hash-based validation split equals v2's, so
v2's step 0 is a direct comparison. Actions: data 44730428783 (smoke failed there: --tee-min dropped the synthetic courses,
fixed in 489f21b01), training 44731500659 (8467 steps in 2 jobs, exported step 4500), import 44811363124
(`segment/models/golfseg_own_v3`, README with sha256). Pool loads: 44 exec / 115 short / 1352 regular courses; 82 090
tee components, 37 231 small, 2 387 wooded; 1 511 loads with a canopy mask.

Validation IoU (120 held-out national courses), v2 (step 0) -> v3 (step 4500): green 0.702 -> 0.719, tee 0.360 -> 0.383,
fairway 0.707 -> 0.714, bunker 0.512 -> 0.526, water 0.752 -> 0.763, mean 0.607 -> 0.621. Noisy along the run (step 1500:
tee 0.329; last step 8467: tee 0.372, mean 0.622).

Second-stage object models `fastscene_model/objects_unet_v3` (956aff9d6): v2's recipe on v3's d0 candidates of the same
114 courses (TRAIN 63 + VAL 51); rows green 2121 / tee box 8342 / tee complex 3140 (v2 2093 / 8724 / 3251); thresholds tee
box 0.35 (v2 0.425), tee complex 0.40 (= v2). detector.objects_dir: v3 without its folder falls back to objects_unet_v2
(stderr note).

Gate 1, TEST-40 (read once, production path d0+yall, stride 448). The TEST packages' extra NAIP year tifs had been
deleted locally; refetched per course (heldout_refetch_years.py) and deleted again. Six newest years are no longer in the
catalogue (b20_crow_canyon 2024; b20_chevy_chase, b20_cedar_glen, b20_kittansett, b20_falls_village, b20_twisted_pine 2025),
so v2 is scored on exactly the views v3 has (its cached probabilities, linked; v2's own original read was 0.941 / 0.765 tee
complexes and 0.939 / 0.917 greens, within 0.002 of the paired reference). Verified on a 5-course dry run with v2 weights
standing in for v3: probabilities bit-identical, per-course scores identical. P / R (F1):

| element | v2 (paired, objects_unet_v2) | **v3 (objects_unet_v3)** |
|---|---|---|
| hole greens | 0.939 / 0.917 (0.928) | **0.936 / 0.929 (0.932)** |
| greens any | 0.974 / 0.869 (0.919) | 0.968 / 0.897 (0.931) |
| tee complexes | 0.942 / 0.763 (0.843) | **0.933 / 0.811 (0.868)** |
| tee boxes | 0.863 / 0.674 (0.757) | **0.859 / 0.709 (0.777)** |
| fairways | 0.881 / 0.829 (0.854) | 0.857 / 0.843 (0.850) |
| bunkers | 0.922 / 0.895 (0.908) | 0.930 / 0.895 (0.912) |
| water | 0.732 / 0.479 (0.579) | 0.724 / 0.482 (0.579) |

Regressions: hole-green precision -0.3 pt, tee-complex precision -0.9 pt, fairway precision -2.4 pt (F1 -0.004). Per course:
tee complexes found more on 21, fewer on 6 (largest green_harbor_ma +5, kingwood_ga +4, b20_zintel_creek +4, elmcrest_ma +3,
arrowhead_pointe_ga +3, willowbend_ma +3, woods_hole_ma +2 (a v2 test-28 routing loss traced to lost complexes);
chaska_wi -2); hole greens more on 7, fewer on 4. Gate 1 passes (tees up, greens not worse). Gate 2 (routing bench, paired
v2 / v3 on identically rebuilt scenes) runs on GitHub Actions (routing_bench.yml); v3 is not the default until it passes,
the routing fits are refitted on v3 scenes, and the blind loop and one test-28 read are done.

**Gate 2 result (2026-11-20): fails; v3 stays opt-in.** Paired on 596 TRAIN-BIG courses under v2's routing fits, v3 nets
+2 holes with objects_unet_v2 and +1 with objects_unet_v3 (choice -7 / -17, never-used +9 / +18). Green and tee recall
rise (tees +1.3 / +2.6 pt). Tables, runs and caveats: NOTES_ROUTING.md, "gate 2 for golfseg_own_v3". Next is a
routing refit on v3 scenes against a v2 refit on the same rebuilt inputs (the Actions refit stage).

Reproduce: scratch v3/gate1s.sh (streaming: VAL / TRAIN rows then their probabilities deleted, TEST per course: refetch years,
v3 probs, eval v3, eval v2 on the same views, delete), v3/gate1_pool.py; per-course evals cache/heldout/eval/test_g1v3_<slug>.json,
test_g1v2pair_<slug>.json; rows cache/v3root/heldout/rows.
