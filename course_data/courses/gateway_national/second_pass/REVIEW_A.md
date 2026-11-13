# Review A: holes 1-6 as Will would read them on the tee (Back first, then Middle)

Status: **version 2 (Fri Nov 13)**: checked against the Dec 2023 lidar grass heights, which retracted one
version-1 proposal (hole 2 left) and shrank another (hole 1 right). Page reviewed: `wind_page/index.html` at commit cee080946 (Actions run
43358518302). Map reviewed: `truth/package.json` `zones_ll` (identical to `truth/course.py`, checked to 0.02 yd),
painted in list order, later zone wins. Read-only review: nothing in the map, engine or page was changed.

## Bottom line

**No hole 1-6 has a hole-10-type error.** I looked for an unpenalised creek, ditch, pond edge, tree line or yard
under or beside every Driver / 2-wood / 4-wood oval, from both tees, on NAIP 2023 and on a lidar ground-relief
image. There is none. Driver is the right club on all five long holes from both tees, and the aims sit where I
would put them. One pick is a close call the map could tip (hole 4's club, 7-iron by 0.03). The problems below
are ranked by how likely they are to change what Will does. None is likely to.

| # | hole | verdict | problem | effect |
|---|---|---|---|---|
| 1 | 4 (par 3) | doubt | fescue mound behind and back-right of the green is not in the map (hole 4 has no hand zones at all) | box and "safe miss" are right; long is priced as rough. Club is a 0.03 call between 7- and 6-iron, and the mound favours the 7 |
| 2 | 1 | fine (Middle is a close call) | right fescue starts 3-4 yds nearer the fairway than mapped at 270-345 (lidar), where the Middle Driver finishes | Driver beats 4-wood by 0.030 from Middle; I estimate the edit costs the Driver about 0.005. Worth one re-solve |
| 3 | 2 | fine | none: the left fescue edge matches the lidar to 1-2 yds (my version-1 proposal 2a is withdrawn) | - |
| 4 | 3 | fine | tree row right of the fairway is unmapped for 7 yds in front of the OB line beyond 345 yds (Back) / 282 (Middle) | about 0.5 % of Middle drives; no change expected |
| 5 | 1 | fine | no OB right of the road (x > 57) | under 0.1 % of drives |
| 6 | all | page wording | elevation line reads "1 ft below the tee, so it carries -1 yds" (hole 1); par-3 headline "Plays 181 yds - 7-iron carries 174" with no word about release | Will will ask about both |

Not found, and specifically checked: cart path priced as water in a landing area (no); penalty zone hidden under a
fairway polygon (no); water erased by the hand "rough footprint" inside a landing corridor (no: see Priority).

## How I looked

- `qa_page.js` renders, Back and Middle, phone images 1-6 read one by one, plus the page's own data (calm aim,
  carry, total, oval per club) pulled from the page with Playwright.
- My own renders in the hole frame (x = yds right of the tee line, along = yds from the tee; frame from
  `course.py` `FRAMES`): NAIP 2023 beside the same photo with the engine's FINAL lie per cell outlined (zones painted
  in order, so a hidden zone shows as missing) and the Driver / 2-wood / 4-wood ovals at the calm 35 F aims.
  Whole hole at 1.7 px/yd, landing area at 3.2, problem spots at 7.
- Ground relief from `raw/dtm.tif` (height minus its 50-m mean) for every hole, to find ditches the photo hides.
- Scratch renders are deleted at the end; every polygon below is given in lon/lat and in frame yards.

- Grass and tree height (highest minus lowest return per 0.5-m cell) from F2's lidar grids: Dec 2023 on holes 1
  and 2 (mown 4-6 cm, standing 20-80 cm: a sharp edge), the older flight on 3-6 (good for trees, weak for grass).

Caveats. `raw/naip_2023.tif` is 0.6 m, not 0.3 m, so photo edges are good to about 1-2 yds. The August photo
misled me once: on hole 2 a smooth dark-green band read as mown rough and the lidar shows it standing 25-35 cm.
Where photo and lidar disagree below I follow the lidar. Lie shares I quote are my own Gaussian estimates from the
page's 95 % widths, not engine output. I ran no re-solves.

