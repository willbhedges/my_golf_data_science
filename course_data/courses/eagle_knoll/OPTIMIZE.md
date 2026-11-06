# Eagle Knoll: optimisation and verification of the choices (Nov 3-4 2026)

For Will (KU club golf), NCCGA Central Regional 2, Eagle Knoll GC (Hartsburg MO), Sat-Sun Nov 7-8 2026, Back (blue)
tees. Page: https://claude.ai/artifact/QQkFta99SEstd6Dv8wzgf8 (built from `wind_page/index.html`). The independent
audit (`AUDIT.md`, ec6084ac8) was worked in; section 9 lists each audit item as accepted / rejected with the evidence.

Everything here was measured in a sparse-but-scoring-complete worktree (elevation, library, vision_any/s2,
spirit_hollow, mozingo, product, packages/eagle_knoll present) and on GitHub Actions. Scripts used are named per
section; the local ones live in `opt/` or are described exactly enough to repeat.

## 0. Summary for Will (Back tees)

> **Nov 6 update (section 12): read it first. It supersedes this summary on Back 9 (aim -14 becomes -2: a
> phantom tree polygon removed) and Back / Eagle 14 (4-wood at the green, not Mid iron: the green had no putting
> cost). Back 1 (Long iron) is confirmed on the real lidar crown heights.**

* **Changed picks (calm-day book, Back):**
  * **1: Long iron +6.5** (was Driver 30 L over the corner), by 0.029 +/- 0.005. A close call: the page badges it,
    Driver is better in 39 % of what-if golfers, Driver comes back with any helping wind (Sunday's N wind is behind
    you on 1), and it is a tie if the trees are lower (14 m) or thinner. If you hit Driver, the corner trees are the
    risk.
  * **14: Mid iron +8, a TIE with the new 8-iron** (+0.006). From the 246 box (the 2024 setup) the 8-iron is the play
    (aim +4.5, by 0.10).
  * Aims moved: 4 -10 -> -4, 9 -7.5 -> -14, 8 +12.5 -> +13. Every other Back pick is unchanged and resolved
    (z = 16-65 standard errors).
* **Marginal holes** (where the pick flips under +/-5 yds carry, +/-10 % spread, +/-5 mph wind or soft turf): Back 1
  (helping wind, carry +5), Back 14 (carry +5, a tighter pattern, helping wind). Middle 5, 10 and 11 are ties. Back 15
  is a tie with the 2-wood into a 10 mph wind. Everything else holds.
* **Par 3s:** "Play it like" now includes the temperature (+2 yds at ~50 F). **Superseded on Nov 6 (section 13):** the
  page's box is now the expected-strokes aim for any pin on Will's engine iron pattern, and "Play it like" is the carry
  to that aim. That puts 2 at 1.5 yds short of centre, 6 at 1 short, 12 at 4 short and 16 at 1.5 short (the old box was
  2 long). The earlier "8-10 yds short" on 2 and 12 came from a deeper, mishit-free pattern; it does not survive
  Will's own pattern.
* **On the day:** check each tee plaque against the page and use Move this tee (5-yd steps). The NCCGA moved 10 of 18
  boxes in 2024 (5 at 420, 14 at 246).

## 1. The landing oval ("fix the ovals")

The tournament template drew `spirit_hollow/v2/build_page_v2.cloud`: covariance eigen axes plus a symmetric half of
the 2.5-97.5 % range. Mishits and balls that stop in rough or trees all finish short, so the depth variance nearly
equals the lateral one. The axes then turn (up to 73 degrees off the lateral on hole 1), and the long side is drawn as
deep as the short side. Since 09bd942a9, `v2_course.build_page` swaps in `course_data/library/landing_pattern.page_cloud`,
which is the same simulated finishes measured in the tee-line frame. It gives lateral L / R and depth short / long of
the median after a linear tilt, and leaves out the 2.5 % heavy mishits, as the library pages and the app do since 56530e7ff.
The template itself draws that shape. The library PAGE_PATCHES entry that added the same branch is removed, because
it would otherwise appear twice. Test: `course_data/courses/test_v2_course_landing.py`.

Eagle Knoll calm picks, 50 F, drawn half-extents in yds (lateral L / R, depth short / long). Old = what the page
drew. New = what it draws now, which is the model's own 95 % finish extents:

| hole | club | old drawn (L / R, short / long) | old depth / width | new = model 95 % (L / R, short / long, tilt) | new depth / width |
|---|---|---|---|---|---|
| 1 | Driver | 35 / 35, 33 / 33 (major axis 73 deg off lateral) | 0.93 | 33 / 37, 30 / 28, +0.03 | 0.83 |
| 5 | Driver | 35 / 35, 37 / 37 | 1.06 | 37 / 34, 35 / 26, -0.05 | 0.86 |
| 9 | Driver | 33 / 33, 33 / 33 (35 deg off) | 0.99 | 36 / 36, 30 / 26, +0.16 | 0.79 |
| 14 | Mid iron | 18 / 18, 18 / 18 | 1.01 | 19 / 18, 15 / 11, -0.04 | 0.69 |
| 18 | Driver | 36 / 36, 27 / 27 | 0.75 | 36 / 35, 27 / 21, -0.03 | 0.68 |

Pages rebuilt with it: Eagle Knoll (the nccga-v2 run below), and Gateway National, Pine Dunes and Hot Springs
Arlington (ed93f2365; built locally, same grids, decisions and photos, page QA 18/18 holes with no problems).
Spirit Hollow's live page is built by its own code and template, which are untouched; a test checks this.

## 2. Monte Carlo precision

**Calm-day book (decide.py, prior-averaged).** Before: 128 prior draws, plus 512 on the close calls, each draw with
3,000 own swings. The SE of the paired margin (pick vs runner) across draws is 0.0012-0.011. Every Back, Eagle and
Middle pick was more than 2 SE ahead (z = 6.7-46) except Middle 10 (z = 2.1, already a TIE at 0.004). Unresolved
before (|margin| < 2 SE): **0 of 42 strictly, 1 borderline (Middle 10)**. The page already labels Middle 5 and 10 as TIE.
The rerun uses 256 draws on every hole (after: section 2b).

**Wind grids (what the page plays in any wind).** This was the real problem. One central world with N = 2,500 common
swings for the whole +/-75-yd aim curve. Paired per-swing SE of runner - best at the stored aims
(`opt/grid_se.py`, 50 F, Back 0-15 mph, Eagle / Middle 0 and 10 mph):

| base | cells | median SE | within 2 SE (unresolved) | labelled TIE (< 0.01) | pick differs on 16,000 fresh swings |
|---|---|---|---|---|---|
| Back | 518 | 0.0033 | 33 | 34 | 7 (holes 15 x3, 18 x3, 17) |
| Eagle | 182 | 0.0032 | 7 | 7 | 4 (10 x2, 15 x2) |
| Middle | 182 | 0.0048 | 13 | 10 | 0 |

Example: hole 15 at 10 mph from straight ahead. The grid had 2-wood over 4-wood by 0.0066 (SE 0.0037); 16,000 fresh
swings give 4-wood by 0.0013, and a second seed gives 4-wood by 0.0009. The coarse grid flipped 3 of 13 cells of that
hole in 10 mph.

Fix: `v2_course.refined_solver`. Stage 1 is the original solve. Stage 2 re-evaluates every club on aim +/-10 yds
(0.5-yd steps) with 16,000 fresh common swings, shared by every club, cell, temperature and hole, and takes aim, EV and
pick from that. The aim window keeps the coarse edge where the fine range cuts it. Checked on hole 15, 10 mph: the
pick is identical on two refine seeds in 13 / 13 cells, and margins agree within 0.003. Run on Actions for the card-tee
grids of all three bases (request `refine_swings` 16000); the moved-tee offsets stay coarse.

### 2b. After the rerun

Rerun (GitHub Actions run 41681285865, bb98ecdaa, Nov 3 17:08-23:10Z; Back rev 6, Eagle rev 3, Middle rev 3): new
engine options, 256 prior draws per hole, card-tee wind grids refined on 16,000 swings, every Back offset
recomputed (coarse 2,500).

* **Calm-day book after:** z = margin / SE is 6.1-65 everywhere, except Back / Eagle 14 (z 2.1, margin 0.006: TIE),
  Middle 10 (3.2, 0.0085: TIE), Middle 11 (5.4, 0.0087: TIE) and **Middle 5 (z 0.4, margin 0.001: a true tie, TIE on
  the page)**. Unresolved (< 2 SE): **1 of 42 (Middle 5), labelled TIE** (before: 0 strictly, 1 borderline). More
  draws would not separate Middle 5: the two clubs are equal within the model.
