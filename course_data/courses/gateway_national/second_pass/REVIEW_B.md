# REVIEW_B: holes 7, 8, 9, 11, 12 as Will would read them (Back, then Middle)

Reviewer B, Nov 13. Read-only on the map, engine and page. Page checked: `wind_page/index.html` at cee080946
(rendered with `qa_page.js`, Back and Middle, phone). Map checked: `truth/course.py` and `truth_middle/course.py`
(the zones the engine paints, later zone wins, plus the +/-65-yd "unverified" rule and 8's `checked_extra_ll`)
painted over NAIP 2023 RGB and CIR in the hole frame. Frame: x = yds right (+) / left (-) of the Back tee line,
along = yds from the Back tee. Ground heights: `vision_any/.../dtm.tif`.

**Version 1 (first pass over all five holes). Refinements follow below as they are added.**

## Summary, most important first

| # | hole | verdict | finding | action |
|---|---|---|---|---|
| 1 | 11 (Middle most, Back a little) | **doubt** | The long grass left of the fairway at 300-385 is 6-19 yds closer to the fairway than the map has it, and the map stops it at 345. The photo, the CIR and F1's own lidar table agree. Middle's Driver (0.010 over 4-wood) finishes right beside it | add the native polygon P1, re-solve 11 Back and Middle |
| 2 | 8 Back | **fine** (Driver 50 L is the play) | Nothing under the Driver oval that the map misses. The line is over the left fairway bunker; the ground left of the cart path is junk but already priced | page text only (T1), optional small native P3 |
| 3 | 9 Back / Middle | **fine** | The oval is centred between the left brush / pond and the right tree line. The "water" strip at 300-360 is a real 5-7 ft ditch, not the cart path. No ditch in the fairway gap at 310-330 | none |
| 4 | 7 | **fine, one doubt** | Short of the green on the line is unmown tall grass (x -5..+17, 112-157), mapped as rough | add native P2 (changes the box by little; test) |
| 5 | 7 / 12 Middle | **doubt (page)** | "Plays 167: 8-iron carries 162" and "Plays 120: SW carries 113" name a club 5-7 yds short of the plays-like number | question Q1 |
| 6 | 12 | **fine** | Peninsula: water left / short / long is where the photo has it. Mapped green sits ~3 yds right of the photo green on its left edge | optional P4 |
| 7 | 8, 9, 11 | **doubt (page numbers)** | "To green" in the table and "about N yds in" in the note differ by 3-10 yds on the same card (9: 99 vs 108; 11: 118 vs 128; 8: 108 vs 111) | question Q2 |

## Hole 11 (par 4, 416 Back / 394 Middle): Driver 25 R. Verdict: doubt on the left long grass

Renders: `h11_fill` (0-430, whole hole with the lie map), `h11_none` (215-375 photo with the Driver oval),
`h11_blk2` (295-400, RGB + CIR), `m11_fill` (Middle frame).

What the picture shows. The fairway runs up and to the right; at 293 it spans x +2..+44 (centre +23), so the page's
aim 25 R with the ball finishing 21 R is the middle of it. Right: rough to the cart path at x +58, tall grass blocks
beyond. Left: rough, then a strip of standing grass and brush between this fairway and the next one.

Where the map differs from the picture: that left strip, from 300 on.

| along | mapped native inner edge (x) | photo / CIR edge | F1 lidar edge (FEATURES_10_18.md, hole 11 table) | fairway left edge |
|---|---|---|---|---|
| 300 | -10 | -3 | -7 | +6 |
| 310 | -9 | -1 | -2 | +11 |
| 320 | -8 | +2 | +2 | +17 |
| 330 | -7 | +8 | +8 | +24 |
| 340 | -6 | +12 | +13 | +28 |
| 350 | none (band ends at 345) | +16 | +21 | +33 |
| 360 | none | +22 | +24 | +41 |
| 370-385 | none | +25..+28 | not listed | fairway turns to the green |

So at 320-345 the engine prices 10-20 yds of standing grass as rough, and from 345 to 385 all of it. In the CIR the
strip is grey-blue (not growing, standing) against the pink mown rough; in RGB it is the mottled dark block with a
straight mown edge at about (x +13, 345).

Why it matters for the pick:
* Back: Driver finishes (21, 293), 95 % oval to x -14 and to 315 long. Only the long-left corner reaches the
  difference. My rough estimate is +0.01 strokes on the Driver; the margin is 0.027 over 4-wood. Probably the same
  club, aim a yard or two further right.
* **Middle: Driver finishes about (20, 288) in the Middle frame = ~310 in the Back frame**, with the strip's true
  edge 18-20 yds left of the ball at 320-340 and the map's edge 28 yds left. Roughly 3-4 % of Drivers finish in
  ground the map calls rough and the photo calls long grass. The page says Driver by 0.010 ("≈ tie" with 4-wood).
  This edit can turn Middle 11 into a 4-wood, or move the Driver aim right.

OPTIMIZE.md 5c says the lidar long grass on 11 was tested and moved aims 0.5-2 yds, so it was left out. I do not
know if that test included Middle, where the margin is 0.010.

**P1. add, hole 11, kind `native`** (paint after the existing left band; it overlaps it at 300-345):

* hole-frame yds (x, along): (-10,300) (-3,300) (-2,310) (2,320) (8,330) (13,340) (21,350) (24,360) (28,372)
  (28,385) (8,385) (4,370) (-2,350) (-8,335) (-10,320)
* lon/lat: [-90.1480553, 38.6561849], [-90.1480968, 38.6562325], [-90.1481894, 38.6561928],
  [-90.1482998, 38.6561735], [-90.1484221, 38.6561678], [-90.1485384, 38.6561553], [-90.1486725, 38.6561631],
  [-90.148777, 38.656137], [-90.1489047, 38.6561084], [-90.1490174, 38.656048], [-90.1488988, 38.6559121],
  [-90.1487451, 38.6559546], [-90.1485361, 38.6560068], [-90.1483706, 38.6560358], [-90.1482287, 38.6560919]
* The inner (right) edge is F1's lidar edge at 310-360, the photo at 370-385. The outer edge is not critical (the
  next fairway is beyond).
