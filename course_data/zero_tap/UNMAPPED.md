# Unmapped courses (ROADMAP workstream 4): honest detection vs pairing

*2026-11-01, second pass.* Tiers `unmapped_card` / `unmapped_nocard` of the zero-tap benchmark (BENCH.md): no OSM
golf feature, only the blind perception scene (NAIP + 3DEP lidar -> `course_scene/1`), the NAIP segment model and
lidar pads. Code: `unmapped/` (`detect_eval.py` detection + pairing decomposition, `honest_eval.py` pairing + taps at
the dev threshold, `agree.py` two-router agreement confidence, `seq_extend.py`, `scene_fc.py` / `prep_u.py` /
`run_u.py` pathroute_v2 on scenes). Numbers: `unmapped/eval/honest.json`, `unmapped/eval/detect_{dev,test}.json`
(per-course provenance in `courses`).

## Data and provenance

* **Set: 55 -> 161 courses (dev 77, test 84).** Every v0 benchmark course already had a blind perception scene:
  the 55 in `perception/scenes/` and 106 more that formation's `fetch_inputs.py` built on Actions (run 39039375829)
  with the same `perceive.py` and committed models (`formation/inputs/<slug>/scene.json.gz`); the bench only looked
  in `perception/scenes/`. `bench_set.py` now falls back to the formation scene, and `benchmark.json` points at it
  (no new imagery was needed; the 152 v1 courses still have none, and they also lack formation `hole_pairs/1`, which
  sequence_v3 needs on the unmapped tiers).
