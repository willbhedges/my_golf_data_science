**Verdict: NO.** Nothing on the version-27 page (commit 26b40e93d) puts a wrong club in his hand, moves an aim by 3+ yds or a par-3 number by 3+ yds on a card he will use on Saturday (Back, 10:36, hole 1, Drop). Six wording / consistency items below; the first is the only one that could change what he does on a tee.

# Gateway National page, final independent audit (Nov 14 2026, ~02:00-02:45 UTC)

Subject: `course_data/courses/gateway_national/wind_page/index.html` at 26b40e93d (byte-identical to HEAD e7fa3724d;
audited from a frozen copy). Read-only audit; this file is the only thing written.

**Note for the manager:** while this audit ran, another job started changing the working tree (02:15 UTC:
`config.json` approach_pattern deck lat 1.25 -> 1.0 / depth 2.0 -> 2.25, par-3 tee lat 1.1 -> 1.0;
`par3_decade.py` and `par5_second.py` re-solving; template edited). Everything below is version 27 only. A version
28 built from that will change the Second-shot widths (a 220 shot 58 -> about 43 wide), possibly the go / lay-up
margins and the par-3 boxes, and has not been looked at by anyone independent.

## Findings, ranked by consequence

### 1. Hole 3 (and 18): the pill contradicts the table and the "why" sentence (card contradiction; can change the club he pulls)
- Card: Back 3, Saturday and Sunday. Pill: "Laying up regardless: the 2-wood and 4-wood are just as good off the
  tee". Same card: table 2-wood +0.061, 4-wood +0.074; note "Why Driver: a par 5 with nothing gained by laying
  back ... Driver by 0.061 +/- 0.002 over 2-wood".
- On hole 3 the condition is always true: 327 to the middle after the Driver, and the card's own Second-shot block
  and mode say "the green is out of reach". So the pill reads as a flat statement that the woods are as good as
  the Driver, against a table that says they cost 0.06-0.07. Screenshot `satmap/mont_01_03.jpg`; text in `sat.txt`.
- Back 18 carries the same pill next to a table that says 2-wood +0.119. There the condition is real (the page
  recommends going from 219), so it is only a mild contradiction.
- MANAGER_TODO says the pill is on 6, 13, 18; on the page it is on 3 and 18 only (not 6, not 13).
- Not a wrong club: Driver is the headline, the starred row and the drawn line. Cost if he takes the pill at its
  word: at most 0.06.
- Fix: `gateway_national/par5_second.json`, the `"pill"` of holes/3/Back (d0 and d1; and Middle if present): delete
  it, or reword to "If the second is a lay-up anyway, the 2-wood costs about 0.06 here (table)". For 18: "If you
  will lay up anyway: the woods are within about 0.1 of the Driver".

### 2. Second shot mode can headline a club that is not in his bag (misread risk; holes 6, 18, 3)
- Back 6 from the Driver's spot (237 out), Saturday: top bar "230 shot", play "Go: 230 shot", starred row "230 shot
  - not in bag". The club he can hit is two rows down (hard long iron +0.02) or the hollow-star row (lay up, long
  iron, +0.08, leaves 29). Same pattern: Back 18 from the 2-wood's spot and from 240 (230 shot; his 4-wood +0.02 /
  +0.03), Back 3 from 240 (230 shot; long iron +0.13). The static block on the tee card for hole 6 leads with
  "Go: 230 shot (a hybrid, not in your bag)" as well.
- Evidence: `modes/mB.jpg` (hole 6), `modes/modes.json` labels "390 t0 d0 h6 ss D", "h18 ss W", "h3 ss 240".
- The numbers are right and the sentence underneath names his club; it is the big headline that is unusable.
- Fix: in `wind_page_template_course.html`, Second-shot render (the line that sets `topKey` / `topClub` /
  `hPlay` from `sel`, about line 665 of the built page): when the best row is "230 shot", default the selected
  row to the best row he can hit (`bagStar`, or the 220 / 240 in-between row when it is within 0.03), and keep the
  230 row in the table as the comparison.

### 3. Static Second-shot block on the tee card and the Second shot mode give different yardages for the same shot
- Back 3 Saturday: block "Lay up: 4-wood (265 total) ... leaves about 65"; mode "4-wood, 256 total, leaves 72".
- Back 6: block "long iron, leaves about 25 ... 5-iron (202 total), leaves about 35"; mode long iron 210 total
  leaves 29, 5-iron 197 leaves 42.
- Back 18: block "7-iron (178 total), leaves about 45"; mode 7-iron 175, leaves 48.
- Same clubs in both, so no wrong club; leaves differ by 3-9 yds. The block (par5_second.json) and the menu
  (par5_menu.json) are two solves with different roll / targets.
