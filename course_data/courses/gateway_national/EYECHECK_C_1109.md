# Gateway National, holes 13-18: eye check of the hand truth map (2026-11-09, reviewer C)

Method: the zones in `course_data/courses/gateway_national/truth/package.json` (precedence as stored, later wins)
were drawn over NAIP 2023 RGB (0.6 m grid, contrast-stretched), NAIP 2023 colour infrared, NAIP 2022 RGB, lidar
HAG 2014 and a local-texture layer (std of grey in a 4 m window). I looked at a whole-hole view, the left and right
of the landing area (140-345 yds) at 3.5 px/yd, the tee complex of every set, and the par-3 green surrounds.
Each fescue edge was also measured on 15 x 6 yd cell profiles across the corridor: NAIP 2023 NIR
(native here is NIR 115-165 and textured; mown rough is 165-195 and smooth; fairway is above 195), texture, HAG and
Meta CHM. As a check, the CIR strips I call native match the dark unmown blocks of the June 2022 photo, and the strips
I call rough show mowing stripes in 2022.
NAIP Plus 0.3 m: the proxy refused the request (403), so I used NAIP 2023, which is
0.3 m imagery resampled to 0.6 m. Lidar HAG cannot see the grass (leaf-off, March 2014: HAG is 0 everywhere in the
fescue), so the native calls rest on the photos.

Coordinates: `(along, x)` = yds along / right of the hole's **corridor frame** (`truth/gateway_national/render/frames.json`,
the Back tee to the aim point; the same frame `trace.py` uses, so the `N(...)` lines below drop straight into
`EXTRA`). The par 3s use the Back tee to the green. Every polygon is also given in WGS84 `[lon, lat]` (the
`poly_ll` of `hand_zones_ll.json` / `zones_ll` of the package).

Independent algorithm check (`course_data/product/native_auto.py`, side model, on the truth package with the
frames.json aim points; S2 stack present, course gate open: 100 % of sides >= thr 0.675). It says native on
**both** sides of every par 4/5 on my holes: 13 L 0.91 / R 1.00, 15 L 1.00 / R 1.00, 16 L 1.00 / R 0.99, 18 L 1.00 /
R 0.87. This fits the imagery: every side has unmown grass 10-40 yds off. On 18 R the trees take that role. On
13 L the native sits beyond the left cart path, not where the map has it.

## Summary

| hole | verdict | must fix |
|---|---|---|
| 13 | right fescue band mapped 3-17 yds too close at 200-345; the left strip is mown rough, and the real native is beyond the left path | **yes** (right band) |
| 14 (par 3) | trees, bunkers, green OK; native both sides of the tee-to-green corridor is unmapped (plays as rough) | **yes** (left band) |
| 15 | right: the mapped band (140-260) is mown rough; the real fescue beyond the path at 230-345 is unmapped | **yes** |
| 16 | right: the inner band (x 25-38) is mown rough; the real fescue runs from the cart path out (x 45-55+) | **yes** |
| 17 (par 3) | OK: green, bunkers, the tree line right, and the far-left pond all match | no |
| 18 | left band mapped 15-30 yds too close to the fairway at 260-345 (the fescue swings out with the path) | **yes** |

All tees sit on visible pads. Back is within 6 yds of the card on every hole. Notes on 13 Tips, 15 Back/Champions
and 18 are below. No OB lies inside any corridor, so the rough footprint erases nothing; see the OB section.

---

## 13 (par 5, Back 533)

Checked: fairway (OSM) and bunkers 240-265 R match. Left: the ditch, and the pond at 225-310 (x -45 to -90),
matches the photo and CIR. Tees: below. Green: matches.

**Must fix: 13 R native (modify).** The mapped "prairie right" is x 32..70 for all of 140-345. On the photo, a
mown rough strip runs between the fairway and the unmown blocks, and it widens up the hole. The fescue inner edge is
at x ~20 at 140, 36 at 200, 44 at 250, 48 at 300 and 50 at 345 (CIR dark purple, NIR ~160, texture 8.8; the mown
strip at x 40-46 / 270-300 is NIR 185, texture 5.3, with 2022 mowing stripes). The outer edge is the cart path, at
x ~56 at 140 and 70+ from 250. At 250-345, which is Driver / 2-wood landing, the map puts native 8-15 yds closer to
the fairway than it is. That over-penalises the right side and pushes the aim toward the left pond.
Confidence: high.

    replace  N([(140, 32), (345, 32)], [(140, 70), (345, 70)], "prairie right")
    with     N([(140, 20), (170, 28), (200, 36), (250, 44), (300, 48), (345, 50)], [(140, 56), (200, 61), (250, 69), (300, 70), (345, 70)], "fescue right: unmown blocks inside the cart path")
    poly_ll  [[-90.1493855, 38.6567773], [-90.1490644, 38.6568216], [-90.1487432, 38.6568658], [-90.1482316, 38.6569795], [-90.1477377, 38.657123], [-90.1473002, 38.6572641], [-90.1472118, 38.6571147], [-90.1476404, 38.6569587], [-90.1481211, 38.6567928], [-90.1486327, 38.6566791], [-90.1492263, 38.6565084]]