* How sure: position of the inner edge 85 % (two sources within 1-5 yds). Standing on Nov 14: same doubt as all
  the long grass here.
* Test: 11 Back and 11 Middle. Expect Back to hold Driver; Middle to become 4-wood or the aim to move right 2-4.

Other checks on 11, all fine:
* Right side: native mapped from x +46 at 250 to +60 at 300, matching the blocks right of the cart path. Above 300
  the blocks continue to 365 at x 62-98; the map has rough to 65 and "unverified" beyond, which is priced as
  half trees. Good enough: the Driver oval's right edge is the cart path.
* Pond carry on the 25 R line: far bank at about 100 yds. Not a factor for any club.
* Numbers: fairway at 293 is 42 yds wide for a 70-yd oval, so "fairway 58 %" is believable. Finish (21, 293) to the
  green (76, 395) = 116; the table says 118. The note says "about 128 yds in" (Q2).

## Hole 8 (par 4, 408 Back / 378 Middle): Driver 50 L (Back), 4-wood 40 L (Middle). Verdict: fine

Renders: `h8_all` (0-440), `h8_fill` (120-420 with the lie map, the checked ring and the unverified hatch),
`h8_land_none` (200-400 photo), `h8_z_rgb` / `h8_z_cir` (205-325 x -135..-15), `m8_fill` (Middle frame, the three
ovals).

What is under the Driver oval at (-50, 286), 71 wide:
* Centre: fairway. This is the fat part of the fairway where it turns; it is 55-60 yds wide measured across the
  oval. The map's fairway edge follows the photo within 2-3 yds.
* Upper left of the oval (x -88..-48, 299-336): the unmown square. Mapped native. The mown bank around it is rough.
  Right place, right size (photo: x -86..-50, 300-323 for the tufted block, the map's polygon runs to 336; it is on
  the generous side).
* Left of the oval: mown rough to the cart path (x -85 at 280, -110 at 290). The checked ring covers it. On the CIR
  it is pink (growing, mown) like the other rough. Agreed.
