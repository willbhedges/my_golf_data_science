# Gateway National: eye check of the truth map, holes 7-12 (reviewer B, 2026-11-09, before the Nov 14-15 event)

## Method

- The zones are from `courses/gateway_national/truth/package.json` (`zones_ll`, hand + auto). I drew them over:
  - NAIP 2023-08-19 RGB at 0.3 m (`packages/gateway_national/imagery/naip_rgb.tif`; the NAIP Plus fetch was refused by the proxy);
  - 2023 colour infrared (CIR: NIR-R-G from `naip_nir.tif`);
  - NAIP 2022-06 RGB;
  - 2014 lidar height above ground (`hag.tif`, 0.25 m units);
  - the effective-lie raster (later zone wins).
- Each hole was drawn in the corridor frame of `truth/gateway_national/render/frames.json`, so the (x = yds right, along) values below can be pasted into `trace.py`. Par 3s use a tee-to-green frame.
- Views: the whole hole, the landing area (140-360 along, 10-yd grid, up to 6 px/yd zooms) and the par-3 green surrounds.
- The edges were read by eye and then checked with NIR and NIR/red transects across the corridor every 10-40 yds. Mown turf reads NIR/red 1.3-1.4 and NIR about 200. Fescue/prairie reads 1.0-1.15 and NIR about 150-170, and is mottled grey-teal in CIR. The cart path reads about 0.8.
- **Lidar cannot see the grass.** It was flown in March 2014 with the grass dormant and laid over, so HAG shows nothing on the native bands. It only helps with trees.
- Tees: I checked every set against the pads on the photo. I sampled the first 150 yds of each set's line (±4 yds) against HAG and the Meta CHM.
- OB: I compared `auto/package.json`, `truth/package.json` and `auto/package_v0_no_vision.json`.
- Algorithm check: `product/native_auto.build_layer` on `auto/package.json` (S2 stack present, course gate passes at 92 % of sides).
  - Side p values: 8 L 0.99 / R 0.89; 9 L 1.00 / R 0.46; 10 L 0.99 / R 0.99; 11 L 1.00 / R 1.00 (threshold 0.675).

Polygons are given in two forms:
- `trace.py` form, `N(left_edge, right_edge, note)` with `[(along, x)]`;
- WGS84 `[lon, lat]` rings, built from the same frame (built and checked by round trip).

Zone order matters (later zones win). Hand native goes in `EXTRA` (first), so fairway, sand, water and trees keep winning over it.

## Summary

| hole | verdict | must fix | other |
|---|---|---|---|
| 7 (par 3, 180) | mostly OK | none | Long-right is fescue, not rough (should fix). The short-left "trees" are a shrub mound in 2023 (cosmetic). |
| 8 (par 4, 408) | **edit** | **R 230-300: fescue between the fairway's right edge and the trees is mapped as rough** | Unmapped native diamond at 303-337 L (cosmetic). |
| 9 (par 4, 390) | OK | none | R fescue strip is uncertain (detector p 0.46); kept. |
| 10 (par 4, 271) | OK | none | Tips/Champions "walkback" tee is not on a pad (cosmetic for Back). |
| 11 (par 4, 416) | **edit** | **R: native starts 15-20 yds too close (mown rough + cart path mapped as native, 150-345)** | L native touches the fairway at 160-280; truth is 5-9 yds of rough (should fix). |
| 12 (par 3, 131) | OK | none | Short-left water reaches ~10-15 yds too far short (cosmetic). |

- **Tees:** every set sits on a visible pad, except the hole-10 Tips/Champions walkback. Nothing like the hole-2 issue: no set's line crosses canopy in the first 150 yds, except 10 Back/Middle. Those two leave through the tree chute that actually exists (2023 photo: an open chute; the tee pads are clear).
- **OB:** none in any of these corridors. The only OB in the v0 package is the OSM course boundary on 7, 8 and 12. It is 72 yds or more from the 7 green, 87 yds or more from the 8 line (beyond the trees and the canal) and 110 yds or more from the 12 green. Both the auto and truth packages dropped it, and the hand footprint erases nothing in play.

## Per hole

### 7 (par 3, Back 180; The Tips 204, Champions 200, Middle 160, Forward 145)

**Checked:**
- Tees: Back sits on the OSM pad. Middle is the estimated point 15 yds ahead on the same pad, as in `holes_truth`.
  - Tips and Champions are on pads.
  - The Forward walkback is on open ground on the line; no pad is visible at 145.
  - All lines are clear of canopy. The single lidar hit is 3.2 m, 107 yds out, 4 yds left of the Forward line: one bush.
- Green outline (OSM) matches the photo.
- Bunkers right (150 and 175 along) match.
- Trees long-left (195-215, x -20..+10) match the photo.

**Findings:**
- Long-right of the green is fescue. Behind the green from about 194 along, x +2..+35, NIR/red is 1.05-1.10, against 1.25 on the green; it is tan in RGB. Beyond x ≈ +34 down the right side, the ratio is 1.10-1.16.
  - The map has rough there. The package's par-3 summary says "long: trees"; it is trees long-left and fescue long-right.
