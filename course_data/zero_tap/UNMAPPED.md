# Unmapped courses (ROADMAP workstream 4): detection vs pairing

*2026-11-01.* Tiers `unmapped_card` / `unmapped_nocard` of the zero-tap benchmark (BENCH.md): no OSM golf feature,
only the perception scene (NAIP + 3DEP lidar → `course_scene/1`), the NAIP segment model and lidar pads.
Code: `unmapped/` (`detect_eval.py` detection + pairing decomposition, `scene_fc.py` scene → OSM-style fc,
`prep_u.py` / `run_u.py` pathroute_v2 on perception scenes, `percfeat.py` perception feature columns).
Results: `results/pathroute_v2_unmapped/unmapped_{card,nocard}/`, numbers `unmapped/eval/*.json`.

## What data exists

- **55 courses** (dev 38 / test 17) have a perception scene + segment model + lidar pads; all are v0 courses. The
  152 v1 courses have no NAIP / lidar fetched. Raw raster stacks are local for only 3 courses
  (`perception/dev/`, 700×700 crops), so detection could not be re-run from pixels here; everything below works on
  the perception / segment / pad *outputs*.
- **Leakage caveat (important).** The perception object models (green, tee box, tee complex, green→tee edge) were
  trained on OSM labels of their "train" states (CA IL MA MS NH WI …). **37 of the 55 unmapped courses are in
  those states** (dev 27, test 10), so their detections and `p` values are in-sample. Only GA KY MN UT ME WY
  (dev 11, test 7) are honest. Every table splits the two; trust the **held-out** rows.
- These 55 are courses OSM maps well (the truth needs OSM hole ways), so they are easier than a real unmapped
  course (likely smaller, more canopy, worse NAIP).

## 1. Baseline: detection is not the main loss — pairing is

Detection scored with the bench's own tolerances (green within 12 yd of the true edge / 20 yd of the line end;
tee within 35 yd of the start or 30 yd of the line's first 60 %). "both R" = true holes with a detected green
*and* tee = the ceiling for pairing.

| split | subset | candidates | green R / P | tee-complex R / P | both R | courses with all greens |
|---|---|---|---|---|---|---|
| dev | held-out (11) | scene `kind=hole`, tee p≥0.5 | 98.0 / 94.6 | 91.4 / 85.4 | 89.4 | 9/11 |
| dev | held-out (11) | every candidate | 100 / 90.4 | 93.9 / 77.0 | 93.9 | 11/11 |
| dev | in-sample (27) | scene `kind=hole` | 98.8 / 95.4 | 97.5 / 91.2 | 96.3 | 23/27 |
| test | held-out (7) | scene `kind=hole` | 91.3 / 92.7 | 92.1 / 79.8 | 85.7 | 3/7 |
| test | held-out (7) | every candidate | 96.0 / 85.8 | 96.8 / 64.8 | 93.7 | 5/7 |
| test | in-sample (10) | scene `kind=hole` | 99.4 / 100 | 97.2 / 93.2 | 96.7 | 9/10 |

Pairing of the existing methods (paired = bench "formed"; all-pairs = course with every hole paired; unformed true
holes split into *no green candidate at all* / *no tee candidate at all* / *both exist but mispaired*):

| method | split | paired | all-pairs | numbered | unformed: no green / no tee / mispaired | held-out paired / all-pairs |
|---|---|---|---|---|---|---|
| sequence_v3 card | dev | 89.0 % | 44.7 % | 80.1 % | 3 / 12 / 60 | 87.9 / 36.4 |
| sequence_v3 nocard | dev | 90.5 % | 31.6 % | 25.9 % | 3 / 11 / 51 | 87.9 / 18.2 |
| routing_v2 card | dev | 73.7 % | 5.3 % | 69.3 % | 3 / 12 / 165 | 71.7 / 0 |
| structure card | dev | 67.7 % | 2.6 % | 49.4 % | 3 / 18 / 200 | 62.1 / 0 |
| sequence_v3 card | test | 86.9 % | 23.5 % | 77.1 % | 6 / 3 / 31 | 77.8 / 0 |
| sequence_v3 nocard | test | 87.3 % | 23.5 % | 43.5 % | 6 / 3 / 30 | 80.2 / 0 |
| routing_v2 card | test | 67.3 % | 0 % | 61.8 % | 5 / 2 / 93 | 51.6 / 0 |

On dev, ~80 % of the unformed holes have both a green and a tee candidate (mispairing). Detection costs ~3 % of
holes in-sample but **6–14 % on held-out states** (test held-out: green recall 91 %, both 86 %), and it is
concentrated: one dev course (paintsville_ky, hilly, wooded) holds 9 of the 18 dev tee misses.

## 2. What was tried

**pathroute_v2 on perception scenes** (`scene_fc.py`): perceived greens (all kinds), tee *boxes* of every
complex, fairways, cart-path edges, water, clubhouse are written as OSM-tagged features on top of the tier's
golf-stripped OSM file, so pathroute's v1+v2 features, complex model, crossing / reuse beam and per-hole
calibration run unchanged. Dev = 5-fold OOF over the 38 dev courses (held-out fold removed from the OSM training
pool too); test run once.