* **Wind grids after** (50 F, 0 and 10 mph, 182 cells per base, same check as before: SE on the grid's own swings,
  then 16,000 fresh swings):

| base | median SE before -> after | unresolved (< 2 SE) before -> after | of them not labelled TIE | pick differs on fresh swings before -> after (all of them now TIE-labelled) |
|---|---|---|---|---|
| Back | 0.0033 -> 0.0012 | 13 -> 1 | 0 -> 0 | 6 -> 1 |
| Eagle | 0.0031 -> 0.0012 | 7 -> 3 | 0 -> 0 | 4 -> 2 |
| Middle | 0.0048 -> 0.0015 | 13 -> 6 | 3 -> 0 | 0 -> 2 |

Every remaining unresolved cell is shown as a tie (margin < 0.01). On the 0-15 mph Back set before, 33 of 518 cells
were unresolved and 7 picks changed with fresh swings.

**Picks that changed (calm-day book, old run -> new run):**

| set | hole | old | new | why |
|---|---|---|---|---|
| Back | 1 | Driver -30.5 (0.044 over Long iron) | **Long iron +6.5** (0.029, z 6.1, p 0.61, close call) | flight-path trees at the corner |
| Back | 14 | Mid iron +9.5 (0.059 over 4-wood) | Mid iron +8, **TIE with 8-iron** | the 8-iron added |
| Back | 4 / 9 / 8 | aim -10 / -7.5 / +12.5 | -4 / -14 / +13 | flight trees on the left (4); more draws |
| Eagle | 14 | Mid iron (0.059) | Mid iron, TIE with 8-iron | 8-iron |
| Eagle | 9 / 4 | aim -13.5 / +0.5 | -14.5 / +2 | more draws, flight trees |
| Middle | 5 | Driver +20 (TIE 0.006) | **4-wood +9.5 (TIE 0.001)** | flight trees on the right corner; a coin flip |
| Middle | 14 | Mid iron +18 (0.188 over 4-wood) | **8-iron +4.5** (0.104 over Mid iron) | 8-iron (audit item 2) |
| Middle | 11 | Driver +8 (0.042) | Driver +1, **TIE** with 4-wood (0.009) | most likely the flight-path trees right (not separated: the engine-off A/B was stopped before 11) |
| Middle | 4 | aim -25.5 | -22.5 | |

All other picks (Back 3, 5, 7, 10, 11, 13, 15, 17, 18; Eagle 1, 3, 5, 7, 8, 10, 11, 13, 15, 17, 18; Middle 1, 3, 7,
8, 9, 10, 13, 15, 17, 18) keep their club; aims moved by 1.5 yds or less.

## 3. Player model

* Will's numbers are in the engine: Driver 275 / 300, 2-wood 265 / 280, 4-wood 255 / 270 carry / total at 70 F
  (`spirit_hollow/v2/model.CLUBS`; config sub-title, PROJECT.md, spirit_hollow/README). His stated 95 % widths are
  65 / 60 / 50. The engine centres on 70 / 64.6 / 53.8 (x 70/65, on-course vs stated), with the prior width
  lognormal (median 70, 90 % 62-80) and his ratios 65:60:50 as the per-club ratios. Long iron 210 / 220 / 40 and
  Mid iron 185 / 192 / 34 are the Mozingo / Spirit Hollow book numbers. Depth window 28 / 26 / 24 x 1.25. Mishits:
  12 % slight (92-95 % carry), 2.5 % heavy.
* **There is no measured data from Will in the repo.** `course_data/personal/` holds only synthetic examples and
  the fitting code; `golf_data.csv` is 14 round scores. The page and the app say "Driver 70" and nothing claims a
  fitted profile. Nothing stale was found: the hole-temperature default was fixed on Oct 24 (`activate`), the page
  numbers and the decide use the same table, and the prior width ratios are his.
* **Added: 8-iron 162 / 167, width 30, depth 16** (config `engine.extra_clubs`). These are Will's 210 long iron plus
  the ~12-yd gapping the Spirit Hollow approach book uses; the width is the mid iron's 34 x 162 / 185. **This is an
  assumption: confirm the 8-iron carry with Will.** It matters on hole 14 from the 246 box (section 7).
* The page cannot fit his pattern. If his driver 95 % spread is above ~79 yds, Back 1's book flips. Back 18 flips
  above 76.5 (old run). The new run's width sweeps are in the page notes.

## 4. Course truth

* **Tee set:** Back (blue). The NCCGA Blue sheets cached in `course_data/research/web/eagle_knoll/` show Fall 2015
  6,682 and Fall 2024 6,512 (as set up that day). The Nov 7-8 sheet is not posted, and nccga.org could not be reached
  from this sandbox (DNS blocked).
* **Yardages:** the Back card matches the 2015 sheet on 17 holes; hole 10 is 420 there vs 405 here. The mapped Back 10
  tee measures 405, and Eagle 10 is 420, so 2015 probably used the back box. The 2024 setup moved boxes on 10 holes,
  for example 5 at 420 (card 465) and 14 at 246 (the Middle box). The footer now says this. "Move this tee" now moves
  in 5-yd steps (-60..+60), and the solve snaps to the computed tees every 20 yds. Every Back, Eagle and Middle tee is
  within 5.4 yds of its card on a mapped pad (truth `tee_how`, the third pass). Recomputing tee-to-green along the
  hole line agrees within 7 yds, except where the method itself fails (hole 13, a line point behind the tee).
* **Hazards:** the hand map has had three passes, the third on NAIP 2020 with CIR and the 2015 lidar edge, which
  added the grown-in woods on 5 left and 9 right. I spot-checked the landing renders for 9 and 15 and the par-3 renders
  for 6 against the zones, and found nothing to correct. From the zones I measured the par-3 surrounds 3-15 yds off
  each edge: 2 has water 12+ yds left behind the trees; 6 has water at 6-9 yds left and 12+ right; 16 has water from
  3 yds right and short. The "edge hazard" summary only samples 3-9 yds, so the par-3 EV check (section 6) uses the
  zones themselves. **Not re-verified by me:** the OB line on 18 (+/- 8 yds, no stakes visible), the creek width on 17
  (F4: vision water may be ~2x wide where it runs under the canopy), and anything newer than NAIP 2022 or the 2015 lidar.
* **Elevation:** from the 3DEP 1 m DEM. Tees are at 713-850 ft. Landing drops for the driver range from 1: +61 ft to
  7: -30 ft. Roll factor x1.30 is the DEM **slope** cap (downhill landing on 1, 5, 10, 13 and 15), not a firm-turf
  setting. Soft November turf is covered by the roll x0.8 sensitivity (section 8).

## 5. Conditions

* Temperature grid 35 / 50 / 65 F against the Oct 31 forecast: Sat 44-58 F, about 49 F at 9:00 rising to ~57 F by 18;
  Sun 46-61 F. Early-November normals for Columbia are lows ~37 and highs ~58. The forecast lies inside the grid, and
  EV is interpolated linearly between grid temperatures. Carry is linear in temperature (0.075 %/F, about 2 yds per
  10 F for the driver), so interpolation between grid points 15 F apart is fine. The calm-day decide uses each hole's
  forecast temperature (the 9:00 tee time on day 1).
* **Fixed: par-3 plays-like had no temperature term.** The tee shots had one. The page now multiplies by
  1 / (1 - k (70 - T)), which adds about 2 yds at 50 F on a 135-yd shot, shown as its own chip. Test:
  `test_v2_course_engine.py::test_par3_plays_like_includes_temperature`.
* **Altitude:** ~800 ft, versus Lawrence ~900 ft; the difference is under 0.5 % of carry. No adjustment.
* **Wind:** the 10 m forecast is interpolated per hole time (14 min a hole), as a vector between hours, through the
  grid's 0-25 mph x 12 directions. Sunday's ~9-13 mph N wind is the one that matters (section 8). The forecast is
  7-8 days old. The Nov 5 14:00Z refresh re-fetches it and rebuilds the page. Decisions are not re-run then: a
  temperature change of a few degrees moves carry by under 1 yd.

## 6. Approach and par-3 targets

* The page's par-3 target is the DECADE box (`yardage_book.par3_plan`: cushions ~distance/20, +3 water, +2 trees,
  +1 bunker). It uses green shape and the worse side, but not Will's dispersion.
