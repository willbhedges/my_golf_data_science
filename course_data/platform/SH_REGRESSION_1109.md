# Spirit Hollow scoreboard regression (11 -> 8 / 16 same club, full mode), 2026-11-09

The qa-scoreboard guard (`course_data/qa/scoreboard.py --check --full`, `.github/workflows/scoreboard.yml`) has
failed since 2026-11-04 02:26 with "Spirit Hollow: same club (full) 8/16 vs 11/16 on 2026-11-03 08:05 (7fb8612d)".

**Bottom line.** All of the drop comes from one adopted, held-out-validated package stage: **S4n automatic native
sides** (`product/native_auto.py`, commit 8bf54d7b7, first in the SH package at rebuild 15893e174, 11-03 21:41).
SH went from no long grass at all in the landing corridors to 28 `auto:native_side` zones. On the hand-map truth,
the SH product's **total regret did not change**: 0.3144 -> 0.3142 strokes over 16 tee shots (mean 0.0197 ->
0.0196). The count fell because the change swaps holes. It loses 4 Driver near-ties (truth margins 0.014-0.047)
and gains 8 (Driver -> 4-wood, the correct club). It also lowers the regret on 6 and 18. Per-hole verdicts are
below: 2 of the 4 losses are real map errors from the native classifier (false-positive or too-close bands). The
other 2 had the old answer right by luck, because the old map had no long grass at all. No SH-specific fix exists
that would not tune a held-out-validated classifier on its own training course. So the guard is re-baselined with
this reason (`course_data/requests/qa_scoreboard.json`, id `2026-11-09-native-auto-s4n`), and the two residual map
errors are recorded as known S4n limitations.

## 1. Reproduction (the cheapest faithful one)

The guard metric is `summary.same_full`: `product/decide.run(mode="full", S=64, N=3000)` on the committed
`course_data/packages/spirit_hollow/package.json`. It runs per tee set (Black, plus Gold for 2B / 9B) and is
scored against `spirit_hollow/output/final_decision.json`. Nothing else feeds it: the other workflow steps
(contracts, golden, acceptance) are `continue-on-error`. Since 7fb8612d, nothing changed in `decide.py`,
`product/package.py`, `final_decision.json`, `spirit_hollow/course.py` or `hand_zones_ll.json` (git log). The SH
package last changed at d06e6acee (11-04 02:11). **So the whole regression is a package diff, 8681f8a47
(scored at 7fb8612d) -> d06e6acee, and bisecting code commits is not needed.** The faithful reproduction is
scoreboard.py's own `product_plan(..., mode="full")` + `agree()` on a given package file. That script is
`course_data/platform/sh_regression_1109/run_full.py`: a copy of the scoreboard's SH full branch. It takes about 28 min on 4 cores.

| package | same club (full) | total regret | holes not same |
|---|---|---|---|
| committed HEAD (= d06e6acee), local run | **8 / 16** (exactly the CI number) | 0.3142 | 1, 4, 6, 9B, 10, 13, 17, 18 |
| HEAD minus the 28 `auto:native_side` zones, local run | **11 / 16** (the old number back) | 0.3144 | 1, 6, 8, 9B, 18 |
| 8681f8a47 (CI at 7fb8612d) | 11 / 16 | 0.3144 | 1, 6, 8, 9B, 18 |

## 2. Bisect (package rebuilds between the two scoreboard runs)

Zone counts in the SH package by rebuild (`git show <rev>:course_data/packages/spirit_hollow/package.json`):

| rebuild | built | change in SH |
|---|---|---|
| 8681f8a47 | 11-03 04:12 | baseline (scored 11/16) |
| d3fb639c6, 6d69657f6, 4c14b2b07, c659df16b | 11-03 06:56-16:24 | zones identical |
| **15893e174** | 11-03 21:38 | **+28 native zones, src `auto:native_side` (S4n)**: sides 2 L, 4 both, 5 both, 6 both, 8 both, 10 R, 13 both, 14 R, 16 L, 17 both, 18 both |
| d06e6acee | 11-04 02:09 | tree edge rule +1 m / water filter: sand 95 -> 93, recovery 236 -> 235; hole 11 / 15 tee and green changes (tee merge) |

Holes 4, 10, 13 and 17 differ between 8681f8a47 and d06e6acee **only** in the native zones and their provenance
fields. Holes 11 and 15 changed tees, but 11 is still "same" and 15 is a par 3. The tree / water / tee-merge /
fairway-fill / aim changes cost nothing on SH. The product's long-grass IoU in the scoreboard's corridor goes from
0 to 0.66 (4), 0.31 (8), 0.17 (17), 0.19 (14), 0.25 (16), and so on. The map moved toward the hand map.

## 3. Per hole (renders: NAIP 2023 0.6 m, hand map vs package, looked at for every hole below)

Renders, scripts and the two full-mode result files are in `course_data/platform/sh_regression_1109/`:
`zoom_<hole>_2023.jpg` (hand left, package right; dashed magenta = `auto:native_side`, rings 225-325 yds from
the hand tee), `hole_8.jpg`, `full_head.json` / `full_nonative.json`, `run_full.py` (the full metric on any
package file), `variants.py` / `sides.py` (the quick diagnostics), `render.py` / `zoom.py`.

