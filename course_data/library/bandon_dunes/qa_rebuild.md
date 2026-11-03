# Bandon Dunes (OR): card rebuild QA (2026-11-03)

**Verdict: NEEDS FIX (build failure, not content) → fixed, rebuild pushed.** The card was **not** applied. Run
41604633702's commit at 09:19Z for bandon_dunes only added a `last_attempt` block to `status.json`: "package job ended
without its course data". The page, package and the `status` / `reasons` ("scorecard not matched") are still the
06:00Z build (run 41583713847) from before `card_review.json` existed.

## Why

The package job (job 125813987583, 08:43-09:05Z) passed "Resolve, package, scorecard" (step 7), so
`card_review.json` was not the problem. The runner then died in step 10, "Vision layer + OB evidence". Its annotation
reads `System.IO.IOException: No space left on device` (runner _diag log). The Bandon outline is the whole
five-course resort, so the lidar and multi-year NAIP inputs are large. The 06:00Z run got through the same step, so
this is a disk-margin failure, not a deterministic one. `card_review.json` is a valid scorecard/1 file, and
`review_fixes.CARD_FILES` picks it up first, as it did for Sawgrass and Sand Hollow in the same run.

## Fix (pushed)

- `.github/workflows/course_page_one.yml`: a first step in the package job, "Free runner disk" (continue-on-error).
  It removes the unused .NET, Android, GHC and CodeQL toolchains (~20 GB) and logs `df` before and after.
- `course_page_bandon_dunes.json` rev 4, in `course_batch_qa_cards.json`.

## Page as it stands (06:00Z build, unchanged; the last pass's checks still hold)

`qa_page.js` phone + desktop: 18 holes, 0 problems. The routing is the Bandon Dunes course 1→18 (chains 32-169 yds),
and no Pacific, Old Mac or Trails hole is in it. The pars equal the card on all 18.

| hole | par (card) | page yds (map) | Tournament (card_review) | chain | pick | lie | note |
|---|---|---|---|---|---|---|---|
| 1 | 4 (4) | 404 | 398 | - | Driver 7.5 R | fairway 77%, sand 7%, OB 1% |  |
| 2 | 3 (3) | 215 | 220 | 118 | plays 222 |  |  |
| 3 | 5 (5) | 561 | 563 | 66 | Driver 5.5 R | fairway 87% |  |
| 4 | 4 (4) | 436 | 443 | 166 | Driver 8 R | fairway 47%, sand 3% |  |
| 5 | 4 (4) | 432 | 445 | 64 | Driver 10 L | fairway 74% |  |
| 6 | 3 (3) | 217 | 217 | 49 | plays 216 |  |  |
| 7 | 4 (4) | 380 | 411 | 167 | Driver 1 L | fairway 98% |  |
| 8 | 4 (4) | 387 | 385 | 88 | Driver 22.5 R | fairway 85%, sand 10% |  |
| 9 | 5 (5) | 593 | 585 | 169 | Driver 32 R | fairway 69%, sand 6% |  |
| 10 | 4 (4) | 335 | 380 | 62 | Driver 25.5 R | fairway 77%, sand 11% |  |
| 11 | 4 (4) | 463 | 452 | 110 | Driver 2.5 L | fairway 86%, sand 2% |  |
| 12 | 3 (3) | 238 | 238 | 84 | plays 232 |  |  |
| 13 | 5 (5) | 527 | 553 | 114 | Driver 3 L | fairway 94% |  |
| 14 | 4 (4) | 326 | 390 | 49 | Driver 49.5 R | fairway 63%, sand 15% | wide_aim: Driver aim +54 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 3 (3) | 176 | 206 | 64 | plays 172 |  |  |
| 16 | 4 (4) | 354 | 363 | 47 | Driver 40 R | fairway 64%, sand 15% |  |
| 17 | 4 (4) | 404 | 405 | 32 | 4-wood 8.5 L | fairway 93%, sand 2% |  |
| 18 | 5 (5) | 546 | 558 | 50 | Driver 5 R | fairway 76%, sand 5% |  |

## Check on the rebuild

Expect the card to be matched (no "scorecard not matched"), Black 6,732 chosen by name, card pars, and tee CHECKs
where OSM has no Black box (10, 15). If the package job fails on disk again, look at the new step's `df` lines.
