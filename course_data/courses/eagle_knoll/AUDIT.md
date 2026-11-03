# Eagle Knoll wind page: independent audit (Nov 3 2026)

Audited page: `course_data/courses/eagle_knoll/wind_page/index.html`, blob sha1 `933458d19aa1`, last changed in
ad079f501 (Oct 31). The optimizer may rebuild it after this audit. 09bd942a9 (Nov 3) changes how the landing
pattern is drawn, but the Eagle Knoll page had not been rebuilt with it when I audited, so my screenshots show
the old near-circle patterns. I did not read OPTIMIZE.md before writing this.

**Method.**
* **Screenshots.** I opened the page in headless Chromium at 400 px wide (DPR 2). I stepped through all 18 holes for
  each tee set (Eagle, Back, Middle, Forward). On every par 4 and par 5 I shot both views: the whole hole and the
  landing area. Wind source: the Sat 11/7 forecast (the default) at a 9:00 shotgun start on hole 1. I also read the
  page text with the Sun 11/8 forecast and with Custom calm at 50 F.
  * Screenshots are in `/tmp/claude-0/-home-user-my-golf-data-science/3c0900e1-ef71-58c8-8d72-7f70a9ca40ad/scratchpad/ek_audit/`,
    named `d0_<Set>_hNN_<hole|land>.png`, with `_map.png` holding the map only. Contact sheets are in `sheets/`.
    The scratchpad is temporary, so these files are not in the repo.
  * Extracted page text: `d0_info.json`, `d1_info.json`, `calm_info.json` in the same directory.
* **Truth map.** I read the hand truth map (`truth*/course.py`: zones in the tee-line frame) and printed a
  lateral lie profile every 10 yds from 140 to 360, from x = -70 to +70 (T trees, F fairway, W water, S sand,
  N long grass, O OB). I compared each aim and finish point with that profile. I also used the recheck renders
  (`course_data/truth/eagle_knoll/recheck/hNN_land.jpg`: NAIP 2020, CIR 2020, NAIP 2022 and the 2015 lidar edge).
* **Engine.** I read the engine (`spirit_hollow/v2/model.py`, `spirit_hollow/wind_grid.py`) to check how it
  handles trees, temperature and par-3 plays-like yardages.
* **Card and tee set.** Cross-checked against the NCCGA tee sheets cached in `course_data/research/web/eagle_knoll/`:
  * Fall 2015 (06.txt): "Tee Marker: Blue", 6682.
  * Fall 2024 (08.txt): "Tee Marker: Blue", 6512, as set up that day.
  * A web search agrees with the golfify / OpenGolfAPI Back figures (6,667, 72.8/134). golfpass.com and nccga.org
    cannot be reached from this sandbox, so I could not read a hole-by-hole official card live.

**Not verified.**
* No on-site knowledge: November turf firmness, leaf drop, where the pins go.
* Nothing newer than the 2015 lidar or NAIP 2022.
* I did not re-run the engine, so I report no regret numbers of my own.
* Forecast: fetched Oct 31, 7-8 days before the event.

Verdict key: **Agree** / **Disagree** / **Unsure**. "x" means yards right (+) or left (-) of the tee line.

## Tee set and card