* `opt/par3_ev.py` scores every aim on a 1-yd grid. It uses his iron pattern (5-hcp: lateral sigma 9.4 yds at 150,
  depth 1.5x), 16 pins anywhere 4 yds inside the edge, Broadie putting / short game +5-hcp offsets, and the hand-map
  zones. Strokes for the par 3, Back:

| hole | DECADE box aim (lat, depth) | EV at box | EV at centre | best aim | EV best | sens: depth 1.25x | sens: trees half cost |
|---|---|---|---|---|---|---|---|
| 2 (150) | -0.1, -1.5 | 3.60 | 3.65 | -1, -9 | 3.53 | best -1, -8 (-0.08) | 0, -9 (-0.05) |
| 6 (138) | +1.1, +0.5 | 3.53 | 3.53 | +1, -1 | 3.52 | -1, -4 (-0.03) | -1, -3 (-0.01) |
| 12 (180) | -2.2, -0.4 | 3.60 | 3.58 | +2, -10 | 3.49 | +2, -10 (-0.11) | +2, -11 (-0.08) |
| 16 (158) | +0.4, +2.0 | 3.80 | 3.79 | +1, -3 | 3.77 | (-0.03) | -1, 0 (-0.01) |

  (depth + = long of centre; the 1.25x / half-cost columns give the best aim and its gain over the box.)
* (Nov 6: superseded by section 13; the short side holds, the size does not.) Accepted on 2 and 12: the front of the green is the better miss. Long is trees on both, and open grass or fairway
  is short. The gain is 0.05-0.11 strokes under every setting tried. The hole notes now say "aim about 8-9 (2) / 10 (12)
  yds short of the green centre". The drawn box is unchanged, so Will has both.
* 6 and 16: the box is within 0.01-0.03 of the best aim. No change.
* **Audit item 6 (16: box 159-159):** the DECADE cushions do not fit there, so the worse side (water short) keeps its
  full cushion and the box collapses to a line. That is a display artefact. The box is now drawn at least 4 yds each
  way, centred on the DECADE target. The audit suggested aiming 2 yds long; the EV check says that costs ~0.03 because
  trees are long, so it was not done.
* **Approach shots on par 4 / 5 (the "Eagle Knoll approach targets" item):** MANAGER_TODO has no separate entry
  beyond "approach targets". The tournament page has no second-shot planner (Spirit Hollow's
  `spirit_hollow/approach/` is not wired to v2_course). **Not done.** The tee-shot EV already prices the next shot
  from where the ball finishes.

## 7. Engine changes (bugs and gaps found)

