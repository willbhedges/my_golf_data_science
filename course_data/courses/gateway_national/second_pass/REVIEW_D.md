# REVIEW D: the second shot on every par 4 and par 5 (Back tees)

Nov 13. Read-only review. For each of the 13 holes I put the picked tee shot's finishing spot (calm book aim from
`truth/v2/v2_decisions.json`; finish taken as 290 yds for the Driver, 272 for the 2-wood, 262 for the 4-wood) on the
NAIP 2023 0.3 m photo (`course_data/packages/gateway_national/imagery/naip_rgb.tif`, `naip_nir.tif` for
colour-infrared, `dem.tif` for relief) and drew the engine's zones from the working-tree `truth/course.py` and the
green polygon from `truth/package.json` on top. Frame: the course module's (x = yds right of the Back tee line,
y = yds from the Back tee). Rendered at 3-9 px / yd; positions good to about 2 yds. Renders were in scratch.

Not checked: the ground itself (photo is Aug 2023), mowing changes since, and the lidar vegetation grid outside the
front nine (the cached grid is empty on 6, 13, 15). No engine runs.

**What the engine does with any of this.** It does not simulate the second shot. A finishing spot is valued from
its lie and its distance to the green centre. So nothing below changes a tee club or tee aim (except through the
lie under a tee ball, which reviews A-C covered). These findings are for the page notes and for Will's second-shot
targets. The lead should decide whether to add the polygons to the map for completeness (they are harmless to the
tee solve: none is inside a tee-shot oval) or only to use the words.

## Findings, most important first