| Item | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Tee set NCCGA plays | Back (blue) 6,667 is the default | **Agree** | NCCGA sheets list "Tee Marker: Blue" in Fall 2015 (shotgun) and Fall 2024. | Keep. |
| Card per hole (Back) | 366 151 397 399 465 138 475 407 510 / 405 441 180 546 265 447 158 489 428 | **Unsure on 10** | The 2015 NCCGA Blue sheet lists **10 = 420** (total 6682); 405 sums to 6667. The footer says golfify "= the NCCGA 2015 sheet", which is false for hole 10. The mapped Back 10 tee measures about 405 (truth notes), so 420 is either the Eagle box (Eagle 10 = 420) or a typo. | Correct the footer. Check hole 10 on the posted tee sheet; if it says 420, set "Move this tee" to +20 on 10. |
| Day-of setup | Card Back yardages | **Unsure** | The Fall 2024 "Blue" setup did not match the Back card: 1 = 379, 2 = 144, **5 = 420 (card 465)**, 7 = 461, 8 = 395, 9 = 485, 11 = 430, **14 = 246 (the Middle box)**, 17 = 465, 18 = 417; total 6512. The NCCGA moves boxes hole by hole. | When the Nov 7 tee sheet posts with its yardage row, set the per-hole tee offset, or switch hole 14 to Middle. Tell Will to compare the tee-box plaque with the page on each hole. |
| Eagle 2 yardage | 167 (card) | **Unsure (3 yds)** | The truth_eagle par-3 centre measures 164; the page uses 167. | Minor. Use the measured value or note the difference. |
| Forecast | Sat 3.6 mph ENE, 44-58 F; Sun about 10 mph N, gusts to 23, 46-61 F | **Stale** | Fetched 2026-10-31 14:04Z, 7-8 days out. | Re-fetch on Nov 5-6 and again the evening before each round. |

## Hole by hole

The Back set (what Will plays) gets the full check. Eagle and Middle get the pick and aim checked against their
own truth bases. Forward is checked lightly: it is a women's / short set, synthesized by moving the Back tee
along the line.

### Hole 1, par 4, dogleg left, about 61 ft downhill to the landing area
| Set | Page says (Sat) | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 366 | Driver, aim 30.5 left. Total 328, 33 yds to the green. The page's own note: fairway 15 %, trees 37 %. Long iron +0.048, beats it in only 75 % of 128 worlds; break-even driver pattern 79 yds (page uses 70). | **Disagree (soft)** | `d0_Back_h01_hole.png` / `_land.png`: the pattern is centred past the corner, over the dark canopy between the two tree masses, about 30 yds short of the green. Truth profile: at 320-330 the fairway is only x -55..-45, rough -40..-25, trees from about x -5 rightwards, woods x < -45 at 240-310. The recheck CIR (`recheck/h01_land.jpg`) shows that pocket very dark. The engine prices trees only where the ball finishes. It does not check whether the flight line clears the 270-300 gap; trees near the green cost a cheap punch-out; roll is x1.30 on firm turf. A Nov 9 am first hole means colder, softer ground and a cold swing. | Make **Long iron** (to the fairway at about 230, x -10..+15, about 130 in) the shown pick, or at least badge "near tie, safe option Long iron +0.05". Add a flight-path tree check. |
| Eagle 399 | 4-wood, aim 2.5 left, 285 total, fairway 57 % | **Agree** | `d0_Eagle_h01_land.png`: the pattern is on the fairway short of the corner. | None. |
| Middle 346 | Driver, aim 36.5 left, 20 yds to the green, fairway 10 %, trees 27 % | **Disagree (soft)** | Same corner as Back, cut harder (`d0_Middle_h01_*`). The margin is bigger (2-wood +0.13), but it carries the same unmodelled flight risk. | As for Back. |
| Forward 327 | 2-wood, aim 30.5 left | **Unsure** | The note text under the pick is the Back book's note (see Forward finding). | n/a for Will. |

### Hole 2, par 3, green 60 ft below the tee
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 151 | Plays 130 (150 target, -17 elevation, -3 wind). Box 148-151. Trees left, right and long; safe miss short. | **Agree on the target. The yardage is about 2-3 yds short.** | `d0_Back_h02_hole.png`: the box sits centre to front, which matches "trees long". A 60 ft (20 yd) drop at an iron's roughly 50 deg landing angle gives about 17 yds, so the elevation figure is sound. **Par-3 plays-like yardages ignore temperature**: `solvePar3` and `wind_grid.plays_like` have no temperature term, but the tee-shot model uses 0.075 %/F. At 49 F that is about 1.6 % of carry, roughly +2 yds. | Add the temperature term to par 3s; it would read about 132. |
| Eagle 167 | Plays 144, box 165-166 | **Agree** (same caveats) | `d0_Eagle_h02_hole.png` | As for Back. |
| Middle 132 | Plays 113, box 128-133 | **Agree** | `d0_Middle_h02_hole.png` | As for Back. |
| Forward 98 | Plays 78 | **Agree** | | |