1. **Trees in the flight path (audit item 1).** The engine scored trees only where the ball finished, so a drive over
   a corner of woods was free. `v2_course.flight_tree_ev_curve` (config `engine.flight_trees`) checks the descent,
   from 60 % of the carry on, along the tee-to-landing line. The ball's clearance is the trajectory height (apex 32 yds
   for woods / 30 for irons at 60 % of carry, landing angle 38 / 46 deg) plus the DEM drop of the ground below the
   tee, minus that fraction of the landing drop. Where that is under 20 yds over a tree cell, 70 % of balls stop there
   and are punched out from there. Only cells 140+ yds out are checked; the woods round the tee chutes are not traced
   to the yard (hole 5's chute is 5 yds wide on the map). Ravines are cleared through the DEM: hole 3 is unchanged.
   Effects (central world, two-stage solve, `opt/solve2.py`):
   * **Back 1:** Driver -30 (0.038 over Long iron) becomes **Long iron +7, 0.031 +/- 0.003 over Driver**. Tree height
     14 m: Long iron by 0.004 (a tie). 24 m: by 0.089. 40 % stop: by 0.003. So Long iron is at least as good under
     every assumption, and the page should show it as a close call where it is close.
   * Back 4 aim -10.5 becomes -4; Back 9 aim -8.5 becomes -11. Other holes change by under 0.01.
   * **Middle 1:** Driver stays (0.092 over Long iron), because from 20 yds ahead the line clears the corner.
     Audit item 1 is rejected for Middle on that evidence.
2. **No club under the 185-carry mid iron (audit item 2).** Added the 8-iron. Middle 14 (246, the 2024 NCCGA box)
   now plays **8-iron aim +4, 0.095 over Mid iron**; before it was Mid iron aim +18 into the rough between pond and
   woods. Back 14 (265) stays Mid iron (0.016 over 4-wood), but the 8-iron is the pick at carry +5. From the 246 box,
   use Middle on the page, or Move this tee -20 on 14.
3. **Wind-grid Monte Carlo (section 2).** Fixed with the refined solver.
4. **Par-3 temperature (audit item 3).** Fixed (section 5).
5. **Page:** water / OB outlines on every hole, drawn from the map zones; the creek on 17 and the OB on 18 are now
   visible (audit item 5). Par-3 crops are 32 yds round the green (was 14), so the water short of 6 and 16 shows.
   Moved tees (Forward, the tee slider) no longer show the base tee's book note, which quoted the Back fairway shares
   and yards in; Forward tees moved 100+ yds say they are a rough guide (audit item 7). A close-call badge shows the
   runner's margin and the share of what-if golfers the pick wins when the book margin is under 0.03 or that share is
   under 80 % (audit items 1, 8). The tee slider moves in 5-yd steps.

All engine options are per course (`config.engine`): library pages and the other tournament pages keep the engine
they were solved with. The page-side fixes (5) apply to every page built from the template. Tests:
`course_data/courses/test_v2_course_engine.py` (9) and `test_v2_course_landing.py` (6).

## 8. Sensitivity (Back, central world, two-stage solve, `opt/solve2.py`)

Pick and margin over the runner-up (strokes; +/- is the paired MC SE ~0.001-0.005):

| hole | central | carry+5 | carry-5 | width+10 | width-10 | roll0.8 | flips |
|---|---|---|---|---|---|---|---|
| 1 | Long iron +7 (0.031 vs Driver) | Long iron +6 (0.002 vs Driver) tie | Long iron +7 (0.052 vs Driver) | Long iron +7 (0.049 vs Driver) | Long iron +6 (0.012 vs Driver) | Long iron +7 (0.023 vs Driver) | none |
| 3 | Driver +10 (0.036 vs 2-wood) | Driver +12 (0.032 vs 2-wood) | Driver +8 (0.043 vs 2-wood) | Driver +10 (0.033 vs 2-wood) | Driver +10 (0.040 vs 2-wood) | Driver +10 (0.036 vs 2-wood) | none |
| 4 | Driver -4 (0.029 vs 2-wood) | Driver -8 (0.033 vs 2-wood) | Driver -2 (0.029 vs 2-wood) | Driver -3 (0.029 vs 2-wood) | Driver -6 (0.030 vs 2-wood) | Driver -4 (0.030 vs 2-wood) | none |
| 5 | Driver +4 (0.065 vs 2-wood) | Driver +4 (0.056 vs 2-wood) | Driver +2 (0.076 vs 2-wood) | Driver +4 (0.062 vs 2-wood) | Driver +4 (0.069 vs 2-wood) | Driver +3 (0.069 vs 2-wood) | none |
| 7 | Driver -9 (0.079 vs 2-wood) | Driver -9 (0.078 vs 2-wood) | Driver -10 (0.080 vs 2-wood) | Driver -12 (0.077 vs 2-wood) | Driver -7 (0.083 vs 2-wood) | Driver -10 (0.074 vs 2-wood) | none |
| 8 | Driver +11 (0.057 vs 2-wood) | Driver +12 (0.060 vs 2-wood) | Driver +12 (0.052 vs 2-wood) | Driver +20 (0.060 vs 2-wood) | Driver +10 (0.056 vs 2-wood) | Driver +12 (0.052 vs 2-wood) | none |
| 9 | Driver -11 (0.096 vs 2-wood) | Driver -11 (0.101 vs 2-wood) | Driver -12 (0.088 vs 2-wood) | Driver -14 (0.092 vs 2-wood) | Driver -10 (0.097 vs 2-wood) | Driver -11 (0.087 vs 2-wood) | none |
| 10 | 4-wood +2 (0.058 vs 2-wood) | 4-wood +2 (0.064 vs 2-wood) | 4-wood +2 (0.047 vs 2-wood) | 4-wood +2 (0.064 vs 2-wood) | 4-wood +2 (0.050 vs 2-wood) | 4-wood +2 (0.052 vs 2-wood) | none |
| 11 | Driver -0 (0.031 vs 2-wood) | Driver +0 (0.023 vs 4-wood) | Driver -2 (0.037 vs 2-wood) | Driver -0 (0.026 vs 4-wood) | Driver -0 (0.031 vs 2-wood) | Driver -1 (0.038 vs 2-wood) | none |
| 13 | Driver +13 (0.125 vs 2-wood) | Driver +14 (0.124 vs 2-wood) | Driver +12 (0.124 vs 2-wood) | Driver +12 (0.119 vs 2-wood) | Driver +14 (0.132 vs 2-wood) | Driver +12 (0.115 vs 2-wood) | none |
| 14 | Mid iron +7 (0.016 vs 4-wood) | **8-iron +2 (0.015 vs Mid iron)** | Mid iron +4 (0.055 vs 8-iron) | Mid iron +6 (0.014 vs 8-iron) | **4-wood +1 (0.007 vs Mid iron)** | Mid iron +6 (0.009 vs 4-wood) tie | carry+5, width-10 |
| 15 | 4-wood -12 (0.061 vs 2-wood) | 4-wood -14 (0.065 vs 2-wood) | 4-wood -9 (0.045 vs 2-wood) | 4-wood -12 (0.065 vs 2-wood) | 4-wood -11 (0.053 vs 2-wood) | 4-wood -10 (0.052 vs 2-wood) | none |
| 17 | 4-wood +5 (0.060 vs 2-wood) | 4-wood +6 (0.031 vs Driver) | 4-wood +4 (0.050 vs 2-wood) | 4-wood +4 (0.044 vs Driver) | 4-wood +6 (0.071 vs 2-wood) | 4-wood +5 (0.057 vs 2-wood) | none |
| 18 | Driver -0 (0.046 vs 4-wood) | Driver -2 (0.044 vs 4-wood) | Driver +0 (0.039 vs 4-wood) | Driver -0 (0.030 vs 4-wood) | Driver -2 (0.054 vs 2-wood) | Driver -0 (0.046 vs 4-wood) | none |

Wind +/-5 mph (the page's own refined grid, 50 F, card tee; `opt/wind_sens.py`): calm pick vs every 5-mph cell
(12 directions):
* Back: **1** flips to Driver with a helping wind (5 mph helping: Driver by 0.010; 10 mph: 6 of 12 directions differ).
  Sunday's N wind is behind you on 1 (bearing 191), so expect the page to say Driver there on Sunday. **14** flips to
  the 8-iron with a helping wind (0.015 at 5 mph). 15 at 10 mph into: 2-wood tie (0.000). Every other hole: same club
  in every 5- and 10-mph cell.
* Eagle: 14 (as Back); 10 and 15: one 10-mph direction each.
* Middle: 5 and 10 (helping -> Driver by 0.002-0.012), 11 (helping -> 4-wood, 0.000). Ties already.

**Marginal holes (the pick flips):** Back 1 (carry +5: a tie; helping wind -> Driver), Back 14 (carry +5 -> 8-iron;
spread -10 % -> 4-wood by 0.007; helping wind -> 8-iron), Middle 5 / 10 / 11 (ties). Robust: Back 3, 4, 5, 7, 8, 9,
10, 11, 13, 15, 17, 18 keep the club under every variant (aims move 1-9 yds; 8 moves to +20 with a 10 % wider
pattern).

## 9. Audit items (AUDIT.md), accepted / rejected

| # | item | verdict | evidence / what changed |
|---|---|---|---|
| 1 | Hole 1 Driver over the corner; flight not checked; 79-yd flip; x1.30 roll | **Accepted (Back), rejected (Middle)** | The engine had no flight-path tree check; it is added (section 7). Back 1 is now Long iron, a close call (0.029 +/- 0.005, 61 % of 256 what-if golfers) and badged. Middle 1 stays Driver (0.089, z 19): from 20 yds ahead the line clears the corner. The "x1.30" is the DEM slope cap on a 61-ft-downhill landing, not turf; roll x0.8 (soft November turf) keeps Long iron (0.023). The forecast shows little rain (Sat 5 %, Sun 16 %); turf firmness on the day is not known. |
| 2 | No club under the Mid iron; Middle 14 | **Accepted** | 8-iron 162 / 167 added (assumed gapping, to confirm with Will). Middle 14 -> 8-iron +4.5 by 0.104. Back 14 is a tie Mid iron / 8-iron. |
| 3 | Par-3 plays-like ignores temperature | **Accepted** | Fixed in the template with a test; +2 yds at ~50 F, its own chip. |
| 4 | Card: 2015 sheet 10 = 420; 2024 setup | **Accepted** | Footer corrected (2015 = this card except 10 at 420; the 2024 setup listed). Tee slider in 5-yd steps over -60..+60 covers 5 at 420 (-45), 14 at 246 (-19) and 10 at 420 (+15); the solve snaps to the 20-yd grids. |
| 5 | No water / OB drawn; par-3 crops hide the water | **Accepted** | Outlines from the map zones on every hole; par-3 crops 32 yds round the green. |
| 6 | 16 box 159-159 | **Accepted as a display bug; rejected the "2 yds long" bias** | A collapsed DECADE box is drawn at least 4 yds wide, centred on the target. The EV check says moving 2 yds long (toward the trees) costs ~0.03. |
| 7 | Forward notes copied from Back; Forward 3 tee in the fairway | **Accepted (display)** | Moved / Forward tees no longer show the base book note. Tees moved 100+ yds are flagged "rough guide". Forward stays offered; it is not Will's set and is not solved from its own boxes. |
| 8 | Middle 17 Driver over the creek | **Rejected, resolved** | With 256 draws Driver wins by 0.044 +/- 0.0025 (z 17, 86 % of what-if golfers). That is not a tie and gets no close-call badge. The risk is real (water 18 %, trees 14 %), but the model prices it. |
| - | Middle 5 "show tie" | **Accepted** | Now 4-wood vs Driver at 0.001: TIE. |
| - | Eagle 9 aim | **Unchanged** | New aim -14.5 (the audit suggested about -8); the book's window decides, and the stakes are low. |
| - | Eagle 2 yardage 164 vs 167 | **Noted, not changed** | The page uses the card (167); the measured centre is 164. |

## 10. Scores

`course_data/courses/score_auto.py --slug eagle_knoll --n 6000` was re-run on Nov 3 in this worktree. It scores the
product's quick decision on the blind auto package against the hand truth, so it does not use v2 or anything
changed here:

| | routing / par / green <= 10 | tees <= 10 yds | par 3s planned | same club / same-or-tie | regret | IoU trees / long grass / water / OB |
|---|---|---|---|---|---|---|
| before (score_before.md, Oct 29) | 18 / 18 / 18 | 69 / 72 | 4 / 4 | 13 / 14, 14 / 14 | 0.020 | 0.796 / 0.0 / 0.75 / 0.617 |
| re-run Nov 3 (after this work) | 18 / 18 / 18 | 69 / 72 | 4 / 4 | 13 / 14, 14 / 14 | 0.020 | 0.796 / 0.0 / 0.75 / 0.617 |

The numbers are identical, as expected: the map and the product engine were not changed. The v2 page's own
before / after is in sections 2b and 7.

## 11. Still uncertain

* Will's real dispersion and the 8-iron carry: no measured data. Back 1 and 18 flip with the driver spread, and
  Back 14 flips with carry or width.
* The tree height and stop share in the flight check: hole 1 ranges from a tie to Long iron by 0.09.
* The day's tee boxes: the sheet is not posted, and 2024 moved 10 of 18. Check each plaque.
* The forecast: re-fetched Nov 5. Decisions are at the Oct 31 temperatures.
* The par-3 EV model: pins are unknown, and the depth spread is from published amateur patterns, not Will's.
* OB on 18 is +/- 8 yds; the creek width on 17 is uncertain; trees have grown since the 2015 lidar or NAIP 2022.
* Forward set: still synthesized from the Back tee (not Will's set).

## 12. Tee-shot re-check, Nov 6 (lidar flight trees, roll, aim search, Monte Carlo, the Nov 5 forecast)

Work done on Nov 6 under a 2-hour deadline, on one shared CPU (load average ~23 while a read-only panel re-solved
the course). No Actions run fits, so only results re-solved and verified locally are written to the data.
Scripts: `opt/solve2.py` (two-stage central solve; new variants `roll1.2`, `cap1.0`), `opt/align_canopy.py`.

### 12a. Trees in the flight path from the lidar (engine option `flight_trees.mode = "lidar"`)

The Nov 3 check (section 7) used one crown height for every tree (20 yds) and a flat 70 % stop. It now uses the
measured canopy (`v2_course.lidar_flight_ev_curve`, `canopy_grid`):

* **Crown tops:** `course_data/vision_any/eagle_knoll/raw/hag.tif`, the USGS 3DEP Boone Co. lidar (Jan-Mar 2015,
  leaf-off) height above ground, 0.25 m units, 1 m grid, nodata 255. Each hole's tee frame is sampled on a 1-yd
  grid. Cells under 4 m are not crowns. OB cells (the house roofs on 18) are masked. +1.5 m growth since 2015 is added
  (mature oak-hickory near its height asymptote grows ~0.1-0.2 m a year; sensitivity 0).
* **Trees grown in since 2015** (5 left, 9 right; mapped from NAIP 2020): map tree cells with no lidar crown take
  the Meta / WRI 1 m canopy-height map (`chm_meta.tif`, ~2018-20 imagery), else 10 m. Before the fill, 49 % of hole
  9's mapped trees had no lidar crown, and 58 % of hole 13's.
* **Alignment with the hand map** (landing area 150-340 yds, +/-55 yds, lidar only, before the fill): IoU 0.80-0.95
  on 1, 3, 5, 7, 8, 10, 14, 15, 17 and 18; 0.71-0.76 on 4 and 11; 0.42-0.50 on 9 and 13 (young trees, the fill
  above). Only 1-7 % of lidar crown cells lie over open lies (overhanging edges). The best shift is <= 2 yds on
  every hole. Median crown tops in the mapped trees are 14-22 yds (p90 18-26), against the 20 yds assumed before.
  Hole 1: median 21, p90 23.
* **Crown base:** 0.35 x the tallest top within 7 yds (live-crown ratio ~65 % for edge-grown hardwoods). Below it
  the ball is among the trunks and is not stopped (trunk hits are rare; sensitivity 0.5).
* **Stop chance from the path length in crowns.** Each swing's descent (from 30 % of the carry and 100 yds out, in
  3-yd steps, with the DEM ground drop as before) accumulates its 3-D path length L inside crowns, where
  base < clearance < top. It stops when L passes its own exponential draw: P(stop) = 1 - exp(-k L). The draw is one
  uniform per swing, shared by every aim and club. The ball then finishes where it stopped, on whatever the map says
  is there: trees under the crown pay the punch-out cost, and rough under an overhanging edge pays rough (blocked
  lines included).
* **k = 0.10 per yd** (mean free path ~10 yds of crown), early November:
  * Leaf-off woody area index of broadleaf crowns is 0.5-1.4 (Neumann et al. 1989: 0.5; Southampton NIR/visible
    hemispherical photos: 1.38-1.53). Over ~11 m of crown that is a woody area density of ~0.05-0.13 m2/m3, a ray
    extinction (G = 0.5) of ~0.03-0.06 per m. A 4.3 cm ball meets twigs and branches over a wider band than a ray
    (x ~2 for stopping branches, more for twigs, which mostly deflect).
  * Missouri Dept. of Conservation: oak colour fades and leaves drop in late October, and the season is finished by
    mid-November. On Nov 7-8 most crowns are bare, with some marcescent oak leaves left.
  * Leaf-on crowns (LAI ~4-5) stop about twice as often. That puts k at ~0.08-0.12 per yd in November and ~0.2 in
    summer. The old flat 70 % stop corresponds to roughly k = 0.2 over a 6-yd path: a summer crown.
  * Sensitivity: k 0.05 and 0.2.
  * This is the least certain number here: no published golf-ball-through-crown measurement was found.
* Tests: `test_v2_course_engine.py` (`test_lidar_flight_*`, `test_lidar_opts_env_and_legacy`,
  `test_eagle_knoll_canopy_matches_the_map`). `V2_FLIGHT_MODE=legacy` runs the Nov 3 constant-height check;
  `V2_LIDAR_K`, `V2_LIDAR_GROWTH`, `V2_LIDAR_BASE` and `V2_LIDAR_MIN` override the options for sensitivities.

### 12b. Roll and turf

* **What the x1.30 is.** The product's "soft" ground setting (`product/package.py CONDITIONS`) clips the DEM
  slope roll factor to 0.7-1.3. The physical factor is Penner's rolling-resistance model, MU / (MU + s) times a
  first-bounce term, with MU = 0.15 (`elevation/adjust.py`). The Driver sits on the cap on 1, 5, 10, 13 and 15, and
  so does every club on 1 (a 61-ft drop). The cap is not a turf-firmness number: the Driver's level-ground roll is
  Will's own 25 yds (300 total - 275 carry), times U(0.8, 1.2) per prior world and +/-25 % per swing.
* **Published data.** No controlled carry-vs-total study on firm vs soft fairways was found. Launch-monitor and
  forum sources give driver roll of ~0-15 yds on soft turf, 15-30 on firm, and a 9-degree driver rolling ~32 yds in
  a Golf Digest TrackMan test.
* **This week.** No rain all week (0 % both days), so the turf is dry. The fairways are probably dormant warm-season
  grass, which is firm. Against that, 34-40 F at 7-8 am means dew or frost on the first holes. On balance Will's
  stated 25 yds is a fair central value, with the prior's 0.8-1.2 as the range.
* **The cap.** Lifting it (firm) or tightening it (x1.0) was tested where the pick could depend on it (results
  below).

### 12c. Aim search, blue bar, Monte Carlo (checked, no change)

* **Aim grid.** The coarse grid is -60..+60 in 0.5-yd steps with picks bounded to +/-40 (`decide.AIMS`,
  `AIM_LIMIT`). The page's wind grids add a second stage of 0.5-yd steps over +/-10 yds on 16,000 swings. I scanned
  every stored prior-averaged curve (Back, Eagle, Middle; pick and runner) for a second basin within 0.01 strokes
  of the best more than 8 yds away: there are none. No pick sits on the +/-40 bound (the widest is Middle 1, -33).
  The only curve flat to the edge of the grid is the 2-wood on 8 (Back and Eagle; the open side is hole 4's
  fairway), and that is a runner-up, not a pick. Both sides of every hazard are inside the search.
* **Blue bar (0.005).** Back windows are 4-9 yds wide, and the paired MC SE of a curve difference is ~0.001-0.003.
  The bar is a sensible "no practical difference" band (0.005 strokes on each of 14 tee shots is < 0.1 a round).
  Unchanged.
* **Monte Carlo.** In the calm book (stored, 256 draws), every Back and Eagle pick is resolved (z 6-65) except 14
  (TIE, labelled); in Middle, 5, 10 and 11 are TIE-labelled. At the forecast conditions (stored refined card-tee
  grids, 50 F), Sat ~calm is the 0 mph cell and Sun SW 5 mph is the 5 mph cell at that hole's relative direction.
  Every Back pick there has a margin of 0.032-0.124 except Back / Eagle 14, where SW 5 gives 8-iron by 0.008 (TIE).
  Middle 5, 10, 11 and 18 are close (0.011-0.018). These are the old-engine grids; see 12f for 9 and 14.

### 12d. Bug: the green had no putting cost (drivable 14), engine option `green_putting`

Found by the coordinator's review panel and verified here. The tee-shot raster has no green lie: the green is
fairway. The scoring tables (`model._tour`) are also clipped at 20 yds. A tee ball finishing ON the 14th green
therefore scored fairway-at-20 yds (about 2.60 for Will, even 3 yds from the hole), and a ball just over the green
scored rough-at-20 (about 2.80). That biased the solve against going for the green by roughly 0.1-0.2 strokes per
ball on the green.

The new option (config `engine.green_putting`, Eagle Knoll only; `v2_course.install_green_putting`,
`attach_greens`):

* Cells inside the package's green polygon (`green_polygon_ll`, put in each tee frame) score Broadie's PGA Tour
  expected putts by distance (Every Shot Counts: 1.61 at 10 ft, 1.98 at 30 ft, 2.21 at 60 ft) + 0.10 for a
  5-handicap.
* Fairway, first cut, rough and sand within 20 yds of the hole add Broadie's short-game change below 20 yds (tour
  fairway 2.18 / rough 2.34 / sand 2.43 at 10 yds), with the amateur rough and sand multipliers.

Measured on Back 14 (central world): 8 yds short of the hole on the green now scores 2.02 (was ~2.60); rough
14 yds past the hole 2.60 (was ~2.80); the 70-yd lay-up spot 2.99 (unchanged). Holes where a tee ball can finish
within 20 yds of the hole: 14 (all sets) and Middle 1 (Driver ~20 yds short). Everywhere else the option changes
nothing. Tests: `test_putts_table`, `test_eagle_knoll_14_green_scores_putts`.

### 12e. Map error: a tree polygon on 9 that is not there

Found by the panel and verified here. Hole 9's hand map (third pass, `zones_ll[51]`, src "hand", the "2020 crown at
250-275" in AUDIT.md) had a 16-point tree polygon at x +10..+24, 251-275 yds out. In that box:

| source | that box | real crowns (x +28..+40) | open rough (x -60..-45) | fairway (x -5..+5) |
|---|---|---|---|---|
| 2015 lidar height | 0.0 m (p90 0.0) | p90 10.4 m | 0.0 | 0.0 |
| Meta canopy height | 0.0 m (p90 0.0) | p90 3.0 m | 0.0 | 0.0 |
| NAIP 2020 brightness / NDVI | 120 / 0.12 | 83 / 0.01 | 129 / 0.12 | 127 / 0.20 |
| NAIP 2022 brightness / NDVI | 131 / 0.18 | 113 / 0.22 | 118 / 0.18 | 127 / 0.26 |

It reads as open grass in both years and both height sources. The dark patch traced from NAIP 2020 is the shadow
of the crowns beside the cart path. The polygon is removed from `truth/package.json` and from the three
`course.py` modules (hole 9 only: 53 -> 52 zones; every other hole unchanged).

### 12f. Results (Back central world at the Nov 5 forecast temperatures, two-stage solve, paired SE)

Back, lidar flight trees + green putting + the 9 map fix, against the stored page (calm book):

| hole | page now | re-solved | margin +/- SE | verdict |
|---|---|---|---|---|
| 1 | Long iron +6.5 (0.029) | Long iron +7 | 0.028 +/- 0.003 over Driver -26.5 | **same** |
| 3 | Driver +11 | Driver +10 | 0.038 +/- 0.001 | same |
| 4 | Driver -4 | Driver -5 | 0.038 +/- 0.001 | same |
| 5 | Driver +3.5 | Driver +3 | 0.066 +/- 0.001 | same |
| 7 | Driver -9.5 | Driver -9.5 | 0.077 +/- 0.001 | same |
| 8 | Driver +13 | Driver +11.5 | 0.054 +/- 0.001 | same |
| 9 | Driver -14 | **Driver -2** | 0.095 +/- 0.001 over 2-wood | **aim moves 12 yds right** (12e) |
| 10 | 4-wood +1.5 | 4-wood +1.5 | 0.058 +/- 0.002 | same |
| 11 | Driver -1 | Driver -1 | 0.030 +/- 0.001 | same |
| 13 | Driver +12 | Driver +13 | 0.125 +/- 0.001 | same |
| 14 | Mid iron +8, TIE 8-iron | **4-wood 0** (at the green) | 0.127 +/- 0.005 over Mid iron +7.5 | **club changes** (12d) |
| 15 | 4-wood -11.5 | 4-wood -11.5 | 0.045 +/- 0.002 | same |
| 17 | 4-wood +5 | 4-wood +5.5 | 0.072 +/- 0.004 | same |
| 18 | Driver -1 | Driver -0.5 | 0.031 +/- 0.002 over 4-wood | same |

Eagle and Middle (central):

* **Eagle 9:** Driver -3.5 (page -14.5), by 0.077 +/- 0.001.
* **Eagle 14:** the same box as Back 14, so the same result.
* **Middle 9:** Driver -5.5 (page -13), by 0.092 +/- 0.001.
* **Middle 14** (246, putting on): 8-iron +4 by 0.053 +/- 0.001 (page 8-iron +4.5), the same.
* **Middle 1** (putting on): Driver -33 by 0.113 +/- 0.003, the same.

**Back 1 sensitivity** (lidar engine, central; Long iron margin over Driver):

| variant | margin +/- SE |
|---|---|
| central | 0.028 +/- 0.003 |
| roll x1.2 (firm, dry week) | 0.033 |
| roll x0.8 | 0.021 |
| k = 0.05 (very bare crowns) | 0.009 |
| carry +5 | 0.005 (tie) |
| 5 mph helping | **Driver by 0.010** |
| legacy 20-yd / 70 % check | 0.039 |

Long iron is the pick in every case except a helping wind. Sunday's SW wind (from ~225) is slightly into the hole
on 1 (bearing 191), which favours Long iron, and Saturday is calm. Keep Long iron both days. It is still a close
call: if Will flushes it (carry +5) it is a tie.

**Roll.** Back 1: roll x1.2 0.033, x0.8 0.021, so the pick holds. The x1.30 cap is the soft-ground clip of the DEM
slope factor, and the turf this week (dry, dormant) is if anything firmer, which favours the pick on 1 slightly.
No change to the cap or the roll prior.


### 12g. What was written to the data, and what was not

* **Calm-day book (`v2_decisions.json`), replaced** with `decide.bayes` + shares on the new engine
  (`opt/quickdec.py`, merged by `opt/merge_dec.py`). The runs use fewer prior draws and only the contending clubs
  (plus the hybrid line), because the full decide (256 draws, every club) does not fit the deadline on the shared
  CPU. The record says so (`reduced`, `draws`, `replaced`), and the old ladder / sensitivity / width-sweep extras of
  those holes are dropped:

  | set | hole | old | new | margin +/- SE | p | draws |
  |---|---|---|---|---|---|---|
  | Back | 14 | Mid iron +8 (TIE 8-iron) | **4-wood +0.5** (window -1.5..+2.5) | 0.067 +/- 0.015 over Mid iron | 0.79 | 24 |
  | Eagle | 14 | Mid iron +8 | **4-wood +0.5** (the Back record, same box) | 0.067 +/- 0.015 | 0.79 | 24 |
  | Eagle | 9 | Driver -14.5 | **Driver -4** (-7.5..+0.5) | 0.075 +/- 0.006 over 2-wood | 1.00 | 8 |
  | Middle | 9 | Driver -13 | **Driver -4.5** (-10.5..0) | 0.089 +/- 0.006 over 2-wood | 1.00 | 8 |
  | Back | 9 | Driver -14 | (decide still running at the deadline: the stored record is the old one) | central: Driver -2 by 0.095 +/- 0.001 | | |

  Back 14 with 4-wood: water 13 %, trees 20 %, a median 16 yds from the hole. Every other hole's record is
  unchanged, and the lidar re-solve above agrees with it.
* **Superseded by the Actions run requested in ce5d23833** (holes 9 and 14, all three bases, full 256-draw decide +
  refined card-tee wind grids on this engine). When it merges, its records replace the reduced ones above and the
  9 / 14 wind cells below; the reduced runs are the interim and a cross-check.
* **Wind grids: NOT recomputed locally** (`wind_grid*.json` are unchanged, old engine). One card-tee cell takes ~220 s on
  this box today, so a hole's 183 cells do not fit. Until the nccga-v2 job is re-run (request files
  `nccga_v2_eagle_knoll*.json`, holes 9 and 14 or all; ~3 h), the page's forecast view (Sat / Sun) still shows the
  old 9 aim and the old 14 club. **On the course: 9 aim ~2 yds left of the line (not 14); 14 from the 265 box:
  4-wood at the green, aim on the line.** The only grid cell recomputed (Back 14, 35 F, calm) gives 4-wood +0.5 by
  0.099, which agrees.