* **Honest = the scene's perception models never trained on the course's state.** Every scene records its model id
  (`sources.models.perception`); `unmapped/perc_provenance.json` lists what each id trained on:

  | model id | made scenes for | trained on |
  |---|---|---|
  | perception-20261017-1050 | the 55 `perception/scenes` courses | 63 generalize courses in CA IL MA MS NH WI (list in the json) |
  | perception-20261017-1247 | the 106 `formation/inputs` courses | the same 63 courses / 6 states |

  | split | held-out (state never trained on) | in-sample: state trained on | in-sample: course itself trained on |
  |---|---|---|---|
  | dev (77) | **29** (GA KY ME MN UT WY) | 22 | 26 |
  | test (84) | **74** (AR CT DE IA ID MO NC NE NJ NV PA WA + 7 in GA KY ME UT) | 0 | 10 |

  So the honest test set is **74 courses / 1332 holes** (was 7). The 10 in-sample test courses (validation-set test
  courses in CA IL MA WI, used as perception *training labels*) show the leak clearly: green R / P 99.4 / 100 vs
  94.9 / 89.7 held-out. Other inputs: formation `hole_pairs/1` (sequence_v3's formation) come from A's model trained
  on dev-state courses only, so test is honest for it too; for dev, the 39 added courses use the committed
  (in-sample) hole_pairs, not out-of-fold ones (the OOF artifact is not downloadable here), so dev numbers of
  sequence_v3 / formation_v2 are optimistic.
* **Re-train on bench-dev states only (in flight, not yet in these numbers).** `perception/split.py` +
  `train.py`: the pool = courses in bench dev states that are not bench test courses; final models (used for bench
  test states) + 5 state-fold models `models/fold<k>/` (pool minus fold k's states), and `perceive.py` uses the
  fold that held a course's state out, so every dev-state scene becomes out-of-state (all 77 dev and the 17
  validation-set test courses). `models.json` records the exact course list per model (`courses`, `folds`).
  Pass 1 (`requests/perception_benchdev_pass1.json`, 145 dev-state courses: stacks + tables + training) and pass 2
  (`perception_benchdev_pass2.json`, re-perceive 212 courses with the new models, incl. the 67 test-state courses)
  are queued on Actions (runs 41353156906, 41357754039; runners were saturated). After pass 2: re-point
  `benchmark.json` at `perception/scenes` (`bench_set.py` prefers it), re-run formation hole_pairs on the new scenes
  (zt_formation `inputs`/`eval`), then the commands below.

## 1. Detection (bench tolerances; "every candidate" = the pairing ceiling)

| split | subset | candidates | holes | green R / P | tee-complex R / P | both R | courses with all greens |
|---|---|---|---|---|---|---|---|
| dev | held-out (29) | scene `kind=hole`, tee p>=0.5 | 522 | 96.6 / 93.5 | 91.4 / 82.6 | 88.9 | 17/29 |
| dev | held-out (29) | every candidate | 522 | 99.8 / 86.3 | 95.2 / 71.7 | 95.0 | 28/29 |
| dev | in-sample (48) | scene `kind=hole` | 864 | 95.3 / 90.7 | 94.9 / 84.9 | 91.6 | 35/48 |
| **test** | **held-out (74)** | scene `kind=hole`, tee p>=0.5 | 1332 | **94.9 / 89.7** | **88.7 / 81.0** | **85.4** | 44/74 |
| **test** | **held-out (74)** | every candidate | 1332 | **98.8 / 81.7** | **95.5 / 71.5** | **94.5** | 65/74 |
| test | in-sample (10) | scene `kind=hole` | 180 | 99.4 / 100 | 97.2 / 93.2 | 96.7 | 9/10 |

## 2. Pairing, numbering, taps (test run once; held-out = the 74 honest courses)

Taps = holes the golfer confirms so that pair precision reaches 98 %: the threshold is chosen on **dev** and
applied unchanged to test ("prec" = the precision it actually reaches on test). Unformed true holes split into
no green candidate / no tee candidate / both exist but mispaired.

| method | split | paired | all pairs right | numbered | holes right | taps @ dev threshold (prec) | unformed: no green / no tee / mispaired |
|---|---|---|---|---|---|---|---|
| sequence_v3 card | dev held-out (29) | 91.2 | 31.0 | 78.2 | 24.1 | 5.97 (97.5 %) | 1 / 17 / 28 |
| sequence_v3 card | **test held-out (74)** | **80.3** | **25.7** | **66.0** | **24.3** | 7.99 (96.4 %) | 16 / 43 / 203 |
| sequence_v3 nocard | test held-out (74) | 80.0 | 13.5 | 29.6 | 6.8 | 15.2 (96.9 %) | 16 / 42 / 208 |
| pathroute_v2_unmapped | dev held-out (29) | 87.2 | 27.6 | 28.0 | 6.9 | 6.79 (98.1 %) | 1 / 25 / 41 |
| pathroute_v2_unmapped | **test held-out (74)** | **80.5** | **18.9** | 24.4 | 6.8 | 7.92 (96.9 %) | 16 / 57 / 187 |
| formation_v2 (A, pairs only) | test held-out (74) | 81.1 | 6.8 | (5.2) | 0 | 8.69 (95.7 %) | 16 / 42 / 194 |
| **sequence_v3 + agreement confidence** (`agree.py`) | dev all (77) | | | | | 4.65 (98.1 %) | |
| **sequence_v3 + agreement confidence** | **test held-out (74)** | 80.3 | 25.7 | 66.0 | 24.3 | **6.45 (97.0 %)** | |

All tests: sequence_v3 card 81.9 / 27.4 / 68.7 / 26.2 (84 courses), pathroute 81.7 / 21.4 / 29.4 / 9.5.
pathroute_v2_unmapped was re-fitted with the same configuration chosen earlier (mix + all perception columns),
5-fold OOF over the 77 dev courses, test once; sequence_v3 for the 106 added courses was solved with the request's
settings (form_w 3, card variant c2 / c0) and the committed v3 gate (`seq_extend.py`), no refit.

**Reading.** (1) On honest courses about 80 % of holes are paired by every method (dev held-out 87-91 %), and only
19-26 % of courses get every pair right; with a card sequence_v3 numbers 66 % of holes and gets 24 % of courses
fully right. (2) The dev threshold does not carry to test: every method lands at 96-97 % instead of 98 % pair
precision, so the real taps-to-98 % on new states is higher than the 6-8 shown. (3) Agreement between the two
independent routers is the best confidence signal found: same holes as sequence_v3, ~1.5 fewer taps per course
than either router alone at higher precision (dev-chosen rule, test once).

## 3. Weakest link: pairing between real candidates, then false detections

On the 74 honest test courses, of ~260 unformed true holes per method 72-77 % have both a green and a tee candidate
(mispaired), 16-22 % have no tee candidate within tolerance, ~6 % no green candidate. Classifying the *wrong
predicted holes* (aggregate counts only): pathroute on dev (77) 70 used a real tee of another hole, 49 a false tee,
46 a false green; on test held-out 94 / 63 / 56; sequence_v3 on dev 43 / 47 / 101 (it keeps more uncertain greens).
So roughly half the error is the router choosing among real tees (the cart-path walk model has little to use:
perceived paths reach 37 % length recall) and half is detection precision (tee precision 71-81 %, green 82-90 %).
Per-course failures were not inspected for tuning; the next tuning step should look at dev courses only.

**Next:** (a) finish the bench-dev re-train (passes 1-2) and re-run this table on the new scenes, so dev tuning is
out-of-state too; (b) tee precision: a per-candidate "is this a tee" re-scorer trained on dev with hole context
(nearest green distance / fairway axis / box count), since false tees feed half the mispairs; (c) pairing between real
tees: better cart-path perception or a corridor (fairway-between) term; (d) calibrate the per-hole confidence for
state shift (dev 98 % -> test 96-97 %), e.g. a margin on the dev threshold; (e) v1 courses (152) need imagery + formation
hole_pairs before they can join the unmapped tier.

## Earlier: what was tried on the 55-course set (perception in-sample for 37 of them)

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

## Reproduce

```bash
export OMP_NUM_THREADS=1
python course_data/zero_tap/unmapped/detect_eval.py --split test --results course_data/zero_tap/results/sequence_v3/unmapped_card
python course_data/zero_tap/pathroute/prep.py --cache C1 --split all
python course_data/zero_tap/pathroute_v2/prep2.py --cache C1 --out C2
python course_data/zero_tap/unmapped/prep_u.py --out CU --split all
python course_data/zero_tap/unmapped/run_u.py --cu CU --c1 C1 --c2 C2 --train mix --perc all --test --out course_data/zero_tap/results/pathroute_v2_unmapped   # ~25 min, 1 core
python course_data/zero_tap/unmapped/honest_eval.py --results course_data/zero_tap/results/{sequence_v3,pathroute_v2_unmapped}/unmapped_card --json course_data/zero_tap/unmapped/eval/honest.json
python course_data/zero_tap/unmapped/agree.py agree_mean     # dev rule choice + test once, writes results/sequence_v3_agree/
python -m pytest course_data/zero_tap/unmapped/test_unmapped.py -q
```

Scoreboard note: the unmapped tiers now have 161 courses; methods whose unmapped results cover only the old 55
(routing_v2, structure, sequence_v2) score the other 106 as `no_result` until re-run.