| variant (dev OOF, nocard pairing) | paired | all-pairs | held-out paired / all-pairs | taps to 98 % |
|---|---|---|---|---|
| models from OSM dev only | 87.6 | 23.7 | – | 9.9 |
| unmapped dev only | 87.7 | 28.9 | 84.8 / 36.4 | 14.0 |
| OSM + unmapped (mix) | 86.7 | 28.9 | 84.8 / 27.3 | 7.6 |
| one tee per perceived complex instead of boxes | 81.7 | 13.2 | – | 10.3 |
| greens / tees p ≥ 0.3 only | 83.0 | 23.7 | – | 9.0 |
| + lidar pads / segment tees as extra tee candidates | 84.8 | 18.4 | – | 13.0 |
| unm + perception columns, geometry only (raised_m, box count, same complex) | 87.7 | 31.6 | 83.3 / 27.3 | 12.7 |
| unm + perception p's, no green→tee relations | 88.3 | 28.9 | 84.3 / 18.2 | 11.7 |
| unm + all perception columns (+ p_next / p_edge) | 90.8 | 42.1 | – | 8.1 |
| **mix + all perception columns (chosen on dev)** | **91.1** | **39.5** | **84.8 / 36.4** | **5.1** |

Detection fallbacks, measured before routing: virtual tees at the far end of perceived fairways reach 6–11 of the
18 dev holes with no tee candidate, but **0–1 of them land within 35 yd of the real tee** (they only score through
the bench's generous along-the-line tolerance and would give a wrong tee yardage), so they were not used. Lidar
pads cover 7/18 of the missing tees but come at ~190 pads per course; adding them (and segment-model tee blobs)
tripled the tee candidates and lowered pairing.

## 3. Result (test, run once, mix + all perception columns)

| tier | method | paired | all-pairs | numbered | holes right | held-out paired / all-pairs | taps to 98 % pairs |
|---|---|---|---|---|---|---|---|
| unmapped_nocard | sequence_v3 (baseline) | 87.3 % | 23.5 % | 43.5 % | 5.9 % | 80.2 / 0 | – |
| unmapped_nocard | **pathroute_v2_unmapped** | 83.3 % | 23.5 % | 44.8 % | 11.8 % | 76.2 / 14.3 | 6.4 / course (98.0 %) |
| unmapped_card | sequence_v3 (baseline) | 86.9 % | 23.5 % | 77.1 % | 23.5 % | 77.8 / 0 | – |
| unmapped_card | pathroute_v2_unmapped (card pars only) | 83.3 % | 23.5 % | 44.8 % | 11.8 % | 76.2 / 14.3 | 6.4 / course |

**Not an improvement on pairing.** The dev gain (+4 pts paired, +11 pts all-pairs over the plain adapter) is
entirely on the in-sample courses: on held-out dev it is 84.8 → 84.8 paired, and the columns that give it are the
perception edge model's `p_next` / `p_edge`, whose own held-out top-1 is 53 % vs 73 % in-sample (REPORT.md).
On test it pairs 4 pts fewer holes than sequence_v3. What it does add: a calibrated per-hole confidence (98 % pair
precision at 6.4 taps per course on test; dev threshold 0.917) and better nocard numbering (44.8 vs 43.5 %).
sequence_v3 stays the best unmapped router; with a card it also numbers far better (77 vs 45 %), because
pathroute_v2 has no card-length term. Results are committed for comparison but should not replace sequence_v3.

## What limits it

1. **Evaluation, before anything else.** 18 honest courses (11 dev, 7 test, ~320 holes) — differences of one or
   two courses swing all-pairs by 5–15 pts. The perception models need a re-fit with the bench split (or with
   folds over courses) before any unmapped number above in-sample is meaningful. Cheapest real fix: re-train
   perception on bench-dev states only and re-run `perceive.py` for the 55 (Actions, perception.yml).
2. **Detection on held-out states**: green recall 91 % and tee recall 92 % (test held-out) — every missed green
   costs a hole and usually the numbering after it; false tees (precision 65–80 %) feed mispairing. Losses cluster
   on wooded / hilly courses (leaf-on NAIP hides tees under canopy; lidar pads there are dense and noisy).
3. **Pairing evidence**: the perceived cart paths are weak (length recall 37 %, connectivity 31 %, REPORT.md),
   so pathroute's walk model — what made v2 good on OSM — has little to work with.
4. **No pixels locally**: NAIP 0.6 m / lidar stacks exist for 3 courses only, so texture / flatness detectors
   (green blobs 400–900 m², mown tee rectangles) could not be built or tuned here. Fetch via a
   `ztbench_data_*` imagery request (and for the 152 v1 courses, which have no imagery at all).

## Reproduce

```bash
export OMP_NUM_THREADS=1
python course_data/zero_tap/unmapped/detect_eval.py --split dev --results course_data/zero_tap/results/sequence_v3/unmapped_card
python course_data/zero_tap/pathroute/prep.py --cache C1 --split all
python course_data/zero_tap/pathroute_v2/prep2.py --cache C1 --out C2
python course_data/zero_tap/unmapped/prep_u.py --out CU --split all
python course_data/zero_tap/unmapped/run_u.py --cu CU --c1 C1 --c2 C2 --train mix --perc all --test --out course_data/zero_tap/results/pathroute_v2_unmapped   # ~8 min, 1 core
python -m pytest course_data/zero_tap/unmapped/test_unmapped.py -q
```