| # | hole | what | how sure |
|---|---|---|---|
| 1 | 6 (par 5) | **A pond behind and back-left of the green is not in the map.** Water starts 15 yds past the back edge and 15 yds off the back-left corner. A tree polygon lies partly on it. | 0.95 (photo and colour-infrared) |
| 2 | 6 | **The whole right side from 350 to the green is an unmown field, mapped as rough.** Its edge is 12-14 yds right of the green's right edge and just outside the right bunkers. | 0.7 that it is unfindable in November (lush and uniform in Aug 2023, with hay windrows at 350-420; it may have been cut) |
| 3 | 15 | **Dense tall vegetation 5-8 yds behind the green, not in the map.** Nearest at the back-right corner. | 0.8 on position, 0.7 that it is "native" (bright in infrared, on a low mound) |
| 4 | 13 (par 5) | Map is right, but it matters for the shot into the green: **the ditch runs 3-6 yds off the green's right edge** from 515 to 545, with tall grass beyond it. No bail-out right. | 0.9 (photo and DEM channel agree with the mapped strip) |
| 5 | 3 (par 5) | A strip of brown tall grass in front of the right tree line. By the green its inner edge is at x +73 (5-6 yds off the green's right edge); the map's tree edge is at +82..+88. It also wraps behind the green, 12 yds past the back edge. | 0.8 |
| 6 | 1 | Tall grass 10-13 yds right of the green and 12 yds behind it; the mapped native stops at 345. | 0.8 (2023 lidar vegetation shows it) |
| 7 | all | The note's "about N yds in" is 5-9 yds longer than the geometry on 10 of 12 holes (table below). Same point as REVIEW B Q2 / REVIEW C #3; the table's "To green" is the right number. | certain |

All 13 green polygons sit on the photo greens within about 2 yds, and the engine's green centre is inside the middle
of each. No green needs moving.

## Approach distance: geometry against the page

Straight line from the finishing spot to the engine's green centre, against the page note of the committed build.

| hole | finish (x, y) | green centre (x, y) | geometry | page note "about N yds in" |
|---|---|---|---|---|
| 1 | -8, 290 | +8, 374 | 85 | 91 |
| 2 | +9, 290 | +31, 415 | 127 | 133 |
| 3 | -5.5, 290 | +53, 625 | 340 | 345 |
| 5 | +3.5, 290 | -12, 453 | 163 | 170 |
| 6 | +6, 290 | -7, 531 | 241 | 246 |
| 8 | -45, 290 | -113, 371 | 105 | 111 |
| 9 | +13, 290 | +22, 389 | 99 | 108 |
| 10 | -17.5, 272 | -18.5, 270 | on the green | 19 |
| 11 | +17.5, 290 | +76, 395 | 120 | 128 |
| 13 | +2, 290 | +9, 534 | 244 | 249 |
| 15 | +13.5, 290 | -23, 424 | 139 | 144 |
| 16 | +6, 262 | +9, 354 | 92 | 93 |
| 18 | +14, 290 | -49, 526 | 245 | 249 |

My 290 is crude (the cold Driver may finish 285-295), so read the geometry column as +/- 5. The note's number is
the average over all swings, mishits included. If only one number is shown, it should be the table's.

## Hole 6 (par 5, 530): Driver, finish (+6, 290), 241 to the centre

* **Pond (finding 1).** Photo: open water behind the green from x -48 to +13. The green's back edge is at 548 on
  x -5; water is at 562-567 straight behind and reaches down to 539 at x -45 (a tail along the left). A dead tree
  stands at (+10, 560). The map has no water here; a "recovery" polygon covers the tail and part of the bank.
  **Proposal 6-A, add, kind water** (hole frame x, y):
  (-45.8, 573), (-28, 575), (-20, 569), (-5, 567.5), (2, 575), (10, 582), (13, 578), (12, 567), (3, 561), (-3, 564),
  (-20, 564), (-27.5, 561), (-37, 550), (-45, 539), (-47.5, 550), (-48, 567).
  Lon/lat: [[-90.1522124, 38.6529297], [-90.1523125, 38.6530546], [-90.1522923, 38.6531354],
  [-90.1523465, 38.6532520], [-90.1524494, 38.6532771], [-90.1525521, 38.6533114], [-90.1525280, 38.6533479],
  [-90.1524194, 38.6533799], [-90.1523216, 38.6533346], [-90.1523226, 38.6532794], [-90.1522450, 38.6531533],
  [-90.1521824, 38.6531084], [-90.1520350, 38.6530773], [-90.1518945, 38.6530573], [-90.1519871, 38.6529994],
  [-90.1521456, 38.6529349]].
  Paint it after the recovery polygon so the water wins.
* **Right field (finding 2).** From 350 on, everything right of the mown rough is one unmown field. Inner edge
  (x at y): +50 at 350, +52 at 380, +50 at 400, +44 at 420, +38 at 440, +36 at 460, +24 at 480, +21 at 500, +23 at
  520, +20 at 540, +12 at 556. The green's right edge is at +8 and the right greenside bunker ends at +17. The
  mapped native on the right stops at 345.
  **Proposal 6-B, add, kind native** (x, y): (50, 350), (52, 380), (50, 400), (44, 420), (38, 440), (36, 460),
  (24, 480), (21, 500), (23, 520), (20, 540), (12, 556), (14, 566), (90, 566), (90, 350).
  Lon/lat: [[-90.1505403, 38.6544380], [-90.1508332, 38.6543455], [-90.1510132, 38.6542591],
  [-90.1511750, 38.6541431], [-90.1513368, 38.6540270], [-90.1515169, 38.6539407], [-90.1516513, 38.6537801],
  [-90.1518267, 38.6536863], [-90.1520250, 38.6536296], [-90.1522005, 38.6535358], [-90.1523153, 38.6534192],
  [-90.1524190, 38.6533983], [-90.1527658, 38.6539619], [-90.1507228, 38.6547347]].
* **Second shot.** The hole is two fairways split by a diagonal chain of six bunkers from (-12, 415) to (+12, 505).
  Lay-up: the upper (left) fairway, finish about (-22, 465), leaving 65-70. It is 30 yds wide there (x -37..-7);
  tree crowns on the left reach x -30 at 390-410, the bunker chain is on the right. Going for the green from 241:
  long is the pond, right is the field, left is trees and the cart path; the only safe miss is short on the upper
  fairway. The page should not suggest that long is safe.

## Hole 15 (par 4, 428): Driver, finish (+13.5, 290), 139 to the centre

* **Behind the green (finding 3).** The green's back edge is at 443-444 (x -25..-15). A block of dense, dark
  vegetation starts at 446-449 from x -20 to +7 and at 450-452 further left, and runs to about 473. In infrared it
  is the brightest thing on the hole; the DEM has a low mound under it. Lighter tall grass surrounds it out to the
  cart paths. Nothing is mapped there.
  **Proposal 15-C, add, kind native** (x, y): (-44, 452), (-30, 450), (-20, 449), (-12, 447), (-4, 446), (7, 448),
  (11, 456), (9, 466), (0, 473), (-25, 473), (-44, 465).
  Lon/lat: [[-90.1474630, 38.6583723], [-90.1474929, 38.6584864], [-90.1475184, 38.6585667],
  [-90.1475270, 38.6586342], [-90.1475455, 38.6586990], [-90.1476043, 38.6587787], [-90.1476976, 38.6587875],
  [-90.1477893, 38.6587442], [-90.1478266, 38.6586550], [-90.1477380, 38.6584612], [-90.1475915, 38.6583362]].
* For Will: 139 in, a back pin is a front-number shot. Two bunkers right (mapped, on the photo).

## Hole 13 (par 5, 533): Driver, finish (+2, 290), 244 to the centre

* Map agrees with the photo and the DEM from the ditch crossing to the green. The pond's left edge is at x +22..+25
  from 400 to 485, where the photo has it.
* **At the green (finding 4):** the ditch leaves the pond at (+40, 485), reaches (+13, 508) at the green's
  front-right corner and then runs up the right side at x +20 (520), +32 (540), +40 (550). The green's right edge
  is at x +15..+22. So the channel is 3-6 yds off the putting surface, with unmown ground beyond it. Left of the
  green is one bunker at (-10, 540) and open rough.
* **Second shot.** Lay-up: finish about (-15, 430-445), between the left bunker (-22, 388-402) and the centre
  bunker (-13, 458-472), leaving 90-105. That is 35+ yds from the pond. Going for it from 244: the miss is left,
  never right.
* No polygon proposed. Optional: a native block right of the ditch (x +25..+75, 490-550) for completeness only.

## Hole 3 (par 5, 630): Driver, finish (-5.5, 290), 340 to the centre

* **Second shot.** A 4-wood (about 262 cold) finishes near y 550, leaving about 80. The fairway there is x +15..+58.
  The straight line from the finishing spot to the green crosses y 550 at x +40, 30 yds from the tree line; the
  middle of the fairway is +35. Left is mown rough to the cart path at x -10. Favour +30. The three left bunkers at
  470-485 (x -10..+15) are short of this shot.
* **Right edge (finding 5).** Lay-up zone: brown strip from x +68, trees from +72; the map's tree edge is at
  +70..+72. Fine. By the green: brown strip inner edge +72..+74 from 600 to 640, map's tree edge +82..+88. It
  wraps over the back at 652-655 (green's back edge 640).
  **Proposal 3-D, add, kind native** (x, y): (72, 560), (73, 600), (74, 630), (70, 645), (55, 653), (35, 652),
  (35, 658), (60, 660), (78, 650), (84, 630), (84, 560).
  Lon/lat: [[-90.1511977, 38.6572095], [-90.1514773, 38.6569635], [-90.1516889, 38.6567803],
  [-90.1517587, 38.6566648], [-90.1516928, 38.6565347], [-90.1515258, 38.6564345], [-90.1515665, 38.6563968],
  [-90.1517804, 38.6565173], [-90.1518567, 38.6566760], [-90.1517691, 38.6568336], [-90.1512939, 38.6572733]].
  Paint it before the tree and OB polygons so they still win where they overlap.

## Hole 1 (par 4, 376): Driver, finish (-8, 290), 85 to the centre

* The mapped native on both sides stops at 345, where the rough rectangle stops. The grass does not. The 2023
  lidar vegetation grid shows standing grass from x +30..+33 beside the green (right edge of the green +20) and a
  band at 400-408 behind it (back edge 389). Left of the green the two bunkers and the cart path (x -32) come
  first.
  **Proposal 1-E, add, kind native** (x, y): (30, 345), (31, 370), (33, 390), (28, 400), (15, 404), (-5, 402),
  (-5, 412), (30, 412), (52, 400), (52, 345).
  Lon/lat: [[-90.1417826, 38.6626581], [-90.1419514, 38.6628159], [-90.1420771, 38.6629489],
  [-90.1421866, 38.6629822], [-90.1423159, 38.6629346], [-90.1424572, 38.6628116], [-90.1425279, 38.6628726],
  [-90.1422558, 38.6630664], [-90.1420001, 38.6631151], [-90.1416116, 38.6627799]].
* With a wedge from 85 this is low priority.

## Hole 18 (par 5, 527): Driver, finish (+14, 290), 245 to the centre

Fine. Pond, bunkers and green are where the photo has them. The pond is 3-5 yds off the green's left edge (mapped).
Lay-up: finish about (0, 440-460), leaving 75-95; fairway x -40..+30 there, pond edge at x -45. Bunkers at
(-12, 415) and (+30..+37, 400) are short of it. Going for it from 245: miss right (one bunker at (-25, 530), then
rough).

## Fine holes, one line each

* **2** (127 in): green and three bunkers match. Left of the green the unmown ground continues past the mapped
  block's end at 350, but its edge is 20 yds off the green's left edge. No change.
* **5** (163 in): green and bunker match. Tall grass is 20 yds left, 10 yds behind, and beyond the cart path
  on the right. No change.
* **8** (105 in): the line to the green carries the unmown square (x -85..-50, 300-335, mapped). Green and two
  bunkers match; brown grass starts 10 yds beyond the right bunkers. No change.
* **9** (99 in): green, the centre bunker at 355 and the stream on the left match. Trees 30 yds behind. No change.
* **10**: the tee shot is at the green; covered by HOLE10.md. Green polygon matches the photo.
* **11** (120 in): the line to the green is over fairway. The left tall-grass strip continues past the mapped
  block's end at 385 to about 440, 25-30 yds left of the green centre, outside the left bunker. No change.
* **16** (92 in): pond edge, green, the mound and the bunker at (+28, 332) match. The straight line to the centre
  runs along the pond's right bank at 305-325 (bank at x +8); a carry, not a hazard for a 92-yd shot.
