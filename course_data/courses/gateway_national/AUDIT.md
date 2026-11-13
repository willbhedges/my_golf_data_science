# Gateway National wind page: independent audit (Nov 9 2026)

Audited page: `course_data/courses/gateway_national/wind_page/index.html` as of 879e209dc (built by the Actions
re-solve 6a3c37956). I read the page data (`const D`) and the page code, then checked them against
`truth/v2/v2_decisions.json`, `truth_middle/v2/v2_decisions.json`, `truth/v2/wind_grid.json`, `par3_targets.json`,
the truth course modules, the scorecard caches and the imagery. I edited no code or data.

**Method.**
* **Page.** I drove the page in headless Chromium (Playwright, 400 px, DPR 2). I ran `qa_page.js` on Back and Middle
  (18/18, 0 problems each). I also used my own scripts to read the page text of every hole for Back and Middle,
  Sat and Sun, at the default 9:00 start on hole 1. I evaluated `solveTee` / `solvePar3` inside the page for
  Custom winds, other start holes, other tee times and moved tees.
* **Map.** I rendered the lie zones over the package NAIP 2023 0.3 m RGB, NAIP 2023 CIR (package NIR), NAIP 2022 CIR
  and the 2014 HAG (`vision_any/gateway_national/raw/`) in the tee frame. The renders carry 10-yd ticks and the
  page's Sat / Sun aim and finish points, and I looked at each one. I sampled NAIP 2023 NIR (mean and 3-m texture SD)
  along lateral profiles.
* **Numbers.** I recomputed one par-3 plays-like by hand from the page grid and forecast. I compared the page's
  calm book with `v2_decisions.json` field by field, and one wind cell with `wind_grid.json`.
* **Files.** Screenshots and renders are in
  `/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/gw_audit/`
  (temporary, not in the repo).

**Not verified.**
* No on-site knowledge.
* The tee sheet is not posted.
* nccga.org cannot be reached from here, so the "2024 = Back 6,623 / Nov 2025 = 6,377 combo" claim in the footer has
  no cached source in the repo.
* I did not re-run the engine, so I give no regret numbers of my own.
* Will's iron and wedge carries are assumed (as the record says).

Severity key:
* **CLUB/AIM**: would change the club or the aim Will uses.
* **MISLEADING**: the page says something that is wrong or that hides a caveat.
* **COSMETIC**: wrong, but it changes no decision.

## Findings (ranked)

### 1. Par-3 club line is frozen to the forecast day, while the "Plays" number moves. CLUB/AIM

**Evidence.**
* `p3clubFor` (page code) takes the club from `by_set[set].p3club`, a fixed string such as "Sat: 5-iron; Sun: 6-iron".
  `par3_target.py` solved it once, for the Nov 7 forecast, a 9:00 shotgun on hole 1 and 14 min a hole.
* In **Custom** mode the page always shows the Saturday club (`day = day_labels[0]`), whatever wind or temperature
  is set.
* In page evaluation:

  | Setting | Hole 14 (Back) | Hole 17 | Hole 4 |
  |---|---|---|---|
  | Custom 15 mph into, 45 F | **"5-iron", plays 220** | **"6-iron", plays 210** | |
  | Custom 20 mph into, 38 F | **"5-iron", plays 235** | **"6-iron", plays 220** | |
  | Custom 15 mph helping | "5-iron", plays 182 (a 6- or 7-iron number) | | **"7-iron", plays 187** |

  The assumed carries are 5-iron 198, 6-iron ~185, 7-iron 174.
* The same holds in forecast mode when Will changes the starting hole or the tee time. When the weather workflow
  re-fetches the forecast (OPTIMIZE 4f: "rebuilds the page but not the book"), the number tracks the new forecast
  and the club line stays at the Nov 7 forecast.
* Custom mode is exactly what Will would use when the real wind differs from the forecast. That is when a stale
  club line is most wrong: by 1 to 3 clubs.

**Fix.**
* Pick the par-3 club in the page from the live "Plays" number and the assumed carry table, and show the carry next
  to it ("6-iron, 185 assumed").
