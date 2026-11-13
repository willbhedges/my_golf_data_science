# REVIEW C: holes 13-18 as Will would see them on the tee (Back first, then Middle)

Version 2 (Nov 13). Read-only review of the page built by run 43358518302 (`wind_page/index.html`, commit
cee080946; not rebuilt since) against NAIP 2023, the 1 m 3DEP DEM and the Dec 2023 lidar grid. The engine's zones
were painted in engine order (later zone wins): par 4 / 5 from `truth/course.py` (working tree of 06:29Z), par 3s
from `truth/package.json` plus `opt/par3_features.json` in the par-3 solver's paint order. Frame everywhere: x = yds
right of the Back tee line, along = yds from the Back tee. Renders and scripts were in scratch and are deleted.

Version 1 judged the par-3 surrounds on the raw package zones; the box solve uses the corrected surrounds, which
match the photo. Those two findings are withdrawn below.

## Summary, most important first

| # | hole | verdict | one line |
|---|---|---|---|
| 1 | 13 | fine, with one test and one page line | The ditch is real, is in the map as water where the photo and the DEM put it, and is painted after the rough rectangle, so the engine sees it. It runs diagonally (287 yds at x -40, 312 at x -20, 340 on the line). Mapped 4-5 yds wide; bank to bank it is 8-9. With an 8-yd strip my own swing count puts 0.4 % of Back Drivers in it (unchanged) and 1.2 % of Middle Drivers (0.6 % as mapped; 3 % with x1.25 roll). The page says nothing about a ditch: Will will ask. |
| 2 | 18 | doubt (map), play fine | Left fescue: the mapped block follows the cart path, the real block does not. Its fairway-side edge is 10-12 yds closer than mapped at 300-340 and the block goes on, unmapped, from 345 to 395. And a "water" strip (stream) at x -92..-104, 320-390 lies on the cart-path berm: the DEM shows a 3 m ridge there, no channel. None of it is inside a Driver oval (Back or Middle). |
| 3 | all par 4 / 5 | doubt (wording) | "it finishes about 4 yds left at the dashed spot" reads as 4 yds left of the tee line; it means left of the dot (15: aim 20 right, finish ~16 right). And the table's "to green" (239 / 138 / 235) and the note's "about N yds in" (249 / 144 / 249) are two numbers for one shot. |
| 4 | 13 | doubt (page) | The three right bunkers end at 268 yds; the cold Driver carries 267. About 7 % of Back Drivers finish in sand. The page gives no carry number. |
| 5 | 14 | fine, one question | Corrected surround matches the photo (brush 5-7 yds off the left edge at 205-215, crowns over the top of the left bunker). Wind line asks Will to start the ball 7 yds left of a box whose penal side is the left. |
| 6 | 16 | fine | 4-wood, finish (x +7, 263). Fescue edge x -20..-22 and the mound x +8..+43 / 265-297 both match the photo. The lay-up reason is visible. Middle long iron: fine. |
| 7 | 15 | fine | Driver finish (x +16, 291): fairway x -15..+40, cart path +45, fescue from +49 (mapped from ~+52), left fescue at -38. |
| 8 | 17 | fine | Corrected green, four bunkers in the open, crowns from x +22..28. "Safe miss is left" is right. |

Wind directions and signs check out on all six (hole bearings 65 / 73 / 250 / 43 / 39 / 155, wind from 336-323):
13 L-to-R 5.0; 14 L-to-R 4.9 with 0.7 of tail (-1 yd); 15 R-to-L 4.9; 16 and 17 L-to-R 3.9 with 1.1 of head (+2 on
17); 18 3.9 behind. No pick on 13-18 is a lay-up without a visible reason; every Driver hole is a Driver hole.

## Hole 13 (par 5, 533 / 520): Driver; Back aim 5 left -> finish x +3 at 295; Middle aim 2 right -> finish x +10

Seen on: lie-fill render x -90..90, along 200-400; 9 px/yd photo close-up of the ditch; DTM of the same window;
cross-sections on the 1 m DEM every 10 yds; lie-fill and photo of 330-570.