## Hole 4 (par 3, 180 Back / 153 Middle): doubt

Seen on `h4`, `h4z` (green surround at 6.5 px/yd).

- **Box.** x -1..+5, 170-174 yds from the map tee (174-179 on the page, which moves the tee back 4 yds to match the
  card). It sits in the middle of the right lobe of the green (lobe x -18..+14, 160-190), a touch short and right of
  its centre. Sensible.
- **Unmapped trouble: tufted fescue mound behind the green.** It wraps the back and back-right edge 3-5 yds off the
  putting surface and runs to the cart path. The map calls all of it rough. Hole 4 carries only OSM and lidar-canopy
  zones (fairway, sand, water, trees, OB); none of F1's hole-4 edits were applied.
  - **Proposal 4a, add `native`** (F1's polygon, confidence 0.75, their Sentinel-2 evidence says it is standing now).
    Frame (Back): `[[8,195],[13,188],[15,184],[24,183],[29,179],[28,188],[24,194],[20,202],[16,206],[9,204],[7,200]]`.
    lon/lat: `[[-90.1524779,38.6548633],[-90.1525183,38.6549266],[-90.1525324,38.6549617],[-90.1526242,38.6549814],[-90.1526695,38.6550204],[-90.1526738,38.6549459],[-90.1526422,38.654892],[-90.1526138,38.6548217],[-90.1525789,38.6547841],[-90.152503,38.6547913],[-90.1524757,38.6548213]]`
  - **Proposal 4b, add `native`, my wider read** (confidence 0.5 for the part left of x +7): the same texture
    continues left along the back of the green to x -14. Frame (Back):
    `[[-14,196],[-6,193],[4,191],[11,187],[16,181],[20,176],[27,176],[29,184],[26,192],[20,199],[10,203],[-2,204],[-12,202]]`.
    lon/lat: `[[-90.1522513,38.6548269],[-90.1523294,38.6548615],[-90.1524298,38.6548907],[-90.1524959,38.6549322],[-90.1525379,38.6549874],[-90.1525712,38.6550332],[-90.1526438,38.6550422],[-90.1526777,38.6549797],[-90.1526597,38.6549108],[-90.1526089,38.6548461],[-90.1525117,38.6548008],[-90.1523889,38.6547772],[-90.1522819,38.6547806]]`
  - Lidar: the older flight shows only scattered returns over the mound (it is weak for grass everywhere on 3-6),
    so this rests on the photo's texture and F1's Sentinel-2 series.
  - Why it matters: the box centre is 14-16 yds short of the mound, about two depth-sigmas for a 7-iron, so roughly
    2 % of tee shots. It will not move the box more than a yard. It does settle the club question below.
  - Test: re-run `opt/par3_target.py` and `opt/par3_ladder.py` for hole 4 with 4a, then with 4b.
- **Club: a 0.03-stroke call the page shows as settled.** `par3_ladder.json` Back hole 4: at the page's number
  (plays 181, which is 7.7 yds over the model's own 173.3 carry to the box) the 7-iron beats the 6-iron by 0.029
  (SE 0.004); two yards longer and the 6-iron wins. The whole gap comes from the card (180) against the map (176):
  if the map is right the number is 177 and the 7-iron wins by 0.19. With the mound mapped, long gets worse and the
  7-iron's margin grows. So 7-iron is right, but Will, who carries a mid iron about 184, will read "plays 181" and
  reach for the 184 club. The page should say why not (lands on the front, releases; long is fescue).
- **"Plays like" direction.** Wind from 351 deg on a 189 deg hole is 4 mph behind: -5 is the right sign (a little
  generous; I would expect -3 to -4). +1 uphill 3 ft: right. +8 for 39 F: right sign, plausible size. 177 + 1 - 5 + 8
  = 181: adds up. Middle: 151 + 1 - 4 + 7 = 155, 9-iron (150): consistent with the ladder (9-iron until +10).
- **"The safe miss is left."** Agreed: right is the cart path at x +32, then trees and the industrial yard (OB from
  x +42). Short-left are the two bunkers (x -18..0, 135-165), so "left" means pin-high left, not short-left. Worth
  five more words on the page.
- Green outline is 1-2 yds inside the visible surface on the right and back (F1 said the same). No effect.

## Hole 1 (par 4, 376 Back / 354 Middle): fine (Middle is the close call the page says it is)

Seen on `ov1`, `h1` (landing 180-380), `h1R` (right side at 7 px/yd), `m1` (Middle), relief `dt1`, lidar height
`h1_hag`.

- **Picture.** Fairway 45-50 yds wide at 240-300 (Back), a neck at 300-320 where a tongue of rough cuts in from the
  right, fescue berms both sides (both show as ridges on the relief), cart path on the left at x -40, a road on
  the right at x +57..+66. No ditch in the landing area. The mapped water strip along the cart path (40-140 yds,
  x -45..-38) is what Will's "does this hole think the cart path is a creek?" was about. The crossing at 45-60 yds
  is real (there is a bridge and a channel on the relief); the strip north of it up the path is doubtful. Neither
  touches any club that reaches the fairway.
- **Right fescue is 3-4 yds nearer than mapped at 270-345.** Dec 2023 lidar, median height in cm across the
  right side (x = yds right of the Back line):

  | along | x 26 | 29 | 32 | 35 | 38 | mapped edge |
  |---|---|---|---|---|---|---|
  | 260 | 9 | 6 | 5 | 6 | 19 | 32 |
  | 280 | 5 | 6 | 35 | 38 | 25 | 33 |
  | 300 | 8 | 21 | 80 | 63 | 21 | 34 |
  | 320 | 5 | 7 | 26 | 46 | 34 | 34.5 |
  | 340 | 5 | 9 | 61 | 55 | 21 | 35 |

  Standing grass starts at x +30..+31 from 270 on (+29 in a bulge at 300); at 260, beside the bunkers, it starts
  at +37, so there the map is 5 yds too harsh. The photo's bright band at +27..+30 is short. This is F1's finding,
  which fell under the lead's 3-yd rule. Left side: standing from x -47..-50, mapped from -40..-42 (the cart path
  is inside the band): slightly harsh, fine.
  - **Proposal 1a, add `native`** (the missing strip; confidence 0.8). Frame (Back):
    `[[30,268],[29,290],[28.5,300],[29.5,312],[30.5,345],[35.5,345],[34,300],[32.5,268]]`
    (Middle frame: `[[31,246],[30,268],[29.5,278],[30.5,290],[31.5,323],[36.4,323],[35,278],[33.5,246]]`).
    lon/lat: `[[-90.1412388,38.6621888],[-90.1414019,38.6623173],[-90.1414765,38.6623755],[-90.1415534,38.6624542],[-90.1417787,38.6626608],[-90.1417399,38.6626885],[-90.1414337,38.662406],[-90.1412194,38.6622026]]`.
    Paint it before the hand fairway and sand zones.
  - Back: Driver aim -8, 95 % edge +28: the strip takes under 1 % of drives. No change.
  - Middle: Driver aim -5 finishes in the neck; the strip takes about 1 % of drives (4-wood 0.3 %), about 0.005
    off a 0.030 margin. **Question to test: re-solve hole 1 Middle with 1a.** I expect Driver to hold at about 0.025
    with the aim a yard further left.
- **Would a DECADE player hit Driver from Middle?** Fescue to fescue is about 78 yds at the neck (left of the path
  at -48, right at +30) against a 70-yd pattern, and it leaves 72 yds instead of 100. That is on the Driver side of
  the 65-yd rule, narrowly. Driver is defensible; the page is right to badge it "close call". Back is a clear Driver.
- **Proposal 1b, add `ob`** right of the road (confidence 0.5 that it is OB rather than just dead; minor). Frame:
  `[[57,-10],[57,420],[110,420],[110,-10]]`. lon/lat:
  `[[-90.1390656,38.6606441],[-90.1421024,38.6632646],[-90.1416905,38.6635581],[-90.1386537,38.6609375]]`.
  The map has OB there only for the first 85 yds. 3.5 sigma from the aim: no effect on the pick.
- Numbers: 376 - 285 = 91 in, right. Wind from 2 deg on a 318 deg hole: 3 into, 3 right-to-left, right. Calm aim
  -8, wind pushes 4 left, headline "aim 5 yds left": consistent.

## Hole 2 (par 4, 422 / 397): fine

Seen on `ov2`, `h2`, relief `dt2`, lidar height `h2_hag`.

- **Picture.** Pond left to 285 yds (right edge x -28 at 250-280), fairway x -14..+40 at 287, cart path right at
  +40, fescue berm beyond it (standing from +45 on the lidar, as mapped), maintenance building from +70. Driver
  aim +8.5 is a few yards left of the fairway's centre, well clear of the pond. Carry 262 lands level with the pond's last 20 yds, 37 yds right of its edge: two sigmas. Right club, right aim.
- **Left fescue block: the map is right. Version-1 proposal 2a is withdrawn.** On the August photo the 10 yds
  next to the fairway look like smooth mown rough. The Dec 2023 lidar says otherwise (median height, cm):

  | along | x -33 | -30 | -27 | -24 | -21 | -18 | -15 | mapped edge |
  |---|---|---|---|---|---|---|---|---|
  | 295 | 35 | 33 | 14 | 5 | 5 | 5 | 5 | -26 |
  | 310 | 25 | 26 | 29 | 34 | 37 | 6 | 5 | -20 |
  | 325 | 21 | 26 | 25 | 25 | 29 | 7 | 6 | -18 |
  | 340 | 17 | 21 | 25 | 28 | 37 | 8 | 5 | -19 |

  Standing grass starts at x -19..-20 from 305 on, which is where the polygon's edge is; the fairway edge is
  10 yds further right at this point of the hole on the lidar image. The lead's F1 edit is in and correct. The
  block's outer third (x -68..-52) is mown on the lidar, but that is beyond any miss that matters.
- The standing grass continues, narrower, past 350 where the polygon stops. Beyond any tee shot from either tee.
- Numbers: Driver 295 total leaves 122 to a green 31 yds right of the line: right. Wind 3 behind, 3 right-to-left:
  right.

## Hole 3 (par 5, 630 / 566): fine

Seen on `ov3`, `h3`, `h3b` (330-600), `m3`, `m3R` (right side from Middle at 7 px/yd), relief `dt3`.

- **Picture.** Dead straight. Right: a bare dirt track (x +20..+27), a tree row over a drainage trench (the relief
  shows it), then the industrial yard. Trees mapped from +28, OB from +42..+45 for the whole hole: right, and Will's
  "wouldn't the trees be a large penalty?" is answered here. Left: rough to the cart path at -38, then a pond from
  285 yds at x < -55.
- **Aim -6** puts the tree line 34 yds right (about 3 % of drives) and the OB line 51 right (about 0.3 %), with the
  left fescue 39 left. With OB on one side and only long grass on the other, left-centre is correct.
- **Tree row unmapped in front of the OB line beyond the hand corridor.** Up to 345 yds (Back) trees are mapped from
  x +30. Beyond it the only trees zone is the lidar canopy, which the OB zone overrides, so the crowns between
  about +38 and the OB line (+40..+47) are rough.
  - **Proposal 3a, add `recovery`** (confidence 0.8). Frame (Back):
    `[[38.3,345.4],[39.6,363.4],[41.9,383.4],[45.4,413.3],[52.4,413.2],[48.9,383.3],[45.6,363.3],[43.3,345.4]]`
    (Middle frame: x 36..49, 282-350). lon/lat:
    `[[-90.1494713,38.6583781],[-90.1496037,38.658272],[-90.1497578,38.6581589],[-90.149989,38.6579893],[-90.1500443,38.6580272],[-90.1498131,38.6581969],[-90.1496511,38.6583045],[-90.1495108,38.6584052]]`
  - Reached only by the Middle Driver's long right tail (about 0.5 %). No change expected.
- **Left native band at 280-345 (x -62..-45) looks mown** on the photo, between the cart path and the pond. The
  water behind it is real, so the cost of being wrong is small and on the cautious side. No proposal.
- The cyan strip between the two left ponds (380-540 yds, x -60..-40) follows a low swale on the relief. It is a
  plausible ditch, not a cart path. It is 20 yds or more left of the fairway, for the second shot only.
- Numbers: 630 - 300 = 330 in, right. Page says fairway 61 % (Back); the fairway is 46 yds wide with a bunker in
  the right edge at 275-290. Plausible.

## Hole 5 (par 4, 452 / 421): fine

Seen on `ov5`, `h5`, relief `dt5`, lidar tree height `h5_tree`.

- No trees anywhere in the landing area (lidar). Pond in front of the tee ends at 85 yds: no club is affected. Fairway x -25..+25 at 287. Left: 15-20 yds of
  rough, then a brushy berm (mapped native -62..-42: matches the ridge on the relief). Right: rough, cart path at
  +40, fescue berm between the two paths (mapped +46..+66: matches). No ditch.
- Driver aim +3.5: fescue 43 right and 46 left. Balanced. The bunker at 240-255 (x -25..-10) is short of the 262
  carry. The 2-wood and 4-wood aims move right (+8, +12) to dodge it: sensible.
- Numbers: 452 - 291 = 161 (page 162). Wind from 347 on an 80 deg hole is a pure 4 mph left-to-right: right. Calm
  +3.5 less 6 of drift is "aim 2 left": consistent.

## Hole 6 (par 5, 530 / 500): fine

Seen on `ov6`, `h6`, `m6`, relief `dt6`, lidar tree height `h6_tree`.

- Fairway x -22..+25 at 287, ending at 350 where the cart path crosses (no ditch at the break: checked on the
  relief). Left: a tree row on a ridge from 250 yds (mapped x -75..-35; the lidar crowns sit inside the mapped outline to
  2-3 yds), and a low basin behind it. Right: cart
  path at +45, berm, second path.
- Driver aim +5.5, right of centre, away from the trees. Correct side.
- Both side bands are harsher than the ground (F1 said so): the left native strip (x -48..-30, 255-345) is thin
  rough in front of the trees, and the right band (+48..+70) covers the path and mown bank as well as the berm.
  The two roughly cancel, and both lean cautious. No proposal.
- The creek in the trees left of the tee (80-200 yds, x -100..-36) is priced as trees, not water, where the
  canopy zone overrides it. Only a duck hook finds it.
- Middle: Driver finishes 287 with the fairway ending at 315; long is rough and the path. Fine.
- Numbers: 530 - 291 = 239 (page 240). Wind 4 right-to-left: right. "Aim 12 right" = 5.5 + 6: consistent.

## Priority check (zones hidden by later zones), holes 1-6

Painted every hole at 1 yd and listed each water / OB / trees / native polygon that ends up as another lie:

- Inside the landing corridors (145-345 yds, |x| < 65) nothing penal is hidden by a fairway polygon or by the hand
  "rough footprint", except lidar-canopy cells that the hand tree polygons redraw.
- Water shown as trees, off the tee: hole 6 creek (x -100..-36, 77-196), hole 2 second pond (x -114..-38, 52-115).
- Hole 3: trees shown as OB beyond x +42 (harsher, correct), and the gap in proposal 3a.

## Page wording Will would query

1. **Elevation line.** Hole 1 Back: "landing area for Driver is 1 ft below the tee, so it carries -1 yds and rolls
   x1.16". Below should carry further, and a 1-ft drop does not explain 16 % more roll (the roll factor is the local
   slope). Hole 1 Middle prints "carries -0 yds". Either print the slope that drives the roll or drop the "so".
2. **Par-3 headline.** "Plays 181 yds - 7-iron carries 174" gives no reason for a club 7 yds short of the number.
3. **Fairway %.** The note line and the table's "95 % width" are fine, but 79 % (hole 6) and 67 % (hole 5) on
   fairways of the same width will get a question. Both are explained by the bunker and the fairway shape short of
   the aim; nothing to fix.