* At least hide the club line whenever the source is Custom, or the hour or start hole differs from 9:00 / 1. In
  that case show only "Plays N".

### 2. Hole 16 (Back 354): an unmapped fescue mound right of the fairway at 275-300, exactly where the pick finishes. CLUB/AIM

**Evidence.**
* Render `p16.jpg` (RGB, CIR 2023, CIR 2022) shows a raised, tufted patch, with a white stone edge on its left.
  * It sits at about x +8..+40, 270-300 yds, between the fairway's right edge and the cart path.
  * NIR 178-185 with texture SD 6-7. The mown rough beside it reads NIR 193 / SD 3.7, and the fairway 202 / SD 2.
  * CIR 2023 shows mottled tufts. In CIR 2022 the patch is dark, with a shadowed ridge.
* The Nov 9 edit (EYECHECK_C "replace both right bands") removed the inner band (x 25-38, 140-300), which partly
  covered this patch. It replaced that band with fescue from the cart path out (x ~49-52 at 280-300). The patch is
  now priced as **rough**.
* After that edit the Back aim moved **right**, from -1.5 to +4 (OPTIMIZE 4a: "the right fescue moved out"). The
  4-wood margin over the 2-wood fell from 0.059 to 0.020.
* The page's Saturday 4-wood aims 3 left and finishes about 5 right at 266 yds (pattern 95 % width 55). Its long-right
  quarter reaches the patch. The 2-wood (277 total) and the Driver go deeper into it.
* Middle 16's book Driver is aimed **25 right**. On Saturday it finishes about (285, +27) in the Middle frame, which
  crosses the same patch (see finding 4).

**Fix.**
* Add `N([(268, 8), (300, 10)], [(268, 42), (300, 45)], "fescue mound right of the fairway, inside the path")`, or
  trace it on NAIP 2023 CIR.
* Re-solve 16 for Back and Middle. Expect a smaller right aim, and the 4-wood held more firmly against the 2-wood /
  Driver.

### 3. Hole 9 (Back 390): native left of the fairway at 260-310 is mapped as rough. CLUB/AIM

**Evidence.**
* Lateral NIR profiles (`nir.py`):
  * At 280 yds, NIR is 134-161 from x -36 to -18. The fairway edge is at about -12.
  * At 300 yds, NIR is 148-169 from x -45 to -12.
  * Texture SD there is 6-10.
  * For comparison: the mapped native left at (200, -42) reads 126; mown rough at (230, -22) reads 188 / SD 4; the
    fairway reads 203 / SD 2.
* `p09.jpg` RGB: tufted, tan, unmown grass runs to within about 5-8 yds of the fairway edge at 265-310.
* The map's left band is only x -48..-33, from 140 to 300 (EYECHECK_B: "correct"). It misses the inner 15-20 yds and
  everything past 300.
* For contrast, I also sampled 310-360 across the line: that area is mown (2022 mowing stripes, low texture). Only
  the left strip is native.
* 9 is a three-way near tie (4-wood 0.019 over Driver, p 0.71; Driver is the pick if the width is under 62). On
  Saturday the page's 4-wood aims 8.5 left (to finish on the line in the L-to-R wind), and the pattern's left 95 %
  edge reaches about x -27.

**Fix.**
* Move the left band's inner edge to about x -15 from 255 to 315, and extend it to 320.
* Re-solve 9. I expect the aim to move a few yards right. The Driver, which finishes nearer 300 where the strip is
  widest, probably loses ground.

### 4. Middle 16: the page shows the book's Driver while its own wind model says 4-wood by 0.032. CLUB/AIM (Middle)