### Hole 3, par 4, forced carry over the ravine and pond
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 397 | Driver, aim 11 right, 296 total, about 100 yds in, fairway 64 % | **Agree** | Truth: the fairway starts at about 185; at 300 it spans x -5..+30, so the aim is centred where it bends right. Water at 140-160 is a trivial carry. The woods left are what to avoid, and the aim is right. `d0_Back_h03_land.png` | None. |
| Eagle 409 | Driver, aim 6.5 right | **Agree** | `d0_Eagle_h03_land.png` | |
| Middle 361 | Driver, aim 21 right, 65 yds in | **Agree** | | |
| Forward 203 | "Par 4", **Mid iron** to 11 yds short of the green. The tee is drawn in the fairway. Badges: "Nearest computed tee 200 up", "past the hand map". | **Disagree** | `d0_Forward_h03_hole.png`: the red tee sits on the fairway, not on a pad. From 203 yds a player just goes at the green; the hole is effectively a par 3. The note text is the Back note. | Treat Forward 3 as a par-3-style approach, or drop Forward from the men's page. |

### Hole 4, par 4
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 399 | Driver, aim 10 left (finishes about 15 left in the R-to-L wind), 299 total | **Agree** | Truth: the fairway bends left; at 300 it spans x -35..0 (centre about -17). Woods left are 20-30 yds off; hole 8's fairway on the right is a fairway lie. `d0_Back_h04_land.png` | None. |
| Eagle 416 | Driver, aim 0.5 right | **Agree** | | |
| Middle 363 | Driver, aim 25.5 left, 66 in | **Agree** | Follows the bend. | |
| Forward 313 | Driver (tie 2-wood), past the hand map | **Unsure** | Lands off the hand-checked map. | |

### Hole 5, par 4, 465 (hardest hole, hcp 2)
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 465 | Driver, aim 3.5 right, 322 total, about 146-166 in, trees 9 % | **Agree** | At first glance the aim looked like it favoured the tight right side. The profile shows the fairway at 320 runs x +5..+35 (centre about +20), so +3.5 is on the **left (open) side** of the fairway, away from the right woods (0-10 yds off). The left woods have grown in since 2015 and are mapped. `d0_Back_h05_land.png` | None. On the 2024 setup this hole played **420**: check the tee sheet. |
| Eagle 473 | Driver, aim 2.5 right | **Agree** | | |
| Middle 380 | Driver, aim 20 right, trees 20 %; 4-wood ties (+0.017) | **Unsure** | 20 % trees for 0.017 strokes; 4-wood is the lower-variance choice. | Show it as a tie and let Will choose. |
| Forward 353 | 4-wood, past the map | **Unsure** | | |

### Hole 6, par 3, water left, right and short; 47 ft down
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 138 | Plays 128 (139 target, -13 elevation, +2 wind). Box 138-140 on a 126-149 green. | **Agree** on the target (centre to slightly long, away from the water short, with 9 yds to the trees long). Same temperature gap as hole 2 (about +2). | `d0_Back_h06_hole.png`: the box is wide and centred. Water is all round the front. Elevation: 47 ft is about 13 yds, which is sound. | Add temperature. Draw the water on par-3 maps: the frame is cropped to the green, so the water short is not visible. |
| Eagle 149 | Plays 139 | **Agree** | | |
| Middle 120 | Plays 112 | **Agree** | | |
| Forward 84 | Plays 73 | **Agree** | | |

