# Eagle Knoll: optimisation and verification of the choices (Nov 3-4 2026)

For Will (KU club golf), NCCGA Central Regional 2, Eagle Knoll GC (Hartsburg MO), Sat-Sun Nov 7-8 2026, Back (blue)
tees. Page: https://claude.ai/artifact/QQkFta99SEstd6Dv8wzgf8 (built from `wind_page/index.html`). The independent
audit (`AUDIT.md`, ec6084ac8) was worked in; section 9 lists each audit item as accepted / rejected with the evidence.

Everything here was measured in a sparse-but-scoring-complete worktree (elevation, library, vision_any/s2,
spirit_hollow, mozingo, product, packages/eagle_knoll present) and on GitHub Actions. Scripts used are named per
section; the local ones live in `opt/` or are described exactly enough to repeat.

## 0. Summary for Will (Back tees)

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
* **Par 3s:** "Play it like" now includes the temperature (+2 yds at ~50 F). On **2 and 12 the front of the green is
  the better miss** (aim ~8-10 yds short of centre); on 6 and 16 the box is right.
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
* Accepted on 2 and 12: the front of the green is the better miss. Long is trees on both, and open grass or fairway
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