**Evidence.**
* `solveTee` keeps the book pick whenever the quick model's pick in the wind equals its pick in calm air (`pick ===
  calmQuick`). It does not check whether the quick model agrees with the book.
* On Middle 16, the book says Driver by 0.017 ± 0.004 (p 0.59). The quick grid says 4-wood by 0.011 in calm air, and
  4-wood **by 0.032** in Saturday's forecast cell (NNW 7, 48 F).
* Because the quick pick is 4-wood both times, the page shows **Driver, aim 16 right**, with the badge "Close call ·
  4-wood +0.017".
* The club table then lists the 4-wood as "≈ tie" (d = -0.032 < 0.01 prints "≈ tie"). It should say the 4-wood is
  better by 0.032.
* No Back hole has this disagreement at the forecast (I checked every hole, both days).

**Fix.**
* When the book pick and the quick pick differ, do not override silently. Show a "Tie / model split" badge with both
  clubs.
* Print negative deltas as "better by".
* On Middle 16 specifically, present it as a coin flip between the 4-wood and the Driver (also see finding 2).

### 5. A wind-flipped pick gets no close-call badge, and the note underneath contradicts the play (10, Sun 8, and every aim). MISLEADING

**Evidence.**
* **Hole 10, Saturday 11:06 (NNW 8, 45 F).**
  * The page shows **2-wood, aim 6 left**, by 0.014 over the 4-wood, with only the badge "Calm-day pick: 4-wood".
  * There is no "close call", although 0.014 is closer than the 0.020 that earns the badge in calm air. The SE on 10
    is about 0.004-0.006 (z ≈ 3).
  * Directly below, the note still reads "**4-wood** by 0.020 ± 0.006 ... **Aim 16.0 yds left** ...".
* **Sunday 8:** 4-wood by 0.022, with only "Calm-day pick: 2-wood". The note says 2-wood, aim 40 left.
* **On every hole**, the note's "Aim X" is the calm aim, while the dot moves with the wind. Saturday examples (dot vs
  note):

  | Hole | Dot | Note |
  |---|---|---|
  | 2 | 27 R | 17.5 R |
  | 3 | 1 R | 8.5 L |
  | 5 | 10 L | 1 L |
  | 6 | 15 R | 6 R |
  | 9 | 8.5 L | on the line |
  | 11 | 28 R | 19 R |
  | 15 | 20 R | 12 R |

  A golfer who reads the text and not the dot aims 8-10 yds wrong in the wind.

**Fix.**
* Label the note "Calm-day book (no wind, X °F):".
* When the shown pick differs from the book, replace the note's first sentence with the quick model's margin.
* Badge any shown margin under 0.03 as a close call, whichever model it comes from.

### 6. Hole 8: the aim search stops at 40 yds left, and the page does not say so. MISLEADING (could change club in some winds)

**Evidence.**
* `v2_decisions.json` hole 8: `at_bound: true`, window [-40, -37.5] (Back and Middle).
* In `wind_grid.json` hole 8, the *finish* line is clamped at -40. The picked club is at the bound in 28 / 39 / 44 of
  the 61 cells at 35 / 50 / 65 F, and the Driver is at the bound in every cell checked.
* Saturday's page aim (2-wood **47 left**, finishing 40 left in the L-to-R wind) is the clamp, not an optimum. The blue
  bar (-47.9..-43.8) is truncated.
* The Driver's "+0.086" on the page is a Driver forced to finish at -40. OPTIMIZE 4d puts its unbounded best at about
  -50 (calm +0.064), and "about level with the 2-wood" in a 10-mph crosswind. At 10 mph into, the clamped grid already
  picks the Driver.
* The note's "anywhere from 40 left to 37.5 left" hides that the window was cut.

**Fix.**
* Widen the aim bound on 8 (-60 or more) and re-solve.
* Until then, add a page note on 8: "Best line is at or past 40 left; the Driver over the left side (45-50 left) is
  close to the 2-wood."

### 7. Par-3 distances come from the card, which is 3-5 yds longer than the map on 4 and 7, and on par 3s the tee cannot be moved. MISLEADING (about half a club)

**Evidence.**
* PAR3.md: the map's tee-to-centre is 176 / 176 on Back 4 / 7 (card 180 / 180). On Middle it is 150 (card 153) on 4
  and 155 (card 160) on 7, where the Middle 7 tee is estimated.
* The page builds "Plays N" from the card. PAR3.md says the page number is about 4 yds longer than the model's carry
  to the same spot, and "take the distance from the tee plate or a laser". The page says none of this.
* The footer tells Will to "use Move this tee to match" the plaque, but `renderTeeCtl` hides `#adjRow` on par 3s
  (verified: `adjRow.hidden = true` on 14). On the holes where a day-of box change is most common, he cannot adjust
  the number.