### Hole 7, par 5, 30 ft uphill landing
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 475 | Driver, aim 9 left, 273 total (-13 carry uphill) | **Agree** | Truth: fairway x -15..+15 at 270; woods right from +20; hole 13's fairway further left. Aiming left of centre is correct. `d0_Back_h07_land.png` | None. |
| Eagle 493 / Middle 451 | Driver, aim 9-10 left | **Agree** | | |
| Forward 390 | Driver | **Agree** | | |

### Hole 8, par 4
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 407 | Driver, aim 12.5 right (finishes about +18), 285 total, sand 8 % | **Agree** | Truth: fairway x -5..+15 at 280-290, bunkers left at 250-270, open rough and hole 4's fairway right. Favouring the right is correct. `d0_Back_h08_land.png` | None. |
| Eagle 424 / Middle 376 | Driver, right aim | **Agree** | | |
| Forward 322 | Driver | **Agree** | | |

### Hole 9, par 5
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 510 | Driver, aim 7.5 left (finishes about 11.5 left), sand 9 %, trees 7 % | **Agree, mild unsure** | Truth: fairway x -10..+5 at 290-300; bunkers left at 260-300 (x -25..-20); trees right 150-280 plus a 2020 crown at 250-275; long grass right from 280. Left is the cheaper miss. `d0_Back_h09_land.png` | None. |
| Eagle 526 | Driver, aim 13.5 left | **Unsure** | `d0_Eagle_h09_land.png`: the dot sits about 5-10 yds right of the two left fairway bunkers, with the pattern centred over them (sand 9 %). | Consider about 8 left. Low stakes. |
| Middle 486 | Driver, aim 5.5 left | **Agree** | | |
| Forward 454 | Driver | **Agree** | | |

### Hole 10, par 4, tree chute
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 405 | 4-wood, aim 1.5 right, 278 total, about 127-135 in. Driver +0.070, 2-wood +0.064. | **Agree** | Truth: a chute about 30 yds wide (fairway -10..+15), trees right at the fairway edge the whole way, trees left from 260. The narrower 4-wood pattern is right. `d0_Back_h10_land.png` | Card: see the 405 vs 420 question above. |
| Eagle 420 | 4-wood | **Agree** | | |
| Middle 380 | Driver, tie with 4-wood (Sat); 4-wood (calm) | **Agree** (a coin flip) | | |
| Forward 264 | 4-wood to 14 yds short of the green; the note says "135 yds in" | **Disagree (display)** | The note is the Back book's note. | See the Forward finding. |

### Hole 11, par 4, dogleg right
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 441 | Driver, aim 0.5 left, 288 total, about 159 in | **Agree** | Truth: fairway x -5..+20 at 290; long-grass strip left (x -70..-45); trees right at 230-280 beyond the path. `d0_Back_h11_land.png` | None. |
| Eagle 448 / Middle 420 | Driver | **Agree** | | |
| Forward 364 | Driver | **Agree** | | |

### Hole 12, par 3, bunker right, trees long
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 180 | Plays 174 (179 target, -3 elevation, -2 wind). Box 176-182, centre-left. Sun: plays 190 (+13 into an 11 mph N wind). | **Agree** on the side and the depth. Add about +3 for temperature. | `d0_Back_h12_hole.png`: the box sits left-centre, away from the bunker right; it is the long par 3, and centre is right with the trees long. The Sunday wind is dead into the hole (bearing 350): +13 is plausible. | Add temperature. |
| Eagle 198 | Plays 193; the truth also has a bunker short | **Agree** | | |
| Middle 162 | Plays 156 | **Agree** | | |
| Forward 120 | Plays 114 | **Agree** | | |