- Fix: build the block's lay-up lines from the menu's rows for the same start (one source), or drop the totals and
  leaves from the block and keep only the club names.

### 4. Fairway percentages disagree inside one note (hole 18: 72 % vs 79 %)
- Back 18: "Why Driver: a par 5 with 72% fairway ... With driver at 48°F: fairway 79%". Back 8: 66 % vs 64 %.
  Back 11: 58 % vs 59 %. Back 13: 70 % vs 71 %.
- The first number is hand-written `why` text (18's predates the tee move of version 13), the second is computed.
- Fix: `config.json` page_text why for Back 18 -> 79 %, Back 8 -> 64 %; or remove the percentage from the why text.

### 5. Small number mismatches a golfer may notice (no effect on club or aim)
- "N wide" in the yellow strip and on the oval is 1-4 yds more than the table's 95 % width for the same club:
  hole 1 74 vs 72, 15 74 vs 70, 13 73 vs 71, 3 71 vs 69, 10 55 vs 54. The strip uses the drawn pattern
  (cloud left + right), the table the grid width. Fix: print the same `wide` number in the table's starred row.
- "Close call" pill quotes the calm book, the table the wind model: hole 8 pill "2-wood +0.040", table +0.061;
  hole 9 pill +0.021, table +0.034; hole 11 +0.025 / +0.027. Fix: use `r.margin` in the pill when `r.bayes`.
- Aim sentence: "finishes about 3 yds left of the dot (wind 2 left)" (hole 1), "8 right (wind 6 right)" (9),
  "3 left (wind 5 left)" (15), "3 right (wind 6 right)" (8): the two numbers differ by 1-3 because the first
  includes the pattern's own offset. Fix: drop the bracket, or say "(wind 6 right, pattern 3 left)".

### 6. Settings panel: the wind dial's caption is the wrong way round
- "The yellow end of the needle points into the wind." The needle is drawn with `rotate(st.from + 180)`: the
  yellow knob sits on the downwind side and the arrowhead points to where the wind comes FROM (Sunday hole 18,
  wind from ENE 57°: arrowhead at NE, knob at SW; `modes/mC.jpg`). The card arrows point where the wind blows TO, so
  the dial reads opposite to the cards. Forecast mode never needs the dial; it only matters if he goes to Custom.
- Fix: template line with `rotate(${st.from + 180})` -> `rotate(${st.from})` and move the arrowhead / knob so the
  arrow points downwind like the cards, or change the caption to "the arrowhead points to where the wind comes from".

### Residual, already known, restated because it touches a par-3 number
- Holes 4 and 7: card 180 to the middle, map 176 (tee-to-green from the package coordinates: 176 and 176). The
  page uses the card. Saturday the club is the same either way (4: plays 178 by card, 174 by map: 7-iron; 7: 189 /
  185: 6-iron). Sunday hole 4 is the case that flips (plays 186: 6-iron; the pill says "177 or less to the middle
  of the green today: 7-iron"), so laser 4 on Sunday.

## Checked and found correct

- **A. All 18 Back cards, Saturday, Drop, at 390 px** (`sat/`, `satmap/mont_*.jpg`, `sat.txt`): headline club = Play
  label = starred row = line / oval drawn on every card; headline aim = solver aim (rounded) = dot; oval width
  measured on hole 1 (73 yds) matches the label; To green = straight line from the finish to the green centre,
  recomputed on 1, 3, 8, 11, 18 (89, 327, 108, 115, 219: all match); par-5 "to the middle" = the tee table's To
  green for Driver and 2-wood on 3, 6, 13, 18.
- **Wind**: head / cross components re-derived for all 18 holes on both days from the package tee / green
  coordinates and the forecast file; every card's wind sentence matches to the rounded mph, every arrow points the
  right way (looked at all 18 Saturday). Clock runs 10:36 am to 2:34 pm in 14-minute steps; 43 °F to 48 °F.
- **Par 3s, Saturday** (recomputed): 4: 177 + 1 - 6 + 6 = 178, 7-iron (174); 7: 182 + 0 + 1 + 6 = 189, 6-iron
  (185); 12: 131 - 1 + 1 + 4 = 135, PW (138), pill "129 or less: GW" agrees with the ladder change-over (133.3
  plays-like); 14: 195 - 1 + 1 + 6 = 201, 5-iron (198); 17: 190 - 1 + 4 + 6 = 199, 5-iron (198). Ladder margins
  0.08-0.10 on all five, no change-over within 3 yds except 12 (1.7 yds, pill shown). Boxes drawn inside the green
  outlines; edge distances sum to 25 x 25, 22 x 28, 27 x 29, 19 x 33, 21 x 31 yds and agree with the card's front /
  back numbers within 3 yds. Targets and margins equal PAR3.md section 9 exactly; trouble-side margins met on all
  five (14 right 8.0 vs 10.4 and 17 left 8.8 vs 10.1 are the documented lesser-of-two-evils).
- **Sunday, 18 Back cards** (`sun.txt`, wind table): same tee clubs as Saturday; 4 becomes 6-iron (plays 186), 12
  GW (plays 132), both with the change-over pill; hole 10 4-wood 25 L (finish point the same 22 L as Saturday's
  15 L: the wind pushes the other way). Tee time 9:00.
- **Hole 10 Lay up mode**, Sat and Sun (`modes/mA.jpg`): filled star on the 4-wood (best), hollow star on the
  8-iron; pill "8-iron leaves about 108 (+0.29)" = table 108 / +0.291 (Sun 106 / +0.29).
- **Second shot mode**, 3 / 6 / 13 / 18 from the Driver's spot, the 2-wood's spot, 240, 260 (Sat): rows in order
  of "vs best"; filled star on row 1, hollow star on the best stock club when row 1 is an in-between shot; top
  sentence agrees with the table in all 16 states; width labels 220 shot 58, 230 shot 62, 240 shot 65-67, 4-wood
  70-72.
- **B. Fast solver re-solve** of Back 1, 9, 10, 11, 13, 16, 18 (`fs/`, default settings, current map): calm book
  same pick on 7 of 7, aims within 0.5 yd (1: -8.0 vs -8.5), margins within 0.002; the Saturday cell interpolated
  as the page does is identical to the page to 0.001 strokes and 0.1 yd on every club. Hole 10 is the post-change
  map: 4-wood 15.0 L Saturday, book 2-wood 20 L, margin 0.024 (page 0.026).
- **C. Data sets**: forecast in the page = `forecast_gateway_national.json` (28 rows, 0 differences, fetched
  00:45:48 UTC); tee hours 10.6 / 9.0. Drop vs Lost ball over 70,455 grid values (Back + Middle, all offsets): Lost
  is never lower by more than 0.011 (41 values beyond 0.004, all sampling noise at the 0.01 level; none in the
  Saturday Back cells, where the minimum difference is -0.001). Hole 10 lay-up grid: no value lower under Lost.
  Lost ball, Back Saturday: 9 Driver 9 R (was 6 R), 10 4-wood 15 L, 11 4-wood 18 R (was Driver); par 3s unchanged;
  tag "Tall grass: lost ball (re-tee)" shown.
- **D. Text**: 543 page states driven (18 cards x 2 days x 2 rule sets, whole-hole and landing views, Lay up,
  Second shot incl. rough, settings; widths 375, 390, 430): none of water, creek, ditch, pond, penalty, native,
  bunker, fescue, hazard, lake; no NaN / undefined / null / Infinity; no element past the card's edge, no clipped
  text, no sideways scroll; no page errors.
- Not looked at as pictures (data only): the Lost ball cards for 9, 10, 11 and the Sunday maps.

## Saturday card, Back tees, 10:36 off hole 1, Drop (as read off the page)

| hole | play | aim or plays-like |
|---|---|---|
| 1 | Driver | aim 7 yds left, 287 total |
| 2 | Driver | aim 15 yds right, 297 total |
| 3 | Driver | aim 1 yd left, 303 total; second: 4-wood lay-up |
| 4 | 7-iron | plays 178 (target 177) |
| 5 | Driver | aim 3 yds left, 293 total |
| 6 | Driver | aim 12 yds right, 294 total; 237 left: go (hard long iron / easy 4-wood) |
| 7 | 6-iron | plays 189 (target 182) |
| 8 | Driver | aim 49 yds left, 287 total (close call with the 2-wood) |
| 9 | Driver | aim 6 yds right, 290 total (close call with the 2-wood) |
| 10 | 4-wood | aim 15 yds left, 264 total (level with the 2-wood) |
| 11 | Driver | aim 23 yds right, 296 total (close call with the 4-wood) |
| 12 | PW | plays 135 (target 131); 129 or less to the middle: GW |
| 13 | Driver | aim 3 yds left, 293 total; 241 left: go with the 4-wood |
| 14 | 5-iron | plays 201 (target 195) |
| 15 | Driver | aim 18 yds right, 295 total |
| 16 | 4-wood | aim 3 yds right, 261 total |
| 17 | 5-iron | plays 199 (target 190) |
| 18 | Driver | aim 10 yds right, 299 total; 219 left: go with the long iron |

Scratch (screenshots, records, solver output):
`/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/audit_final/`