* Middle 7 on Saturday: page 162 "8-iron (tie 9-iron)". The map distance would make it about 157.

**Fix.**
* Enable the tee slider on par 3s (add the offset to `S3.center` and the box).
* Add a par-3 line: "Card 180; the map measures 176. Use the plaque or a laser and add the box depth."

### 8. "Move this tee (5-yd steps)" moves the tee in steps the solve cannot follow. MISLEADING

**Evidence.**
* The offsets are solved every 20 yds (-160..+40). In the page (Back 16):
  * 5 back: changes nothing but the yardage label.
  * 10 back or up: the same solve plus the badge "Nearest computed tee: 0 yds back".
  * 15 back: jumps to the +20 solve and drops the book ("Tie · Driver just as good").
* On the Middle alt base only offset 0 exists, so every move is cosmetic.

**Fix.**
* Make the slider step 20 to match the grid, or say "solved every 20 yds" beside it.
* Refine ±10 offsets for the card-tee holes.

### 9. Middle: no "Lands past the hand-checked map" badge where the drive does land past it. MISLEADING

**Evidence.**
* The badge fires when `total - B > 345`, measured from the page tee. The Middle course module's hand footprint (the
  rough box) ends at Back-frame 345, which is **282** from the Middle tee on 3, **304** on 18 and 316 on 5.
* Middle 3's Driver totals 303 (Sat) and 286 (Sun). Middle 18's totals 309 (Sat). No badge is shown on either.
* OPTIMIZE 4f notes this for 3, but the page does not.
* I looked at Middle 3 past 282 (render `lr_truth_middle_03.jpg`): the auto layers look reasonable (clean fairway,
  OB along the yard), so the risk is low.

**Fix.** Compute the badge against each base's own footprint end (`max along` of the rough box).

### 10. Forecast staleness and the record's dates. MISLEADING

**Evidence.**
* The page and footer use a forecast fetched **2026-11-07 14:05Z**, 7-8 days before the rounds. OPTIMIZE 4f says
  "The forecast is from Nov 9", which is wrong.
* A re-fetch updates the hole-by-hole wind and the "Plays" numbers, but not:
  * the calm-book temperatures (Sat 39-49 F at a 9:00 start);
  * the par-3 club lines (finding 1).
* `tee_hour` 9.0 is an assumption: no tee sheet is cached.

**Fix.**
* Re-fetch on Nov 12-13 and again the evening before each round.
* Re-run `par3_target.py page` with the new forecast.
* Correct the date in OPTIMIZE.
* Set the real start time and hole once the NCCGA posts them.

### 11. The wind-arrow colours mean opposite things on the map and on the dial. MISLEADING (minor)