* **Engine:** `config.engine.flight_trees.mode = "lidar"` and `green_putting` are on for Eagle Knoll, so any rebuild
  of decisions or grids uses them.

### 12h. Still uncertain (Nov 6)

* The stop extinction k (0.10 per yd) has no golf-specific measurement behind it. Back 1 goes from a tie (k 0.05)
  to Long iron by 0.04 (the old summer-like check).
* Back 14 on the new pick: the 4-wood needs ~255-265 carry over the pond at 50-55 F (Will's 255 at 70 F, +13 for
  the drop). The 8-iron carry (162) is still an assumption, but it no longer decides 14 from the 265 box. From the
  246 box (Middle) the 8-iron lay-up stays the pick (0.053).
* The width-sweep line of the hole note ("same club for any driver pattern") is not re-checked for 9 and 14.
* Not re-solved under the new engine: Eagle and Middle holes other than 1 (Middle), 9 and 14.

### 12i. Back 14: crown ricochets and lidar escape shots (Nov 6, `opt/h14_ricochet.py`)

The engine stops a ball in a crown and scores a generic punch-out. This check keeps the engine's swings and its
path-length stop (same per-swing draw) and then deflects each stopped ball off a branch, flies it on through the
crowns, drops it on the lidar DTM and rolls it out. Balls under trees take a lidar escape shot (low punch along 37
rays, or a pitch under the crown base toward the hole; trunks, understory and the crown base from hag.tif). The
assumptions are in the JSON. Results: `opt/results/h14_ricochet.json`, 40,000 common swings, central world.

