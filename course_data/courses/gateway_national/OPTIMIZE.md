# Gateway National: page, engine, map fixes and re-solve (Nov 9-12 2026)

## Round 2, Nov 13 (strategy lead, second shift; running log, newest checkpoint last)

Starting point: version 9 of the page (f50e64f7b). Tools of this shift: scratchpad `r2/` (walk.js: every hole of the
built page for each set x day x starting hole straight from the page's own solver functions; rend.js: the rendered
text of the same; zoom.py: photo / infrared / 2020 lidar relief / lidar contours with the map's outlines, tees, par-3
surrounds and box; qa_all.sh: qa_page.js on the five sets in parallel, 23 s, plus the hazard-word scan).

### R2-1. Sunday walk-through, both possible starts (page as built; 9:00, 14 min a hole)

Forecast the page uses (fetched Nov 13 02:44Z): Sat 4-5 mph from N / NNW, 35 F at 9:00 rising to 47 F; Sun 3.5-4 mph
from ESE (104-108 deg), 43 F at 9:00 rising to 53 F. Aim = yds left / right of the tee line; in brackets the margin
over the next club (wind model at the hole). Par 3s: the plays-like number and the club.

**Back**

| hole | calm book | Sat, start 1 | Sat, start 10 | Sun wind at the hole (start 1) | Sun, start 1 | Sun, start 10 | flag |
|---|---|---|---|---|---|---|---|
| 1 | Driver 8.5 L | Driver 5 L (0.051) | Driver 7 L (0.053) | behind 3 / from R 2 | Driver 5.5 L (0.044) | Driver 5 L (0.041) |  |
| 2 | Driver 9.5 R | Driver 13.5 R (0.057) | Driver 16 R (0.056) | behind 2 / from L 3 | Driver 5 R (0.056) | Driver 5 R (0.051) |  |
| 3 | Driver 6 L | Driver 2 L (0.060) | Driver 0.5 R (0.060) | behind 2 / from L 3 | Driver 11 L (0.060) | Driver 11 L (0.061) |  |
| 4 | par 3 | 180: 7-iron | 178: 7-iron | in 0 / from L 4 | 183: 6-iron | 182: 6-iron (0.02) | club differs; Sun margin < 0.03 |
| 5 | Driver 4.5 R | Driver 1.5 L (0.089) | Driver 3 L (0.085) | in 3 / from R 2 | Driver 7.5 R (0.095) | Driver 7 R (0.094) |  |
| 6 | Driver 5.5 R | Driver 11 R (0.116) | Driver 11.5 R (0.114) | behind 3 / from L 2 | Driver 2 R (0.114) | Driver 2.5 R (0.113) |  |
| 7 | par 3 | 187: 6-iron | 184: 6-iron | in 3 / from R 3 | 189: 6-iron | 187: 6-iron |  |
| 8 | Driver 44.5 L | Driver 49.5 L (0.061) | Driver 51 L (0.048) | in 2 / from R 3 | Driver 40 L (0.062) | Driver 41.5 L (0.055) |  |
| 9 | Driver 12.5 R | Driver 5.5 R (0.033) | Driver 7.5 R (0.023) | in 3 / from R 3 | Driver 16.5 R (0.036) | Driver 16 R (0.031) |  |
| 10 | 2-wood 26 L | 4-wood 20 L (0.020, level: shown by rule) | 4-wood 21.5 L (0.020, level: shown by rule) | behind 3 / from L 2 | 4-wood 30 L (0.090) | 4-wood 30 L (0.053) | club differs |
| 11 | Driver 16 R | Driver 23 R (0.026) | Driver 21 R (0.024) | behind 2 / from L 3 | Driver 13.5 R (0.027) | Driver 13.5 R (0.026) | Sun margin < 0.03 |
| 12 | par 3 | 137: PW | 137: PW | behind 4 / from L 1 | 131: GW | 132: GW | club differs |
| 13 | Driver 3 R | Driver 4 L (0.118) | Driver 5 L (0.103) | in 3 / from R 2 | Driver 6 R (0.115) | Driver 4 R (0.104) |  |
| 14 | par 3 | 201: 5-iron | 203: 5-iron | in 3 / from R 2 | 205: 5-iron | 207: 5-iron (0.03) | Sun margin < 0.03 |
| 15 | Driver 13.5 R | Driver 20 R (0.109) | Driver 20.5 R (0.108) | behind 3 / from L 2 | Driver 8.5 R (0.091) | Driver 9.5 R (0.094) |  |
| 16 | 4-wood 5.5 R | 4-wood 0 (0.091) | 4-wood 1.5 R (0.068) | in 2 / from R 3 | 4-wood 11.5 R (0.095) | 4-wood 12.5 R (0.085) |  |
| 17 | par 3 | 197: 5-iron | 201: 5-iron | in 1 / from R 3 | 196: 5-iron | 198: 5-iron |  |
| 18 | Driver 14.5 R | Driver 15.5 R (0.136) | Driver 14 R (0.136) | in 2 / from L 3 | Driver 10.5 R (0.130) | Driver 10.5 R (0.124) |  |

**Middle**

| hole | calm book | Sat, start 1 | Sat, start 10 | Sun wind at the hole (start 1) | Sun, start 1 | Sun, start 10 | flag |
|---|---|---|---|---|---|---|---|
| 1 | Driver 6.5 L | Driver 3 L (0.028) | Driver 4.5 L (0.028) | behind 3 / from R 2 | Driver 3.5 L (0.022) | Driver 3.5 L (0.022) | Sun margin < 0.03 |
| 2 | Driver 11 R | Driver 16 R (0.030) | Driver 19 R (0.030) | behind 2 / from L 3 | Driver 8 R (0.030) | Driver 8 R (0.029) | Sun margin < 0.03 |
| 3 | Driver 4.5 L | Driver 0 (0.086) | Driver 2 R (0.087) | behind 2 / from L 3 | Driver 9 L (0.086) | Driver 9 L (0.089) |  |
| 4 | par 3 | 155: 9-iron | 153: 9-iron | in 1 / from L 4 | 158: 9-iron (0.02) | 157: 9-iron | Sun margin < 0.03 |
| 5 | Driver 0 | Driver 6 L (0.055) | Driver 6.5 L (0.054) | in 3 / from R 2 | Driver 2.5 R (0.057) | Driver 2.5 R (0.055) |  |
| 6 | Driver 7.5 R | Driver 13.5 R (0.052) | Driver 14 R (0.050) | behind 3 / from L 2 | Driver 4.5 R (0.030) | Driver 4.5 R (0.025) | Sun margin < 0.03 |
| 7 | par 3 | 167: 8-iron | 165: 8-iron | in 3 / from R 3 | 169: 8-iron | 167: 8-iron |  |
| 8 | 4-wood 33.5 L | 4-wood 40.5 L (0.028) | 4-wood 40 L (0.050) | in 2 / from R 3 | 4-wood 28.5 L (0.028) | 4-wood 30.5 L (0.042) | Sun margin < 0.03 |
| 9 | 4-wood 11 R | 4-wood 3 R (0.036) | 4-wood 5 R (0.039) | in 3 / from R 3 | 4-wood 15.5 R (0.034) | 4-wood 15 R (0.036) |  |
| 10 | 4-wood 23 L | 4-wood 15 L (0.221) | 4-wood 16.5 L (0.213) | behind 3 / from L 2 | 4-wood 27 L (0.144) | 4-wood 26.5 L (0.183) |  |
| 11 | Driver 18.5 R | 4-wood 18 R (0.004, level: shown by rule) | 4-wood 16 R (0.003, level: shown by rule) | behind 2 / from L 3 | 4-wood 7 R (0.003, level: shown by rule) | 4-wood 6.5 R (0.003, level: shown by rule) | club differs; Sun margin < 0.03 |
| 12 | par 3 | 120: SW (0.04) | 119: SW | behind 4 / from L 1 | 115: SW | 116: SW |  |
| 13 | Driver 11 R | Driver 4 R (0.116) | Driver 3.5 R (0.129) | in 3 / from R 2 | Driver 13 R (0.126) | Driver 11.5 R (0.130) |  |
| 14 | par 3 | 187: 6-iron | 189: 6-iron | in 3 / from R 2 | 190: 6-iron | 192: 6-iron |  |
| 15 | Driver 7 R | Driver 13.5 R (0.047) | Driver 13.5 R (0.047) | behind 3 / from L 2 | Driver 3 R (0.039) | Driver 3.5 R (0.040) |  |
| 16 | long iron 7 R | long iron 2.5 R (0.101) | long iron 3 R (0.097) | in 2 / from R 3 | long iron 12 R (0.101) | long iron 12.5 R (0.102) |  |
| 17 | par 3 | 176: 7-iron | 179: 7-iron | in 1 / from R 3 | 175: 7-iron | 176: 7-iron |  |
| 18 | Driver 9.5 R | Driver 9 R (0.137) | Driver 7.5 R (0.134) | in 2 / from L 3 | Driver 6 R (0.140) | Driver 6 R (0.138) |  |

10 from The Tips / Champions (grid +40): 4-wood at the right fairway on both days and both starts: Sat 17.5 R / 16 R
(0.029 / 0.031 over the 2-wood), Sun 9.5 R / 8.5 R (0.042 / 0.038). 11 from there: 4-wood by the level rule, as Sat.

Checks made on every hole, both days, both starts:

* **Wind sign.** Each hole's bearing in the grids was recomputed from the tee and aim-line coordinates of the truth
  package (all 18 within 0.2 deg; Back 2's package field still says 236.6, the grid uses the moved tee's 222.6, which
  is the geometry). Head / cross components recomputed from the forecast direction and the bearing: the sign and size
  on the page agree on all 18 holes x 2 days x 2 starts (e.g. 1 heads 318: Sat's N wind is 3 into and 3 from the
  right, Sun's ESE wind is 3 behind and 2 from the right; 5 heads 80: Sat 4 from the left, Sun 3 into).
* **Aim follows the drift, not the other way.** For every tee shot the aim plus the wind's sideways drift (the
  finishing line) is within 2.6 yds of the calm book's line on both days and both starts (median 0.3). Sunday's aims
  differ from Saturday's by 6-11 yds on most holes only because the crosswind changes side.