* The ditch. Photo: a pale, stone-lined dry channel 4-5 yds wide. DEM: flat bottom ~3 yds wide, 0.6-0.7 m below the
  fairway side and 1.0-1.1 m below the far side, each bank ~3 yds wide (about 20 % slope). Bottom centreline
  (x, along): (-41, 286) at the pond's corner, (-34, 295), (-25, 304.5), (-18, 314.5), (-11, 325), (-4.5, 335.5),
  (+1.5, 347; footbridge at ~350), (+8, 357.5), (+14, 367), then on to the big pond at 395. The mapped water strip
  sits on this line within 1-2 yds. No priority problem: it is drawn after rough zone 36 and fairways 39-41.
* What reaches it. On the line a ball needs 340 (finish is 295). At x -20 it needs 312, i.e. 17 long and 23 left.
  With the engine's own pattern (carry sd 7, 15 % mishits, fixed roll) my count is 0.4 % of Back Drivers. From
  Middle the finish is 308 in this frame and the engine has already moved the aim 7 yds right for it.
* PROPOSAL 13-A (replace the ditch part of the water zone, or add on top; kind water; how sure: 0.8 on position,
  0.7 on width): an 8-yd strip, bank to bank. Hole-frame (x, along):
  (-37, 297.6), (-28.1, 307), (-14.4, 327.2), (-8, 337.5), (-2, 349), (10.6, 369.1), (17.4, 364.9), (5, 345),
  (-1, 333.5), (-14.7, 312.2), (-21.9, 302), (-31, 292.4), (-37.8, 283.5), (-44.2, 288.5).
  Lon/lat: [[-90.1481364, 38.6577495], [-90.1480075, 38.6577156], [-90.1477546, 38.6576833],
  [-90.1476281, 38.6576712], [-90.1474921, 38.6576663], [-90.1472449, 38.6576419], [-90.1472548, 38.6575766],
  [-90.1474992, 38.6576002], [-90.1476353, 38.6576051], [-90.1478988, 38.6576336], [-90.1480277, 38.657652],
  [-90.1481594, 38.6576866], [-90.1482743, 38.6577066], [-90.148255, 38.6577717]].
  Why: a ball stopping on the fairway-side bank rolls in; the mapped strip leaves 2-3 yds of "rough" between the
  fairway edge and the water, which stops rolling balls short of it in the engine. Own count with the strip added
  (100,000 swings): Back 0.4 % water (same as now); Middle at finish x +10: 1.2 % (0.6 % now), 3.0 % with roll
  x1.25; Middle at x +16: 0.5 %. Expected: Back unchanged, Middle aim 1-3 yds further right, Driver stays. By the
  3-yd rule this is probably a no-edit; test Middle only.
* Page line (Back and Middle), since the page is silent and Will has asked this question twice: "Ditch crosses
  from the left pond: 310 to reach it down the left edge, 340 on the line. In the book."
* Right bunkers: three, x +12..+35, 238-268. Driver carry in the cold is 267 on the page, so a ball 10-30 right
  that is a few yards short is in sand: 7 % of Back swings in my count (1.5 % from Middle). The engine prices it;
  the page should print "268 to carry the right bunkers" because that is the number Will wants on the tee.
* Right fescue (mapped from x +45 at 220-345): matches the photo's edge at 230-300. Past 345 the right side is
  weeds between the ditch and the big pond (x +30..+100, 345-395) and brush north of the pond by the green (x +15..
  +100, 490-560), both unmapped. No tee ball gets there; it matters only if second shots are ever simulated.
* Fairway 70 % (Back) fits the picture. Driver is the play from both tees.

## Hole 18 (par 5, 527 / 494): Driver; Back aim 14 right, finish 300; Middle aim 7 right, finish 341 in the Back frame

Seen on: lie-fill and photo x -100..80 / 170-370 and x -130..90 / 300-560; Dec 2023 lidar height x -130..10 /
180-420 with the zones outlined; DEM profiles across the "stream" at 310-385.

* The play. Fairway x -27..+42 at 300-340. Bunkers left at x -8..0 / 258-270 and x -30..-10 / 290-305 (mapped).
  Tree line right at x +45 (200), +50 (240), +58 (300): mapped edge within 3 yds of the crowns on the photo. Aim 14
  right puts the oval at x -20..+48: 24 yds from the nearer bunker edge, 41 from the trees. That is the DECADE
  aim. Nothing stops a long straight ball before the bunker at (-12, 415). Middle: finish (x +6, 341), fairway
  -28..+42, right bunkers start at 385: fine. Back markers 17 yds up: finish 317, same fairway: the pill is enough.
