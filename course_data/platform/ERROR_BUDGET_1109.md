# Error budget 2026-11-09: leak-free baseline, joint tees, mowing line, ensemble decision (STOPPED EARLY)

Status: the work was stopped by the manager after about 30 minutes of machine time (one agent at a time). **Nothing
is adopted and no default pipeline behaviour changed.** The code is saved as a patch, not applied:
`course_data/platform/wip_1109/accuracy.patch` (`tees/localize.py`, `platform/package.py`, new
`product/mowing_line.py`); the evaluation scripts are in `wip_1109/accuracy_scripts/`. Every number below says
whether it was measured.

## 0. Leak-free baseline: PARTIAL (18 of 24 card courses scored)

Set-up: `rebuild_tees_trees.py` (S4n band stripped, commit 95e0c8e4e) -> `apply_native.py` (leave-one-course-out
side p, nested threshold and course gate from `mapper/eval_native_auto.json`; unseen courses the shipped model) ->
`error_budget.py`, every configuration, n 4000, seed 31. The run was killed with Spirit Hollow, Colbert Hills (v1)
and Sand Creek, Eagle Bend, Prairie Dunes, Buffalo Dunes, Mariah Hills (v2) not yet scored, so there is **no
headline, no cause ranking and no > 0.02 count yet**.

Measured auto matches (par-4/5 tee shots) on the courses that finished:

| course | match | | course | match |
|---|---|---|---|---|
| blue_hills | 12 / 14 | | tomahawk_hills | 9 / 12 |
| eagle_knoll | 14 / 14 | | la_nickell | 13 / 14 |
| gateway_national | 7 / 13 | | buffalo_ridge | 11 / 13 |
| hot_springs_arlington | 11 / 14 | | rivercut | 13 / 14 |
| pine_dunes | 13 / 14 | | gustin | 11 / 14 |
| veenker | 6 / 13 | | amana_colonies | 13 / 14 |
| coldwater | 11 / 14 | | osage_national | 11 / 14 |
| ellis | 9 / 14 | | annbriar | 9 / 14 |
| (national_kc 1 / 14: no card, not counted) | | | wakonda | 10 / 14 |

Sum of the 17 counted courses: 183 / 232 (78.9 %). Not comparable with 254 / 331 until the 7 missing courses
(6 of them the native courses, where the leak matters) are scored. Regret per course is in the result json that
was not written (the run writes it at the end); only the decision caches survive.

Held-out native gate, as applied (measured): fires on Gateway, Coldwater, Spirit Hollow, Sand Creek, Prairie
Dunes, Buffalo Dunes, Mariah Hills; shut on Annbriar (share 0.07) and Eagle Bend, as on 11-03.

## 1. Joint tee assignment: implemented, tee positions measured, plans NOT measured

In the patch (`tees/localize.py`):
* `localize_course(joint=...)`: one pad serves one hole. A pad two holes use goes to the hole whose chain cost
  rises most without it; the others are re-solved with the pad banned (holes whose lines start within 30 yds may
  share).
* `canopy_sampler` + a canopy cost: yds of the sight line 15-150 yds from a pad under lidar HAG >= 5 m
  (`vision_any/<slug>/raw/hag.tif`, uint8 in 0.25 m units), 0.3 per yd beyond 6, capped at 40 yds.

Measured, scored-set tees vs the truth tees, 23 courses, 361 holes (`accuracy_scripts/tee_var.py`,
`tee_var_result.json`; first version of the canopy cost, absolute, also charged to walk-backs):

| variant | tees > 10 yds off | mean error (capped 100) |
|---|---|---|
| today | 53 | 6.90 |
| pad exclusivity only | 54 | 6.81 |
| canopy cost only | 50 | 6.71 |
| both | 51 | 6.69 |