* **Club changes Sat -> Sun on Back: none on a tee shot.** 10 is the 4-wood on both days (Sat by the level rule,
  0.020 behind the 2-wood; Sun outright by 0.05-0.09 with 3 mph behind: red team's table). Par 3s: **4** 7-iron Sat
  (180 / 178), 6-iron Sun (183 / 182: 4 mph across instead of 4 behind); **12** PW Sat (137), GW Sun (131, 4 mph
  behind). Middle: no club changes Sat -> Sun.
* **Start on 10** moves each hole's clock by about two hours (1-9 warmer, 10-18 colder). No tee-shot club changes on
  either day from Back or Middle. Margins under 0.03 on the forecast: Back 9 Sat from a 10 start (0.023; pill
  shown), Back 11 (0.024-0.027, close-call pill), Middle 1 (0.022-0.028), Middle 2 (0.029-0.030), Middle 6 on Sunday
  (0.025-0.030: the helping wind takes the Driver further into the narrowing; Saturday 0.05), Middle 8 from a 1 start
  (0.028), Middle 11 (level: 4-wood shown). All carry the page's close-call mark (threshold 0.045).
* Nothing found wrong; nothing changed on a tee shot from this task.

### R2-2. Par 3s, adversarial

Looked at each green and tee complex on the 2023 photo, the infrared and the 2020 lidar ground (zoom.py):

| hole | green outline vs photo | tee pads (lidar: flat raised pads; photo: divot scars) | card / map centre | surround |
|---|---|---|---|---|
| 4 | on the putting surface (x -19..+17, 161-190); the darker lobe to its left is collar-height grass, mapped as fairway | Back point on its own round pad (pad spans 171-182 to the centre); The Tips / Champions on the pad behind | 180 / 176 (every set is 3-5 over the map on this hole) | the tufted mound back-right (lidar crest 1.5 m above the green, 3-12 yds off the edge) IS in the par-3 solve as long grass (`opt/par3_features.json`, reviewer A's 4a); 4b's extension to the left along the back is mown in the photo: not added |
| 7 | on the surface (x -12..+10, 160-191) | one long strip, 57 yds; Back point on it with divots at that spot; Middle point on its left edge, divot field 146-159 from the centre | 180 / 176 and 160 / 155 (every set 4-5 over the map) | unmown ground short on the line is in the solve (reviewer B's P2) |
| 12 | on the surface; the solve uses the re-traced outline with the left edge 2 yds further left (B's P4 is in already) | Back and Middle share the rectangular pad | 131 / 131, 115 / 114 | everything left, short and long is as mapped |
| 14 | on the surface (x -12..+11, 183-218) | Back pad 183-205 from the centre, Middle its own pad | 200 / 200, 185 / 185 | left side: sand, long grass, crowns: in the solve |
| 17 | on the surface; solve uses the re-traced outline | Back pad 181-204, Middle pad 165-178 | 195 / 193, 173 / 171 | four pots re-traced: in the solve |

Elevation: tee and green heights from the 2020 lidar agree with the page's (4: green 2.9 ft above, 7: 0.9 below, 12:
2.3 below, 14: 2.4 below, 17: 2.5 below; Middle within 0.2 ft of the page on all five).

"Plays like" sums, Back (target + elevation + wind + temperature): Sat 4: 176 + 1 - 5 + 8 = 180; 7: 179 + 0 + 1 + 7 =
187; 12: 131 - 1 + 2 + 5 = 137; 14: 196 - 1 - 1 + 7 = 201; 17: 190 - 1 + 2 + 6 =
197. Sun 4: 183, 7: 189, 12: 131, 14: 205, 17: 196. The wind term is 0.9 % per mph into, 0.6 % per mph behind.

**The ladder and the close mark.** `par3_ladder.json` has a step every 2 yds; the page took the nearest step, so a
number 1 yd from a change of club could show that step's 0.10 margin. Now (template, `page_text.simple` pages only)
the margin is interpolated between the two steps and the change-over sits where it crosses zero; "close" is shown
under 0.03. 17 Back is NOT a coin flip on the page's number: the 0.018 in `par3_targets.json` is the solve at the
map's 193; the page plays the card's 195, which is 3.4 yds above the 6-iron / 5-iron change-over (5-iron by 0.10).
The fragile ones are the holes where card and map differ. New pill, shown when the other club takes over within 3
yds of real distance: "182 or more to the middle of the green today: 6-iron" (Back 4, Sat), "178 or less ...:
7-iron" (Back 4, Sun: the map's 176 is under it), so the laser on the tee settles it.

Change-overs of the ladder (plays-like number): GW | PW 134, 9 | 8 158, 8 | 7 169-170, 7 | 6 181.6, 6 | 5 194-195,
5 | 4 207.7: each 1-4 yds above the midpoint of the two stock carries, growing with the club (longer irons release
more), so the ladder is consistent with the bag 100 / 113 / 126 / 138 / 150 / 162 / 174 / 185 / 198 / 210.

**If a named iron were 4 yds off** (log only; a 4-yd error moves that club's two change-overs by about 2): the picks
within 2 yds of a change-over on the forecast are Back 4 Sat (7-iron, 1.5 below the 6-iron: 6-iron if the 7- or
6-iron is 4 shorter than assumed), Back 4 Sun (6-iron, 0.7-1.7 above: 7-iron if either is 4 longer), Back 12 Sun from
a 10 start (GW, 1.6 below the PW), Back 14 Sun from a 10 start (5-iron, 0.9 below the 4-iron), Middle 12 Sat (SW,
0.6-0.9 below the GW), Middle 4 Sun (9-iron, 0.4-1.3 below the 8-iron), Middle 7 Sun (8-iron, 1.5 below the 7-iron).
Every other par-3 pick is 2.3 yds or more from a change-over.

### R2-4. Hole 3's green in the Whole hole picture (second checkpoint, photo only)

Cause: a local build has no fetched display folder, so the page cropped the 920 x 2000 hole render (559 yds above the
tee) and 3's green (630 yds, 53 yds right) was off the top. `display_imagery.fallback_dir` (new; `v2_course.display_dir`)
points a build without a fetched folder at the committed package imagery (NAIP 2023 0.30 m, the photo the page
already shows): every page photo is then rendered directly at page size (the `direct` path the Actions build used),
and the crop box is free to go above the render. 3 shows its green from Back and Middle. The wind badge moves to the
top left corner on tee shots whose green is 25+ yds right of the line (2, 3, 11: it sat on 3's green). qa.json of the
five sets is identical to the first checkpoint, every field. Page file 11.9 -> 8.9 MB.

### R2-3. Tee positions (photo + lidar pads): no coordinate moved; pills rewritten (third checkpoint)

**18.** Pads on the 2023 photo and as flat raised rectangles in the 2020 lidar ground, in yds along the line from the
mapped Back point: A -10..+2, B 14..33, C 44..68, forward pad 152..164. Behind A is the cart path and brush: no pad.
The mapped points are Tips / Champions -11, Back 0, Middle 42, Forward 145. Writing each set's position as
(533 - card + o), o = how much longer the card's line is than the map's tee - corner - green line: Tips -17 + o,
Champions -12 + o, Back 6 + o, Middle 39 + o, Forward 142 + o. All five are on a pad only for o = 10..14, which puts
**Back at +16..+20 (pad B), Middle at +49..+53 (pad C)**, Tips and Champions on pad A. Back on pad A would need the
Tips 4+ yds behind pad A, in the path. So F2's reading stands (my confidence 0.85): the Back markers are one pad
forward. Effect on the tee shot, from the stored grids: Driver either way (0.13 over the 2-wood), aim 14.5 R at the
mapped spot, 12 R from the grid 20 yds forward. Under the freeze rule (a club change or 3 yds of aim) the coordinate
stays; the pill now says "probably on the next pad forward, about 17 yds ahead ... same club and line, every
yardage 17 shorter", and Middle 18 has its own (8 yds). Moving the tee (holes_truth.py TEE_FIX, re-solve of 18 for
both bases and the offset grids) is the next step if he confirms on site.

**Middle 7.** One 57-yd strip tee. The mapped Middle point is 20.6 yds ahead of the Back point; the card says 20.
The card is 4-5 yds longer than the map for ALL five sets on 7 (and 3-5 on 4), so the Middle point is not the odd one
out; F1's 159 would fit the card for Middle only. Left as is; the page already shows card 160 / map 155 and, new in
this round, at which laser distance the 7-iron takes over ("163 or more to the middle of the green today").

### R2-5. The two failing Eagle Knoll tests: both fail since Nov 6, neither from the Nov 12-13 engine edit

Checked on a sparse worktree (full checkout does not fit on this disk), `git bisect`:

* `test_eagle_knoll_cloud_is_wider_than_long`: passes at 1d173fa34 (Nov 5), first fails at 8731bf7eb (Nov 6, "Eagle
  Knoll tee shots: lidar flight trees, green putting on 14, hole 9 phantom tree removed"): with the phantom tree
  gone, hole 9's Driver pattern is 27.7 short / 27.5 long and the test wants short > long + 3. Same numbers at
  233afd672 (before the strategy pass) and now.
* `test_eagle_knoll_nov6_calm_book`: passes at a78e0dc0e~1, fails from a78e0dc0e (Nov 6 21:59, Actions run
  42260496093 rewrote the stored decisions without the hand re-solve's `replaced` flag). It only reads stored JSON.

Nothing in tonight's engine touches either. Eagle Knoll's data and page are untouched; the tests are left failing
(fixing them means editing Eagle Knoll's stored records or the tests' expectations: the manager's call).

### R2-6. Reviewer items skipped last night, each tested in memory on Back and Middle (64 draws)

| item | test | Back | Middle | verdict |
|---|---|---|---|---|
| A 1b: OB right of the road on 1 (x 57..110) | add it | Driver 8.5 L 0.050 -> identical, 0.0 % of drives | identical | no effect: not applied |
| C 15-A: right long-grass edge 3 yds closer on 15 | whole edge moved 3 yds in | Driver 14 R -> 12.5 R, 0.103 -> 0.102 | 7 R -> 6.5 R | evidence does not support it at the landing distance: the cart path's outer edge measured on the photo (brightness profile) is at x 72.9 / 63.0 / 52.4 / 41.2 at 232 / 260 / 290 / 320, the mapped edge 73 / 63 / 53 / 43; only at 305 is the map 4 yds generous. Not applied |
| B P3: tan grass by the square on 8 | add it | Driver 45 L -> 46 L, 0.047 = 0.047 | 4-wood 34.5 L, 0.059 -> 0.057 | no effect: not applied |
| C 18-B: cart-path crest stored as a channel left of 18 | remove it | Driver 14.5 R, 0.127 -> 0.125 (noise) | not in the Middle corridor | no effect, not drawn on the page: left |
| B P4: 12's green edge | | | | already in the par-3 solve (`opt/par3_features.json`: outline re-traced, left edge 2 yds further left) |

### R2-7. Text a golfer would misread (third checkpoint)

* The "Why" sentences carried yards-in numbers from the calm book's average over all swings: 3-11 yds above the
  table's "To green" on the same screen on Saturday (1: 92 against 91; 2: 133 / 122; 9: 108 / 100; 11: 128 / 118;
  15: 144 / 138) and 15 above on Sunday's 1 (92 / 77). Rewritten as differences between clubs, which hold in any
  wind ("20 yds closer than the 2-wood").
* 10 on Sunday (4-wood outright): the page dropped the "Why" sentence and showed "Calm-day pick: 2-wood" and a
  sentence about the two models. Now the Why line stays and the pill / models sentence are not shown when the club on
  the page is the level-rule club (`prefer_on_tie`).

## Night of Nov 12-13: strategy pass (strategy lead; running log, newest state first)

**State.** Map, config and engine option below are committed. Back + Middle re-solved in full with the local fast
solver (`course_data/courses/fastsolve/run.py solve`, 128 prior draws, 145 s for both), outputs copied into
`truth/v2/` and `truth_middle/v2/`; par-3 boxes and ladder re-solved for Back and Middle; page built locally
(`v2_course.py page --slug gateway_national --which truth`, 48 s; photos = package NAIP 2023, sharper than the
published v6 build, checked side by side). The manager publishes.

### What changed tonight

1. **The golfer's rule: standing tall native is penalty area** ("no finding it, too thick and tall").
   `config.engine.native_penalty_area: "relief"`; `v2_course.activate` relabels every `native` zone as `water` for
   the engine (Gateway only: default off): the ball is gone from the first yard in, one stroke + a shot from rough
   at the point where it crossed the edge. Before: lost with probability 25 % at the edge rising to 65 % (stroke and
   distance), punch-out otherwise. `V2_NATIVE_PENALTY=off|relief|stroke_and_distance` overrides for A/B runs.
   Effect on Back (card-only solve, before any map edit): no club change and no aim move over 1.5 yds; the old model
   was already about as expensive. Stroke-and-distance variant (if a strip is unstaked): 11 Back becomes a
   Driver / 4-wood tie (0.004), 9 Driver 15 R by 0.018, nothing else moves. Par 3s: native row = 1 + rough at the
   same distance (`opt/par3_target.py`; `P3_NATIVE=found` restores the old found-ball row).
2. **Hole 10** (second_pass/HOLE10.md sections 1-7): ditch at its true width (hole-10 agent), the band between the
   ditch and the right fairway as penalty area (the golfer's first drawing; lidar / NDVI read it as mown: kept as the
   low-regret map), tall grass closed up behind the left greenside bunkers (lidar agrees). Go at the green still
   wins by 0.29 calm (0.20 with a 15 % wider pattern on frozen ground); **break-even is about 40 % of tee balls in
   the penalty area, he is at 16-20 %**. Aim moves to the left half of the green (26 L calm); the two woods are
   level, the page shows the 4-wood when it is within 0.03 (`page_text.prefer_on_tie`).
3. **Ditch / creek sweep, all 18 holes** (NAIP 2023 RGB + CIR, Dec 2020 lidar ground, the engine's lie raster):
   the mapped ditches on 9 (left, 300-395), 13 (crossing 290-410) and 3 (left, 380-540) sit on the lidar trench and
   are within 0-2 yds of its width; none is overpainted by another zone; no unmapped narrow feature under any tee
   shot. Only 10's strip was at half width. Every water zone widened by 1 / 2 yds a side: 9 and 3 unchanged, 13
   Driver 2 R -> 2.5 / 4 R.
4. **Reviewers' map edits** (second_pass/REVIEW_A-D.md), each looked at on a render (RGB / CIR / lidar relief / lie
   raster) and re-solved:

| hole | change | evidence | Back before -> after | Middle before -> after |
|---|---|---|---|---|
| 1 | right fescue edge at x +28.5..+30.5 from 268 to 345, out to the road (was +32..+35 to +52) | REVIEW_A v2 1a, NAIP 2023 | Driver 8 L 0.051 -> 8.5 L 0.050 | Driver 5 L 0.030 -> 6.5 L 0.027 |
| 3 | tree row before the yard 345-413 | REVIEW_A 3a | Driver 5.5 L -> 6 L, 0.060 | Driver 4 L -> 4.5 L |
| 10 | ditch width, band right of it, tall grass behind the left bunkers | HOLE10.md | 2-wood 17.5 L 0.053 -> 2-wood 26 L 0.012 over 4-wood (page: 4-wood) | 4-wood 16 L 0.215 -> 23 L 0.229 |
| 11 | left long grass 300-385 (6-19 yds closer, was cut off at 345) | REVIEW_B P1 (photo, CIR, F1 lidar) | Driver 17.5 R 0.027 -> 16 R 0.024 over 4-wood | Driver 18 R 0.010 -> 18.5 R 0.004: a tie with the 4-wood |
| 13 | ditch bank to bank (8 yds; OSM strip 4-5) | REVIEW_C 13-A | Driver 2 R 0.110 -> 3 R 0.102 | Driver 8.5 R 0.107 -> 11 R 0.090 |
| 18 | left fescue fairway-side edge 260-395 | REVIEW_C 18-A | Driver 14 R -> 14.5 R, 0.128 | Driver 8 R -> 9.5 R |

   Not applied: A 2a (withdrawn by the reviewer), A 1b (OB right of the road on 1: under 0.1 % of drives), B P3
   (8, optional), B P4 (12 green edge, optional), C 18-B (the "water" way on 18's cart-path crest is an auto-package
   zone outside the corridor, 70 yds left of every oval, not visible on the page), C 15-A (edge 3 yds closer moves
   the aim 1 yd), D's second-shot polygons (6-A pond behind 6 green, 6-B right field, 15-C, 3-D, 1-E: none is inside
   a tee-shot oval, the engine values the second shot from lie and distance only, hazards are not drawn: no effect
   on any number on the page; they belong in the next map revision). Par-3 items A 4a and B P2 were already in
   `opt/par3_features.json` (the par-3 solve's surrounds).
5. **Robustness to the native edges (now that they cost a stroke): every native edge 3 yds closer.** Back: no club
   change, no aim move of 3 yds or more (largest 1.5); 11 Driver falls to 0.005 over the 4-wood; 10 2-wood 0.007
   over the 4-wood. Middle: 8 4-wood aim 34.5 L -> 31 L; **11 flips to the 4-wood (10.5 R) by 0.011**; rest hold.

### Back book after the pass (128 draws; calm, forecast temperature per hole; aim + = right)

| hole | club | calm aim | margin over | in penalty | the reason, in one sentence |
|---|---|---|---|---|---|
| 1 | Driver | 8.5 L | 0.050, 2-wood | 3.0 % | 75 % fairway and 92 in; the 2-wood finds 3 points more fairway but leaves 20 yds more |
| 2 | Driver | 9.5 R | 0.062, 2-wood | 4.2 % | same 76 % fairway as the 2-wood, 19 yds closer |
| 3 | Driver | 6 L | 0.060, 2-wood | 2.6 % | par 5, nothing gained by laying back; left-centre keeps the yard side out of play |
| 5 | Driver | 4.5 R | 0.091, 2-wood | 2.1 % | 452 yds: 170 in against 189 |
| 6 | Driver | 5.5 R | 0.114, 2-wood | 3.0 % | 79 % fairway into the widest part |
| 8 | Driver | 44.5 L | 0.046, 2-wood | 0 % | down the left it leaves 111 with 66 % fairway; 2-wood leaves 130 |
| 9 | Driver | 12.5 R | 0.024, 2-wood (close) | 2.7 % | 108 in but 51 % fairway; 2-wood / 4-wood trade 17-26 yds for 10-14 points of fairway |
| 10 | 2-wood (page: 4-wood, level) | 26 L | 0.012, 4-wood | 19 % (4-wood 16 %) | 5 in 6 finish on or around the green; the lay-up costs 0.25 more |
| 11 | Driver | 16 R | 0.024, 4-wood (close) | 6.0 % | 128 in; the 4-wood is straighter (71 % fairway against 58 %) but leaves 153 |
| 13 | Driver | 3 R | 0.102, 2-wood | 2.2 % | par 5, 70 % fairway, the ditch needs 310+ down the left |
| 15 | Driver | 13.5 R | 0.103, 2-wood | 1.2 % | carries the bunkers at 222-250 that take 7 % of the shorter woods |
| 16 | 4-wood | 5.5 R | 0.086, 2-wood | 2.2 % | stops at the mouth of the 25-yd neck (77 % fairway, 93 in); Driver reaches the mound / pond half the time |
| 18 | Driver | 14.5 R | 0.128, 2-wood | 0.7 % | par 5, 72 % fairway |

Middle: 1 Driver 6.5 L (0.027 over 4-wood), 2 Driver 11 R (0.029), 3 Driver 4.5 L, 5 Driver 0, 6 Driver 7.5 R,
8 4-wood 33.5 L (0.055), 9 4-wood 11 R (0.036), 10 4-wood 23 L (0.229 over the long-iron lay-up), 11 Driver 18.5 R
(0.004 over 4-wood: a tie), 13 Driver 11 R, 15 Driver 7 R (0.047), 16 long iron 7 R, 18 Driver 9.5 R.
10 from The Tips / Champions (315-317, grid +40): 4-wood to the right fairway, aim 9-11 R, 0.03-0.04 over the 2-wood.

### Page changes (template, Gateway via `page_text.simple` / new config keys)

* `page_text.why`: one sentence per Back tee shot (the table above, without hazard words), first line of the note.
* `page_text.prefer_on_tie` (10): show the 4-wood when it is within 0.03 of the best club, with a pill.
* `page_text.set_notes` (10, The Tips / Champions: "Green is out of reach from here: 4-wood at the right fairway,
  leaves about 65"); `page_text.par3_notes` (4: "pin-high left"); the base-tee condition pills no longer show on
  moved tees; 10's frozen-ground pill removed (the 4-wood is shown anyway).
* Hole 10 was also attacked by an independent red team (second_pass/HOLE10_REDTEAM.md: flip table): the go survives
  at Back and Middle (+0.30 engine, +0.19 at the most hostile mix; the woods' sideways spread must reach x2.3 to
  flip Back, x1.6-1.9 Middle); from The Tips / Champions the pick is the position 4-wood; Sunday's helping wind
  makes it the 4-wood by 0.08-0.16 (30-32 L).
* "the ball finishes about N yds left **of the dot**" (was read as left of the tee line).
* The note no longer prints "about N yds in" (the average over all swings, 5-9 yds longer than the table's
  "To green" from the finish spot: flagged by three reviewers). One number: the table's.
* Elevation line: under 1.5 yds of carry change it says "no change in carry" (was "carries -1 yds" / "-0 yds").
* Par-3 headline: "5-iron (198 carry)" when the club is within 3.5 yds of the number; otherwise "SW (113) is the
  better miss than GW (126)"; "close" when the ladder margin is under 0.03 (17).

### Second checkpoint (after v7 was published from 5ed8b2279)

* **Adversarial pass on the close calls** (central world, 16,000 swings; pattern x1.15 / x0.85, roll x1.5 frozen, x0.6
  soft): Back 1, 8, 13, 16 hold in every case (16 4-wood 0.039-0.095). **Back 9**: Driver 0.031, 0.017 with the wider
  pattern, 0.004 on frozen ground, 2-wood by 0.001 with both: pill on Back 9 ("Frozen or very firm ground: the
  2-wood is just as good, aimed 3 yds further left"). **Back 11**: Driver 0.026, 4-wood by 0.002 with the wider
  pattern, Driver 0.017 frozen. **Middle 11**: Driver 0.005 = a tie; 4-wood on frozen ground, with the wider
  pattern and with the long-grass edges 3 yds closer: `prefer_on_tie` 11 = 4-wood within 0.015 (fires from Middle
  and from The Tips / Champions, where the +20 grid has the Driver by 0.011-0.013 on Sat and Sun; it does NOT fire
  from Back on Sat or Sun: Driver by 0.026 / 0.027; over the whole Back grid it fires in 9-15 of 61 wind cells per
  temperature). Middle 1 Driver 0.023 (4-wood by 0.008 with the wider pattern), Middle 2 0.031, 8 4-wood 0.036,
  9 4-wood 0.041, 15 Driver 0.046: unchanged, badged as close calls where under 0.045.
* **Reviewer D's ground near the greens mapped** (trace.py, end): 6-A pond behind / back-left of 6 green (water),
  6-B the unmown field right of 6 from 350 (native), 15-C behind 15 green, 3-D right of / behind 3 green, 1-E right
  of / behind 1 green (lidar 0.08-0.10 m, 45-52 % over 0.10 m; NDVI 0.48-0.71). Holes 1, 3, 6, 15 re-solved for
  every offset, Back and Middle: every pick and aim identical, margins within 0.001.
* Page: a tee below the picture is labelled "below the picture" (the yards shown were to the picture's edge, not
  the tee's distance back).

### Open

* Frames (third checkpoint, photo only): `display_imagery.include_green_yds` 25: the Whole hole crop reaches the
  green + 25 yds (was 400 yds out, 75 either side). 8's green is in the picture; 2, 5, 6, 11, 13, 15, 18 show their
  greens; 3 (630 yds) reaches the top of the 920 x 2000 render (559 yds), its green is still off the top (needs a
  taller render = a display rebuild). Middle 3 and 8 carry their own photo (their view no longer fits inside the
  Back photo). Every word and number on all five sets is identical to the second checkpoint (qa.json compared).
* OB replay value on 3 / 10 (MODEL.md item 5), 18 Back tee note, Middle 7 tee: unchanged from the HANDOFF below.
* Forecast refresh Sat 00:30 UTC: now simply re-run `v2_course.py page` after the weather fetch (REFRESH_LOCAL.md).

## HANDOFF: state at the stop, Nov 13 ~04:30 UTC (integrator)

Work stopped on the golfer's instruction. Nothing of mine is uncommitted; no local job is running. Details of the
second pass are in section 5 at the end of this file; AUDIT.md's last section has the status of the 13 findings.

### 1. What rev 7 is solving (Actions run 43358518302, nccga-v2, started 03:22Z, head 5ef2a228c)

Back rev 7 + Middle rev 6, every hole, every offset, 256 prior draws, card-tee grids refined on 16,000 swings.

* **Map** (`course_data/truth/gateway_national/trace.py` + `features_applied.json` -> `hand_zones_ll.json` ->
  `truth/package.json` -> `truth/course.py`, `truth_middle/course.py`): the Nov 9 map plus the edits of table 5c and
  the three F1 edits added after it was written: **2** (left block beyond the pond and the unmown ground right of the
  cart path from the lidar: Driver +14.5 -> +9), **3** (right "fescue strip" x +18..+32 is a bare track: removed;
  Driver -9 -> -5.5), **5** (strip between rough and cart path is mown, long grass from the lidar line 64 -> 41 R
  at 200-300; Driver 0 -> +3.5). Lidar polygons only on 2, 5, 10, 16; 16's mound priced as "sand".
* **Config** `engine`: 8-iron, green putting, aim_limit 60, `checked_extra_ll` (hole 8), `physics` (temp_k 0.00135,
  drift 1.5 yds / mph, per-club wind multipliers). Table "am" (golfer's decision, Nov 13).
* **Forecast** for the book temperatures: fetched Nov 13 02:44Z (Sat 35 F at 9:00), 9:00 start on hole 1.
* **The committed tree matches it.** `git diff 5ef2a228c HEAD` on the map, the course modules, the engine and
  `config.engine` is empty. The commits after it touch only the par-3 boxes (ca4480af1) and page text
  (c3b289149: `page_text.close_margin`, template).

### 2. Pending items

| item | status |
|---|---|
| 8: trees inside the dogleg (F1: canopy at x 31 / 27 / 17 / 11 / 7 / 2 / -4 / -13 at 270-340) | tested in memory, **not applied**: Driver -44.5 by 0.057 with and without (identical to 3 decimals: the Driver finishes 285 at x -48 +/- 36, the crowns start at +31) |
| 8: unmown square as native vs rough | tested: identical (0.057). The Driver's margin does not depend on it from Back. From Middle it does (the Driver reaches it): Middle 8 is 4-wood -35.5 |
| 10: aim | **not done.** My single-seed central solve says -20.5; the statistics review's 40,000-swing search says -17.25 (six swing sets -17 to -19). The page takes the aim from the 256-draw book, which averages its own swings: read it after rev 7 lands. If it is outside -17..-19, the cost is 0.007 strokes |
| OB replay value on 3 / 10 | **not done** (not trivial; 3's margin 0.051 -> 0.044, aim unchanged) |
| 18 tee note | done (`page_text.condition_notes["18"]["Back"]`, a pill on Back 18). Not yet seen on a built page |
| par-3 boxes and ladder (ca4480af1) | committed for Back and Middle (`par3_targets.json`, `par3_ladder.json`); the page reads them at build. The boxes moved 1-2 yds deeper on every hole; a control run (7, no surround edits) gives the same shift, so it comes from the second-pass physics / forecast, not from the surrounds. Lateral moves from the surrounds: 12 1 yd left, 14 1.5 right, 17 1 right. The Tips / Champions / Forward keep the Nov 9 boxes. Not yet seen on a built page |
| close-call badges 9 / 11 | done (`close_margin` 0.045). Not yet seen on a built page |
| "N% sure" / "what-if" wording | removed in the template (`page_text.simple`). Checked on a local test build before the last edit; not after |
| frozen-ground line on 10 | done (pill on 10, Back and Middle). Seen on a local test build |
| 8's green out of frame | **not done** |
| F1's Middle 7 tee (159 not 155) and F2's 18 tees | not applied (note on 18 only) |

### 3. Steps after rev 7's merge commit lands

1. **Did it land?** `git log origin/<branch> --grep 43358518302`: one commit "NCCGA courses: v2 decisions + wind
   grids + wind page (GitHub Actions run 43358518302)". The superseded runs (rev 4 = run 43354322476, rev 5, rev 6)
   each commit `truth/course.py` with their own timestamp line, which later commits also changed, so their
   `git pull --rebase` conflicts and their Commit step fails after 5 tries. That is expected. If rev 7's own Commit
   step fails, or a commit with another run id appears AFTER rev 7's, bump `rev` in both
   `course_data/requests/nccga_v2_gateway_national*.json` (no other change) and wait ~1 h 45.
2. **The page the merge job built is NOT the final page**: it was built at 5ef2a228c, before the par-3 boxes and the
   last template commit. Rebuild: bump `rev` in `course_data/requests/display_gateway_national.json` (keep
   `"year": 2023`), ~5 min.
3. **QA**: `node course_data/courses/qa_page.js course_data/courses/gateway_national/wind_page/index.html <out> "<set>"`
   for The Tips, Champions, Back, Middle, Forward (18 holes, 0 problems each); look at the phone screenshots of every
   Back hole; text scan for hazard words (none expected: water, pond, creek, bunker, sand, tree, OB, fescue, prairie,
   native, long grass) and for "what-if" / "% sure" (none expected).
4. **Check the Back book against this table** (central world, 16,000 swings, final map; the 256-draw book should be
   within ~2 yds and ~0.01 strokes; aim + = right of the tee line):

| hole | club | calm aim | margin over | badge expected |
|---|---|---|---|---|
| 1 | Driver | 8.5 L | 0.054, 2-wood | none |
| 2 | Driver | 9 R | 0.062, 2-wood | none |
| 3 | Driver | 5.5 L | 0.059, 2-wood | none |
| 5 | Driver | 3.5 R | 0.094, 2-wood | none |
| 6 | Driver | 6 R | 0.118, 2-wood | none |
| 8 | Driver | 44.5 L | 0.057, 2-wood | none |
| 9 | Driver | 13 R | 0.025, 2-wood (4-wood 0.039) | close call |
| 10 | 2-wood | 17-21 L (see item above) | 0.060, 4-wood | frozen-ground pill; at 35 F or into the wind the grid may show another club |
| 11 | Driver | 17.5 R | 0.031, 4-wood | close call |
| 13 | Driver | 1 R | 0.122, 2-wood | none |
| 15 | Driver | 14.5 R | 0.109, 2-wood | none |
| 16 | 4-wood | 6.5 R | 0.108, 2-wood (long iron 0.111) | none |
| 18 | Driver | 14.5 R | 0.132, 2-wood | tee-note pill |

   Par 3s on Saturday at the 9:00 default should read about 178 (4), 183 (7), 136 (12), 198 (14), 197 (17), each with
   a crosswind line of 3-6 yds. Middle: 8 4-wood 35.5 L, 9 4-wood 11 R, 10 4-wood 16 L, 16 long iron 7 R, the rest
   Driver.

### 4. The forecast refresh (Sat 00:30 UTC)

Do: bump `rev` in `course_data/requests/weather_gateway_national.json`, wait for the "weather-course" commit, then
bump `rev` in `display_gateway_national.json` (year 2023), QA as above, publish. It rebuilds the page's wind picks and
par-3 numbers on the new forecast. Do NOT touch the `nccga_v2_*` requests, the map, config `engine` or the par-3
files: the calm book keeps the Nov 13 02:44Z temperatures (within a few F), and a full re-solve does not fit.


For Will (KU club golf), NCCGA Regional 3, Gateway National Golf Links (Madison IL), Sat-Sun Nov 14-15 2026, Back
tees (6,623). Same process as Eagle Knoll (`course_data/courses/eagle_knoll/OPTIMIZE.md`, Nov 3-8), which went well.
Scripts: `opt/` (copied from Eagle Knoll's `opt/` and made course-generic: `SLUG` env, default gateway_national).

## 1. Page display (Nov 9)

Golfer feedback from Eagle Knoll: the first photos were blurry (par 3s worst); no hazard outlines or hazard words on
the page; the current club above the hole number (the shared template already does that).

* **Photos:** config `display_imagery` = Eagle Knoll's (USGS NAIP Plus at 0.3 m, rendered directly at page size with
  Lanczos, 900 px, unsharp mask, par 3s show a 150-yd view, alt-base photo sharing), `fallback_year` 2023 (the year
  the truth map was checked on; the IL 2023 NAIP item is itself 0.30 m: `il_m_3809023_se_15_030_20230819`).
  Rebuilt through `display_imagery.yml` (request `course_data/requests/display_gateway_national.json` rev 1, run
  42647177803): NAIP Plus fetched (6,677 x 5,457 px at 0.3 m, 20 tiles, no fallback), 18 photos rendered directly.
* **Superseded the same day: the page photo is now NAIP 2023 (config `display_imagery.year` 2023).** Putting the
  NAIP Plus photo beside the 0.30 m NAIP 2023 photo of 14 (the package imagery, rendered the same way) shows NAIP Plus
  serves an *older, shadowed* image at Gateway: a different bunker left of the green, different green and collar
  shapes, long tree shadows over the green (the reason the 14 outline looked as if it ran into the trees). The truth
  map was traced on NAIP 2023, and on it the 14 outline sits on the green (RGB and CIR). NAIP 2023 is also sharper
  (page-photo Laplacian 1.60-2.23 against 1.25-1.59 for NAIP Plus, every hole). The nccga-v2 merge fetches it
  (Planetary Computer, 0.3 m).
* **Sharpness check** (mean absolute Laplacian of the page photos, the same measure at the same 900-px scale):
  Gateway par 3s 1.25-1.55, tee shots 1.29-1.59; Eagle Knoll's final page (accepted by the golfer) par 3s 1.40-1.53,
  tee shots 1.24-1.84. The same 0.3 m source detail; nothing sharper exists for this ground. I looked at the par-3
  photos (4, 7, 12, 14, 17) at full size: greens, bunkers, cart paths and the tee boxes are crisp at 2x the source;
  the green outline sits on the green in the photo on 4, 7, 12 and 17; on 14 the top-left of the outline runs into
  the tree shadow (August photo), left to the hole 13-18 map review (section 3).
* **No hazards:** config `page_text.hide_hazards` (no water / OB outlines, hazard words dropped from the notes).
  Gateway has no `hole_notes`, so `map_notes` is empty. qa_page.js text scan on every hole: no water, pond, creek,
  bunker, sand, tree, OB, fescue, prairie or "long grass" word appears (only "2-wood / 4-wood").
* **qa_page.js on the rebuilt page:** The Tips, Champions, Back, Middle, Forward: 18 / 18 holes, 0 problems each.

## 2. Engine options (Nov 9)

Eagle Knoll's engine options (`config.engine`, OPTIMIZE.md sections 7 and 12) checked one by one for Gateway.
Central-world two-stage solve (`opt/solve2.py`: 3,000 swings on -60..+60, then 16,000 fresh common swings on aim
+/-10), Back, every tee shot, three engines side by side (margin over the runner-up, strokes; paired SE 0.001-0.004):

| hole | engine as solved Oct 17 (`V2_ENGINE=0`) | + 8-iron + green putting | + lidar flight trees |
|---|---|---|---|
| 1 | Driver -7.5 (0.050) | same | same (0.050) |
| 2 | Driver +1.5 (0.078) | same | 0.077 |
| 3 | Driver -7.5 (0.062) | same | 0.062 |
| 5 | Driver -1 (0.088) | same | same |
| 6 | Driver +6.5 (0.116) | same | 0.116 |
| 8 | 2-wood -36 (0.021 vs Driver) | same | same |
| 9 | 4-wood 0 (0.016 vs 2-wood) | same | 0.016 |
| **10** | **4-wood -15 (0.004 vs 2-wood: a tie)** | **4-wood -16.5 (0.032 +/- 0.004)** | same |
| 11 | 4-wood +6 (0.068) | same | same |
| 13 | Driver -1 (0.137) | same | same |
| 15 | Driver +14.5 (0.102) | same | same |
| 16 | 4-wood -2 (0.052) | same | same |
| 18 | Driver +15 (0.133) | same | Driver +14.5 (0.133) |

### 2a. Green putting: ON (it matters on the drivable 10th)

The bug Eagle Knoll's panel found (OPTIMIZE.md 12d) is general: the tee-shot raster has no green lie, and the tables
stop at 20 yds, so a tee ball on the green scored as fairway-at-20 yds. On Gateway it decides 10 (271 yds from
Back): with putts on the green every club near the green gets cheaper (4-wood 3.837 -> 3.612, 2-wood 3.841 -> 3.643,
Driver 3.918 -> 3.865), and the 4-wood-vs-2-wood tie becomes 4-wood by 0.032. No other Back tee ball reaches 20 yds
of a hole; the other holes are unchanged.

### 2b. 8-iron: ON (no Back pick uses it)

Added as on Eagle Knoll (162 / 167 carry / total, width 30, depth 16; assumed gapping below the 210 long iron,
**confirm with Will**). It is never within 0.07 of the pick on a Back tee shot (10: 8-iron 4.14 vs 4-wood 3.61).
It is there for the forward sets and the moved tees.

### 2c. Lidar flight-path trees: NOT enabled (they do not matter here, and the canopy file has artefacts)

* **The file:** `vision_any/gateway_national/raw/hag.tif` is the USGS 3DEP Madison Co. IL lidar (2014-03-23..31,
  leaf-off), height above ground, uint8 in **0.25 m units, nodata 255** (file tags and meta.json; the same encoding
  as Eagle Knoll's), 1 m grid, EPSG:32615. 0.5 % nodata (the ponds: no returns from water).
* **Artefacts:** at the pond edges the HAG has interpolation spikes, e.g. hole 2 at 130 yds, 24-29 yds left: a block
  of value 215 (53.8 m) beside the nodata void, ramping 156 / 98 / 59 (39 / 25 / 15 m) toward the shore, class 0 in
  the classification raster. A flight check would read those as 55-m trees. If the option is ever enabled here,
  water must be in `exclude` and crowns over ~35 m dropped.
* **Where the trees are:** crown cells (lidar >= 2.5 m + 3 m growth, OB / water masked) in the descent corridor
  (150-320 yds, +/-45) of each Back tee shot (`opt/canopy_check.py`): none on 1, 2, 5, 11, 13, 15, 16; 10 cells
  on 10 (a single small tree, 6 yds high); 186-1,463 on 3, 6, 8, 9, 18, almost all on the mapped trees (the tree map
  came from this lidar), medians 8-17 yds high (p90 10-23).
* **Does it matter?** With the Eagle Knoll model (k = 0.10 / yd) the picks, aims and margins of every hole change by
  at most 0.0004 strokes and 0.5 yd (table above). Worst case (+6 m growth, k = 0.25 / yd, summer-like): 3, 6, 8, 9,
  18 keep club and aim, margins within 0.0003 (the share of balls stopped in crowns is 0-2 %). Gateway's trees stand
  back from the lines, below the descending ball: a ball that reaches them was already finishing in them.
* The Meta canopy fill Eagle Knoll used (for trees grown in since its lidar) would be wrong here: Gateway's tree map
  was traced FROM this lidar (> 2.5 m), so a mapped tree cell without a 4-m crown is a crown edge or a 2.5-4 m tree,
  not a missing tree, and the fill would put a 10-m default crown on it. Meta's heights also run 1-12 m under the
  lidar on the same cells (its known bias), so they give no growth estimate either.

### 2d. Monte Carlo precision (as Eagle Knoll ended up)

* Calm-day book: 256 prior draws per hole (was 64 here; config `draws` 256 for the page text).
* Card-tee wind grids: `refine_swings` 16,000 (second stage on aim +/-10, `v2_course.refined_solver`; Eagle Knoll
  section 2: median SE of a margin 0.0033 -> 0.0012, unresolved cells 13 -> 1 on Back). Moved-tee offsets stay
  coarse (2,500).
* `nccga_v2.yml` gains `wind_split` (a refined offset's holes dealt over several jobs) and `wind_holes` (wind jobs
  limited to some holes; the merge keeps the stored grid's other holes): 13 refined tee shots x 183 cells x ~25 s on
  4 cores is ~4 h, too close to the 300-min job limit for one job.

### 2e. General fixes from Eagle Knoll that Gateway already gets

* Hole temperature: the stored Gateway book (Oct 17) was decided at the 48 F fallback on every hole (`temp_f` 48.0
  in `v2_decisions.json`): the `hole_temp` default fix (Oct 24) came after it. The re-solve uses the forecast
  temperature per hole.
* Par-3 plays-like temperature term, the tee-frame landing oval, the 5-yd tee slider, close-call badges, moved-tee
  notes: template / page code, already on this page.

## 3. Map fixes from the Nov 9 eye check (EYECHECK_A/B/C_1109.md)

Three reviewers checked holes 1-6, 7-12 and 13-18 on NAIP 2023 0.3 m RGB + CIR, NAIP 2022 and the 2014 lidar. I
applied every must-fix and should-fix edit, plus 13's Tips tee, and checked each one on a render
(`opt/lie_render.py`: the course module's lie map painted over the NAIP 2023 photo in the page frame; `geo_crop`
panels RGB / CIR / 2022 / lidar for the tees and the par 3s).

* **Source of truth:** `truth/gateway_national/trace.py` (EXTRA / LATE bands, each edit commented) and
  `holes_truth.py` (`TEE_FIX`, par-3 `EXTRA_ZONES`). `opt/map_edits.py` puts the edited bands into
  `hand_zones_ll.json` and keeps every other stored zone. A full `corridor.py build` would also re-read the Nov 4
  package OSM, which moved a few fairway vertices on 13, 15 and 18 since Oct 17. It then rebuilds
  `courses/gateway_national/truth/package.json` with `score_auto.truth_package`. Before the edits that call reproduced
  the stored package exactly. Unedited holes 1, 2, 5, 6, 9, 10: zones byte-identical. The reviewers' WGS84 rings
  agree with the converted bands within 5e-8 deg.

| hole | edit | reviewer | checked on the render |
|---|---|---|---|
| 2 | **Back tee moved to its own pad (OSM way 719497753, [-90.1434917, 38.663402])**. The old tee was hole 18's rear pad, 54 yds left, behind an 8-20 m tree block | A (M1) | The new point is on the mown pad between Champions / Tips and Middle, on the line SW. The old point is on 18's pad chain heading SSE (RGB, CIR, lidar) |
| 3 | tree / shrub line right x +32..+44 (recovery), then the industrial yard x +44..+65 (**OB**), 145-345 | A (M2) | The OB band lies on the paved yard and buildings, the recovery band on the shrub line |
| 7 (par 3) | native long-right of the green | B | Tan, mottled in CIR, outside the mown collar |
| 8 | fescue inside the dogleg, from the fairway's right edge to the trees, 225-300 | B | The tan grass right of the fairway bend |
| 11 | left prairie inner edge 5-9 yds off the fairway at 160-280; right fescue from the cart path out (was 15-20 yds inside it) | B | Both bands now off the fairway, the right one beyond the path |
| 13 | right fescue inner edge 20 -> 50 up the hole (was a flat 32); left "fescue strip" removed (mown rough); native / wetland between the left path and the ditch; **The Tips** tee to the back of the Champions pad (card +5; was a lidar pad 50 yds right across the ditch) | C | Yes |
| 14 (par 3) | native strip down the left of the tee-to-green corridor, 0-185 | C | On the dark textured CIR band left of the approach |
| 15 | left prairie inner edge 5-10 yds out before the bunkers; "prairie right" removed (mown rough); fescue beyond the cart path at 230-345 | C | Yes |
| 16 | both right bands replaced by one from the cart path out | C | Yes |
| 18 | left fescue swings out with the cart path from 260 | C | Yes |

Not applied (cosmetic: out of reach, or no effect on any shot): 1 C1 (a vision water triangle 40-80 yds out), 2 C2
(native right beyond the path, 25-35 yds off the fairway), 3 C3 (Forward tee), 4 C4, 5 C5, 7 short-left
recovery -> native (both penal), 8 the native square at 303-337 L, 9 R fescue (kept: uncertain, p 0.46), 10
Tips / Champions walkback, 12 water short-left, 14 R native 25+ yds off line, 18 water basin by the tees, OB
outside 13-18 (nowhere near a corridor).

Manager's questions:
* **14 green outline:** correct. On NAIP 2023 RGB and CIR the OSM outline sits on the putting surface. The "tree
  shadow" was the NAIP Plus photo (section 1).
* **15 Back tee chute:** no nudge. With flight trees off, the engine prices only where the ball finishes. Every
  modelled swing finishes 150+ yds out (heavy mishits carry 65-85 %), so canopy 5-40 yds from the tee cannot
  change anything. On the course the chute is real and open on the 2023 photo.
* **2 Back tee:** the highest-impact fix. From the real pad the Driver aim moves from 1.5 yds right of the line to
  16 right (central world, section 4), and the line and yardages are now the right ones.

Middle as an alt base: the NCCGA's Nov 2025 setup (6,377) mixed Back and Middle boxes, so Middle
(`truth_middle`, config `alt_bases`) is solved from its own pads like Eagle Knoll's Middle. The hand footprint
starts 145 yds from Back. Middle 3 is 64 yds ahead, so its long drives land past the 345-yd footprint end, where
the auto layers apply (OSM, lidar, and the package OB along the yard).

## 4. Re-solve on the final map and engine

### 4a. Central world, Back (`opt/solve2.py`, two-stage, paired SE; forecast temperatures)

Pick and aim (yds, + = right of the page's tee line) and the margin over the runner-up. "Old map" is the same
engine (8-iron, green putting) on the Oct 17 map; "stored" is the page's book before this work (Oct 17, 64 draws,
48 F):

| hole | stored book | old map | **final map** |
|---|---|---|---|
| 1 | Driver -7 | Driver -7.5 (0.050) | Driver -7.5 (0.050 +/- 0.001 vs 2-wood) |
| 2 | Driver +2.5 | Driver +1.5 (0.077) | **Driver +16** (0.070 +/- 0.001 vs 2-wood): the real Back pad |
| 3 | Driver -7.5 | Driver -7.5 (0.062) | Driver -8.5 (0.056 +/- 0.001 vs 2-wood): OB right |
| 5 | Driver -1 | Driver -1 (0.088) | Driver -1 (0.088 +/- 0.001) |
| 6 | Driver +6 | Driver +6.5 (0.116) | Driver +6.5 (0.116 +/- 0.001) |
| 8 | 2-wood -37 | 2-wood -36 (0.021) | 2-wood -39.5 (0.022 +/- 0.001 vs 4-wood): fescue inside the dogleg |
| 9 | 4-wood +0.5 | 4-wood 0 (0.016) | 4-wood 0 (0.016 +/- 0.002 vs 2-wood) |
| 10 | 4-wood -14 (TIE) | 4-wood -16.5 (0.032) | 4-wood -16.5 (0.032 +/- 0.004 vs 2-wood): green putting |
| 11 | 4-wood +6.5 | 4-wood +6 (0.068) | **Driver +19** (0.034 +/- 0.002 vs 2-wood): the right fescue starts beyond the path |
| 13 | Driver +0.5 | Driver -1 (0.137) | Driver +4 (0.138 +/- 0.002) |
| 15 | Driver +14.5 | Driver +14.5 (0.102) | Driver +12.5 (0.096 +/- 0.001) |
| 16 | 4-wood -1.5 | 4-wood -2 (0.052) | 4-wood +4 (0.021 +/- 0.001 vs 2-wood): the right fescue moved out |
| 18 | Driver +15.5 | Driver +15 (0.133) | Driver +13.5 (0.139 +/- 0.001) |

### 4b. Sensitivity (central world, final map; carry +/-5 yds, 95 % width +/-10 %, roll x0.8 / x1.2, 5 mph head / tail / either cross)

| hole | central | flips under | closest variant |
|---|---|---|---|
| 1 | Driver -7.5 (0.050) | none | width +10 %: 0.042 |
| 2 | Driver +16 (0.070) | none | carry +5: 0.062 |
| 3 | Driver -8.5 (0.056) | none | width +10 %: 0.036 vs 4-wood |
| 5 | Driver -1 (0.088) | none | carry +5: 0.075 |
| 6 | Driver +6.5 (0.116) | none | 0.103 |
| 8 | 2-wood -39.5 (0.022) | none, but **ties**: 5 mph into 0.003 vs Driver, 5 mph helping 0.005 vs 4-wood, carry +5 0.009 | aim sits on the +/-40 bound with carry +5, helping or L>R wind; the curve is flat there (-42: +0.003) |
| 9 | 4-wood 0 (0.016) | **width -10 % -> Driver +1.5 (0.004)**; carry -5 and 5 mph into: 4-wood by only 0.002 over Driver | a three-way near tie (4-wood / 2-wood / Driver) |
| 10 | 4-wood -16.5 (0.032) | **carry -5 -> 2-wood (0.065); 5 mph into -> 2-wood (0.105); soft turf (roll x0.8) -> 2-wood by 0.006** | carry +5 or helping: 4-wood by 0.115-0.125 |
| 11 | Driver +19 (0.034) | none | width +10 %: 0.018 vs 4-wood |
| 13 | Driver +4 (0.138) | none | |
| 15 | Driver +12.5 (0.096) | none | |
| 16 | 4-wood +4 (0.021) | none | width -10 %: 0.016 |
| 18 | Driver +13.5 (0.139) | none | |

Crosswinds move the aims 5-7 yds (drift held off); they never change the club. The 10th is a real decision
between reaching the green and not: the 4-wood finishes on the green 35 % of the time (on the green 2.97 strokes
for the hole, fairway 3.22, the creek 8 %, sand 6 %). The 2-wood gets there 32 % of the time and goes through into
the rough 41 %. The Driver goes long (rough 77 %, 3.86). Into the wind or on a cold, soft morning, the 2-wood is the
better club; the page's wind grid makes that call by the hole.

### 4c. The Actions re-solve (run 42650772096, 6a3c37956; 16:03-17:49Z)

Back rev 2 + Middle rev 1. Every job finished in 15-45 min: without flight trees a refined card-tee cell is ~4 s,
against ~25 s on Eagle Knoll. 256 prior draws per hole, the card-tee grids refined on 16,000 swings (3 jobs each),
9 coarse offsets. The merge fetched NAIP 2023 0.3 m for the photos, wired the par-3 targets (`par3_targets.json`,
PAR3.md), and built Middle as a solved alt base. The calm-day book is decided at the forecast temperature per hole
(Sat: 39 F on 1 to 49 F on 18).

**Back, calm-day book** (aim yds right of the line, 0.005 window, margin over the runner +/- paired SE, share of the
256 what-if golfers the pick wins):

| hole | pick | window | runner | margin +/- SE | p | note |
|---|---|---|---|---|---|---|
| 1 | Driver -7 | -10..-4 | 2-wood | 0.049 +/- 0.002 | 0.98 | |
| 2 | Driver +17.5 | +14..+21 | 2-wood | 0.069 +/- 0.002 | 1.00 | from the real pad (was +2.5) |
| 3 | Driver -8.5 | -11..-6 | 4-wood | 0.057 +/- 0.002 | 0.97 | 4-wood if the driver 95 % width is over 89 yds |
| 5 | Driver -1 | -3.5..+1.5 | 2-wood | 0.088 +/- 0.003 | 0.99 | |
| 6 | Driver +6 | +3..+9 | 2-wood | 0.113 +/- 0.002 | 1.00 | |
| 8 | 2-wood -40 | -40..-37.5 | 4-wood | 0.017 +/- 0.002 | 0.71 | **close call**; aim on the +/-40 bound (below) |
| 9 | 4-wood 0 | -2.5..+2.5 | Driver | 0.019 +/- 0.002 | 0.71 | **close call**; Driver if the width is under 62 |
| 10 | 4-wood -16 | -18..-14 | 2-wood | 0.020 +/- 0.006 | 0.62 | **close call**; 2-wood when cold or into the wind (below) |
| 11 | Driver +19 | +16.5..+21.5 | 4-wood | 0.029 +/- 0.002 | 0.84 | **close call** (was 4-wood +6.5 on the old map) |
| 13 | Driver +4.5 | +1..+8 | 2-wood | 0.118 +/- 0.003 | 1.00 | |
| 15 | Driver +12 | +8.5..+15.5 | 2-wood | 0.095 +/- 0.003 | 1.00 | |
| 16 | 4-wood +4 | +1..+7.5 | 2-wood | 0.020 +/- 0.001 | 0.86 | **close call** (was 4-wood -1.5, 0.059) |
| 18 | Driver +13.5 | +10..+17 | 2-wood | 0.132 +/- 0.003 | 1.00 | |

Every margin is more than 3 SE (z 3.1-75). 10 is the least resolved (z 3.1).

**Middle, calm-day book:** 1 Driver -4.5 (0.027 vs 4-wood, p 0.81), 2 Driver +21.5 (0.040), 3 Driver -8 (0.081),
5 Driver -1.5 (0.042), 6 Driver +7.5 (0.037), 8 4-wood -40 (0.098), 9 4-wood +0.5 (0.053), 10 4-wood -13 (0.180),
11 **Driver +19.5, 0.012 +/- 0.002 over 4-wood (p 0.67)**, 13 Driver +10 (0.095), 15 Driver +6.5 (0.041),
16 **Driver +25, 0.017 +/- 0.004 over 4-wood (p 0.59: close; the Driver finishes on the green 7.5 % of the time,
in the pond 12 %)**, 18 Driver +6.5 (0.140).

### 4d. Wind grids: Monte Carlo check and wind / temperature sensitivity

* **Fresh swings** (`opt/grid_se.py`: 169 Back card-tee cells at 50 F, 0 and 10 mph; the top 3 clubs
  re-optimised +/-6 yds on 16,000 new swings). The pick differs in 2 cells: 8 at 10 mph from 120 and 240, 4-wood vs
  2-wood, |margin| <= 0.005, both labelled TIE on the page. 8 cells are within 2 SE on the fresh swings, all on 8, 9
  and 11 at 10 mph; their stored margins are 0.003-0.02.
* **The +/-40 aim bound on 8.** On 8 at 10 mph from 60 / 300 the stored margin is 0.020 and the fresh check gives
  0.002. The check has no bound, and the Driver's best aim on the dogleg is about -50 (calm central curve: Driver
  -50 4.337, 2-wood -40 4.273, 2-wood -42 4.276). So the bound does not change the calm pick (2-wood by 0.06 even
  against an unbounded Driver). In a 10-mph crosswind, Driver at -45..-50 is about level with the 2-wood. On the
  course: 2-wood over the left side is the play; Driver only if you can start it 45-50 left of the line.
* **Calm pick vs every 5-mph cell** (`opt/wind_sens.py`, refined grid):
  * Back at 50 F: every hole keeps its club except 10 (into the wind -> 2-wood by 0.02-0.09) and 8 (5 mph
    helping -> 4-wood by 0.004, a tie).
  * Back at 35 F: 10 calm is already 2-wood (by 0.007), and any helping wind gives 4-wood by 0.05-0.10. 8: into
    the wind -> Driver (0.003).
  * Middle: 16 with a helping wind -> Driver (0.03-0.06); 6, 8 and 9 change in 1-3 of the 12 10-mph directions.
  * Sunday's forecast and Saturday's NNW 8-9 mph are read off these grids by the page, hole by hole.
* **10 is temperature-sensitive.** The Back calm pick is 2-wood at 35 F, 4-wood at 50 F, and the book at the
  hole's 45 F is 4-wood by 0.020. The page interpolates between the grid temperatures, so it shows 2-wood on a cold
  calm morning and 4-wood once it warms up. The Saturday 11:06 forecast cell (45 F, NNW 8, slightly into) shows
  2-wood (screenshot checked).

### 4e. Page (final)

The merge built `wind_page/index.html` from the new grids, the Middle alt base, NAIP 2023 photos and the par-3
targets. qa_page.js on The Tips, Champions, Back, Middle and Forward: 18 / 18 holes each, 0 problems. I looked at the
phone screenshots of every Back par 3 (4, 7, 12, 14, 17: sharp; the box sits on the green, short of centre) and of
the tee shots that changed (2, 10, 11), and at Middle 16. Par-3 club line: each set shows its own club
(`by_set.p3club`). The Tips / Champions 14 and 17 and Forward 12 show only "Plays N" (config `par3_club_hide`).

### 4f. Still uncertain

* Will's dispersion and the 8-iron / short-iron carries are assumed, as on Eagle Knoll. 3, 8, 9 and 11 flip with the
  driver width (89 / 87 / 62 / 83 yds).
* The tee sheet is not posted: the NCCGA's 2025 setup mixed boxes. Middle is solved; The Tips / Champions /
  Forward are the Back line moved.
* Middle 3's long drives land past the hand-checked footprint (auto layers there).
* The map fixes were made on 2023 imagery. Fescue edges are good to +/-3-5 yds (reviewers' estimate).
* The forecast is from Nov 9; the weather workflow refresh (~Nov 12, 13) rebuilds the page but not the book.

## 5. Nov 12-13 second pass (integrator)

One integrator (this section) with four specialists writing proposals only (`second_pass/`: PHYSICS.md, MODEL.md,
FEATURES_1_9.md, FEATURES_10_18.md, WILL_REVIEW.md). Golfer's rules for this pass: his stated carries as given, one
normal shot pattern per club, one club and one aim per hole; only real external conditions vary (forecast wind and
temperature, firm or frozen ground, tee position). No "if you are hitting it well / badly" cases on the page.

### 5a. The audit's 13 findings on the built page

Status per finding: AUDIT.md, last section. In short: 1, 4, 5, 6, 9, 10, 11, 12 fixed; 7 and 8 fixed as designed with
a residual (the par-3 number is still the card's by default; 20 / 40 up on a Back tee shows the card-tee solve with a
pill); 2 right; 3 over-corrected (re-fixed here); 13 mostly.

### 5b. New evidence for the map

* **Sentinel-2 NDVI, Nov 8 + 10 2026 (10 m, cloud-free)**, `second_pass/s2/`: fairway 0.87, mown rough ~0.80, dormant
  prairie / fescue 0.50-0.65. It shows what is dormant warm-season grass today. It cannot tell standing from cut, and
  unmown cool-season grass stays green, so it is used to confirm or reject a mapped band, not to trace one alone.
* **USGS 3DEP lidar point clouds of Dec 2020 and Dec 2023** (F2 / F1): grass height on a 0.5 m grid (mown 0.02-0.04 m,
  standing fescue / prairie 0.10-0.35 m). The direct measure of long grass, late in the season.
* **The summer photo misleads on unirrigated rough:** tan and "textured" in August (NAIP), short and green in
  November. That is how the right side of 9 and the inside of 8's dogleg were mapped as fescue on Nov 9.
* Every applied edit was looked at by me on a render (NAIP 2023 RGB + CIR at 4-9 px / yd, NDVI, lidar height) before
  and after (`opt/lie_render.py`, the engine's own lie raster).

### 5c. Map edits (rule from Fri 03:00Z: apply only if a Back or Middle aim moves >= 3 yds or a club changes)

Aim in yds right (+) / left (-) of the tee line; central world, 16,000 swings (SE 0.001-0.004), Nov 13 forecast
temperatures, second-pass physics. "v5" = the published page's calm book.

| hole | edge, old -> new | evidence | Back pick / aim, v5 -> now |
|---|---|---|---|
| 8 | ground left of the fairway at 240-345 (x -65..-128): "unverified" (priced as half trees) -> rough | outside the +/-65-yd hand corridor; looked at on NAIP + NDVI: mown rough, then the cart path (`engine.checked_extra_ll`) | 2-wood -41 -> **Driver -44.5** (0.057 over 2-wood). This artefact alone was worth 0.05 to the Driver |
| 8 | unmown square inside the bend (299-336, x -88..-48): unmapped -> native | NAIP 2023 tufted block ringed by a mown bank; F1 confirms the position (6-9 yds larger east); standing now: not settled | part of the above (the Driver finishes 285, short of it; from Middle it stops the Driver: Middle 8 4-wood -35.5) |
| 8 | right side at 220-312: native from the fairway edge (two bands) -> native from the lidar brush line (x 47 / 45 / 34 / 28 / 21 / 9 / -7 at 220 / 250 / 260 / 270 / 280 / 290 / 300) | F1: no standing grass in the Dec 2020 lidar, NDVI Nov 2024-26 0.76-0.84; mown collar visible on NAIP | part of the above |
| 9 | right "fescue" band x +30..+45, 140-340 -> removed (rough) | mowing stripes on NAIP 2023; NDVI 0.87 (= fairway); F1: no lidar height out to the trees | 4-wood +3 -> **Driver +13** (0.025 over 2-wood, 0.039 over 4-wood): close call |
| 9 | left inner edge at 250-340: x -24 / -19 / -14 / -16 / -22 -> -34 / -29 / -19 / -22 / -27 / -28 (250 / 265 / 280 / 300 / 320 / 340) | worn line on NAIP; NDVI edge; F1 lidar within 1-4 yds at 270-340 | part of the above |
| 10 | long grass: hand bands (left x < -45, right x > 30-52) -> lidar polygons (left from x -55..-60 beyond the bunkers, a band across 300-315 behind the green, right strip between the two cart paths) | F2, Dec 2020 lidar; checked on the lidar render | 4-wood -16 -> **2-wood -20.5** (0.060 over 4-wood): the aim is the green centre; the club is the colder, shorter ball (5d) |
| 16 | left native inner edge at 235-300: x -30..-34 -> -26 at 235 to -18 at 295 (lidar polygons, whole hole) | F2, Dec 2023 lidar (0.22 m in the block); my NAIP read was -27..-22 | 4-wood -3 -> 4-wood **+6.5** (0.108 over 2-wood, 0.111 over long iron) |
| 16 | mound right at 264-298 (x +6..+43): native (lost-ball) -> a penal lie priced as "sand" | tufted in every summer photo, 0.036 m in the Dec 2020 and Dec 2023 lidar (the block across the fairway reads 0.22 m), stone wall on its fairway face. Deliberate: found but awkward, between rough and native; the engine has no heavy-rough lie | part of the above. As native: aim +4; as plain rough: +7.5, 2-wood only 0.038 behind |

Tested and NOT applied (under the rule): lidar long grass on 11, 13, 15, 18 (aims moved 0.5-2 yds: the Nov 9 hand
bands stay); 18 Back tee 17 yds forward onto pad B (F2, confidence 0.7: Driver aim 14.5 -> 12.5, same club; the hole
may play ~17 shorter than the card from that pad); fairway right edges 2-5 yds narrower on 10 / 15 / 18; 8 fairway
left edge 3-7 yds inside the OSM line at 240-290; tree lines 3-15 yds further from play on 8, 9, 14, 17, 18 (the map
is conservative); OSM greens and bunkers 1.5-3 yds off on 10-18; par-3 surrounds on 12, 14, 17 (no par-3 target
re-solve). My own notes that fell under the rule: 1 right native 5-8 yds further right at 290-340, 2 native right of
the cart path from x +48.

Process errors of this pass, so they are not repeated: (1) `opt/map_edits.py` splices by the OLD trace's zone
counts; run twice on already-edited zones it dropped hole 9's right tree zone (request rev 4 was solved on that).
It is now always applied from the v5 zones. (2) trace.py first read the specialists' working JSON and applied only
"add" edits, which silently deleted 16's mound (rev 5). It now reads a frozen copy
(`truth/gateway_national/features_applied.json`) and raises on any other action.

### 5d. Physics (PHYSICS.md), adopted behind `config.engine.physics` (Gateway only)

| change | old -> new | check | effect this weekend |
|---|---|---|---|
| carry lost per F below 70 | 0.00075 (air only) -> 0.00135 | air 0.00075 (0.39 % of carry per 1 % of density: Titleist altitude rule 0.40) + a ball at air temperature ~0.0004 (about 1 % of ball speed at 45 F) + the 1027-1031 hPa high ~0.0002 | Driver about 4 yds shorter at 45 F; par 3s +2 to +4 yds |
| crosswind drift | 1.14 yds / mph for the driver, 0.8 mid iron -> 1.5 for every full shot | lag formula W (T - x / v0): driver 6.8 s, 250 m, 75 m/s -> 17 yds at 10 mph; 6-iron 6.3 s -> 16 | aims 1-2.5 yds further up wind |
| head / tail multipliers | 1.0-1.3 -> 2-wood 1.2, 4-wood 1.3, long iron 1.5, mid iron 1.65, 8-iron 2.0 | mid iron -9 % into 10 mph (rule of thumb 1 % per mph) | par 3s +/-1 yd |

Golfer's answers (Nov 13): he will rotate balls from a pocket as best he can (gives back ~1.5-2 yds of Driver carry
against a fully cold ball), and his carries were measured in Lawrence KS at ~850-900 ft (Gateway is ~410 ft: costs
~1.5 yds). The two cancel within a yard, so 0.00135 stays.

Not changed: roll. The fairways are dry (0.43 in of rain in three weeks, none since Nov 3) and Saturday starts
frozen (24 F overnight, 35 F at 9:00): the stated totals are a fair centre, firm is the likely side (5e).

Also fixed: from a moved tee (The Tips / Champions / Forward grids) the putting-green polygon stayed in card-tee
yards, so on the drivable 10th the "green" sat 20-60 yds off. Back and Middle were not affected.

### 5e. Frozen or firm ground (roll x1.25 / x1.5), a condition like wind

| hole | normal | x1.25 | x1.5 |
|---|---|---|---|
| 8 | Driver -46 (0.056) | Driver -46.5 (0.042) | Driver -48.5 (0.028) |
| 9 | Driver +15 (0.030) | Driver +15.5 (0.020) | Driver +16 (0.007: a tie with 2-wood) |
| 10 | 2-wood -20.5 (0.060) | 2-wood -20.5 (0.019) | **4-wood -21.5 (0.015)** |
| 16 | 4-wood (0.108) | 4-wood (0.087) | 4-wood (0.057) |

(Run before the last 8 / 9 edge edits; those moved the aims 1.5-2 yds.) The page carries one condition pill, on 10:
"Frozen or very firm ground (drives running 35+ yds): 4-wood, same line".

### 5f. Page

* Par 3s: the number uses the new temperature rule; a crosswind line ("The wind moves the ball about 6 yds right:
  start it that far left of the box", 1.4 yds per mph); the club still follows the live number.
* One aim number per hole, the one at the top; the calm note keeps club, margin and shares. "what-if worlds" ->
  "N% sure". Pattern break-even sentences dropped. The hybrid he does not own sorts last.
* Footer: temperature rule and tee-slider wording corrected.

### 5g. Honest list of what is still uncertain

* Whether the long grass is standing on Nov 14. The lidar is Dec 2020 / Dec 2023, the photo Aug 2023; the Nov 2026
  satellite shows dormancy, not height. 8's square and 16's mound are the two that matter.
* 9 (Driver vs 2-wood vs 4-wood within 0.04) and 10 (2-wood vs 4-wood, decided by 4 yds of carry and the turf) are
  coin flips in strokes. 8's Driver rests on the left side being open rough (F1 confirms).
* Tee positions: 18 Back may be 17 yds forward of the mapped point; par 3 on 4 is 176 from the pad centre (card 180).
* Tee time (9:00 assumed; a frost delay is likely on Saturday) and the tee set.