- Short-left of the green (135-165 along, x -45..-10) is auto "recovery" from the 2014 lidar. The 2023 photo shows a dense shrub/prairie mound with only a few small trees. Both lies are penal, so the shot plan does not change.
- Left side beyond x ≈ -38 (160-200 along) is prairie. It is 25 yds or more off the green edge.

**Edits:**
- **Should fix: add native long-right** (medium confidence; a long miss of 3 yds or more over a back-right pin).
  - Insert it at the start of hole 7's `zones_ll` so the sand, fairway and recovery zones still win.
  - `{"lie":"native","src":"hand","poly":[[-90.1486416,38.6539565],[-90.1486196,38.6538909],[-90.1486344,38.6538094],[-90.1485995,38.6536741],[-90.148894,38.6535472],[-90.1487878,38.6533956],[-90.1481436,38.6536732],[-90.1484116,38.6540557]]}`
  - In the tee-to-green frame, (x, along): (2,195) (10,193) (18,187) (34,182) (34,150) (55,150) (55,220) (2,220).
- **Cosmetic: add native left.** It is 25 yds or more off the green.
  - `{"lie":"native","src":"hand","poly":[[-90.149166,38.6541064],[-90.1487979,38.654265],[-90.1489091,38.6544238],[-90.1492773,38.6542652]]}`
  - Frame: x -60..-38, 160-200.
- **Cosmetic:** the short-left recovery could become native; both are penal.

### 8 (par 4, Back 408, dogleg left)

**Checked:**
- Tees: Back (lidar pad), Champions and Tips sit 9-11 yds behind on pads; Middle (30 ahead) and Forward (110 ahead, right) are on pads.
  - Lines are clear. The only hit is a tree clump 5 yds right of the Back tee at 5-7 yds out.
- Fairway (hand/OSM) matches the photo.
- Bunkers at 205 L and 270 C match.
- Hand trees on the right (x +40..+60) match the canopy within 3-5 yds.
- The "prairie beyond the end of the fairway" rectangle (300-345, x -40..+25) is real unmown grass with shrubs: CIR grey-teal, tufted. Correct.
- The "fescue before the trees right" band (220-345, x +25..+45) is correct where it is (NIR/red 1.0 at 230, x +26..+40).

**Must fix (high confidence):** at 230-300, inside the dogleg corner, the fairway's right edge bends left. It goes from x +22 at 225 to about -8 at 270-280, around the 270 bunker. Everything between that edge and the trees is the same tan fescue.
- At 260: x +0..+4 is turf at 1.3; x +6..+26 is fescue at 1.03-1.13.
- The map scores x ≈ -8..+25 at 250-300 as rough. That is 10-30 yds of fescue exactly where a Driver (275 carry / 300 total) or 2-wood finishes.
- The detector agrees: 8 R p 0.89.
- `trace.py` EXTRA["8"], add:
  `N([(225, 22), (240, 19), (250, 14), (260, 8), (268, 0), (280, -20), (300, -25)], [(225, 45), (300, 45)], "fescue inside the dogleg: fairway right edge to the trees")`
  - The left edge deliberately overlaps the fairway; the fairway and the 270 bunker still win.
  - WGS84: `[[-90.1461413,38.6545318],[-90.1460324,38.6546244],[-90.1459784,38.6547062],[-90.1459305,38.6547945],[-90.1459119,38.6548866],[-90.1459335,38.6550779],[-90.1457945,38.655208],[-90.1453623,38.6547418],[-90.1459993,38.6543786]]`

**Cosmetic:** a square of unmown/wetland vegetation (tan, CIR grey with red patches) sits at 303-337, x -78..-44, between the end of the landing fairway and the fairway to the green. It is unmapped.
- It only matters for a pulled Driver of 300 or more, or from the Middle tee.
- `N([(303, -78), (337, -78)], [(303, -44), (337, -44)], "unmown square inside the dogleg left")`
- WGS84: `[[-90.1460963,38.6555755],[-90.1458075,38.6557401],[-90.1455976,38.6555137],[-90.1458863,38.6553491]]`

### 9 (par 4, Back 390)

**Checked:**
- All five tees are on OSM pads and the lines are clear.
- The fairway, both bunker groups and the pond/ditch on the left (hand water) match the photo. The pond's right edge is at x -45, 230-295.
- The left fescue strip (x -48..-33, 140-300) sits on the dark shrubby wetland edge (CIR dark red / grey) beside the pond. Correct.
  - More of the same vegetation lies at 150-230, x -65..-48. That is too far left for a tee shot, so it is cosmetic.
- Trees on the right (x +45 and beyond) match.

**Uncertain, kept:** the right "fescue before the tree line" band (x +30..+45).
- For native: it is tan and lighter than the rough in the 2023 RGB, and grey-teal in CIR.
- For rough: its NIR is 170-185, between the rough (about 200) and the native elsewhere (150-165). It looks mown with stripes in June 2022. The detector gives 9 R p 0.46, below the 0.675 threshold.
- A ball there finishes 5-20 yds right of the fairway. If the manager wants the conservative plan, keep it.