**Should fix (low impact; short of the Driver landing): 13 L.**
(a) Remove `N([(140, -35), (260, -35)], [(140, -27), (260, -27)], "fescue strip between the path and the fairway left")`.
That strip is mown rough: NIR 170, texture 4.6, smooth in 2023 and mown green in 2022. Confidence: medium-high.
(b) Add native / wetland between the left cart path and the ditch at 140-225. It is textured and grey in CIR,
NIR ~160, texture 7.9. Ditch water stays on top because water comes later in the zone order. Confidence: medium.

    add      N([(140, -54), (160, -59), (180, -64), (200, -72), (225, -80)], [(140, -44), (180, -44), (225, -46)], "native / wetland between the left cart path and the ditch")
    poly_ll  [[-90.1497127, 38.65733], [-90.1495443, 38.6574367], [-90.149376, 38.6575433], [-90.1492208, 38.6576724], [-90.1490181, 38.6578189], [-90.1488677, 38.657565], [-90.1492875, 38.657394], [-90.1496685, 38.6572553]]

Tees: Back (0) and Middle (+13) share OSM pad 719514943, Champions is on 719514314 (-24) and Forward is on its pad
(+72); all are on visible pads. **The Tips is doubtful.** It is lidar pad `lidar:132`, 50 yds right of the line on a
large mown oval across the ditch (p_assign 0.58 against 0.41 for the Champions pad). It is not hole 12's green
(that green is at x +31, along -67). Tips is only 5 yds longer than Champions on the card, so the back of the
Champions pad (x ~5, along -29) is at least as likely. It does not matter for a Back-tee event. Cosmetic.

## 14 (par 3, Back 200)

Checked: green outline (OSM) matches the photo. The left bunker, the short-right bunker at 150 and the
approach / fairway match. Trees behind and left of the green (recovery, from lidar) look further from the green on
the 2023 photo, but Meta CHM still has canopy there (62-88 % above 3 m at x -45..-18 / 180-215), so keep them.
Tees: all on visible pads (Champions / Tips share pad 720212663 at -36 / -40). No canopy on any line.

**Must fix: 14 L native (add).** An unmown strip runs the whole left side of the tee-to-green corridor, from the
tee to 185 yds. It is dark and textured in 2023 (NIR 135-150, texture 8.2) and has no mowing arcs in 2022, while
the rough beside it does. Its inner edge is x ~-22..-24, 2-6 yds outside the approach's left edge, short-left of the
green. Today the whole hole outside the approach plays as rough. A pulled long iron or hybrid that comes up short-left
lands in fescue, so this changes the miss side on a 200-yd par 3. Order: put it before the tree / sand zones so they
stay on top. Confidence: medium-high.

    add native, frame = Back tee -> green: left edge [(0, -52), (185, -52)], right edge [(0, -22), (60, -22), (120, -24), (185, -24)]
    poly_ll  [[-90.1454631, 38.6592946], [-90.1436005, 38.6597278], [-90.1435169, 38.6595068], [-90.1441713, 38.6593546], [-90.1447694, 38.6591983], [-90.1453735, 38.6590578]]

**Cosmetic: 14 R native (add).** A fescue strip lies between the two cart paths, x 28-48, 25+ yds right of the
green line (NIR 140-160, texture 11.6). The light strip between the approach and the first path is mown.

    add native: left edge [(0, 28), (200, 30)], right edge [(0, 46), (200, 48)]
    poly_ll  [[-90.1452242, 38.6586631], [-90.1432046, 38.6591156], [-90.1431508, 38.6589735], [-90.1451704, 38.658521]]

## 15 (par 4, Back 428)

Checked: fairway (OSM) and the bunkers at 240-260 L match. Trees around the tee chute match lidar and CHM. Green
matches.