**Evidence.**
* On the map, the yellow arrowhead is where the wind blows **to** (`windArrow`: "arrow shows where the wind blows
  TO").
* On the dial, "The yellow end of the needle points **into** the wind", that is, where it blows **from**.
* The map arrow itself is drawn correctly: hole 4's NNW wind shows as helping, and hole 2's as right-to-left. But a
  golfer who learns "yellow = from" on the dial reads the map arrow backwards.

**Fix.** Make both ends mean the same thing, or label the map arrow "wind →".

### 12. Hole 12 (peninsula green) has no safe-miss note. COSMETIC

**Evidence.** 4, 14 and 17 say "The safe miss is left/right". 12 says nothing, although the water is 3-5 yds off the
left and long edges and the creek is short (PAR3.md section 2). This is the par 3 where the miss side matters most.

**Fix.** Add "The safe miss is right" (no hazard words, per the golfer's request).

### 13. Record and display nits. COSMETIC

* PAR3.md section 7 still says the targets are "not wired yet". They are wired.
* Every calm note says "first cut 0%". The Gateway map has no first-cut class, so drop the phrase.
* Hole 3: the package OB polygon's edge runs diagonally inside the tree line at 150-250 (x about +22..+32 at 150-200),
  inside the hand recovery band. That spot is only reachable by a heavy mishit, so the impact is nil. Clip it to the
  hand OB band (x ≥ +44).
* The footer's NCCGA tee-set history (2024 Back 6,623; Nov 2025 6,377 combo) has no source cached in the repo.

## Checked and found correct

* **Card.** Back and Middle per-hole yardages (`tee_opts`) match the golfify / OpenGolfAPI card exactly. Back = 6,623
  and Middle = 6,154, par 71.
* **Tee positions.** The straight-line tee-to-green distance on the page frame matches the card within 0-5 yds on
  every non-dogleg hole, for Back and Middle. The exceptions are explained:
  * 8, 11 and Middle 18 are doglegs (-20 / -14 / -7);
  * the par-3 card-vs-map gaps are finding 7.
  * The Back 2 tee is on its own pad (the render shows it on the line SW; the aim moved to +17.5 as recorded).
* **Decision record vs page.** Pick, aim, window, runner, margin, temperature, p and SE match `v2_decisions.json`
  exactly on all 13 Back and 13 Middle tee holes. One wind cell (hole 2, 10 mph, rel 120, 50 F) matches
  `wind_grid.json` to rounding.
* **Plays-like by hand.** Back 14, Saturday:
  * Inputs: hole time 12:02, wind 7.4 mph from 327 (vector-interpolated 12:00-13:00); bearing 73.4, so rel 253.5 (2.1
    mph helping, 7.1 mph from the left); 47.2 F.
  * Grid plays 197.31 (calm 199.28), box target 193.0, temperature factor 1/(1 - 0.00075 × 22.8) = 1.0174.
  * Play = 193 × 197.31 / 200 × 1.0174 = **193.7**. The page shows **194**: "193 target, -1 elevation, -1 wind, +3 at
    47 °F".
  * Back 4 the same way: 173.2, page 173.
  * Signs are right: uphill adds (4: 2.8 ft up, +1), a helping wind subtracts (4: 7.3 mph tail, -6), cold adds
    (~+3-4 at 41-47 F).
* **Wind conventions.**
  * Forecast "from" degrees, local America/Chicago hours.
  * rel = from - bearing; 0 = into; positive sin = from the right, read as "right-to-left".
  * Drift and aim go the right way: on hole 2 the wind is right-to-left, so the dot moves right and the ball
    finishes left.
* **Forecast time mapping.**
  * Hole n at 9:00 + 14 (n-1) min, counted from the start hole (shotgun), wind vector-interpolated between hours.
  * The calm-book temperatures (39.0 F on 1 to 48.9 F on 18) equal the Saturday forecast at those times.
* **Close-call labels in calm air.** 8, 9, 10, 11 and 16 get "Close call" with margins and p equal to the record. The
  other Back holes are ≥ 0.048 and p ≥ 0.97. Middle 1, 11 and 16 are labelled the same way. The exceptions are
  findings 4 and 5.
* **Map renders, Back landing areas (120-380 yds).**
  * 1, 2, 3, 5, 6, 8, 10, 11, 13, 15 and 18: fairways, bunkers, water and the Nov 9 native / OB edits sit on the
    photo, and every Sat / Sun aim and finish lies on fairway.
  * The 8 fescue inside the dogleg, the 11 bands either side, the 3 OB yard band and the 2 pond are all right.
  * The 10 creek and green are right. On Saturday the 2-wood is aimed over the creek and finishes 8 yds left on the
    green side.
  * The exceptions are 9 and 16 (findings 3 and 2).
* **Par-3 boxes.** They sit on the green outline, short of centre, on 4, 7, 12, 14 and 17 (Back) and on Middle 12. The
  green outlines match NAIP 2023.
* **Temperature model.** 0.075 %/F of carry, about 2 yds per 10 F for the driver, as the footer says. It is applied to
  tee shots and par 3s.
* **No hazard words or outlines** on the page, as the golfer asked.

## Status of each finding on the published page (re-verified Nov 13 2026, second pass)

Checked on the built page itself (v5, `wind_page/index.html` of 2fe7b33ed): headless Chromium, every hole, Back and
Middle, Sat and Sun at the default start, Custom winds (calm, 10-20 mph from each side, 38-70 F), other tee times and
start holes, moved tees, The Tips / Champions / Forward. Map findings looked at on my own renders (NAIP 2023 RGB + CIR
at 5-9 px per yard, and the Sentinel-2 NDVI of Nov 8 + 10 2026).

| # | finding | status on v5 | what I saw |
|---|---|---|---|
| 1 | par-3 club frozen to the forecast day | **fixed** | The club follows the live number: Back 4 at 15 mph into, 45 F shows 5-iron (plays 201); 14 at 15 mph into shows "Between clubs: 4-iron 210 / 4-wood 255" and no club; a helping wind drops a club; tee time, start hole and Move this tee all move it. Each shown club is the nearest-carry club or its neighbour within 6 yds of the number (the ladder's expected-strokes choice). |
| 2 | 16: unmapped fescue mound right at 275-300 | **fixed, map correct** | The mound (264-298, 8-42 R, white stones on its left edge) is real and the polygon sits on it. New on the same hole: the LEFT native edge was 6-8 yds too far left (fixed Nov 13, below). |
| 3 | 9: native left at 260-310 mapped as rough | **over-corrected, re-fixed Nov 13** | The Nov 9 edge was drawn to 14-22 yds left of the line at 300-340; the tufted grass stops at a worn line 22-28 left (photo and the Nov 2026 NDVI agree). Also the right "fescue" band (30-45 R) is mown turf. Both changed Nov 13. |
| 4 | Middle 16 showed the book while the wind model disagreed | **fixed** | "Models split" badge and the wind model's pick are in the page code; with the mound mapped Middle 16 no longer splits (long iron in both). |
| 5 | wind-flipped picks without a close-call badge; note contradicts the play | **fixed** | The note is labelled "Calm-day book (no wind, N F)"; a wind-changed pick gets a first sentence and a tie / close-call badge (Sat 10: "2-wood by 0.006 ... Tie"). |
| 6 | 8: aim search stopped at 40 yds | **fixed** | Bound 60 (grid to 80). The deeper problem found Nov 13: left of 65 yds the engine priced open rough as "unverified" (half trees), which held the Driver back; fixed below. |
| 7 | par-3 distance from the card (4 yds long on 4 and 7); no tee slider on par 3s | **fixed as designed, residual** | Par 3s have Move this tee (5-yd steps), a Map row and a card-vs-map line. The default number is still the card's. On 4 the Back pad is 10 yds deep and centred 176 from the green centre (card 180 = its back edge); on 7 the tee is a 50-yd strip, so the card is as good as the map. |
| 8 | tee slider steps the solve cannot follow | **partly** | The slider moves in 20s and says "solved every 20 yds". Because the page keeps only the grids a tee set uses (`grid_prune`), 20 / 40 up on most Back holes still shows the card-tee solve, with a "Nearest computed tee" pill. The footer's "5-yd steps" wording is corrected Nov 13. |
| 9 | no past-the-map badge on Middle | **fixed** | Middle 3 and 18 show it on Saturday. |
| 10 | forecast staleness | **fixed** | Forecast of Nov 12 on v5; refreshed again Nov 13 02:44Z (Saturday is colder: 35 F at 9:00 after a 24 F night). The calm book is re-solved on it (below). |
| 11 | wind-arrow colours | **fixed** | One arrow, labelled, pointing where the wind blows to. |
| 12 | 12: no safe-miss note | **fixed** | "The safe miss is right." |
| 13 | nits | **mostly** | No "first cut" in the notes; PAR3.md updated. Still open: hole 3's package OB edge runs inside the tree band at 150-250 (heavy mishits only). |

New findings of the second pass are in OPTIMIZE.md, section "Nov 12-13 second pass".