**Edits:** none required.

### 10 (par 4, Back 271, drivable)

**Checked:**
- Back and Middle are on the two pads in the tree chute. Middle's point is about 5 yds right of its pad's centre, under the canopy edge (cosmetic).
- Forward is on a pad at 202.
- The Tips/Champions walkback is not on a pad (details under Edits).
- Lines from Back and Middle cross 2014 canopy within 4 yds of the line in the first 40 yds. The 2023 photo shows that chute open.
- The main fairway and its centre bunker at 200 match.
- The creek between the fairway and the green (hand water) and the pond at 160-215 L match CIR.
- The green sits left of the creek; its outline matches.
- Left prairie (x -70..-45) and the bunkers in it match.
- Right prairie beyond the cart path matches. The path is at x +45 (150) to +35 (250); the native edge sits on its far side within about 2 yds.

**Edits:**
- Cosmetic: the Tips/Champions walkback (44 yds behind Back) is in an unmown strip behind the trees and the shelter, with no pad. The real 315/317 tee is elsewhere; Back is unaffected.
- Cosmetic: the auto canopy covers the Back/Middle pads, which are open in 2023.

### 11 (par 4, Back 416)

**Checked:**
- All five tees are on OSM pads and the lines are clear.
- The fairway matches.

**Must fix (high confidence): right native.**
- A cart path runs up the right side. Its first edge is at x +28 (150), +30 (170), +36 (210), +44 (250), +54 (280), +62 (300) and +70 (315).
- Between the fairway and the path is smooth mown rough: deep red, unmottled in CIR; NIR/red 1.25-1.4 at 250-310. The fescue (tan, mottled) starts only on the far side of the path.
- The map's native starts at (150,+18), (260,+30), (345,+55). That puts 15-20 yds of rough plus the path inside native in the Driver landing zone (270-300, where the fairway runs -4..+36). Below 240 it is 8-12 yds.
- This makes the right side look like native at 0 yds out (NOTES: "270-320R native 0 yds out"). It pushes the aim left into the left band.
- Replace EXTRA["11"][1] with:
  `N([(150, 32), (170, 33), (210, 39), (250, 47), (280, 57), (300, 64)], [(150, 70), (300, 70)], "fescue beyond the cart path right")`
  - Past 300 the band lies beyond the ±65 footprint.
  - WGS84: `[[-90.1470043,38.6571677],[-90.1471835,38.6570816],[-90.1475658,38.6569364],[-90.1479599,38.6568048],[-90.1482793,38.6567333],[-90.1484941,38.6566879],[-90.1485297,38.6567286],[-90.1472296,38.657426]]`

**Should fix (medium confidence, ±4 yds): left native.**
- The strip between 11 and the parallel fairway is real fescue, but at 160-280 its inner edge is 5-9 yds off the fairway, with deep rough between.
  - Raw NIR at 180: native to -49, fairway from -42.
  - At 220: native to -35, fairway -30.
  - At 250: -23 vs -18.
  - At 280: -18 vs -6.
- The map polygon runs into the fairway there, so the effective native is at 0 yds out. From 300 on, the map is right.
- Replace EXTRA["11"][0] with:
  `N([(160, -68), (200, -62), (230, -50), (260, -42), (345, -27)], [(160, -48), (180, -48), (220, -35), (250, -23), (280, -17), (300, -10), (345, -6)], "prairie strip between 11 and the parallel fairway")`
  - WGS84: `[[-90.146498,38.6564416],[-90.1468803,38.6562964],[-90.1472115,38.6562385],[-90.1475189,38.6561534],[-90.1483446,38.6558602],[-90.1484691,38.6560029],[-90.1480554,38.6561849],[-90.1478405,38.6562303],[-90.1475449,38.656329],[-90.1472137,38.656387],[-90.14679,38.6564846],[-90.1466166,38.6565775]]`

The two edits together move hole 11 from "native both sides at the fairway edge" to "~8 yds rough left, ~20 yds rough right". The aim moves right of where the current map puts it.

### 12 (par 3, Back 131; Tips 154, Champions 147, Middle 115, Forward 90)

**Checked:**
- Back and Middle (estimated 10 yds ahead) are on the rectangular pad; Tips, Champions and Forward are on pads; lines are clear.
- The green outline matches.
- Water left of the green (x ≤ -17) and long-left matches CIR.
- The channel crossing in front (about 100-110 along) matches within about 5 yds. The front carry is about 110.
- The bunker right (115) and the mown oval at 65-90 match.
- The par-3 summary "water left / short / long" is correct.

**Cosmetic:** the short-left water polygon reaches down to about 75-80 along at x -55..-20. The open water there starts about 95-100; below that is marsh grass. It is irrelevant for a 131-yd shot.

**Edits:** none required.