* Lower left, beyond the cart path at 215-280 (x -120..-66): weeds and brush around two tee pads of another hole.
  It is NOT mown. The map has it as "unverified" (hatched in `h8_fill`), i.e. half trees. That is about the right
  price for it, so no edit. Only a short pull gets there (the oval's edge touches the path at (-75, 270)).
* Right of the oval: fairway to x -15, bank, then native from x -28 at 312. The photo agrees (tan, tufted slope up
  to the trees).
* Trees inside the dog-leg start at x +5..+30, 55-80 yds right of the Driver's finish. Not in play for this line.

The line itself. From the Back tee the 50 L line passes directly over the left fairway bunker (mapped sand at x
-40..-30, 218-228; the line is at x -39 at 222). Carry to clear it is 228; the Driver's cold carry is 264, so it
clears by 36. That bunker is what Will will see and aim at. The ball lands at about (-46, 262), on the fairway's
left edge coming in at an angle, and runs up the fairway. Near the tee the line passes 15-20 yds right of the tree
block on the left (edge x -40 at 100-130) and over the corner of the small pond at 108-135 (x -53..-18): no carry
issue for a Driver.

Ball that runs through the bend: at x -50 the fairway ends at about 300, then the bank, then the square from ~305.
At x -30 it ends at 305 and the native slope starts at 312. A 300+ total is the 10 % long tail; the map prices both.

DECADE view: the oval's centre is on fairway, the left 95 % edge is the cart path and the right 95 % edge is the
fairway's far side. Penalty-type ground (square, native slope) is only long. A good player sees a wide target with
a bunker to fly as the line. Driver is right from Back. 2-wood (+0.062) lands in the same place 20 yds back.

Middle: the 4-wood oval (-35, 258 in the Middle frame) is the same fat part of the fairway. The 2-wood's oval top
touches the square and the Driver's is centred on the square and its bank (`m8_fill`), so 4-wood, with the Driver
+0.249, is what the picture says.

Numbers: finish (-47, 286) to the green (-113, 371) = 108, as the table has it. Fairway 66 % for a 71-yd oval on a
55-60 yd target: believable.

**T1 (page text, no map change).** Will's question on this hole will be "50 yards left of what?". Suggest a
condition note for 8 Back: "Line: over the left fairway bunker (228 to clear it; your Driver carries 264 in this
cold). Unmown square past the bend from 300." And the whole-hole picture still cuts the green at the left edge
(HANDOFF item "8's green out of frame", not done).

**P3 (optional, low). add, hole 8, kind `native`:** the tan grass between the square and the mapped right-hand
native, which is the same grass as the mapped slope. hole-frame (x, along): (-48,312) (-36,312) (-36,345) (-52,345)
(-56,336) (-48,330); lon/lat [-90.1458346, 38.6554193], [-90.1457605, 38.6553394], [-90.1454802, 38.6554992],
[-90.145579, 38.6556057], [-90.1456802, 38.6555888], [-90.1456817, 38.6555065]. Sure it is unmown in Aug 2023: 70 %.
Reached only by a 312+ Driver from Back (about 3 %); from Middle it backs up the 4-wood pick. I do not expect it to
change anything.

## Hole 9 (par 4, 390 Back / 360 Middle): Driver 6 R in the wind (book 13 R), Middle 4-wood 3 R. Verdict: fine

Renders: `h9_fill` (180-400 with the lie map), `h9_none` (200-360 photo). DTM cross-sections at 290, 320, 340.

* Under the Driver oval (6, 290): fairway x -8..+28, rough both sides. The fairway ends at 308. The gap at 310-330
  before the second piece of fairway is mown rough. I checked it for a ditch because fairways usually break for a
  reason: the lidar ground is flat across it (0.5 ft dip). No ditch.
* Left: brush from x -20 (mapped native from -20 at 275-300, -28 above 300), then the pond (tip at x -37, 290).
  Photo and map agree; the DTM has a ridge at x -25 and the pond floor at -45.
* The blue strip at 300-360 (x -47..-29): this is the one that looks like a cart path on the photo (a grey line).
  The lidar ground has a trench 5-7 ft deep there (bottom at x -45 at 320, x -35 at 340). It is a ditch. Leave it.
* Right: rough to x +45, a tan band to the cart path at +50, trees from +55. The map starts "trees" at +48. The
  removed "fescue" band (x +30..+45) shows mowing stripes; I agree with removing it.
* The aim: trouble edges at x -20 (left) and +48 (right) at 290; the midpoint is +14. The book's 13 R (wind version:
  aim 6 R, finishes 14 R) is exactly the DECADE centre of the two edges. Right bunkers at 237-248 (x 22-33) are
  flown by the Driver's 265 carry and are level with a 4-wood's 245 carry.
* Driver vs 2-wood (0.023-0.030): no penalty edge is nearer to the Driver's oval than to the 2-wood's, and the
  Driver leaves 99 instead of 120. Driver is what a DECADE player hits; the call is close because the fairway
  narrows and ends at 308.
* Middle: 4-wood finishes at the same spot as the Back Driver (290 in the Back frame). Consistent.
* Numbers: finish (14, 290) to the green (22, 389) = 99, as in the table. The note says "about 108 yds in" (Q2).

## Hole 7 (par 3, 180 Back / 160 Middle). Verdict: fine, one map doubt short of the green

Renders: `h7_fill`, `h7_none` (110-220).

