# REVIEW C: holes 13-18 as Will would see them on the tee (Back first, then Middle)

First version (Nov 13). Read-only review of the page built by run 43358518302 against NAIP 2023 with the engine's
zones painted in engine order (`truth/course.py` working tree of 06:29Z; par 3s from `truth/package.json`). Frame:
x = yds right of the Back tee line, along = yds from the Back tee. Renders were made in scratch and are not kept.
Refinements (lidar cross-sections, lon/lat polygons, test solves) follow in a later version of this file.

## Summary, most important first

| # | hole | verdict | one line |
|---|---|---|---|
| 1 | 13 | doubt | The ditch is real, IS in the map (water, drawn after the rough rectangle so the engine sees it) and runs diagonally: 287 yds at x -40, 312 at x -20, 340 on the line, 360 at x +15. The Driver oval (finish 295, x +3, 70 wide) touches it only with a pulled, long ball. The mapped strip is 4-5 yds wide; the lidar channel looks 6-8 yds wide. Test a wider strip (below). The page says nothing about it: Will will ask. |
| 2 | 18 | doubt | Left fescue is under-mapped on its fairway side at 285-345 (mapped edge x -45 / -57 / -63 at 300 / 320 / 340; the photo's tan fescue ends near x -35 / -45 / -50). 10-15 yds beyond the Driver oval's left edge (x -20), so the pick and the aim (14 right) should not move. Test. |
| 3 | 14 | doubt | Tree zone touches the green's left edge at 205-218 (photo: 6-8 yds of grass there) and dips to 213 long-right where the photo is grass to ~226. Both make the box sit right and short; direction is right, size may be 1-2 yds over. Wind line "start it 7 yds left of the box" starts the ball over the left third of the green on the brush / bunker side: a gust-free moment puts it in the trouble. |
| 4 | 13, 15, 18 | doubt (wording) | "To green" in the table (239 / 138 / 235) and "about N yds in" in the note (249 / 144 / 249) differ by 6-14 yds on the same card with no explanation. |
| 5 | 16 | fine | 4-wood, finish (x +7, 263): fescue edge x -20..-22 (3-5 yds off the fairway) and the mound (x 8..43, 265-297) both match the photo. Lay-up reason is visible: 25-yd neck 265-300, pond front 305-310 left of x +5. Middle: long iron to the 52-yd-wide part: fine. |
| 6 | 15 | fine | Driver finish (x -4, 291): fairway x -15..+40, 23 yds of mown rough to the left fescue (x -38), cart path +45 and fescue +48 right. |
| 7 | 17 | fine | Green, 4 bunkers, tree edge right (x +20..22) match. Trees long-right drawn ~5 yds too close (to 1-2 yds off the back-right edge; photo is grass). "Safe miss is left" is right. |

Wind directions and signs check out on all six (hole bearings 65 / 73 / 250 / 43 / 39 / 155 against wind from
336-323): 13 L-to-R 5.0, 14 L-to-R 4.9 with 0.7 tail (-1), 15 R-to-L 4.9, 16 and 17 L-to-R 3.9 with 1.1 head (+2 on
17), 18 3.9 behind.

## Hole 13 (par 5, 533 / 520): Driver, aim 5 left, finishes x +3 at 295 - doubt

Seen on: lie-fill render x -90..90, along 200-400; 9 px/yd close-up of the ditch; DTM of the same window.

* The ditch: pale stone / dry channel 4-5 yds wide in the photo, a clear 1.5-2.5 m trough in the DTM. It leaves the
  pond's north-east corner at (x -45, 285) and runs up and right: (x -40, 287), (-30, 300), (-20, 312), (-10, 326),
  (0, 340), (+8, 350, where a footbridge crosses), (+15, 360), (+30, 400). The map has it as water in the same
  place and it is painted after the rough rectangle, so the engine does see it (no priority problem here).
* What reaches it: a Driver that is both long and left. On the line it needs 340 total (45 past the 295 finish: no).
  At x -20 it needs 312 (17 long and 23 left of the finish spot): a real but small share of swings, maybe 2-4 %.
  2-wood (273) essentially never. The pond (x < -45 at 230-320) takes the big pull.
* Right side: three bunkers x +12..+35 at 238-268 (Driver's 267 carry clears all but the short ones), fescue from
  x +45. Fairway at 295 is x -20..+40, centre +10; finishing at +3 is a sensible compromise between the
  ditch / pond left and bunkers / fescue right. Driver is the play.
* Problem to test (width): the DTM trough is wider than the 4-5 yd strip, and a ball landing on the fairway-side
  bank rolls in. TEST: widen the ditch water strip to 8 yds (2 yds more on each side) between along 285 and 365 and
  re-solve; expectation: Driver stays, aim moves 1-3 yds right. Polygon to follow in the next version.
* Page: there is no line telling Will the ditch is known. Suggest a condition pill on 13 (Back and Middle): "Ditch
  crosses left-to-right: 310 to reach it down the left edge, 340 on the line."
* Numbers: fairway 70 % fits the picture (oval x -32..+38 against fairway x -20..+40). Table "to green 239" vs note
  "about 249 yds in" (see finding 4).

## Hole 18 (par 5, 527 / 494): Driver, aim 14 right, finish 300 - doubt (map detail), play fine

Seen on: lie-fill and plain renders x -100..80, along 170-370.

* Right: tree line at x +45 (200), +50 (240), +58 (300): mapped edge within 3 yds of the canopy. Left: bunkers at
  x -8..0 / 258-270 and x -30..-10 / 290-305, both mapped. Fairway at 300-340 is x -27..+42.
* Aim 14 right puts the oval at x -20..+48: nearer bunker edge 24 yds left of centre, trees
  41 right. That is where I would aim. Driver is the play; nothing stops a long straight ball before 360.
* Left fescue: the native polygon follows the cart path. At 180-260 it covers path + fescue (x -47..-20): right.
  From 285 on the path swings left and the polygon follows it, but the fescue's fairway-side edge does not move as
  far: the photo's tan, tufted ground reaches x -35 at 300, -45 at 320, -50 at 340 while the map stops at -45, -57,
  -63. PROPOSAL (add native, how sure: medium, photo only): hole-frame polygon (x, along) =
  (-30, 270), (-35, 300), (-45, 320), (-50, 340), (-63, 340), (-57, 320), (-45, 300), (-33, 275). Lon/lat to follow.
  Expected effect on the Driver from the card spot: none (the oval's left edge is x -20).
* Back tee 17 yds forward: finish 317 at x +14, still fairway x -27..+42, nothing new in reach. The pill is enough.

## Hole 14 (par 3, 200 / 185): plays 201, 5-iron (198) - doubt

Seen on: 8 px/yd lie-fill and plain renders x -50..50, along 150-240.

* Green polygon matches the photo within 1-2 yds (x -10..+12, 181-217). Left bunker is mapped a little small (the
  sand reaches x -8 at 178; map stops at x -11, 181).
* Tree / brush zone: its edge runs (-30, 193) - (-15, 205) - (-3, 224) - (0, 225) - (22, 213) - (30, 218). At along
  210 that is x -11, i.e. ON the green's left edge. The photo shows mown surround out to x -17..-18 there and dark
  canopy only from x -22. Long-right the notch at (22, 213) covers tan, open ground; the canopy starts ~226.
  PROPOSAL (replace the two vertices; how sure: medium, to be confirmed on the lidar grid): (-15, 205) ->
  (-20, 205); (-3, 224) -> (-12, 226); (22, 213) -> (22, 224). Effect: box may come 1 yd left / deeper.
* Box (lat 0..+5, depth -9..-2, i.e. right-centre and short of the middle): right idea - brush and bunker left,
  open right, trees long. "The safe miss is right" is right.
* Plays-like: 196 -1 (3 ft down) -1 (0.7 mph of tail in a 5 mph cross) +7 (46 F) = 201: every sign is right.
  5-iron 198 against 201 is the club that reaches the box (box plays 197-203).
* Wind line: "moves the ball about 7 yds right: start it that far left of the box" puts the start line at
  x -4.5..-2, the left third of the green, with brush 6-13 yds further left and the bunker short-left. If the wind
  drops for the shot the ball stays there. QUESTION for the lead: on a hole whose penal side is upwind, should the
  page ask for half the drift (start 3-4 left) rather than all of it? 1.5 yds / mph on a 5-iron is also on the
  high side.
* Middle (185, plays 187, 6-iron): same picture, same notes.

## Hole 16 (par 4, 354 / 325): 4-wood on the line, finishes x +7 at 263 - fine

Seen on: 5 px/yd lie-fill and plain renders x -70..70, along 180-370.

* Left fescue: mapped edge x -20..-22 at 245-300; photo's tan edge is at x -22, a mown strip, then fairway from
  x -17. Top of the block at 300, mown rough between it and the pond: as mapped.
* Mound right: mapped x +8..+43, along 265-297; photo's tufted mound with the stone edge at x +10..12 / 280-295:
  same footprint. Priced as sand: reasonable.
* Pond: front edge 305-312 for x -45..+5, reed ring mapped as native. Green at (9, 354).
* The play: 4-wood lands (248) in the 40-yd-wide part (x -18..+25 at 240-262) and stops at the mouth of the neck.
  Driver (268 / 298) lands on the mound line and runs at the pond; 2-wood finishes inside the 25-yd neck. Long iron
  to 214 has 52 yds of fairway and leaves 140: +0.12 is believable. Finishing 7 right keeps the 95 % left edge
  (x -20) exactly at the fescue: I would not aim an inch further left; if anything 2-3 right.
* Middle: long iron finishing ~242 in the Back frame, widest part, 111 in: fine. 94 % fairway fits.

## Hole 15 (par 4, 428 / 408): Driver, finishes x -4 at 291 - fine

Seen on: lie-fill and plain renders x -90..90, along 180-380.

* Bunkers x -8..+22 at 222-250 are carried (262). Fairway at 291 x -15..+40. Left: mown rough to x -38, then
  fescue (as mapped; the tee boxes of another hole sit inside the block further left, irrelevant). Right: path at
  +45, fescue from +48 (as mapped).
* The left fescue rectangle stops at 345 but the fescue goes on to 380+ (x -60..-40): out of Driver range (finish
  291); only matters for a tee moved 40+ yds forward.
* Middle: "close call, 2-wood +0.044": Driver finishes ~311 in the Back frame where the fairway is narrower
  (x -22..+22) - a fair close call.

## Hole 17 (par 3, 195 / 173): plays 197 - fine

Seen on: 8 px/yd lie-fill and plain renders x -50..50, along 150-240.

* Green x -9..+13, 177-208 and all four bunkers match. Tree edge right at x +17..22 (150-195) matches.
* Long-right the zone comes to (14, 200) and (7, 209), 1-2 yds off the green; the photo shows grass to ~215 there
  (the dark patch at x 22-35 / 200-210 is shadow). Low value: the box is short and left of centre.
* 190 -1 +2 (1.1 mph head) +6 = 197: signs right. Drift 5 yds right with trees right: here starting it left is the
  safe direction.

## Finding 4: "to green" vs "yds in"

Back 13: table 239, note 249. Back 15: 138 / 144. Back 18: 235 / 249. Back 16: 91 / 93. The table is the finish
spot to the green; the note is presumably the average over all swings (mishits, rough). Will reads two different
numbers for the same shot. Either label the note "average" or print one number.
