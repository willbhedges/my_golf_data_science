# Sequence v2 on D's benchmark: A's hole pairs + gate v2

Actions run 39054373440 (`.github/workflows/zero_tap_seqv2.yml`, request `course_data/requests/zt_seqv2_v2.json`).
Per-course results are in `course_data/zero_tap/results/sequence_v2/<tier>/` (method `sequence_v2`). The machine-readable
board is in `bench_d.json`, the gate in `gate_params.json`, the dev choice of formation weight in `pick_w.json`, and
the solver rows in `zrows.json.gz`. **The gate was fitted on dev only. Test was scored once.**

## Before / after (D's scorer)

"Certain & right" = certified courses where every hole number and every known par is right. "Max coverage at
>= 99 %" is the best coverage any score threshold reaches at >= 99 % precision on that split. On test it is an oracle
number, shown for comparison; the shipped flag is the "certain" column.

| split | tier | version | courses | holes numbered right | fully right | certain | certain & right | precision | max coverage at precision >= 99 % |
|---|---|---|---|---|---|---|---|---|---|
| dev | osm_card | v1 | 77 | 59.8% | 15.6% | 4 | 4 | 100.0% | 5.2% |
| dev | osm_card | v2 | 77 | 79.3% | 22.1% | 1 | 1 | 100.0% | 1.3% |
| dev | nocard | v1 | 77 | 31.0% | 3.9% | 0 | 0 | - | 0.0% |
| dev | nocard | v2 | 77 | 36.2% | 3.9% | 0 | 0 | - | 0.0% |
| dev | unmapped_card | v2 | 38 | 79.7% | 31.6% | 0 | 0 | - | 5.3% |
| dev | unmapped_nocard | v2 | 38 | 25.9% | 7.9% | 0 | 0 | - | 2.6% |
| **test** | osm_card | v1 | 84 | 58.0% | 11.9% | 7 | 3 | 42.9% | 2.4% |
| **test** | osm_card | v2 | 84 | **71.8%** | **14.3%** | 0 | 0 | - | 0.0% |
| **test** | nocard | v1 | 84 | 17.3% | 0.0% | 2 | 0 | 0.0% | 0.0% |
| **test** | nocard | v2 | 84 | **27.2%** | 0.0% | 0 | 0 | - | 0.0% |
| **test** | unmapped_card | v2 | 17 | 73.9% | 17.6% | 0 | 0 | - | 5.9% |
| **test** | unmapped_nocard | v2 | 17 | 43.5% | 0.0% | 0 | 0 | - | 0.0% |

v1 did not run the unmapped tiers. For reference, on test osm_card routing_v2 (D's scoreboard) has 69.4 % of holes
numbered right and 14.3 % of courses fully right.

Formed (pairs right) for v2: dev 88-91 %, test 82-87 %. Dev uses out-of-fold pairs, so these match A's own numbers on
new states.

**Verdict.** Ordering got much better: +14 points of holes numbered right on test osm_card and +10 on test nocard.
That beats routing_v2 on hole numbers and ties it on courses fully right. The gate no longer makes false claims:
v1 certified 9 test courses and 6 were wrong; v2 certifies none. The ≥ 99 % gate still covers almost nothing,
though: 1 dev course and 0 test courses. The zero-tap promise is not met yet.

## What changed

1. **A's pairs are the formation** (`solve.py run_pairs`). The scene is rebuilt exactly as A built it: the OSM
   scene, or for the unmapped tiers the perception scene, plus A's fairway-end virtual tees
   (`formation/data.add_virtual_tees`). Pairs are joined by (green id, tee id) and checked by location. **Parser
   check:** on every course checked locally, 100 % of the listed pairs joined by id with 0 unmatched. v1's
   `pair_offsets` also reads A's files without error, but it maps pairs by location onto the structure solver's
   hypotheses. That drops A's virtual tees: on arroyo_seco_ca osm_card it formed 9/18 against 17/18 with the v2
   join. The route CRF's formation term is `W * log P(pair)` over A's top 6 tees per green. The no-tee slack is
   already in A's marginals, so the per-green practice-green cost is set to 0, and the kept greens are the top N + 3
   (at most 19) by `p_paired`. With no card, the hole count comes from A's `expected_holes`.
2. **Reassigning low-confidence pairs.** The route CRF sums over each green's candidate tees, using A's log P plus
   walk and anchor terms, under the tee-exclusivity Lagrangian. So it can move a hole off A's MAP tee when the routing
   disagrees. W was chosen on dev only from {1, 3, 8} (`pick_w.json`; dev fully right 36 / 37 / 33). The pick was
   **W = 3**. Explicitly dropping low-`p_corridor` pairs was not added, because the slack already lets a green go
   unused.
3. **Gate v2** (`gate.py`):
   - Per-pair features: the min, sum of logs (log of the product) and count below 0.9 of the chosen pairs'
     `p_corridor`; the same for the route's own corridor posterior; the number of holes moved off A's MAP tee; the
     weakest used green's `p_paired`; and the strongest unused green's `p_paired`.
   - **Hard rule:** a course with no card is never certain unless every par has P >= 0.95.
   - L2 logistic regression. The feature set (full / small / tiny) and L2 were chosen by cross-fitted dev coverage at
     zero dev errors among courses the hard rule allows. The pick was `pairs_tiny`, L2 = 5.
   - Threshold: just above the highest cross-fitted score of a wrong dev course.
4. **Honest dev certainty** (`oof_pairs.py`). All 77 dev courses were in A's training set, so A's committed dev
   `p_corridor` values are in-sample: formed is 91-94 % there, against 82-87 % on test. The workflow refits A's
   two-stage model in A's six state folds and writes out-of-fold hole_pairs/1 for every dev course and tier. The gate
   was fitted only on those. Test courses use A's committed files.

## What did not work

- **Coverage at ≥ 99 % is near zero.** On dev, 37 of the 219 pooled rows are fully right. The highest-scoring wrong
  dev courses score above almost all of the right ones, so the zero-error threshold certifies 1 course
  (pezhekee_national_mn, osm_card). `p_corridor` features do not separate them. The main dev failure is still
  pairing: 42 of 60 failed osm_card courses, plus 12 missed tees. A course with 1-2 wrong pairs, each still at
  `p_corridor` 0.6-0.9, looks like a right one.
- **The no-card hard rule blocks nearly everything.** Only 0-1 courses per no-card tier have every par at
  P >= 0.95, because the length mixture is rarely that sure on an 18-hole course. No-card courses also fail on nine
  swaps and start holes (dev nocard: 7 of 74 failures). With today's evidence, a no-card course cannot honestly
  be certain.

## Next step

Make the gate's input separable rather than tuning the gate:

- (a) A's pair confidence must flag the 1-2 wrong pairs on a course. A needs a per-course "all pairs right"
  calibration, or a second-best-tee margin per hole.
- (b) Add independent per-hole evidence, such as workstream B's hole numbers, card yardage per tee set, or imagery
  checks on the tee-green line. With it, a 99 % gate needs only a handful of agreeing signals.
- (c) More dev courses. With 37 dev positives, a 99 % claim cannot be shown; Learn-then-Test needs about 300
  certified calibration courses.