* **Crowns by the green** (lidar, +1.5 m growth): left of the green and pond, tops 22 yds (p90 24), base ~8 yds,
  cover 0.90, understory 6 %. Right: 22 (p90 25), cover 0.80, understory 9 %. Behind: 23, cover 0.63. Ground under
  the trees slopes 20-26 %. The pond bank slopes 18 % (p90 30 %), and the tree floor sits ~1.5 yds above the water.
* **Results:**

  | | 4-wood -3 | 4-wood 0 | Mid iron +8 | 8-iron +1 |
  |---|---|---|---|---|
  | average (ricochet + escape) | **3.786** | 3.798 | 4.043 | 4.071 |
  | engine | 3.929 | 3.917 | 4.044 | 4.072 |

  4-wood (-3) finishes: green 14.2 % (3.00), grass round the green 50.1 % (3.61), short grass 1.7 % (4.07), trees left
  16.4 % (3.97), trees right 2.7 % (4.20), trees behind 2.1 % (3.84), pond direct 10.3 % (4.94), pond by ricochet
  2.6 % (5.09). Margin over Mid iron **0.257 +/- 0.003**, over 8-iron 0.285 +/- 0.003.
* **Ricochet into the pond:** 23 % of the crown-stopped 4-wood balls end in the pond, which is 1.8-2.6 % of all
  swings (4.4 % in the worst case). Ricochets on their own (engine punch-out costs kept) change little: 4-wood at 0
  scores 3.908, margin 0.130, and the aim stays at 0.