**Must fix: 15 R native (remove + add).** The mapped "prairie right" (x 52..70, 140-260) lies between the fairway
and the cart path, and that ground is mown rough (NIR 157-177, pink in CIR, mowing stripes in 2022). The real
fescue starts just outside the cart path, which crosses toward the fairway as the hole goes on: path at x 77 at 215,
67 at 245, 57 at 275, 50 at 290, 42 at 305, 38 at 335. The fescue runs from there about 25-30 yds out (NIR 117-160).
At 260-345 it begins only 8-15 yds off the fairway's right edge (fairway to x ~42 at 260, ~30 at 330), right where a
Driver that is pushed or held up the right side ends up. **Nothing is mapped there now.** Confidence: high
(it is the same strip as 13's right fescue, seen from the other end).

    remove   N([(140, 52), (260, 52)], [(140, 70), (260, 70)], "prairie right")
    add      N([(230, 73), (260, 63), (290, 53), (320, 43), (345, 41)], [(230, 103), (260, 90), (290, 80), (320, 70), (345, 66)], "fescue right beyond the cart path")
    poly_ll  [[-90.1456833, 38.6598963], [-90.1459444, 38.6597354], [-90.1462055, 38.6595745], [-90.1464666, 38.6594136], [-90.1467067, 38.6593286], [-90.1467953, 38.6595224], [-90.1465624, 38.6596229], [-90.1463013, 38.6597838], [-90.1460401, 38.6599447], [-90.1457897, 38.6601288]]
    (at 140-230 the same fescue is at x 76-118, beyond the +/-65 footprint and 30+ yds off the fairway; left out)

**Cosmetic: 15 L native (modify inner edge).** Before the bunkers, the mapped inner edge is 5-10 yds too close to
the fairway. Measured edge: -15 at 140, -20 at 170-200, -28 at 230, -33 at 260. From 300 on it matches. The outer
part (x -75..-58 at 190-290) holds hole 16's tee pads, which are mown. They are 60+ yds off line, so leave them.

    replace  N([(140, -70), (345, -70)], [(140, -5), (200, -12), (260, -25), (300, -38), (345, -40)], "prairie left")
    with     N([(140, -70), (345, -70)], [(140, -15), (170, -20), (200, -20), (230, -28), (260, -33), (300, -38), (345, -40)], "prairie left")
    poly_ll  [[-90.1442867, 38.6590381], [-90.1463132, 38.6584683], [-90.1464195, 38.6587008], [-90.1459818, 38.6588414], [-90.1456041, 38.6589913], [-90.1453253, 38.6591135], [-90.1450571, 38.6592589], [-90.1447605, 38.6593423], [-90.1444817, 38.6594644]]

Tees: Back (pad 720212665), Middle (720212666), Forward (720212668), and Champions / Tips (shared 720212664, 453 vs a
card of 454 / 458) are all on OSM pads in the tree chute. **Note:** the chute is narrow (open at x -8..-2 at 0-40 on
the 2014 HAG). The straight line from the Back tee clips 11-17 m canopy at 5-15 yds, and the Champions / Tips line
runs under 25-30 m crowns for its first 40 yds, which overhang a pad you can't see on the photo. This is a real
chute, not a wrong pad: the pads follow the card and the opening. If the strategy penalises trees in the first
~25 yds of the line, move the Back tee ~3 yds left (x -3). Otherwise no change.

## 16 (par 4, Back 354)

Checked: left fescue (x -70..-32) matches. Its inner edge is ~8 yds generous at 140-245 and right at 245-300, so it
stays. The pond at 305-350 L, the fairway and the bunkers match. A native carry lies between the tees and the
fairway (0-120), out of play for this player. Tees: all on visible pads; Champions / Tips share 720212676.

**Must fix: 16 R native (replace both right bands).** The inner band "fescue between the fairway rough and the
path" (x 25..38) is mown rough at 180-300 (NIR 170-195, pink in CIR, a light green strip in 2022). The real fescue
is the dark band from the cart path out: path at x 37 at 155, 45 at 185, 50 at 200, 55 at 220-245, 53 at 260, 49 at
280-290, 47 at 305. Fescue runs from there to x ~80 (NIR 114-160). At 140-170 it also reaches inside the path to
x ~33. The map has native 0-14 yds off the fairway at 170-300 (NOTES "180R native 0 yds out" etc.). The real
fescue is ~25-30 yds off. On a 354-yd hole where the club and the line off the tee are the whole question, this is
the largest error on my holes. Confidence: high.

    remove   N([(140, 25), (300, 25)], [(140, 38), (300, 38)], "fescue between the fairway rough and the path right")
    remove   N([(140, 55), (300, 55)], [(140, 70), (300, 70)], "prairie beyond the path right")
    add      N([(140, 33), (170, 38), (180, 45), (200, 51), (220, 57), (260, 55), (280, 52), (300, 49)], [(140, 70), (300, 70)], "fescue right from the cart path out")
    poly_ll  [[-90.1458573, 38.660115], [-90.1456025, 38.660266], [-90.1454769, 38.6602861], [-90.1452866, 38.6603716], [-90.1450964, 38.6604571], [-90.1448227, 38.6607075], [-90.144701, 38.660844], [-90.1445794, 38.6609805], [-90.1444193, 38.6608616], [-90.1455753, 38.6599054]]

## 17 (par 3, Back 195)

Checked: the green outline, the bunkers left and right, the tree line right (lidar recovery, matching the 2023
canopy edge at x +8..+14), and the cart path left all match. The pond far left (x ~-50, 135-165) is mapped, 33+
yds left of the green. No unmapped native in reach; the textured strip inside the cart-path loop by the tees is out
of play. Tees: all on visible pads. Champions / Tips (720212686) sit against the tree line: their line to the green
runs along the crowns' edge at 13-37 yds (HAG 3-8 m at x +12). This is real and not my set. Verdict: OK, no edits.

## 18 (par 5, Back 527)

Checked: trees right (lidar recovery, from x ~+40 at 250) match the canopy edge. Between the fairway and the trees
is mown rough, not fescue. Fairway, bunkers and green match.

**Must fix: 18 L native (modify).** The mapped strip is x -45..-27 for all of 140-345. On the photo the fescue lies
between the cart path and the 18 rough, and it swings out with the path. Up to 250 it sits at x -46..-18 (the map is
5-7 yds short on the inside, which is fine). From 260 on the path bends left: fescue at -66..-36 at 275, -75..-42 at
290 and -90..-58 at 330. The strip the map calls native at 260-345 (x -45..-27) is mown rough: NIR 167-194, and
2022 shows mowing stripes there. So in the Driver landing area (275-300) the real fescue is 30-40 yds off the
fairway's left edge (x ~-6), not 20. The over-mapped left side pushes the aim toward the trees on the right.
Confidence: medium-high.

    replace  N([(140, -45), (345, -45)], [(140, -25), (345, -27)], "fescue strip between the cart path and the fairway left")
    with     N([(140, -46), (170, -46), (200, -48), (230, -48), (260, -52), (290, -75), (320, -90), (345, -90)], [(140, -18), (200, -22), (245, -30), (275, -36), (290, -42), (305, -48), (320, -58), (345, -64)], "fescue left between the cart path and the rough")
    poly_ll  [[-90.142015, 38.6621517], [-90.1418814, 38.6619279], [-90.1417288, 38.6617112], [-90.1415952, 38.6614875], [-90.1414236, 38.6612777], [-90.1410712, 38.6611343], [-90.140795, 38.6609629], [-90.1406836, 38.6607765], [-90.1409309, 38.6606857], [-90.1410993, 38.6608512], [-90.1412612, 38.6609282], [-90.1413851, 38.6610191], [-90.1415089, 38.66111], [-90.1416996, 38.6613128], [-90.1419761, 38.6616204], [-90.1422813, 38.6620539]]

**Tees (coordinator question).** Back, Champions and The Tips all use **OSM tee way 720212696**, and it belongs to
hole 18. It is the rear pad of 18's tee complex, at the south end, on 18's line (Back at the front, along 0; Champions /
Tips at -11). Measured 533 / 544 / 544 against a card of 527 / 545 / 550, and there is no canopy anywhere on the first
150 yds. Middle is on pad 720212698 (+42, 491 vs 494). A middle pad at +15..+35 is unassigned, and the Back card
length would put Back about +6. That is within tolerance, so no change. Forward (`lidar:45`, +145, x +33) sits
against the right tree line next to the path; plausible, not checked further. Cosmetic: the "water" polygon right of
the tees (inside the trees, along 0-80, x +40..+80) is a grassed basin on the 2023 photo and in CIR. It is out of
reach, so leave it.

## OB / rough footprint (coordinator question)

The truth package has **no OB zones on 13-18**. The auto package (`auto/package_v0_no_vision.json`) had
course-boundary / OSM OB on 13, 15, 16 and 18, and they were dropped. None of them lies inside a hand corridor (0
sq yds of overlap with 140-345 / +/-65 on every hole), so the rough footprint erases nothing. The nearest pieces:
16, the industrial site, 66 yds left of the line at along -75..120; 18, buildings / boundary 59-150 yds left at
along -51..174, plus the clubhouse area 114-124 yds left of the line at the green (~65 yds left of the green). Out of
reach of a tee shot or approach. **Cosmetic:** restore them as `ob:outside` for consistency with 1-4 if the build
dropped them by mistake.

## Not done / limits

- The 0.3 m NAIP Plus fetch was refused by the proxy (403). Edges are good to about +/-3-5 yds (0.6 m pixels, 6-yd
  profile cells).
- I did not run the strategy / score to measure the aim change. "Must fix" here means the mapped native moves
  8-30 yds against the real edge inside the 250-320 landing window, or (14) a whole miss side changes lie.
- Renders, the profile scripts and `proposals.json` (every polygon above, machine-readable) are in the reviewer's
  scratch dir and are not committed.