* **Gateway 2 Back (regression case): fixed by either term.** 720212696 (hole 18's pad, p 0.49) ->
  **719497753** (the truth pad), p 0.94 (exclusivity) / 0.97 (canopy); 54 -> 5 yds from the truth tee.
* Exclusivity: fixes Gateway 2, Osage 5 (70 -> 10 yds), Buffalo Dunes 11 (58 -> 42); breaks Veenker 3 (4 -> 26),
  Osage 9 (2 -> 51), La Nickell 1 (6 -> 29). Three for three: **as a hard rule it is neutral** (real shared
  complexes exist). Left in the patch, default off.
* Canopy: fixes Gateway 2, Hot Springs 9 (28 -> 4), Gustin 11 (15 -> 7), Gustin 14 (12 -> 2); breaks La Nickell 1
  (an OSM box in a tree chute lost to a walk-back) and Rivercut 7 (4.5 -> 7). The patch's last edit makes the cost
  relative to the hole's clearest own pad and removes it from walk-backs, to stop the La Nickell case. **That last
  version was not re-measured** (the re-run was killed; the one check printed was from the version before it).
* Not measured: plans (match / regret) with either term; runtime (expected well under 1 s per course: at most a
  few extra chain solves and ~135 raster samples per pad).

Recommendation when resumed: canopy term on, exclusivity off, after the re-measure and a budget run
(`--configs auto,+tees`).

## 2. Mowing line: implemented, edge geometry measured, NOT better than the 10-yd band so far

`product/mowing_line.py` in the patch (not wired into the build): 1-yd corridor grid per hole, an "unmown" score per
cell, a Viterbi line per side (distance beyond the package fairway per 5 yds along, cart-path prior), native from
the line outward on the sides `native_auto` fires. Three scores were tried
(`accuracy_scripts/mow_{extract,pix,self,eval}.py`), all held out (pixel model leave-one-course-out; the
self-calibrated scores have no fitted model):

Edge error = line minus the hand native's inner edge per 5-yd station, fired sides only. "Traced" = Gateway,
Coldwater, Spirit Hollow, Sand Creek (2,024 stations); the other three native courses' truth is the tracer's
"fairway + 10 yds" convention (`truth_sets_v2/*/trace.py native_beyond`), so it cannot judge an edge.

| inner edge | median abs error, traced | stations > 8 yds off | mean signed | native IoU, traced |
|---|---|---|---|---|
| fairway + 10 yds (today) | 6.7 | 41.9 % | -5.8 (starts too close) | 0.468 |
| LightGBM pixel model, LOCO (pixel AUC 0.66-0.90) | 9.2 | 56.4 % | +2.9 | 0.463 |
| self-calibrated per side (LDA near rough vs far, 2 EM rounds) | 7.1 | 44.9 % | -0.2 | 0.470 |
| self-calibrated per course | 8.5 | 52.7 % | +4.2 | 0.380 |
| per side + per course, 50 / 50 | 6.9 | 43.6 % | +1.2 | 0.456 |

* The per-side line removes the bias and halves the false native area (Spirit Hollow 70k -> 37k cells, Gateway
  56k -> 34k) but misses more true native (Gateway 8k -> 20k). By side it is a trade: it fixes sides where the
  band started on mown rough (Spirit Hollow 4 L, 5 L, 6 L / R, 8 L, 18 R: -8..-17 -> within 1-6 yds; Gateway 3 L,
  6 R, 15 L, 16 R) and breaks sides where the hand native starts at the fairway edge (Gateway 3 R, 5 R, 8 L, 9 L,
  Spirit Hollow 14 R: +10..+30).
* Why it breaks (looked at Gateway 8, 9, 11 and Spirit Hollow 17 renders): the score calls the first 1-6 yds off
  the fairway "mown". On Gateway 8 the hand map (corrected in today's review) has native from the fairway edge:
  a tan ring ~18 yds wide, then dense green. The line goes to the tan / green boundary. From the image I could not
  tell whether that ring is thin fescue or unirrigated mown rough; the truth says native. On Gateway 11 and Spirit
  Hollow 17 the line follows the hand edge / the cart path closely and the 10-yd band is visibly wrong.
* The Spirit Hollow false-positive sides (10 R, 13 L / R, 5 R) are not separated by the near / far contrast
  (0.7-4.0 against 0.9-10 on true sides): no veto found.
* **Not measured: plans.** No budget run was made on mowing-line packages, so adopt / reject is open. The geometry
  alone does not justify adopting it.
* Runtime, measured roughly: grid + features + line ~1 s per hole side pair on one core, i.e. ~15-20 s per course
  as written (shapely point tests dominate); not optimised.

## 3. Decision under map uncertainty: NOT STARTED (design only)

Plan: minimising expected regret = maximising the ensemble-mean EV per (club, aim); members one factor at a time
(edges -5 / +5 yds, each uncertain native side flipped with its probability, the alternative tee pad), about 6
decisions per hole. At ~4 s per quick decision (n 4000) that is ~7 CPU-minutes per course: too slow for the
runtime goal as designed. The cheap version to try first: simulate the shots once per club / aim and re-read only
the lies on each member map (same landing points; tee alternatives need their own shots).

## Resume

Scratch (may not survive): `/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/acc`
holds the clean auto packages (`rbc_v*`, `an_v*`), decision caches (`cache_v*.json`), corridor grids (`mow/`).
From the repo root, `A` = a scratch dir, `W=course_data/platform/wip_1109/accuracy_scripts`:

```
git apply course_data/platform/wip_1109/accuracy.patch          # only to work on steps 1-2
# step 0 (run this on the UNPATCHED tree, or with localize.PARAMS canopy_w=0, joint=False)
for v in v1 v2; do python3 course_data/platform/rebuild_tees_trees.py --set $v --out $A/rbc_$v; done
for v in v1 v2; do python3 $W/apply_native.py $PWD $A/rbc_$v $A/an_$v $v; done
for v in v1 v2; do python3 course_data/platform/error_budget.py --set $v --n 4000 --workers 2 \
    --auto-dir $A/an_$v --out $A/eb0_$v.json --cache $A/cache_$v.json; done        # ~40 min on 4 cores
python3 course_data/platform/budget_causes.py $A/eb0_v1.json $A/eb0_v2.json --out $A/causes0.json
# step 1
python3 $W/tee_var.py $A/tee_var.json          # tee error per variant (edit VARS at the top)
# step 2 (scripts expect to run from $A, with the patch applied)
python3 $W/mow_extract.py $A/an_v1 $A/an_v2 $A/mow
python3 $W/mow_pix.py $A/mow $A/mow_pix.pkl
python3 $W/mow_eval.py $A/mow $A/mow_pix.pkl $A/an_v1 $A/an_v2 $A/ml1 '{"score":"self"}'   # writes $A/ml1_v*/
python3 course_data/platform/error_budget.py --set v1 --courses gateway_national,coldwater,spirit_hollow \
    --auto-dir $A/ml1_v1 --configs auto --out $A/ebml_v1.json --cache $A/cache_v1.json
```

Paths inside the scripts point at this session's scratch dir; change `S=` / `WT` at the top when resuming.
Tests: none were added or run for the patch (the tree is as it was at db5330732 plus this folder).