Quick-mode diagnostics (n 8000, the scoreboard's quick decision, Black) on HEAD with the auto native kept,
removed, replaced by the hand map's native polygons, or with one side dropped. Quick and full picked the same
club on all of these holes at HEAD.

| hole | truth (margin) | HEAD | no native | hand native in place of auto | drop auto L | drop auto R | verdict |
|---|---|---|---|---|---|---|---|
| 4 | Driver (0.047) | 4-wood | Driver | **4-wood** | Driver | Driver | **old answer lucky** |
| 10 | Driver (0.030) | 4-wood (0.065) | 4-wood (0.002) | 4-wood (0.013) | 4-wood | 4-wood (0.002) | **real, small: auto R is a false positive** |
| 13 | Driver (0.014) | 4-wood | Driver | Driver | **Driver** | 4-wood | **real: auto L is a false positive** |
| 17 | Driver (0.015) | 4-wood | Driver | Driver | 4-wood | **Driver** | **real: auto R band starts inside mown rough** |
| 8 | 4-wood (0.046) | 4-wood | 4-wood (0.004) | 4-wood | | | **fixed by S4n** (full mode: Driver -> 4-wood) |
| 6 | 2-wood, tie (0.010) | 4-wood | Driver | 4-wood | | | improved (regret 0.017 -> 0.0095) |
| 18 | 2-wood (0.026) | 4-wood | Driver | Driver | | | improved (regret 0.062 -> 0.026) |

- **4**: lucky before. The hand map has native on both sides, tight to a fairway about 37 yds wide. The auto
  bands are on the same two sides (both p > 0.85, IoU 0.66), and the imagery shows tan unmown grass beyond the cart
  path on the left and toward the houses on the right. With the hand map's own native polygons in the product
  package, the product still picks 4-wood. So the Driver / 4-wood gap against the truth comes from the other layers
  (tee 10.9 yds off, fairway shape). The old Driver came from a map with no long grass at all.
- **10**: real, but a coin flip. The auto R band (p 0.747, thr 0.675) covers striped, mown parkland around the
  pond, the cart path and the neighbouring fairway's rough. The hand map's only native is a thin creek strip on the
  left. Without the band the hole is a 0.002 tie (quick: 4-wood), and in full mode the old map said Driver.
- **13**: real. The hand map has no native in the corridor, and the imagery shows mown rough between the fairway
  and the pond (left) and up to the tree line (right). Both sides fire just above the threshold (0.722 / 0.723). The
  left band, on the mown strip next to the pond, flips the club.
- **17**: real (geometry). The right side does have native (the hand map has it), but beyond the cart path. The
  package's OSM fairway is narrower than the mown, striped area, so the band (10 yds beyond the package fairway)
  starts on mown rough. The left band (p 0.947) fills the open, tan gaps between the tree polygons, where the hand
  map has recovery. That is penal either way and does not flip the club: dropping L keeps 4-wood, dropping R gives
  Driver.

## 4. Why no code fix

- S4n was adopted on held-out evidence over 18 truth courses (mapper/EVAL_native_auto.md: 167 -> 186 matches /
  250, regret 8.79 -> 4.34). Spirit Hollow is in that evaluation as a control, with its classifier errors already
  measured: sides 11 TP / 4 FP / 7 FN; plan 7 -> 7 matches, regret 0.892 -> 0.886. It lists 4, 13 and 17 by name.
  What is new here is only that the SH scoreboard's Bayesian truth counts the swap as 3 lost holes.
- The flipping sides are the course's low-p positives (0.72-0.75 against thr 0.675). Raising the threshold or the
  band's inner edge (MIN_BEYOND 10 yds, the truth sets' own `native_beyond` convention) until SH's 13 L, 10 R and
  17 R go away would be tuning a held-out-chosen rule on one of its training courses. It would cost sides that are
  right elsewhere: SH 5 R, 8 R and 18 L/R sit at 0.68-0.75 too, and 8 / 18 are improvements.
- 17 R really needs a better fairway edge (the OSM fairway stops short of the mowing line). That is the fairway
  layer's job (S4f fairway fill, platform/fairway_edge.py), not something to bolt onto the native band.
- Since no generalization code changed, the held-out error budget is unchanged: **254 / 331, regret 4.738
  (0.200 / round)** (ERROR_BUDGET.md "Leave-one-course-out over all 11 rules"). No before / after run was needed.

## 5. What changed

- `course_data/requests/qa_scoreboard.json`: rev 8, `rebaseline` id `2026-11-09-native-auto-s4n` with the reason
  below. The next full CI run records it on its history rows (`baseline_reset`) and skips the drop check once. The
  push touches the request file, so it triggers that run. Later runs compare against the new 8/16 baseline, so a
  further drop of more than 1 hole fails again.
- This note. No generalization code changed.

Reason recorded: "SH 11 -> 8/16 full: S4n automatic native sides (native_auto, rebuild 15893e174) put long grass on
SH. Total regret unchanged (0.3144 -> 0.3142). Lost 4 (old Driver lucky: no long grass in the old map), 10, 13, 17
(auto-native false-positive / too-close bands, known S4n FPs on SH). Gained 8; 6 and 18 regret lower. See
course_data/platform/SH_REGRESSION_1109.md".

## 6. Follow-ups (not done here)

- Native band inner edge from the measured mowing line (NAIP texture / stripe edge) instead of the package
  fairway + 10 yds. It would fix 17 R, and possibly some of the other "BROKEN" holes (Ellis 2, Sand Creek 8) (EVAL_native_auto "BROKEN"). It must
  be measured held-out with `mapper/eval_native_auto.py` + `platform/error_budget.py`.
- An SH-like "mown parkland next to water" false-positive pattern (10 R, 13 L): look at the per-side features of
  those FP sides across the 18 courses before adding any veto.

Tests: `course_data/qa/test_scoreboard.py` (8 passed), `course_data/product/test_native_confirm.py` (16 passed).