* Green: photo x -11..+12, 161-191, centre 176. The mapped green matches within 1-2 yds. Bunkers right (168-178) and
  the pot bunker (149-154, x 22-27) are mapped where they are.
* Box: 177-181 "card" yds = about 173-177 on the map, i.e. on the centre, a touch short. Sensible: trees and a
  tan band are long, the surround left and right is mown.
* Plays like: 179 + 0 elevation + 1 wind + 7 cold = 187. Wind from 342 on a hole heading 61: 79 deg off the nose
  from the left, so 1 mph into and 5 across, left to right. The page says exactly that, and "start it 6 yds left".
  Direction and size are right. 6-iron (carries 185) for 187: right club.
* **Short of the green on the line is unmown.** In the photo the mower line runs from (-25, 163) through (0, 156)
  to (15, 146) and down to (17, 112); inside it is tufted tall grass with two trees. The map has the left half of
  it as trees ("recovery", from the lidar canopy) and the right half (x -5..+17, 112-157) as rough.

**P2. add, hole 7 (par-3 surround), kind `native`:** hole-frame (x, along): (-6,112) (17,112) (16,135) (14,146)
(6,153) (-3,157) (-8,158); lon/lat [-90.149446, 38.6536852], [-90.1493297, 38.6535192], [-90.1491231, 38.6536176],
[-90.1490319, 38.6536757], [-90.149008, 38.6537611], [-90.1490167, 38.653842], [-90.1490327, 38.653882].
Sure: 75 % that it is unmown (Aug 2023 photo); its top edge is 4-5 yds short of the green's front. Effect: only a
shot 20+ yds short finds it, so the box should move at most a yard deeper. Test with the par-3 target solve; apply
only if the box moves.

* Middle 7: the page says card 160, map 155, and FEATURES_1_9 (F1) measured the Middle pad at 159. The box (157-162)
  follows the card. Unchanged from the HANDOFF ("not applied"); Will should laser it.

## Hole 12 (par 3, 131 Back / 115 Middle, peninsula). Verdict: fine

Renders: `h12_fill`, `h12_none` (70-180).

* Water: lake left (wall at x -17 beside the green), the outlet channel short (crosses the line at 98-110, the
  green's front is 116), lake long from 150 (the green's back is 146). All mapped where the photo has them. Right is
  grass and one bunker (x 16-20, 114-122): "the safe miss is right" is correct.
* Box: centred on x 0, 129-133. The photo green is x -14.5..+11 at 131, so the box is 1.5 yds right of the true
  centre, with 16 yds to the wall on the left and 11 to the right edge. With water left and grass right that is the
  correct side to favour.
* Plays like: 131 - 1 + 2 + 5 = 137. Hole heads 269, wind from 336: from the right-front, 2 into and 5 across,
  right to left, pushing the ball toward the lake. The page says "moves the ball about 6 yds left: start it that
  far right". Right direction. PW (carries 138) for 137: right club.
* Carry: 112 clears the channel's far bank and 116 is the front edge; everything in the bag for this shot does.

**P4 (optional, low). replace, hole 12 green polygon:** the mapped green's left edge is at x -11.5, the photo's at
-14.5 (the collar to the wall is 2 yds, the map has 5.5). Shift the left edge 3 yds left between 122 and 142. It
makes the left water slightly less likely from the engine's view of "on the green", nothing else. Sure: 70 %.

## Questions for the lead

**Q1. Par-3 club line, Middle.** Middle 7: "Plays 167 yds · 8-iron carries 162". Middle 12: "Plays 120 yds · SW
carries 113" (peninsula, water short). Back shows clubs within 1-2 yds of the plays-like number (6-iron 185 for 187,
PW 138 for 137). If "carries" is the 70 F carry and the club is chosen on carry + release, say so in the line
("SW carries 113, finishes ~118"); if the ladder simply has no club nearer, Will will read these two as a club
short. On 12 short is the channel, 21 yds short of the centre, so SW is not dangerous, but it reads wrong.

**Q2. "To green" vs "about N yds in".** Same card, two numbers: 8 Back 108 / 111, 9 Back 99 / 108, 11 Back 118 /
128. The table's number matches the geometry from the finishing spot. If the note's is the average over all
swings (mishits included) in the calm book, label it ("average 108 left") or drop it; a 10-yd disagreement on one
screen invites the "this can't be right" reaction.

**Q3. qa.json `adj` field** on the par 4s repeats hole 7's par-3 line ("179 target±0 elevation+1 wind+7 at 41°F").
It is not visible on the page pictures I rendered; it looks like a stale hidden element. Harmless unless something
reads it.