* **The escape shot is the real change.** Under leaf-off crowns with an 8-yd base and little understory, a ball
  10-25 yds from the hole has a clear punch or pitch. A tree finish costs ~0.35 more than greenside rough, against
  ~1.0 in the generic punch-out.
* **Sensitivity (margin over Mid iron):** retention low / high 0.275 / 0.241; scatter glancing / head-on 0.278 /
  0.248; softer bank roll 0.252; unplayable 0 / 8 % (lost 0 / 5 %) 0.272 / 0.234; escape easy / hard 0.306 / 0.153;
  k 0.05 / 0.20 0.267 / 0.245; everything bad at once 0.123 +/- 0.003. 4-wood wins in every case.
* **Break-even:** laying up wins only if each 4-wood tree finish costs **~1.3 strokes more** than modelled (~5.3 on
  the hole, against 3.98 here and 4.60 in the engine), or ~0.8 more than the worst case.
* **Aim:** with the escape model, the best aim moves left to -3 (flat from -5 to -2, within 0.003; +0.5 costs 0.015).
  With hard escapes or the worst case it goes back to 0 / -1. Ricochets alone keep it at 0. Nothing moves it right.
  Keep "4-wood at the green, on the line to 2 yds left".
* **Not verified:** no measured golf-ball/branch data (COR and scatter are assumed, with the range above). The 2015
  DTM may differ from today's bank. Lie quality in November leaf litter is folded into delta, unplayable and lost.
  The escape-value fixed point assumes a failed shot stays where it was.

## 13. Par-3 targets for an unknown pin (Nov 6 2026)

The page's par-3 box was the DECADE box (`yardage_book.par3_plan`: edge cushions, worse side), drawn round the DECADE
target, and "Play it like" was the carry to that target's depth. Both are now the **expected-strokes optimum for an
unknown pin on Will's own iron pattern**, and they are switched on for this page only (config `par3_targets` ->
`par3_targets.json`, read by `course_data/courses/par3_targets.py`; every other page keeps DECADE, a test checks this).
Script: `opt/par3_target.py` (`solve`, `robust`); full results with surfaces and SEs: `opt/results/par3_target_<set>.json`,
`opt/results/par3_robust.json`.

**Model.**
* **Ball:** the engine's `model.shots` at the central world. Lateral sigma = 95 % width / 4 x 70/65; carry sigma =
  depth window x 1.25 / 4; rho 0.1; kappa 0.08; 12 % slight mishits (92-95 % carry); 2.5 % heavy (65-85 %); temperature
  as on the tee shots. Long iron 210, Mid iron 185 and 8-iron 162 are the engine's clubs. **5-iron 198, 7-iron 174,
  9-iron 150, PW 138 and GW 126 are assumed**, from the Spirit Hollow approach bag (~12-yd gaps); width and depth window
  are scaled with carry the way the engine's 8-iron is. Wind: `wind.adjust` per club, including the gust scatter. The
  box is the landing point, so the mean drift is aimed off.
* **Terrain:** every ball lands where its flight meets the 3DEP 1 m DEM: x = flat carry + 0.839 x (tee height minus
  ground height at x). 0.839 is the page's own elevation factor. The DEM tee-to-green drops are 60.1 / 46.5 / 12.2 /
  38.9 ft (2 / 6 / 12 / 16), equal to the page's meta. Then the ball rolls its stated roll (+/-25 %) along the line,
  x0.3 in rough, and stops in sand, trees or water.
* **Green and pins:** the truth-map green polygon. Pins are uniform over the green at least 4 yds inside the edge
  (140-192 pin spots per green on a 1-yd grid). The DEM plane fit (residual 0.2-0.3 ft) gives back-to-front tilts of
  2.1 % (2, also 2.1 % up to the right), 2.1 % (6), 2.5 % (12) and **5.0 % (16)**. Putting: Broadie by feet + 0.06
  (5-hcp). A slope term (**assumed size**) adds 0.02 strokes per 1 % of downhill grade along the putt, at full size from
  15 ft, and takes the same off uphill.
* **After the shot:** short game by lie + 0.15 within 40 yds, and the engine's amateur table beyond that. Trees use
  Broadie's recovery row. Water costs 1 + rough from the drop. OB costs 1 + 3.2. Everything is pin-averaged on a
  0.5-yd raster.
* **Statistics:** common random numbers across aims and clubs. A 1-yd coarse grid (6,000 swings; Eagle and Middle
  3,000) is followed by a 0.5-yd refine of +/-4 yds on fresh swings (40,000; Eagle and Middle 16,000). The centre and
  DECADE aims are scored on the same fresh swings. Every margin below is a paired mean +/- its SE. The box is the
  extent of aims within 0.02 strokes of the best, at least 4 yds each way. There is one box per page wind class:
  calm, and 7 / 14 / 24 / 32 mph averaged over head, tail and both crosswinds.

**Back, calm, 50 F** (depth: + = long of the green centre; strokes for the hole):

| hole | best aim (lat, depth) | box lat / depth | EV best | gain vs centre aim | gain vs old DECADE aim (its lat, depth) | aim 4 / 8 long of centre | 4 / 8 short | 4 / 8 left, right |
|---|---|---|---|---|---|---|---|---|
| 2 (151) | -0.5, **-1.5** | -2.5..1.5 / -4..0 | 3.077 | +0.020 +/- 0.001 | +0.000 +/- 0.000 (-0.1, -1.5) | +0.24 / +0.55 | +0.03 / +0.16 | +0.04 / +0.18, +0.07 / +0.25 |
| 6 (138) | 0, **-1** | -2..2 / -2.5..1.5 | 3.043 | +0.002 +/- 0.001 | +0.012 +/- 0.001 (+1.1, +0.5) | +0.13 / +0.35 | +0.06 / +0.22 | +0.04 / +0.19, +0.04 / +0.17 |
| 12 (180) | +0.5, **-4** | -2..3 / -7..-2 | 3.255 | +0.042 +/- 0.001 | +0.042 +/- 0.001 (-2.2, -0.4) | +0.16 / +0.31 | +0.00 / +0.03 | +0.04 / +0.14, +0.03 / +0.13 |
| 16 (158) | 0, **-1.5** | -2.5..1.5 / -4..0 | 3.385 | +0.015 +/- 0.002 | **+0.070 +/- 0.002** (+0.4, +2.0) | +0.16 / +0.41 | +0.04 / +0.26 | +0.06 / +0.24, +0.09 / +0.34 |

(Surface columns: the coarse grid, strokes above the best, at aims 4 / 8 yds from the green centre on the best aim's line. Sunday, SW 5.5 mph with
gusts to 12: the same aims within 0.5 yd, and the gains vs centre are 0.027 / 0.001 / 0.038 / 0.009.)

**What changed against section 6.** Section 6's 8-10 yds short on 2 and 12 used a published amateur *finish* pattern
(depth sigma 1.5 x lateral, about 14 yds at 150) with no mishits. Will's engine pattern is tighter in depth: carry
sigma 4-6 yds, with mishits making a short tail. So a long miss into the trees is less likely, and a short aim
throws away more good shots. The short side still holds on 12 (4 yds short, 0.04). On 2 it is 1.5 short and ties the
DECADE target. Doubling the depth spread (the "depth x2" row below) moves 2 only to 3 short. On 16 the old box sat
2 yds long (toward the trees and above a 5 % slope) and cost 0.07; the new aim is 1.5 short of centre. 6 is the centre.