* Left fescue (lidar height: the tall-grass band is unmistakable, 0.2-0.4 m against 0.03):
  band at 300 is x -75..-38; 320: -85..-45; 340: -92..-52; 360: -98..-53; 380: -100..-55; it ends at a path at
  ~395. The mapped native zone has its fairway-side edge at -45 / -57 / -63 at 300 / 320 / 340 and stops dead at
  345 (the rectangle's top). At 200-260 the mapped edge is within 2-3 yds of the band.
  PROPOSAL 18-A (add native; how sure 0.85, lidar + photo, agrees with FEATURES_10_18 item 5): hole-frame
  (x, along): (-30, 260), (-34, 280), (-38, 300), (-45, 320), (-52, 340), (-53, 360), (-55, 380), (-52, 395),
  (-100, 395), (-100, 380), (-98, 360), (-92, 340), (-85, 320), (-75, 300), (-62, 280), (-52, 262).
  Lon/lat: [[-90.1416328, 38.6612009], [-90.1415057, 38.6610658], [-90.1413786, 38.6609306],
  [-90.1412229, 38.6608059], [-90.1410673, 38.6606812], [-90.1409687, 38.6605355], [-90.1408606, 38.6603933],
  [-90.1408224, 38.660271], [-90.1403659, 38.6604386], [-90.1404326, 38.6605504], [-90.1405407, 38.6606926],
  [-90.1406868, 38.6608208], [-90.1408425, 38.6609455], [-90.1410266, 38.6610598], [-90.1412394, 38.6611635],
  [-90.1414146, 38.6612628]]. Paint it before the fairway and sand zones.
  Own count, Back Driver at x +14: native 0.2 % -> 0.4 %. No aim or club change expected.
* "Stream" on the cart path. Water zone 29 of hole 18 in `truth/course.py` (12 points, x -121..-69, along
  292-390; first vertices lon/lat [-90.1406052, 38.6607235], [-90.1405482, 38.6607131], [-90.1404041, 38.6605837])
  runs along the cart path. DEM across it: the strip sits on a crest 2-3 m above the ground on both sides at 330,
  350 and 370; there is no channel. PROPOSAL 18-B: remove it (how sure 0.8). It is 60+ yds left of every oval, so
  nothing on the page moves; it is the "does this hole think the cart path is a creek?" kind of thing.

## Wording on every par 4 / 5 (finding 3)

* "Aim at the dot ...; it finishes about 4 yds left at the dashed spot (wind 6 left)" under a header "Aim 20 yds
  right" (Back 15). I read "4 yds left" as a position on the hole and reviewed 15 at x -4 until the header put me
  right. Say "finishes 4 yds left of the dot" or give the finish like the aim ("finishes 16 yds right").
* The same lines show wind 7 right / finish 8 right (13), wind 6 right / finish 7 right (16), wind 6 left / finish
  4 left (15): a constant 1-2 yds to the right that the text does not explain.
* Table "to green" vs note "about N yds in": Back 13 239 / 249, 15 138 / 144, 16 91 / 93, 18 235 / 249. Presumably
  finish spot vs average over all swings. Label the second "on average" or drop it.

## Hole 14 (par 3, 200 / 185): plays 201, 5-iron (198); Middle plays 187, 6-iron

Seen on: 8 px/yd lie-fill (corrected surround) and photo, x -50..50, along 150-240.

* Corrected surround against the photo: brush (native) left from x -17 at 210 and x -9 at 218, i.e. 5-7 yds off the
  green's left edge at the middle and 1-2 yds at the back-left corner; crowns over x -30..-14 at 183-204, covering
  the top lobe of the left bunker; open rough right out to the cart path at x +38; crowns long only from ~228
  (10 yds past the back edge). All as the photo shows. Green outline within 1-2 yds.
* Box (0..+5 right of centre, 2-9 short of the middle): right. "The safe miss is right": right.
* 196 - 1 (3 ft down) - 1 (0.7 mph tail) + 7 (46 F) = 201: every sign right. The box plays 197-203, the 5-iron's
  198 is inside it and the 6-iron is not: right club.
* QUESTION 14-A: "The wind moves the ball about 7 yds right: start it that far left of the box" puts the start
  line at x -4.5..-2, over the left third of the green, with the bunker short-left and brush 6-13 yds further
  left. 7 yds for 5 mph is 1.5 yds / mph, on the high side for a 5-iron. If the wind is 2 mph for his swing the
  ball stays on the penal side. Should the page ask for less than the full drift when the penal side is upwind
  (start it 3-4 left, accept a finish right of the box, where the miss is free)? On 17 the same instruction is
  safe (trouble is downwind).

## Hole 16 (par 4, 354 / 325): Back 4-wood on the line, finish (x +7, 263); Middle long iron, finish (x +8, 242)

Seen on: 5 px/yd lie-fill and photo, x -70..70, along 180-370.

* Left fescue: mapped edge x -20..-22 at 245-300; the photo's tan edge is at x -22, then a mown strip, then
  fairway from x -17. Block ends at 300; mown rough between it and the pond. As mapped.
* Mound right: mapped x +8..+43, 265-297 as sand; photo's tufted mound with the stone edge at x +10..12 / 280-295
  has the same footprint. Pond front edge 305-312 for x -45..+5 with its reed ring as native. As mapped.
* The play. 4-wood carries 248 into the 40-yd-wide part (x -18..+25 at 240-262) and stops at the mouth of the
  25-yd neck (x -15..+8 at 265-300). Driver (268 / 298) lands level with the mound and runs at the pond. 2-wood
  finishes inside the neck. Long iron has 52 yds of fairway and leaves 140. Lay-up, with reasons you can point at.
  Finish +7 keeps the 95 % left edge (x -20) on the fescue line: not one yard further left. Own count: fairway
  82 %, native 1.4 %, mound + bunkers 3.6 %.
* Middle: long iron to the widest part, 111 in, 94 % fairway: fits.

## Hole 15 (par 4, 428 / 408): Driver; Back aim 20 right, finish (x +16, 291); Middle finish (x +10, 307)

Seen on: lie-fill and photo, x -90..90, along 180-380.

* Bunkers x -8..+22 at 222-250 are carried by 12+ yds (262). Fairway at 291: x -15..+40. Left: mown rough to x -38,
  then fescue (mapped edge on the photo's edge). Right: path at +45..48, fescue from +49 on the photo; the mapped
  right block starts at ~+52 at 291 (its edge runs diagonally from +42 at 345 to +70 at 235). 3 yds generous;
  QUESTION 15-A: pull the right native edge in to the path's outer edge (x +49 at 280-300) and see whether the aim
  comes left of +14.5. The oval's right 95 % edge is +51.
* Left fescue rectangle stops at 345; the fescue goes on to 380+ (x -60..-40). Out of reach from Back and Middle.
* Middle "close call, 2-wood +0.044": the Driver finishes at 307 where the fairway narrows to x -18..+33. Fair.

## Hole 17 (par 3, 195 / 173): plays 197, 5-iron; Middle plays 176, 7-iron

Seen on: 8 px/yd lie-fill (corrected surround) and photo, x -50..50, along 150-240.

* Corrected green (x -9..+13, 177-208) and all four bunkers match the photo; the three right bunkers are in the
  open, crowns from x +22..28; small fescue patch long-right at x +20..38 / 205-220. Left is open to the path
  (x -35). Box short and a touch left: right. "The safe miss is left": right.
* 190 - 1 + 2 (1.1 mph head) + 6 = 197: signs right. Sat pick 5-iron over 6-iron by 0.018: a near tie the page
  shows as a plain "5-iron" (Back). Worth the close-call treatment the tee shots get.

## Withdrawn from version 1

* 14 "tree zone touches the green's left edge / dips to 213 long-right" and 17 "trees long-right 1-2 yds off the
  green": true of the raw `package.json` zones only (which still feed the `haz` note text in `course.py`: "Trees
  left, trees long" on 14); the box solve and the picture agree.
* 15 "finishes x -4": misreading of the page sentence (see wording).