### Hole 13, par 5
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 546 | Driver, aim 12 right, 320 total | **Agree** | Truth: the fairway drifts right (x +5..+40 at 320); +12 is its left half, toward the safe side (hole 7's fairway); trees right from +50. `d0_Back_h13_land.png` | None. |
| Eagle 556 / Middle 524 | Driver | **Agree** | | |
| Forward 438 | Driver | **Agree** | | |

### Hole 14, par 4, 265, pond 200-260 in front of the green
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 265 | **Mid iron** lay-up, aim 9.5 right, 198 total, 63 in, fairway 68 %. 4-wood (+0.066) would carry to 11 yds short. | **Agree** with laying up | `d0_Back_h14_land.png`: the dot is short and right of the pond. Truth: the pond starts at about 200 near x -20..-15 and at about 228 at the aim's x +10; the fairway runs to about 210 at x +15..+20; woods on both sides and long. Carrying 265 over water to a green in the trees with an approximately 55-yd-wide 4-wood pattern is not worth 0.07. **Caveat:** the bag model's shortest club is "Mid iron" (190 carry), so a shorter lay-up to a full-wedge yardage is never evaluated. | Add 8-iron / 9-iron / wedge lay-up options for short par 4s. |
| Eagle 265 | Same as Back (same box) | **Agree** | | |
| Middle 246 | **Mid iron, aim 18 right, fairway only 17 %**, water 2 %, 51 in | **Disagree** | Truth (Middle frame): at 200 the pond spans x -30..0 and the fairway has ended; +18 is rough between the pond and the right woods (+45). The fairway lay-up is at 170-190 (x -5..+20), which needs a shorter club than the model has. **This matters:** NCCGA played 14 at **246** (this box) in 2024. | Add shorter lay-up clubs. Until then, tell Will "from 246: lay up with a club that finishes about 175-185, middle of the fairway". |
| Forward 215 | Long iron at the green, 5 short; the note says "fairway 68 %, 62 in" | **Disagree (display)** | The note is the Back note. The tee is 10 yds off the nearest grid offset. | See the Forward finding. |

### Hole 15, par 4, chute bending left
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 447 | 4-wood, aim 13 left, 280 total, trees 15 %. Sun (12 mph N, into): 2-wood, tie with 4-wood. | **Agree** | Truth: at 280 the fairway is x -35..0 with trees right from +5; Driver (318) reaches the narrowest part (x -55..-25). `d0_Back_h15_land.png` | None. |
| Eagle 459 | 4-wood (Sat), Driver tie (Sun) | **Agree** | | |
| Middle 427 | 4-wood, trees 20 % | **Agree** | | |
| Forward 345 | Long iron | **Unsure** (Back note text) | | |

### Hole 16, par 3, water right and short, trees left and long; 39 ft down
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 158 | Plays 150 (159 target, -11 elevation, +2 wind). **Box 159-159** (a point), slightly left of centre. | **Agree on the side, unsure on the depth** | `d0_Back_h16_hole.png`: the box is left of centre, away from the water right, and at the card centre of a 28-yd-deep green with water short. A 1-2 yd longer target would respect the short side more; trees long are 14 yds behind the centre. A 0-yd-deep "box" in light wind looks like a display artefact (DECADE -1 on each edge). The water short and right is outside the cropped photo. | Floor the box depth at about 4 yds. Bias the target 2 yds long. Add temperature (+2). |
| Eagle 177 / Middle 136 / Forward 107 | Plays 169 / 129 / 97 | **Agree** (same notes) | | |

### Hole 17, par 5, creek left, then crossing diagonally 240-345
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 489 | 4-wood, aim 6.5 right, 264 total, water 6 %, trees 8 %. Driver +0.081. | **Agree** | Truth: on the aim line (x +5..+10) the creek reaches about 285-300; a 264 total plus depth spread stays short of it. Trees right at +20..+25. Driver (289) would finish at the creek. `d0_Back_h17_land.png`. The creek is under the trees and **not visible in the photo**, and the page draws no hazard outlines. | Draw the water polygon on the map. Tell Will: "do not hit driver; the creek crosses at about 285 on your line". |
| Eagle 499 | 4-wood | **Agree** | | |
| Middle 471 | **Driver, aim 9 left over the creek to the left fairway**, water 18 %, trees 14 %; hybrid +0.018, 2-wood +0.042 | **Disagree (soft)** | `d0_Middle_h17_land.png`: the dot sits over dark canopy on the photo; truth puts it on the left fairway (x -35..0 at 280) with the creek at +5..+10 and trees beyond -40. That is 32 % penalty lies for less than 0.02-0.04 strokes. | Prefer the 4-wood / 2-wood line used from Back, or badge it a near tie. |
| Forward 424 | 4-wood (Sat), 2-wood tie (Sun) | **Agree** | | |

### Hole 18, par 4, house lots / OB left
| Set | Page says | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|
| Back 428 | Driver, aim 0.5 left, 282 total (uphill, roll x0.70), tie with 4-wood, OB 2 % | **Agree** | Truth: fairway x -25..+5 at 280; OB x -70..-45; trees right at +40. The aim is right of the fairway centre (about -10), away from the OB. `d0_Back_h18_land.png`. The OB line (no stakes visible, +/-8 yds) is not drawn. | Draw the OB line. |
| Eagle 442 / Middle 405 | Driver | **Agree** | | |
| Forward 353 | Driver | **Agree** | | |

## Cross-cutting findings

1. **Hole 1 (Back and Middle): driver over the dogleg corner.** The fairway hit rate is 10-15 % and the trees hit rate is 27-37 %. The page's own uncertainty says it is about a coin flip against Long iron (75 % of worlds, break-even pattern 79 yds against an assumed 70). The engine has no flight-path tree check and assumes firm-turf roll (x1.30). This is the one Back pick I would change: show Long iron, or at least a "safe: Long iron +0.05" badge.
2. **Shorter lay-up clubs are missing (hole 14).** The shortest club is the 190-carry "Mid iron". From Back it happens to fit. From the **246 (Middle) box, which NCCGA used in 2024**, it lands past the fairway in rough beside the pond (fairway 17 %). The model cannot recommend the obvious 170-185 lay-up.
3. **Par-3 plays-like yardages ignore temperature.** The engine applies 0.075 %/F to tee shots but not to `solvePar3` or `plays_like`. At 45-56 F the par-3 numbers read about 2-3 yds short: holes 12 and 16 have trees long, but hole 6 has water short.
4. **Card and tee setup.**
   * The footer claims golfify = the NCCGA 2015 sheet, but that sheet has hole 10 at **420** (6682), not 405.
   * The 2024 NCCGA "Blue" setup varied hole by hole (5 at 420, 14 at 246, 6512 total).
   * The page needs the day's tee-sheet yardages entered per hole. The "Move this tee" slider can do it.
5. **Hazards not drawn; Forward set unreliable.**
   * The page draws no water or OB outlines. The creek on 17 and the OB on 18 are invisible on the photo, and par-3 maps are cropped to the green, so the water short on 6 and 16 is not shown.
   * Forward-set notes ("fairway 68 %, 62 in", aims) are copied from the Back book and contradict the Forward table on 3, 10, 14 and 15.
   * The Forward 3 tee is drawn in the fairway of a 203-yd "par 4".
   * Fix: drop Forward from the men's page, or strip the Back notes from moved tees.

Everything else agrees with the truth map and with what I would choose. On the Back set, 17 of the 18 picks and
targets agree; hole 1 is the exception. The four par-3 yardages carry the temperature caveat, and hole 16's depth is
"unsure". That covers the Back aims on 4, 5, 8, 13 and 18, which all favour the safe side, and the 4-wood choices on
10, 15 and 17. Elevation effects on the par 3s (-17 / -13 / -3 / -11 for 60 / 47 / 12 /
39 ft) are physically sensible. The forecast should be refreshed close to the day: Sunday's 10-12 mph north wind
already flips 15 to 2-wood and adds 13 on hole 12.