**Club (Back, stock carries, the lateral aim optimised; margin over the runner-up +/- SE):**

| hole | Sat (47 F, calm) | Sun (54 F, SW 5.5 g12) | stock club lands (Sat) | cost of the stock club vs the ideal number |
|---|---|---|---|---|
| 2 | **PW** by 0.148 +/- 0.003 over GW | PW by 0.198 +/- 0.003 | +1.8 (aim -1.5) | 0.07-0.15: a full PW is ~3 yds past the ideal number; a touch easy if you can |
| 6 | **GW** by 0.449 +/- 0.002 over PW | GW by 0.643 +/- 0.002 | -1.8 | 0.01 (Sun 0.06) |
| 12 | **7-iron** by 0.134 +/- 0.002 over 6-iron | 7-iron by 0.139 +/- 0.002 over 8-iron | -7.0 (Sun -2.0) | 0.00-0.01 |
| 16 | **9-iron** by 0.464 +/- 0.004 over PW | 9-iron by 0.050 +/- 0.004 over PW | +0.2 (Sun +4.4) | 0.02 (Sun 0.15: the 9-iron flies ~4 long; still better than PW) |

All clubs are resolved (z >= 11); there is no TIE. The page shows the number, not the club. The club is in the hole
note, and in `p3club` for a template that shows it.

**Plays like, carry to the best aim** (the page: (wind plays-like + elevation) / temperature factor, at the hole time
for a 9:00 shotgun on 1; numbers to the centre in brackets):

| hole | Sat (44-55 F, calm) | Sun (49-62 F, SW 5-6) |
|---|---|---|
| 2 | 135-136 (137) | 137 (138) |
| 6 | 126-127 (127-128) | 121-123 (122-124) |
| 12 | 177 (181) | 172 (176) |
| 16 | 146-147 (148-149) | 142-143 (144) |

The page builds the number from the box, so the hook rescales the per-cell plays grid by card / aim distance. The
template's own formula (box x plays / card x temperature) then gives the carry to the aim exactly, and its elevation
chip is still the DEM drop. A test pins the template formula.

**Robustness (Back; `robust`: 4,000-swing 1-yd grid, 20,000 fresh swings for the comparison).** Each cell gives the
best aim under the variant, then the regret of keeping the page aim +/- SE, then the page aim's gain over the centre
under that variant:

| variant | 2 | 6 | 12 | 16 |
|---|---|---|---|---|
| carry +5 (you fly it 5 longer than the model) | -7; 0.181 +/- 0.003; +0.106 | -6; 0.102; +0.048 | -9; 0.052; +0.128 | -7; 0.138; +0.084 |
| carry -5 | +3; 0.075; -0.042 | +4; 0.109; -0.035 | 0; 0.040; -0.040 | +2; 0.138; -0.082 |
| dispersion +/-10 % | -2; <= 0.002; +0.018..0.025 | -1; 0.000; +0.002 | -4; <= 0.001; +0.042 | -1..-2; <= 0; +0.014..0.021 |
| wind +3 mph (calm -> 3, any direction) | -2; 0.001; +0.023 | -1; 0.000; +0.002 | -4; 0.000; +0.042 | -2; 0.000; +0.018 |
| Sunday wind +/-3 mph | -2; 0.000; +0.026..0.031 | -1; 0.000; +0.000 | -4; 0.000; +0.036..0.041 | -1..-2; 0.000; +0.013 |
| roll x0.5 (soft greens) | -1; 0.003; +0.002 | 0; 0.005; -0.005 | -2; 0.008; -0.006 | -1; 0.002; -0.003 |
| no slope term / slope x2 | -2; 0.000; +0.018 / +0.027 | -1; 0.000; 0.000 / +0.005 | -4..-5; 0.001; +0.037 / +0.047 | -2; <= 0.001; +0.013 / +0.025 |
| trees half the cost | -2; 0.000; +0.016 | -1; 0.000; +0.002 | -4; 0.000; +0.041 | -2; 0.005; +0.008 |
| no mishits | -3; 0.015; +0.047 | -2; 0.004; +0.017 | -5; 0.001; +0.063 | -3; 0.013; +0.048 |
| pins 3 / 6 yds in | -2; <= 0.002; +0.021 / +0.027 | -1; 0.000; +0.001 / +0.005 | -4; 0.000; +0.041 / +0.038 | -2; 0.000; +0.018 / +0.024 |
| depth spread x2 (section 6's kind of pattern) | -3; 0.006; +0.017 | 0; 0.005; -0.005 | -7; 0.006; +0.046 | 0; 0.011; -0.011 |

* **The aim is robust.** Under every dispersion, wind (+/-3 mph), roll, slope, tree, pin and mishit variant, the page
  aim is within 0.015 strokes of that variant's best (usually within 0.005), and the variant's best is within 1.5 yds
  of the page aim (12 with a double depth spread: 3 yds). Averaging the surface over a carry error of sd 3 or 5 yds
  gives the same aims within 1 yd (2: -2 / -3; 6: -1; 12: -4 / -5; 16: -1).
* **The number is what matters.** If Will's real carry with that club is 5 yds off the model, he loses 0.04-0.18
  strokes a hole at any aim (on 2 and 16, long is the dearer error). The 9-iron, PW and GW carries are assumed
  gapping, so **confirm the wedge and short-iron carries with Will**: this is worth more than any aim change here.
* Gains vs centre are significant on 2, 12 and 16 (z 10-38). On 6 the aim is the centre: gain 0.002 +/- 0.0005, and
  it changes sign with soft greens or a deeper pattern.

**Not verified / limits.** The pins are uniform, not the day's sheet. The slope term's size is assumed (±100 %
shown). The DEM is the 2015 lidar (green surfaces may have been rebuilt since). The short-club carries are assumed.
Lateral wind drift is aimed off, not modelled as a miss. Release does not depend on the green slope. The DECADE wind
classes use direction-averaged wind; the page does not know whether the wind is into or across.

**Eagle and Middle** (own boxes, from their own tees; quick mode: 3,000 / 16,000 swings, and the 14-32 mph boxes
copied from the 7 mph box, which on Back differ by 0.5 yd or less):

| set, hole | best aim (lat, depth) | gain vs centre | gain vs old DECADE aim | club Sat / Sun (margin +/- SE) |
|---|---|---|---|---|
| Eagle 2 (167) | -0.5, -3 | 0.051 +/- 0.003 | 0.010 +/- 0.002 | 9-iron by 0.11 +/- 0.005 / 9-iron by 0.17 |
| Eagle 6 (149) | 0, -1 | 0.007 +/- 0.001 | 0.041 +/- 0.002 | PW by 0.42 / **GW** by 0.07 +/- 0.005 (SW wind helping: the PW flies long) |
| Eagle 12 (198) | +0.5, -6 | 0.066 +/- 0.002 | 0.070 +/- 0.002 | 5-iron by 0.068 +/- 0.003 / 6-iron by 0.16; calm 50 F: **TIE** 6-iron / 5-iron (0.009 +/- 0.003) |
| Eagle 16 (177) | -0.5, -2.5 | 0.023 +/- 0.003 | 0.114 +/- 0.005 | 8-iron by 0.13 +/- 0.007 / 8-iron by 0.37 |
| Middle 2 (132) | 0, -1.5 | 0.013 +/- 0.001 | -0.001 +/- 0.001 (same) | GW, which lands ~6 long: **the model bag has no sand wedge** |
| Middle 6 (120) | 0, -1 | 0.004 +/- 0.001 | 0.014 +/- 0.001 | GW lands ~14 long: **no sand wedge in the model** |
| Middle 12 (162) | 0, -3 | 0.023 +/- 0.002 | 0.013 +/- 0.001 | 8-iron by 0.16 +/- 0.002 / 9-iron by 0.047 +/- 0.003 |
| Middle 16 (136) | 0, -1 | 0.006 +/- 0.002 | 0.014 +/- 0.002 | GW by 0.33 / GW by 0.55 |

The pattern is the same on every set: the centre line, a little short (1-3 yds; 12: 3-6 yds), and never long. On
Middle 2 and 6 the club column is limited by the model bag (shortest GW 126). Add SW ~113 / LW ~100 before the club
on those holes means anything. The aim and the number do not depend on it.
