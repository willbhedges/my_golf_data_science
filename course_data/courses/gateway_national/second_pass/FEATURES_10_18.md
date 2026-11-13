# Gateway National, holes 10-18: second-pass feature detection (specialist F2)

Status: **CHECKPOINT 3** (native lines, tree lines, par-3 surrounds, tees, tee chutes, greens, bunkers, fairway outlines, water edges, validation). Machine-applicable edits:
`features_10_18.json` (same folder). All coordinates: corridor frame of `render/frames.json` (x = yds right of the Back
tee -> aim line, along = yds from the Back tee; par 3s: Back tee -> green centre) and WGS84.

## What is new in the evidence

| source | date | what it gives | where |
|---|---|---|---|
| USGS 3DEP lidar point cloud IL_10CoNRCS_3_D23 (EPT on usgs-lidar-public) | flown Dec 2023 - Jan 2024 (GPS time), ~27 pts/m2 | vegetation height above ground on a 0.5 m grid: mown turf 0.02-0.03 m, rough 0.03-0.04 m, standing fescue / prairie 0.10-0.35 m, trees; leaf-off = the same season as the tournament | only north of UTM northing 4282838: all of 17, 18 (to ~480 yds), 16 beyond ~130 yds, 15 from the tee to ~250 yds |
| USGS 3DEP lidar "IL_HicksDome_FluorsparDist_3_2019" work unit (misnamed project; this tile was flown 2020-12-02) | Dec 2020, ~8 pts/m2 | same, lower sensitivity (floor 0.00-0.01 m, +0.022 m added to match) | everything else (10, 11, 12, 13, 14, rest of 15 / 16) |
| NAIP 2023-08-19 at native 0.3 m + 2016, 2018, 2019, 2020, 2021, 2022 at 0.6 m | summer / autumn | mowing lines (brightness, NDVI, 2-yd texture), sand, water (NIR) | all |
| Sentinel-2 L2A NDVI 8 + 10 Nov 2026 (integrator file) | this week | native present now or mown (10 m) | all |

The 2014 lidar in `raw/hag.tif` is superseded: the map's tree zones (2014 canopy + 3 m buffer) are 4-15 yds too
close to play on 14, 17 and 18.

Method: per hole a rectified stack at 3 px / yd; random-forest classifiers (fairway / rough / native / trees /
water / sand / green) trained on eroded interiors of the map on the *other* holes (three leave-holes-out groups),
separately on NAIP 2023 only, NAIP 2019-22 only, and all sources; native = lidar height >= 0.07 m (or >= 0.04 m where
the NAIP-2023 classifier also says native), trees = lidar >= 2.5 m; cross-track first-hit edges every 5 yds (median
over +/-2 yds) for truth and detection; every hole checked by eye on NAIP 2023 overlays (shadows, paths and pond
banks rejected). Uncertainty of a detected line: native +/-2 yds in the 2023-lidar area, +/-3-4 yds in the 2020 area;
fairway +/-2 yds; trees +/-2 yds (crown edge, leaf-off: add 1-2 yds for leaves); bunkers +/-1.5 yds.

## MUST APPLY (ranked by likely effect on club / aim)

Offsets are detected - mapped, in yds; "closer" = closer to the fairway / line of play than mapped.

1. **16 left native block (lead from the integrator: confirmed, and larger).** The inner (right) edge of the fescue
   block left is at x -26 / -24 / -22 / -22 / -21 / -20 / -20 / -19 / -18 at 235 / 240 / 250 / 260 / 265 / 270 / 280 /
   290 / 295 yds (mapped -33 ... -30): **7 yds closer at 235, 9-10 at 240-265, 11-12 at 270-295**; the fairway's left
   edge there is -17 ... -15, so only **3-6 yds of mown rough** separate fairway and fescue (mapped 13-15). Lidar
   2023-12 (median height 0.22 m in the block), the NAIP-2023 classifier (within 1-2 yds of the lidar line at every
   station) and S2 Nov 2026 (NDVI 0.64 vs 0.85) agree. Confidence 0.9, +/-2 yds. 140-210: mapped edge is right
   (+/-1-3). At 215-225 there is a mown throat round the 208-yd bunker (native starts at -40 behind it).
   Also new: a 3-4 yd ring of bank vegetation round the pond (305-330 yds, x +3 ... +9, left of the fairway).
2. **16 right mound (264-298 yds, x +6 ... +43): NOT standing fescue.** Lidar Dec 2023 height over the mound is
   0.036 m (mown rough 0.029-0.038, fescue blocks 0.15-0.22); only its stone edge (x +7 ... +10, 280-292) stands up.
   S2 Nov 2026 over the polygon 0.78 (fairway 0.85, real native 0.54-0.64; the polygon is ~30 yds wide so mixing does
   not explain it). NAIP Aug 2023 shows a weedy, tufted mound: it reads as thin / low native that plays like rough
   with a bad-lie risk, not lost-ball fescue. Suggest penalty weight of rough-plus, or native with p <= 0.4.
   Confidence 0.7 (this conflicts with the integrator's S2 reading: decide on the solver's sensitivity).
3. **10 (drivable par 4): right native is a strip between the two cart paths, not a wedge out to +70.** Inner edge
   at 130 / 150 / 170 / 190 / 210 / 230 / 250 / 270 yds: +32 / +36 / +38 / +42 / +46 / +45 / +48 / +50 (mapped
   52 -> 30 as a straight diagonal): **10-15 yds closer at 140-190, 5-13 yds further at 210-290**; outer edge +56 ...
   +62 (beyond the second path it is the mown rough and tees of the next hole: mapped native there is wrong).
   Left: native wraps the pond's left bank and the three left bunkers; left of the green-side fairway it starts at
   x -59 ... -66 at 240-260 (mapped -47 ... -49: 12-19 yds further, more room short-left of the green) and -52 at 270,
   -47 at 290. Behind the green: native band from 13 yds past the back edge (303 yds) on and beyond the cart path
   (unmapped). The fairway's right edge is 2-5 yds narrower than OSM at 140-230 (minor). Lidar 2020 + NAIP 2023 +
   S2 2026. Confidence 0.85, +/-3 yds.
4. **15 left native: 7-10 yds closer at 150-190 and 220-260** (inner edge -9 ... -11 at 150-190, -14 at 220, -21 at
   230, -24 / -25 at 250 / 260; mapped -16 ... -20, -25, -28, -31 / -33), 2-5 closer at 200-210 (-18 / -17), 6 at 270,
   right at 280-345 (+/-2). A
   detached native patch sits just left of the three bunkers at 230-245 (x +17 ... +22). New on the right: fescue
   between the two paths from x +82 ... +89 at 150-220 (unmapped; 20 yds right of the fairway edge). Fairway right
   edge 3-4 yds narrower than OSM along 150-345 (both NAIP classifiers agree; minor). Confidence 0.8, +/-3 yds.
5. **18 left fescue strip: inner edge 4-10 yds closer the whole way.** Detected -16 / -19 / -19 / -20 / -23 /
   -26 / -29 at 200 ... 260 and -34 / -37 / -40 / -44 / -48 / -53 / -56 at 280 ... 340 (mapped -22 / -23 / -25 / -27 /
   -28 / -30 / -32 and -38 / -42 / -46 / -51 / -58 / -60 / -62): +4 ... +7, +10 at 320. **Tree line right is 3-5 yds
   further right at 200-300 and 9-15 at 310-340** than the 2014-canopy zone (present crowns 49-52 at 200-230,
   54-65 at 240-300, 68-73 at 310-340); thin fescue slivers in front of the trees at 200-220 (x +40) and 310-340
   (x +58 ... +62). Fairway right edge 2-4 yds narrower. Lidar 2023. Confidence 0.85, +/-2 yds.
6. **13 right fescue: inner edge 4-9 yds further right at 210-300** (+42 / +44 / +49 / +50 / +50 / +53 / +55 /
   +54 / +53 at 210 ... 290; mapped 38 ... 47): more room right of the fairway. Left at 150: -36 (mapped -44, 8
   closer), 160-180 right (+/-2), 190-220 5-13 further. Confidence 0.8, +/-3 yds.
7. **11 left strip: 5-8 yds further left at 160-270** (-54 / -54 / -52 / -47 / -43 / -41 / -42 / -34 / -30 / -26
   / -27 at 160 ... 270 by 10s; mapped -48 ... -19), right at 280-300, then **6-13 yds closer at 310-340** (-3 / +1 /
   +7 / +4; mapped -9 ... -6) and it continues unmapped past 345 along the left of the green complex. Right fescue
   3-5 yds further at 200-260 (10 at 160). Confidence 0.8, +/-3 yds.
8. **Par 3 surrounds.** 14: tree zone behind and right of the green is 10-14 yds too close (trees start 18 yds past
   the back edge, mapped 7; long-right 22 vs 12; long-left 14 vs 0), but on the LEFT the brush / overhanging canopy
   by the left bunker is 3-5 yds off the green edge (mapped 11) and rough brush starts 4 yds long-left: left is
   worse, long is better than mapped. 17: tree line right is 5-15 yds further (right 17 vs 11, long-right 20 vs 5,
   short-right 18 vs 13): the three right bunkers are in the open, not under trees. 12: no native mapped; bank
   vegetation starts 5 yds past the back edge (water at 9), native block right from 18 yds; the OSM water line
   front-left includes ~6-8 yds of exposed bank (keep it: it is inside the penalty area); green outline is ~2 yds
   small on the left / front (minor).

9. **18 tees: the Back marker is probably one pad too far back (17 yds), Middle 8 yds.** Pads on NAIP 2023 0.3 m:
   A along -10..+2, B 14..33, C 44..68, forward 152..164 (x +22..+30). The map has Tips / Champions at -11 (1.5 yds
   behind pad A), Back at 0 (front of pad A), Middle at 42.3 (1.5 yds behind pad C), Forward at 144.8, x +33 (by the
   path, not on a pad): spacings 11 / 42 / 102. The card spacings are Tips-Champions 5, Champions-Back 18,
   Back-Middle 33, Middle-Forward 103; the only placement that puts all five on mown pads with those spacings is
   Tips -6, Champions -1 (pad A), **Back +17 (pad B), Middle +50 (pad C)**, Forward +153 (forward pad), +/-3. The map
   chose markers to match the card length along its 3-point line (533 vs 527); with the pads the line measures
   ~516, i.e. the card is ~11 yds longer than the straight tee - corner - green line (normal for a dogleg par 5).
   Effect: every "from the Back tee" distance on 18 is ~17 yds too long (Middle ~8). Confidence 0.7; if the
   integrator keeps the mapped markers, at least treat Back as "pad A front edge .. pad B" (+0..+33).
10. **11: grass hollow inside the fairway at 212-238 yds, x -4..+12** (213 yd2, ~9 x 26 yds on the diagonal):
   longer textured grass in NAIP 2023, a shadowed hollow in NAIP 2021 / 2022; both NAIP classifiers break the
   fairway here. Plays as rough in the middle-right of the lay-up zone. Confidence 0.7.

11. **OSM greens and bunkers carry a per-hole registration shift of 1.5-3 yds** (NAIP 2023 is tied to the 2023
   lidar within 0.5 m on 17 bunker centroids: dx -0.16, dy +0.43 m, so the shift is OSM's). Replacement outlines
   for all 9 greens and 41 bunkers are in the json (`replace green`, `replace sand`; every edit also carries
   `priority` must | minor; one 17 bunker under the canopy keeps its OSM outline). What changes a number:
   - 15 fairway bunkers (230-250): reach from the Back tee 226 -> 222, 236 -> 231, 241 -> 238 (2.5-3 yds left, 2-2.5
     shorter than OSM, and 30-45% larger); 16 left bunker reach 207 -> 204 (2.4 yds right, 60% larger); 16 right
     bunker at 229 is twice the OSM area (19 -> 44 yd2).
   - 14 left green-side bunker: OSM shape is wrong (its upper lobe is rubble under the trees); real sand is 63 yd2
     centred 6 yds right and 6 short of the OSM centroid (Back reach / carry 178 / 190, was 180 / 199).
   - 10: two OSM bunkers left of the green complex do not exist ((-79, 242) and (-71, 276): native); the other
     five are 1.5-2 yds left / short of OSM.
   - Greens: 12 is 2.5-3.7 yds bigger on the left and front (toward the water: 3 yds of collar and rock edge, not
     6) and 1.5 at the back, area 513 -> 657 yd2; 17 is 2.5-2.8 yds further right and short (toward the right
     bunkers), 501 -> 606; 14 is 2-3.4 yds wider on the right, 604 -> 705; 10 is 2-3 yds bigger left and front and
     1.5-2 narrower on the right (the ditch is 1-2 yds off the right edge), 650 -> 720; 13 +3-4 right and long;
     11 +3 left and front; 16 +4 long-right; 18 +3-4 long (back lobe; uncertain: could be collar).

## Validation of the method

- **Two lidar flights agree.** Where both cover (16, 17, 18, part of 15) the native inner edge from the Dec 2020
  flight alone and the Dec 2023 flight alone differ by: 16 left +1.3 yds median (MAD 1.8; at 240-300: -26.0 /
  -27.0 / -23.3 / -21.7 / -20.7 / -18.7 / -24.0 in 2020 vs -24.7 / -22.0 / -21.7 / -20.3 / -20.0 / -18.7 / -21.7 in
  2023), 16 right +0.5 (MAD 1.2), 18 left 0.0 (MAD 1.0), 18 right +1.0, 15 right -0.7 (MAD 2.2). The mowing lines
  did not move in three years, and the 16 left edge is confirmed by a second independent flight. The 16 mound is
  low in both flights (only its stone edge at x +7..+10 stands up in 2020 and 2023).
- **NAIP 2023 vs lidar registration** 0.5 m (above); NAIP crowns of 25-30 m trees lean up to 5-8 yds from their
  true position (17 right, 15 tee): tree polygons come from lidar only.
- **Classifiers** (leave-holes-out, fairway vs rough accuracy on held-out holes): NAIP 2023 only 0.79-0.96, NAIP
  2019-22 only 0.71-0.92, all sources 0.85-0.98; lidar intensity alone does not separate fairway from rough
  (0.55-0.68) and was not used for fairway edges.

## Greens (NAIP 2023 0.3 m outline vs OSM)

| hole | area OSM / det yd2 | centroid shift x / along | det - OSM edge by direction: long, long-right, right, short-right, short, short-left, left, long-left (capped +4) | years agreeing (2022 / 2021 within 1.5 yds, of 8 dirs) |
|---|---|---|---|---|
| 10 | 650 / 720 | -1.7 / -1.1 | -0.2, -2.1, -1.5, -1.3, +2.0, +3.0, +2.7, +2.3 | 7 / 8 |
| 11 | 653 / 777 | -1.7 / -0.5 | -0.2, -0.3, -0.7, -0.6, +3.9, +2.7, +2.7, +3.1 | 5 / 7 |
| 12 | 513 / 657 | -1.4 / -0.4 | +1.6, +0.7, -0.3, +1.5, +3.3, +2.6, +3.7, +2.6 | 6 / 8 |
| 13 | 543 / 743 | +1.7 / -0.3 | +3.6, +3.0, +4.0, +2.8, +4.4, -0.8, -0.1, -1.0 | 5 / 7 |
| 14 | 604 / 705 | +1.9 / -0.6 | +1.7, +2.8, +2.0, +3.4, -0.7, -1.0, -0.0, -0.7 | 4 / 5 |
| 15 | 624 / 688 | -1.8 / -2.1 | -0.9, -2.2, -1.1, -1.4, +1.8, +1.8, +2.3, +3.0 | 2 / 5 |
| 16 | 781 / 921 | +1.2 / -0.6 | +1.3, +3.9, +2.1, +1.0, +1.4, +1.3, +0.5, -0.9 | 6 / 7 |
| 17 | 501 / 606 | +1.2 / -0.8 | +0.1, +1.7, +2.5, +2.7, +2.8, -0.9, +0.7, -0.7 | 5 / 8 |
| 18 | 775 / 985 | +0.5 / +0.5 | +4.0, +1.0, +1.8, +4.0, +0.9, -0.1, +0.2, +3.2 | 7 / 8 |

## Bunkers (NAIP 2023 0.3 m outline vs OSM), with reach / carry

| hole | bunker x / along (OSM centroid) | area OSM / NAIP yd2 | IoU | shift x / along | Back reach / carry: OSM -> NAIP | Middle reach / carry: OSM -> NAIP | edit |
|---|---|---|---|---|---|---|---|
| 10 | 72 / 134 | 40 / 42 | 0.42 | -2.1 / -0.7 | 149 / 155 -> 147 / 153 | 130 / 136 -> 128 / 134 | replace |
| 10 | 8 / 198 | 41 / 41 | 0.54 | -1.7 / -0.9 | 194 / 201 -> 193 / 201 | 174 / 181 -> 173 / 181 | replace |
| 10 | -79 / 242 | - | - | - | - | - | not found as sand in 2023 |
| 10 | -32 / 250 | 39 / 23 | 0.32 | -1.5 / -0.2 | 247 / 256 -> 249 / 255 | 228 / 237 -> 230 / 236 | replace |
| 10 | -60 / 262 | 43 / 40 | 0.44 | -1.8 / -1.9 | 265 / 272 -> 264 / 271 | 247 / 253 -> 245 / 252 | replace |
| 10 | -71 / 276 | - | - | - | - | - | not found as sand in 2023 |
| 10 | -49 / 279 | 40 / 58 | 0.54 | -0.2 / -1.5 | 277 / 288 -> 275 / 287 | 257 / 269 -> 256 / 268 | replace |
| 10 | -43 / 293 | 27 / 24 | 0.34 | -1.5 / -1.4 | 293 / 299 -> 291 / 297 | 274 / 279 -> 272 / 278 | replace |
| 11 | 52 / 381 | 57 / 89 | 0.29 | -2.9 / -1.1 | 380 / 391 -> 376 / 390 | 358 / 369 -> 354 / 368 | replace |
| 12 | 18 / 118 | 40 / 37 | 0.42 | -1.8 / -1.7 | 114 / 123 -> 113 / 121 | 98 / 107 -> 97 / 105 | replace |
| 13 | -69 / 108 | 28 / 90 | 0.31 | +0.8 / +1.3 | 125 / 131 -> 124 / 133 | 115 / 120 -> 113 / 122 | replace |
| 13 | -64 / 120 | 18 / 26 | 0.44 | +1.5 / +0.8 | 133 / 139 -> 133 / 139 | 122 / 127 -> 121 / 127 | replace |
| 13 | 34 / 235 | 36 / 53 | 0.48 | +1.4 / -0.2 | 233 / 242 -> 232 / 242 | 220 / 229 -> 219 / 229 | replace |
| 13 | 26 / 247 | 94 / 140 | 0.66 | +0.2 / +0.3 | 242 / 256 -> 240 / 257 | 229 / 243 -> 227 / 245 | ok |
| 13 | 14 / 262 | 46 / 74 | 0.48 | +1.1 / +0.9 | 258 / 267 -> 257 / 270 | 245 / 254 -> 244 / 257 | replace |
| 13 | -27 / 394 | 79 / 99 | 0.48 | +2.4 / +0.7 | 387 / 402 -> 388 / 402 | 374 / 389 -> 375 / 389 | replace |
| 13 | -18 / 468 | 41 / 61 | 0.37 | +1.9 / -0.5 | 462 / 473 -> 461 / 473 | 449 / 460 -> 447 / 460 | replace |
| 13 | -9 / 539 | 77 / 71 | 0.65 | +1.6 / +0.1 | 533 / 545 -> 533 / 545 | 520 / 532 -> 520 / 532 | replace |
| 13 | 82 / 565 | 27 / 24 | 0.28 | +1.5 / +1.4 | 568 / 574 -> 570 / 576 | 555 / 562 -> 557 / 563 | replace |
| 14 | 21 / 144 | 40 / 42 | 0.43 | +2.0 / +0.8 | 142 / 149 -> 143 / 150 | 126 / 133 -> 127 / 134 | replace |
| 14 | -18 / 190 | 119 / 63 | 0.20 | +6.0 / -6.1 | 180 / 199 -> 178 / 190 | 166 / 185 -> 164 / 175 | replace |
| 15 | -47 / 47 | 118 / 64 | 0.19 | -5.8 / +6.7 | 59 / 78 -> 68 / 81 | 50 / 67 -> 57 / 70 | replace |
| 15 | 18 / 232 | 99 / 140 | 0.42 | -2.6 / -1.8 | 226 / 240 -> 222 / 240 | 206 / 220 -> 202 / 220 | replace |
| 15 | 8 / 240 | 60 / 88 | 0.43 | -3.0 / -2.6 | 236 / 243 -> 231 / 242 | 216 / 223 -> 211 / 222 | replace |
| 15 | -5 / 247 | 79 / 102 | 0.50 | -1.0 / -2.0 | 241 / 252 -> 238 / 251 | 221 / 232 -> 218 / 231 | replace |
| 15 | -9 / 394 | 43 / 43 | 0.42 | -1.6 / -0.9 | 389 / 399 -> 388 / 398 | 369 / 379 -> 368 / 378 | replace |
| 15 | -7 / 413 | 108 / 96 | 0.64 | -1.7 / -0.2 | 406 / 421 -> 406 / 420 | 386 / 401 -> 386 / 400 | replace |
| 15 | -94 / 441 | 49 / 28 | 0.54 | +0.8 / +2.9 | 444 / 458 -> 448 / 458 | 425 / 439 -> 429 / 439 | replace |
| 16 | -28 / 208 | 48 / 78 | 0.42 | +2.4 / -0.7 | 207 / 214 -> 204 / 213 | 179 / 185 -> 176 / 185 | replace |
| 16 | 39 / 229 | 19 / 44 | 0.41 | +0.4 / -1.3 | 228 / 235 -> 226 / 235 | 199 / 206 -> 197 / 206 | replace |
| 16 | 34 / 250 | 55 / 102 | 0.54 | +0.1 / +0.3 | 247 / 259 -> 245 / 259 | 218 / 229 -> 216 / 230 | replace |
| 16 | 26 / 333 | 15 / 40 | 0.23 | +2.0 / -1.3 | 331 / 337 -> 328 / 337 | 302 / 307 -> 299 / 308 | replace |
| 17 | -52 / 68 | 15 / 40 | 0.24 | +1.9 / -1.5 | 83 / 88 -> 80 / 87 | 68 / 72 -> 64 / 71 | replace |
| 17 | 6 / 161 | 47 / 53 | 0.42 | +1.7 / -0.1 | 156 / 167 -> 155 / 167 | 134 / 145 -> 133 / 145 | replace |
| 17 | 15 / 170 | 47 / 43 | 0.49 | +1.1 / -0.4 | 166 / 176 -> 166 / 176 | 144 / 154 -> 144 / 153 | replace |
| 17 | -24 / 179 | 70 / 76 | 0.49 | +0.9 / -0.1 | 173 / 188 -> 173 / 187 | 152 / 166 -> 151 / 165 | replace |
| 17 | 18 / 185 | 63 / 20 | 0.33 | -0.2 / -0.1 | 180 / 191 -> 181 / 190 | 158 / 169 -> 159 / 168 | replace |
| 18 | -44 / 87 | 59 / 66 | 0.48 | -0.6 / +3.2 | 93 / 103 -> 95 / 106 | 63 / 71 -> 64 / 74 | replace |
| 18 | -56 / 96 | 44 / 52 | 0.43 | -0.3 / +2.1 | 106 / 116 -> 108 / 118 | 77 / 87 -> 78 / 88 | replace |
| 18 | -5 / 264 | 93 / 119 | 0.63 | -1.2 / +1.4 | 256 / 270 -> 257 / 271 | 214 / 228 -> 215 / 229 | ok |
| 18 | -19 / 298 | 181 / 229 | 0.65 | -1.0 / +2.6 | 288 / 308 -> 289 / 310 | 246 / 267 -> 248 / 268 | replace |
| 18 | 29 / 388 | 40 / 50 | 0.55 | -0.7 / +2.7 | 383 / 394 -> 385 / 397 | 340 / 352 -> 342 / 355 | replace |
| 18 | 36 / 394 | 29 / 51 | 0.56 | -0.3 / +0.4 | 392 / 399 -> 390 / 400 | 349 / 356 -> 347 / 358 | replace |
| 18 | -13 / 415 | 58 / 86 | 0.50 | -0.3 / +1.5 | 407 / 422 -> 409 / 424 | 365 / 380 -> 367 / 382 | replace |
| 18 | 25 / 493 | 91 / 132 | 0.55 | -2.3 / +2.1 | 486 / 500 -> 488 / 502 | 444 / 457 -> 445 / 459 | replace |
| 18 | -25 / 528 | 93 / 83 | 0.69 | +0.2 / +1.6 | 522 / 535 -> 523 / 536 | 480 / 493 -> 481 / 494 | replace |

## Water edges (NIR 2023 + 2022 vs truth, x of the first water going outward from the fairway centre)

Open-water edge is 1-4 yds beyond the OSM line everywhere (OSM follows the top of the bank; exposed bank in August):
no edit. 13 at 290-300: the mapped ditch running in toward the fairway is a real narrow ditch that NIR cannot see.

| hole | along | water L truth / NIR / off | water R truth / NIR / off |
|---|---|---|---|
| 10 | 140 | -30 / . / . | . / . / . |
| 10 | 150 | -32 / . / . | . / . / . |
| 10 | 160 | -33 / -36 / -3 | . / . / . |
| 10 | 170 | -31 / -34 / -3 | . / . / . |
| 10 | 180 | -30 / . / . | . / . / . |
| 10 | 190 | -28 / . / . | . / . / . |
| 10 | 200 | -24 / -26 / -1 | . / . / . |
| 10 | 210 | -20 / -22 / -2 | . / . / . |
| 10 | 220 | -16 / -19 / -2 | . / . / . |
| 13 | 220 | -49 / -50 / -1 | . / . / . |
| 13 | 230 | -48 / -47 / +1 | . / . / . |
| 13 | 240 | -46 / -45 / +1 | . / . / . |
| 13 | 250 | -45 / -45 / -0 | . / . / . |
| 13 | 260 | -43 / -43 / +0 | . / . / . |
| 13 | 270 | -46 / -45 / +1 | . / . / . |
| 13 | 280 | -46 / -46 / +0 | . / . / . |
| 13 | 290 | -34 / -46 / -12 | . / . / . |
| 13 | 300 | -25 / -66 / -41 | . / . / . |
| 16 | 315 | 4 / 2 / -2 | . / . / . |
| 16 | 325 | 6 / 3 / -3 | . / . / . |
| 16 | 335 | 1 / -1 / -2 | . / . / . |
| 16 | 345 | -3 / -4 / -1 | . / . / . |
| 18 | 400 | -106 / . / . | . / . / . |
| 18 | 410 | -69 / . / . | . / . / . |
| 18 | 420 | -68 / . / . | . / . / . |
| 18 | 430 | -70 / -70 / -1 | . / . / . |
| 18 | 440 | -70 / -72 / -1 | . / . / . |
| 18 | 450 | -69 / -71 / -2 | . / . / . |
| 18 | 460 | -64 / -66 / -2 | . / . / . |
| 18 | 470 | -61 / -63 / -2 | . / . / . |
| 18 | 480 | -56 / -60 / -4 | . / . / . |
| 18 | 490 | -49 / -53 / -4 | . / . / . |
| 18 | 500 | -40 / -44 / -4 | . / . / . |
| 11 | 60 | -6 / -6 / +0 | -6 / -6 / +0 |
| 11 | 70 | -6 / -6 / +0 | -6 / -6 / +0 |
| 11 | 80 | . / -7 / . | -7 / -7 / +0 |
| 11 | 90 | . / . / . | 5 / 2 / -3 |
| 11 | 100 | . / . / . | 38 / 35 / -3 |
| 11 | 110 | . / . / . | 50 / 46 / -4 |
| 11 | 120 | . / . / . | 74 / . / . |
| 11 | 130 | . / . / . | 81 / . / . |
| 11 | 140 | . / . / . | 88 / . / . |

## Tees (all sets) and tee chutes

Back and Middle pads read on NAIP 2023 0.3 m at 4x (+/-1.5 yds); other sets +/-4 yds. All Back / Middle markers of
10-17 sit on their own mown pad and their spacing matches the card within 1 yd; only 18 is inconsistent (item 9).
Useful ranges for "tee moved on the day": 14 Back pad is 23 yds long (hole plays 195-218), 12 Back / Middle share a
32-yd pad, 13 Back / Middle share a 27-yd pad.

| hole | set | card | marker x / along | pad along range | note |
|---|---|---|---|---|---|
| 10 | The Tips | 317 | -0.0 / -46.1 | ? | as Champions |
| 10 | Champions | 315 | -0.0 / -44.1 | ? | no pad visible under the marker (shadow, across the service path); a mown patch lies 10-20 yds LEFT at along -37..-44: lateral position uncertain +/-10 |
| 10 | Back | 271 | 0.0 / 0.0 | -7 .. 10 | centre of its pad |
| 10 | Middle | 251 | 2.9 / 20.1 | 14 .. 29 | on its pad, right of centre |
| 10 | Forward | 202 | 20.4 / 71.3 | 66 .. 77 | on its pad |
| 11 | The Tips | 444 | -0.5 / -28.1 | -33 .. -22 | on the small back pad |
| 11 | Champions | 442 | -0.6 / -26.1 | -33 .. -22 | on the small back pad |
| 11 | Back | 416 | 0.0 / 0.0 | -12 .. 9 | centre of its pad |
| 11 | Middle | 394 | 1.0 / 22.2 | 12 .. 32 | centre of its pad |
| 11 | Forward | 330 | -19.3 / 85.7 | 80 .. 92 | on its pad |
| 12 | The Tips | 154 | -0.5 / -23.1 | -27 .. -12 | on the back pad |
| 12 | Champions | 147 | -0.0 / -16.1 | -27 .. -12 | on the back pad |
| 12 | Back | 131 | 0.0 / 0.0 | -8 .. 24 | one 32-yd rectangular pad shared with Middle |
| 12 | Middle | 115 | 0.4 / 16.6 | -8 .. 24 | same pad as Back |
| 12 | Forward | 90 | 13.4 / 41.8 | 37 .. 47 | on the round forward pad |
| 13 | The Tips | 562 | 5.0 / -29.0 | -29 .. -11 | back end of the back pad |
| 13 | Champions | 557 | 5.2 / -24.0 | -29 .. -11 | on the back pad |
| 13 | Back | 533 | 0.0 / 0.0 | -4 .. 24 | one 27-yd pad shared with Middle; marker at its back end |
| 13 | Middle | 520 | -0.3 / 13.0 | -4 .. 24 | same pad as Back |
| 13 | Forward | 462 | -14.1 / 72.1 | 65 .. 80 | on its pad |
| 14 | The Tips | 240 | 1.6 / -40.1 | -44 .. -31 | back edge of the back pad |
| 14 | Champions | 236 | 1.6 / -36.1 | -44 .. -31 | on the back pad |
| 14 | Back | 200 | 0.0 / 0.0 | -18 .. 5 | front quarter of a 23-yd pad: the hole plays 195-218 off this pad |
| 14 | Middle | 185 | 5.6 / 15.1 | 9 .. 27 | on its pad |
| 14 | Forward | 155 | 13.8 / 45.9 | 40 .. 54 | on its pad |
| 15 | The Tips | 458 | -7.1 / -26.2 | -30 .. -21 | as Champions |
| 15 | Champions | 454 | -7.1 / -26.2 | -30 .. -21 | small clearing under the canopy (lidar), not visible in NAIP |
| 15 | Back | 428 | 0.0 / 0.0 | -15 .. 2 | front-right corner of the clearing in the tree chute (pad x -11..+4) |
| 15 | Middle | 408 | 2.1 / 20.0 | 18 .. 32 | back edge of its pad |
| 15 | Forward | 330 | 34.5 / 98.6 | 99 .. 113 | back edge of its pad |
| 16 | The Tips | 390 | 4.1 / -35.8 | -38 .. -24 | back edge of the back pad |
| 16 | Champions | 384 | 4.0 / -30.0 | -38 .. -24 | on the back pad |
| 16 | Back | 354 | 0.0 / 0.0 | -10 .. 10 | centre of its pad |
| 16 | Middle | 325 | 2.7 / 29.1 | 21 .. 40 | centre of its pad |
| 16 | Forward | 274 | 19.2 / 81.2 | 76 .. 86 | on its pad |
| 17 | The Tips | 231 | 10.2 / -34.3 | -36 .. -22 | back edge of the back pad |
| 17 | Champions | 225 | 9.6 / -29.2 | -36 .. -22 | on the round back pad |
| 17 | Back | 195 | 0.0 / 0.0 | -11 .. 12 | centre of its pad |
| 17 | Middle | 173 | 0.9 / 22.2 | 16 .. 28 | centre of its pad |
| 17 | Forward | 156 | -0.8 / 39.1 | 33 .. 46 | on its pad |
| 18 | The Tips | 550 | -0.0 / -11.1 | -10 .. 2 | mapped marker 1.5 yds behind pad A |
| 18 | Champions | 545 | -0.0 / -11.1 | -10 .. 2 | mapped marker 1.5 yds behind pad A |
| 18 | Back | 527 | 0.0 / 0.0 | -10 .. 2 | MAPPED marker is on pad A (-10..+2) with Champions / Tips; card spacing puts Back on pad B (14..33): see the tee edit |
| 18 | Middle | 494 | 5.5 / 42.3 | 44 .. 68 | mapped marker 1.5 yds behind pad C; card spacing puts it at ~50 |
| 18 | Forward | 391 | 33.0 / 144.8 | 152 .. 164 | mapped marker (144.8, x +33) is NOT on a pad (by the path); the forward pad is at 152-164, x +22..+30 |

Tee chutes (lidar canopy >= 2.5 m within 15 yds of the tee -> aim line; rows only where something is that close):

| hole | tee | yds from tee | nearest canopy >= 2.5 m left / right of the line (yds) | canopy top over the line +/-2 yds (m) |
|---|---|---|---|---|
| 10 | Back | 10 | -38 / 4 | open |
| 10 | Back | 20 | -32 / 5 | open |
| 10 | Back | 30 | -27 / 9 | open |
| 10 | Back | 50 | -15 / . | open |
| 10 | Middle | 10 | -32 / 5 | open |
| 13 | Back | 10 | . / 11 | open |
| 13 | Back | 20 | . / 12 | open |
| 13 | Back | 30 | . / 6 | open |
| 13 | Middle | 10 | . / 13 | open |
| 13 | Middle | 20 | . / 4 | open |
| 15 | Back | 10 | -0 / 0 | 32 |
| 15 | Back | 20 | -14 / 4 | open |
| 15 | Back | 30 | -26 / 9 | open |
| 15 | Back | 40 | -16 / 9 | open |
| 15 | Back | 50 | -35 / 10 | open |
| 15 | Middle | 10 | -28 / 7 | open |
| 15 | Middle | 20 | -18 / 7 | open |
| 15 | Middle | 30 | -37 / 8 | open |
| 17 | Back | 120 | . / 12 | open |
| 17 | Middle | 90 | . / 15 | open |
| 17 | Middle | 100 | . / 14 | open |
| 18 | Back | 10 | . / 12 | open |
| 18 | Back | 20 | . / 14 | open |
| 18 | Back | 30 | . / 15 | open |
| 18 | Middle | 10 | . / 14 | open |

- **15 (tee in the tree chute)**, from the 2023 point cloud by 3-yd lanes: the canopy closes over the line 0-20 yds
  in front of the Back marker but its lowest limbs there are 20-27 m up (x -1.5..+1.5) and 14-17 m (x +1.5..+4.5):
  not in a drive's flight. At ball-flight height the clear lane is x -10..+7.5 out to 50 yds (brush 1.5-2.5 m at
  x < -10.5 from 20-45 yds; limbs down to 7.6-11 m at x >= +7.5 from 30-50 yds). Start lines within about 8 deg
  either side of the line are clear from the Back tee; the Middle tee (pad 18-31) is in the open. The mapped tree
  zone (-11 / +4 at 35 yds) is 5-6 yds too tight on the right, right elsewhere. The Back marker sits at the
  front-right corner of the pad clearing (pad x -11..+4, along -15..+2).
- 10 Back: crowns of the big trees right reach x +4..+9 over the first 30 yds (2020 lidar, limb height not
  measured); single tree left at 45-60 yds, x -15..-30. The green is at x -18, so the line is clear.
- 13 Back / Middle: tall reeds / shrubs on the pond bank right of the tees, x +4..+13 at 10-30 yds.

## Minor

- Fairway edges: all within +/-3 yds of OSM except the right edges of 10 (-2 ... -5), 15 (-3 ... -4) and 18
  (-2 ... -4), and 13 left (+2 ... +3): narrower than mapped.
- Bunkers: every mapped bunker found in NAIP 2023 within 2 yds (table below) except 10 (-71, 276): no sand there
  in RGB or CIR (phantom OSM bunker inside the native: remove edit in the json).
- Fairway outlines for 10, 15, 18 are in the json as `replace fairway` (confidence 0.6).
- 12: green outline ~2 yds small on the left / front; bunker ~1.5 yds off (short-right).

## Not resolved / caveats

- The 2020 lidar area (holes 10-14) under-reads short fescue: polygons there are a lower bound (confidence -0.05).
- Lidar is Dec 2020 / Dec 2023, NAIP Aug 2023: mowing lines can move; S2 Nov 2026 confirms every mapped native
  block is still standing (table below) but cannot fix an edge better than +/-5 yds.
- Narrow ditches (10 between fairway and green, 13 crossing at ~340) are not detected by NIR: truth kept.


## Mapped native polygons vs lidar height and Sentinel-2 Nov 2026 (present now?)

| hole | mapped native polygon (note) | area yd2 | detected native % | lidar tall % | median veg height m | S2 Nov-2026 NDVI (integrator file) polygon / hole fairway | verdict |
|---|---|---|---|---|---|---|---|
| 10 | prairie left | 4647 | 67 | 59 | 0.08 | 0.61 / 0.87 | mostly present, edges off |
| 10 | prairie beyond the cart path right | 5945 | 54 | 51 | 0.07 | 0.62 / 0.87 | mostly present, edges off |
| 11 | prairie strip between 11 and the parallel fairway | 3939 | 57 | 46 | 0.06 | 0.70 / 0.88 | mostly present, edges off |
| 11 | fescue beyond the cart path right | 3978 | 76 | 69 | 0.14 | 0.60 / 0.88 | present |
| 13 | fescue right: unmown blocks inside the cart path | 5276 | 75 | 65 | 0.13 | 0.63 / 0.86 | present |
| 13 | native / wetland between the left cart path and the ditch | 1533 | 81 | 74 | 0.11 | 0.61 / 0.86 | present |
| 14 | from a neighbouring hole's map (hand:extra) | 5431 | 80 | 72 | 0.12 | 0.55 / 0.88 | present |
| 15 | prairie left | 8495 | 50 | 42 | 0.04 | 0.62 / 0.88 | mostly present, edges off |
| 15 | fescue right beyond the cart path | 3090 | 87 | 81 | 0.10 | 0.54 / 0.88 | present |
| 16 | fescue mound right of the fairway, inside the cart path | 870 | 14 | 7 | 0.04 | 0.78 / 0.85 | LOW / thin: lidar height = mown rough, S2 near turf (see 16) |
| 16 | prairie left | 5862 | 71 | 68 | 0.17 | 0.64 / 0.85 | present |
| 16 | fescue right from the cart path out | 3425 | 86 | 85 | 0.15 | 0.55 / 0.85 | present |
| 18 | fescue left between the cart path and the rough | 5491 | 79 | 78 | 0.10 | 0.55 / 0.88 | present |

## Station tables (par 4 / 5)

x in yds right of the Back-tee line (negative = left); `off` = detected - truth (positive = the real edge is further RIGHT). Fairway `det` = all-source classifier; in brackets the NAIP-2023-only and the NAIP-2019-22-only classifiers (leave-holes-out). Native `det` = lidar vegetation height >= 0.07 m (plus low fescue where NAIP 2023 agrees), in brackets the lidar-only edge. First hit going outward from the fairway centre; `.` = none within the frame.


### Hole 10

| along | fairway L: truth / det (2023, 2019-22) / off | fairway R: truth / det (2023, 2019-22) / off | native L: truth / det (lidar) / off | native R: truth / det (lidar) / off | trees L truth/det | trees R truth/det/off |
|---|---|---|---|---|---|---|
| 140 | -25 / -27 (-27, -28) / -2 | 25 / 23 (22, 25) / -2 | -45 / -36 (-36) / +9 | 52 / 34 (34) / -18 | . / . | . / . / . |
| 150 | -25 / -27 (-27, -26) / -3 | 28 / 24 (23, 26) / -3 | -45 / -36 (-37) / +9 | 51 / 35 (35) / -15 | . / . | . / . / . |
| 160 | -26 / -27 (-27, -25) / -1 | 29 / 24 (23, 28) / -5 | -46 / -45 (-42) / +1 | 49 / 37 (37) / -13 | . / . | . / . / . |
| 170 | -26 / -27 (-27, -22) / -1 | 30 / 27 (26, 30) / -4 | -47 / -48 (-48) / -2 | 48 / 38 (38) / -10 | . / . | . / . / . |
| 180 | -24 / -25 (-25, -25) / -1 | 33 / 30 (15, 32) / -3 | -45 / -36 (-36) / +9 | 46 / 40 (41) / -6 | . / . | . / . / . |
| 190 | -21 / -23 (-22, -22) / -2 | 35 / 7 (5, 15) / -28 | -45 / -33 (-33) / +12 | 45 / 41 (42) / -4 | . / . | . / . / . |
| 200 | -18 / -19 (-19, -19) / -1 | 5 / -4 (-5, -1) / -9 | -45 / -41 (-41) / +4 | 44 / 43 (43) / -0 | . / . | . / . / . |
| 210 | -14 / -15 (-13, -16) / -1 | 38 / 34 (34, 35) / -3 | -51 / -51 (-51) / -1 | 42 / 45 (45) / +3 | . / . | . / . / . |
| 220 | -10 / -11 (-10, -13) / -1 | 37 / 34 (34, 35) / -2 | -49 / -53 (-53) / -4 | 41 / 46 (46) / +5 | . / . | . / . / . |
| 230 | -6 / -7 (-6, -11) / -0 | 38 / 36 (35, 37) / -2 | -46 / -59 (-60) / -13 | 40 / 45 (45) / +6 | . / . | . / . / . |
| 240 | -49 / -50 (-50, -48) / -2 | -18 / -20 (-21, -15) / -2 | -49 / -59 (-60) / -10 | 39 / 49 (49) / +9 | . / . | . / . / . |

### Hole 11

| along | fairway L: truth / det (2023, 2019-22) / off | fairway R: truth / det (2023, 2019-22) / off | native L: truth / det (lidar) / off | native R: truth / det (lidar) / off | trees L truth/det | trees R truth/det/off |
|---|---|---|---|---|---|---|
| 140 | . / . (., .) / . | . / . (., .) / . | . / -43 (-44) / . | . / 28 (30) / . | . / . | . / . / . |
| 150 | -34 / -34 (-33, -36) / +0 | -2 / -5 (-5, -3) / -3 | . / -48 (-48) / . | 32 / 31 (39) / -1 | . / . | . / . / . |
| 160 | -38 / -37 (-37, -39) / +1 | 2 / -2 (-1, 1) / -4 | -48 / -52 (-54) / -4 | 32 / 31 (43) / -1 | . / . | . / . / . |
| 170 | -39 / -40 (-40, -41) / -2 | 6 / 3 (3, 5) / -3 | -48 / -53 (-54) / -5 | 33 / 33 (34) / +0 | . / . | . / . / . |
| 180 | -40 / -42 (-42, -42) / -2 | 8 / 5 (5, -10) / -2 | -48 / -54 (-55) / -6 | 34 / 35 (35) / +0 | . / . | . / . / . |
| 190 | -39 / -40 (-41, -41) / -1 | 10 / 8 (8, 10) / -2 | -44 / -51 (-51) / -7 | 36 / 35 (36) / -1 | . / . | . / . / . |
| 200 | -36 / -38 (-38, -38) / -2 | 14 / 13 (12, 14) / -1 | -41 / -47 (-47) / -5 | 37 / 39 (41) / +2 | . / . | . / . / . |
| 210 | -32 / -34 (-34, -35) / -2 | 18 / 16 (15, 18) / -1 | -38 / -42 (-43) / -4 | 39 / 42 (43) / +3 | . / . | . / . / . |
| 220 | -28 / -30 (-30, -30) / -1 | 22 / -3 (-4, -1) / -25 | -35 / -40 (-41) / -5 | 41 / 45 (46) / +4 | . / . | . / . / . |
| 230 | -24 / -26 (-24, -26) / -2 | 25 / 2 (1, 3) / -24 | -31 / -40 (-43) / -9 | 43 / 44 (45) / +1 | . / . | . / . / . |
| 240 | -20 / -21 (-21, -22) / -1 | 26 / 23 (22, 25) / -3 | -27 / -32 (-34) / -5 | 45 / 47 (48) / +2 | . / . | . / . / . |
| 250 | -18 / -18 (-16, -19) / +0 | 19 / 19 (17, 21) / -1 | -23 / -29 (-31) / -6 | 47 / 49 (50) / +2 | . / . | . / . / . |
| 260 | -13 / -15 (-14, -16) / -2 | 29 / 27 (25, 29) / -2 | -21 / -24 (-28) / -4 | 50 / 55 (55) / +4 | . / . | . / . / . |
| 270 | -8 / -10 (-10, -10) / -1 | 34 / 33 (32, 35) / -1 | -19 / -21 (-27) / -2 | 54 / 55 (56) / +1 | . / . | . / . / . |
| 280 | -4 / -4 (-4, -6) / -0 | 37 / 35 (35, 37) / -1 | -17 / -15 (-24) / +1 | 57 / 57 (58) / +0 | . / . | . / . / . |
| 290 | 1 / 0 (0, -2) / -1 | 41 / 40 (39, 41) / -1 | -13 / -12 (-12) / +2 | 60 / 63 (63) / +2 | . / . | . / . / . |
| 300 | 6 / 5 (5, 3) / -2 | 45 / 43 (42, 46) / -2 | -10 / -7 (-8) / +3 | 64 / 66 (66) / +2 | . / . | . / . / . |
| 310 | 11 / 10 (10, 8) / -1 | 49 / 47 (46, 48) / -2 | -9 / -2 (-3) / +6 | . / 70 (70) / . | . / . | . / . / . |
| 320 | 17 / 15 (16, 14) / -1 | 53 / 52 (49, 53) / -1 | -8 / 2 (0) / +10 | . / 76 (76) / . | . / . | . / . / . |
| 330 | 24 / 21 (22, 19) / -2 | 58 / 57 (55, 58) / -2 | -7 / 8 (7) / +15 | . / 79 (79) / . | . / . | . / . / . |
| 340 | 28 / 27 (27, 27) / -1 | 63 / 63 (63, 64) / -0 | -6 / 13 (3) / +19 | . / 85 (88) / . | . / . | . / . / . |
| 350 | 33 / 32 (32, 31) / -1 | 68 / 67 (66, 69) / -1 | . / 21 (19) / . | . / 93 (97) / . | . / . | . / . / . |
| 360 | 41 / 40 (42, 42) / -1 | 73 / 71 (69, 73) / -3 | . / 24 (23) / . | . / 100 (110) / . | . / . | . / . / . |

### Hole 13

| along | fairway L: truth / det (2023, 2019-22) / off | fairway R: truth / det (2023, 2019-22) / off | native L: truth / det (lidar) / off | native R: truth / det (lidar) / off | trees L truth/det | trees R truth/det/off |
|---|---|---|---|---|---|---|
| 140 | . / . (., .) / . | . / . (., .) / . | -44 / -34 (-34) / +10 | 20 / 13 (13) / -8 | . / . | . / . / . |
| 150 | -20 / -16 (-17, -17) / +4 | 5 / 5 (6, -1) / +0 | -44 / -35 (-35) / +9 | 23 / 18 (18) / -5 | . / . | . / . / . |
| 160 | -23 / -20 (-20, -20) / +3 | 9 / 9 (9, -3) / +1 | -44 / -39 (-42) / +5 | 25 / 21 (22) / -4 | . / . | . / . / . |
| 170 | -25 / -22 (-22, -23) / +2 | 11 / 11 (11, 11) / -0 | -46 / -42 (-42) / +4 | 28 / 26 (27) / -2 | . / . | . / . / . |
| 180 | -26 / -24 (-24, -24) / +2 | 12 / 12 (12, 12) / +0 | -49 / -48 (-48) / +1 | 31 / 32 (33) / +1 | . / . | . / . / . |
| 190 | -27 / -9 (-9, -24) / +17 | 14 / 14 (14, 6) / -1 | -44 / -49 (-50) / -5 | 33 / 35 (35) / +1 | . / . | . / . / . |
| 200 | -27 / -25 (-25, -25) / +2 | 15 / 16 (17, -1) / +1 | -45 / -47 (-48) / -3 | 36 / 37 (37) / +1 | . / . | . / . / . |
| 210 | -27 / -26 (-26, -8) / +1 | 17 / 18 (19, 18) / +1 | -45 / -51 (-52) / -6 | 38 / 40 (42) / +3 | . / . | . / . / . |
| 220 | -26 / -25 (-4, -25) / +1 | 21 / 22 (22, 22) / +1 | -45 / -47 (-58) / -2 | 39 / 44 (45) / +5 | . / . | . / . / . |
| 230 | -26 / -24 (-23, -24) / +2 | 25 / 26 (26, 26) / +1 | . / -68 (-69) / . | 41 / 48 (49) / +8 | . / . | . / . / . |
| 240 | -25 / -23 (-23, -23) / +2 | 22 / 23 (19, 24) / +0 | . / -72 (-73) / . | 42 / 49 (50) / +7 | . / . | . / . / . |
| 250 | -24 / -22 (-22, -22) / +2 | 14 / 16 (11, 17) / +2 | . / -74 (-74) / . | 44 / 50 (50) / +6 | . / . | . / . / . |
| 260 | -23 / -20 (-17, -21) / +3 | 8 / 8 (1, 10) / +0 | . / -76 (-77) / . | 45 / 52 (53) / +8 | . / . | . / . / . |
| 270 | -22 / -19 (-16, -20) / +3 | 7 / 7 (4, 7) / -0 | . / -78 (-79) / . | 46 / 54 (55) / +8 | . / . | . / . / . |
| 280 | -22 / -19 (-18, -19) / +3 | 40 / 42 (42, 42) / +2 | . / -78 (-78) / . | 46 / 54 (54) / +8 | . / . | . / . / . |
| 290 | -21 / -18 (-16, -19) / +3 | 39 / 40 (40, 40) / +1 | . / -84 (-84) / . | 47 / 53 (53) / +5 | . / . | . / . / . |
| 300 | -20 / -18 (-15, -19) / +2 | 39 / 38 (39, 39) / -0 | . / -54 (-88) / . | 48 / 52 (52) / +4 | . / . | . / . / . |
| 310 | -13 / -12 (-9, -13) / +1 | 37 / 39 (39, 38) / +2 | . / -55 (-59) / . | 48 / 50 (50) / +1 | . / . | . / . / . |
| 320 | -8 / -7 (5, -8) / +1 | 36 / 38 (38, 37) / +2 | . / -59 (-59) / . | 49 / 49 (50) / +0 | . / . | . / . / . |
| 330 | -2 / 0 (4, -2) / +2 | 34 / 36 (37, 36) / +2 | . / -61 (-62) / . | 49 / 50 (50) / +0 | . / . | . / . / . |
| 340 | 3 / 5 (8, 4) / +1 | 32 / 35 (35, 34) / +3 | . / -65 (1) / . | 50 / 46 (46) / -3 | . / . | . / . / . |
| 350 | -40 / -38 (-38, -39) / +2 | -5 / -4 (-3, -3) / +2 | . / -65 (-64) / . | . / 42 (43) / . | . / . | . / . / . |
| 360 | -38 / -39 (-39, -21) / -1 | 2 / 2 (2, 3) / -0 | . / -64 (-64) / . | . / 38 (38) / . | . / . | . / . / . |
| 370 | -35 / -37 (-37, -38) / -2 | 8 / 6 (6, -11) / -2 | . / -62 (-62) / . | . / 32 (32) / . | . / . | . / . / . |
| 380 | -32 / -31 (-31, -32) / +1 | 13 / 12 (12, -5) / -1 | . / -61 (-61) / . | . / 22 (22) / . | . / . | . / . / . |
| 390 | -23 / -21 (-20, -5) / +2 | 17 / 14 (14, 5) / -3 | . / -60 (-60) / . | . / 27 (27) / . | . / . | . / . / . |
| 400 | -18 / -15 (-15, -16) / +3 | 16 / 17 (17, 17) / +1 | . / -58 (-58) / . | . / 46 (47) / . | . / . | . / . / . |
| 410 | -37 / -34 (-34, -34) / +3 | 14 / 15 (15, 3) / +1 | . / -56 (-56) / . | . / 59 (59) / . | . / . | . / . / . |
| 420 | -37 / -37 (-36, -37) / +0 | 16 / 16 (16, -3) / +0 | . / -55 (-55) / . | . / 62 (62) / . | . / . | . / . / . |
| 430 | -36 / -36 (-36, -36) / +1 | 19 / 19 (19, 3) / +0 | . / -53 (-53) / . | . / . (.) / . | . / . | . / . / . |
| 440 | -36 / -36 (-36, -35) / +0 | 20 / 21 (21, 21) / +1 | . / -53 (-53) / . | . / . (.) / . | . / . | . / . / . |
| 450 | -36 / -35 (-33, -35) / +1 | 21 / 22 (-6, 22) / +1 | . / -51 (-51) / . | . / . (.) / . | . / . | . / . / . |
| 460 | -36 / -13 (-12, -16) / +24 | 21 / 24 (-9, 27) / +3 | . / -51 (-51) / . | . / . (.) / . | . / . | . / . / . |
| 470 | -15 / -8 (-7, -10) / +7 | 21 / 24 (24, 27) / +3 | . / -53 (-56) / . | . / . (.) / . | -60 / . | . / . / . |
| 480 | -35 / -30 (-13, -33) / +5 | 21 / 21 (21, 22) / +0 | . / -50 (-50) / . | . / . (.) / . | -60 / . | . / . / . |
| 490 | -31 / -31 (-28, -31) / +0 | 15 / 14 (14, 15) / -1 | . / -50 (-50) / . | . / 34 (34) / . | . / . | . / . / . |
| 500 | -26 / -26 (-25, -26) / +1 | 7 / 8 (5, 9) / +2 | . / -49 (-49) / . | . / 25 (25) / . | . / . | . / . / . |

### Hole 15

| along | fairway L: truth / det (2023, 2019-22) / off | fairway R: truth / det (2023, 2019-22) / off | native L: truth / det (lidar) / off | native R: truth / det (lidar) / off | trees L truth/det | trees R truth/det/off |
|---|---|---|---|---|---|---|
| 140 | . / . (., .) / . | . / . (., .) / . | -15 / -11 (-12) / +4 | . / 66 (66) / . | . / . | . / . / . |
| 150 | 14 / 13 (14, 12) / -0 | 48 / 45 (44, 47) / -3 | -16 / -9 (-11) / +7 | . / 82 (84) / . | . / . | . / . / . |
| 160 | 8 / 6 (5, 7) / -2 | 55 / 51 (51, 52) / -4 | -18 / -10 (-11) / +8 | . / 87 (88) / . | . / . | . / . / . |
| 170 | 5 / 5 (5, 4) / +0 | 59 / 55 (55, 56) / -3 | -20 / -10 (-11) / +9 | . / 89 (89) / . | . / . | . / . / . |
| 180 | 3 / 5 (5, 19) / +1 | 63 / 59 (59, 62) / -4 | -20 / -11 (-12) / +8 | . / 89 (89) / . | . / . | . / . / . |
| 190 | 3 / 5 (5, 3) / +1 | 66 / 63 (63, 64) / -3 | -20 / -10 (-11) / +9 | . / 88 (88) / . | . / . | . / . / . |
| 200 | 4 / 5 (5, 4) / +1 | 68 / 64 (64, 66) / -3 | -20 / -18 (-18) / +1 | . / 85 (85) / . | . / . | . / . / . |
| 210 | 4 / 5 (5, 5) / +0 | 69 / 64 (63, 65) / -5 | -22 / -14 (-16) / +8 | . / 82 (82) / . | . / . | . / . / . |
| 220 | 7 / 24 (24, 23) / +17 | 67 / 63 (62, 64) / -4 | -25 / -13 (-14) / +12 | . / 78 (78) / . | . / . | . / . / . |
| 230 | 28 / 27 (28, 25) / -1 | 64 / 61 (61, 62) / -3 | -28 / -19 (17) / +8 | 73 / 76 (76) / +3 | . / . | . / . / . |
| 240 | 27 / 26 (26, 25) / -1 | 61 / 58 (57, 60) / -3 | -29 / 22 (22) / +51 | 70 / 72 (72) / +3 | . / . | . / . / . |
| 250 | 6 / 5 (6, 4) / -1 | 58 / 54 (53, 56) / -4 | -31 / -24 (-24) / +7 | 66 / 68 (68) / +2 | . / . | . / . / . |
| 260 | -5 / -7 (-7, -7) / -1 | 54 / 50 (49, 51) / -4 | -33 / -24 (-25) / +8 | 63 / 65 (65) / +2 | . / . | . / . / . |
| 270 | -11 / -11 (-10, -11) / +0 | 49 / 45 (45, 46) / -4 | -34 / -28 (-28) / +6 | 60 / 61 (63) / +1 | . / . | . / . / . |
| 280 | -13 / -13 (-13, -14) / +0 | 45 / 42 (41, 43) / -4 | -35 / -32 (-33) / +4 | 56 / 60 (61) / +3 | . / . | . / . / . |
| 290 | -15 / -16 (-15, -17) / -1 | 42 / 39 (38, 39) / -4 | -36 / -34 (-37) / +2 | 53 / 55 (56) / +2 | . / . | . / . / . |
| 300 | -17 / -19 (-19, -19) / -2 | 38 / 34 (33, 34) / -4 | -38 / -36 (-40) / +2 | 50 / 49 (50) / -0 | . / . | . / . / . |
| 310 | -21 / -21 (-21, -22) / +0 | 32 / 28 (28, 29) / -4 | -38 / -38 (-41) / +0 | 46 / 45 (45) / -2 | . / . | . / . / . |
| 320 | -25 / -25 (-25, -26) / +0 | 27 / 24 (23, 25) / -3 | -39 / -40 (-41) / -1 | 43 / 42 (44) / -1 | . / . | . / . / . |
| 330 | -27 / -26 (-26, -27) / +1 | 23 / 21 (20, 23) / -3 | -39 / -39 (-41) / -0 | 42 / 43 (44) / +1 | . / . | . / . / . |
| 340 | -27 / -27 (-27, -30) / +0 | 20 / 18 (17, 19) / -3 | -39 / -42 (-42) / -3 | 41 / 43 (44) / +2 | . / . | . / . / . |
| 350 | -26 / -26 (-26, -29) / +0 | 19 / 15 (15, 15) / -4 | . / -43 (-43) / . | . / 42 (42) / . | -36 / . | . / . / . |
| 360 | -27 / -28 (-28, -29) / -1 | 15 / 12 (12, 12) / -4 | . / -41 (-47) / . | . / 36 (36) / . | -33 / . | . / . / . |
| 370 | -31 / -30 (-30, -32) / +1 | 11 / 8 (7, 9) / -3 | . / -42 (-43) / . | . / 34 (34) / . | -34 / . | . / . / . |
| 380 | -35 / -33 (-33, -34) / +2 | -15 / -18 (-19, -15) / -3 | . / -46 (-46) / . | . / 30 (31) / . | . / . | . / . / . |
| 390 | -38 / -37 (-37, -38) / +0 | -17 / -18 (-19, -16) / -2 | . / -49 (-49) / . | . / 26 (28) / . | . / . | . / . / . |

### Hole 16

| along | fairway L: truth / det (2023, 2019-22) / off | fairway R: truth / det (2023, 2019-22) / off | native L: truth / det (lidar) / off | native R: truth / det (lidar) / off | trees L truth/det | trees R truth/det/off |
|---|---|---|---|---|---|---|
| 140 | -24 / -23 (-21, -24) / +1 | 20 / 22 (11, 22) / +2 | -32 / -31 (-31) / +1 | 33 / 38 (38) / +5 | . / . | . / . / . |
| 150 | -25 / -23 (-22, -24) / +2 | 20 / 22 (22, 22) / +2 | -32 / -33 (-33) / -1 | 35 / 38 (38) / +3 | . / . | . / . / . |
| 160 | -22 / -21 (-21, -23) / +1 | 21 / 23 (19, 23) / +2 | -32 / -33 (-33) / -1 | 36 / 40 (40) / +3 | . / . | . / . / . |
| 170 | -21 / -21 (-21, -22) / -1 | 25 / 25 (24, 25) / +0 | -32 / -32 (-32) / +0 | 38 / 42 (42) / +4 | . / . | . / . / . |
| 180 | -24 / -23 (-22, -25) / +2 | 27 / 28 (17, 28) / +0 | -33 / -32 (-32) / +1 | 45 / 45 (45) / -0 | . / . | . / . / . |
| 190 | -29 / -26 (-26, -18) / +3 | 28 / 29 (11, 29) / +1 | -33 / -33 (-33) / +0 | 48 / 48 (48) / +0 | . / . | . / . / . |
| 200 | -25 / -22 (-21, -23) / +3 | 31 / 31 (32, 31) / +1 | -33 / -35 (-35) / -2 | 51 / 53 (53) / +2 | . / . | . / . / . |
| 210 | -17 / -14 (-12, -16) / +2 | 33 / 34 (35, 33) / +1 | -33 / -30 (-29) / +3 | 54 / 55 (55) / +1 | . / . | . / . / . |
| 220 | -10 / -8 (8, -8) / +2 | 35 / 34 (34, 36) / -2 | -34 / -42 (-43) / -8 | 57 / 57 (57) / +0 | . / . | . / . / . |
| 230 | -17 / -15 (7, -16) / +2 | 32 / 33 (32, 33) / +1 | -33 / -33 (-43) / +0 | 56 / 58 (41) / +2 | . / . | . / . / . |
| 240 | -19 / -17 (-17, -19) / +2 | 30 / 30 (29, 30) / +0 | -33 / -25 (-25) / +8 | 56 / 57 (58) / +1 | . / . | . / . / . |
| 250 | -17 / -16 (-16, -17) / +1 | 25 / 24 (24, 8) / -1 | -32 / -22 (-22) / +10 | 55 / 38 (32) / -17 | . / . | . / . / . |
| 260 | -16 / -16 (-15, -18) / +1 | 22 / 17 (18, 9) / -5 | -32 / -22 (-22) / +10 | 55 / 56 (56) / +1 | . / . | 92 / . / . |
| 270 | -18 / -15 (-15, -14) / +3 | 20 / 16 (17, 7) / -4 | -31 / -20 (-20) / +11 | 20 / 54 (54) / +33 | . / . | 92 / . / . |
| 280 | -18 / -16 (-15, -7) / +2 | 8 / 7 (7, 9) / -1 | -31 / -20 (-20) / +11 | 8 / 10 (10) / +2 | . / . | . / . / . |
| 290 | -17 / -15 (-15, -17) / +1 | 5 / 5 (5, 7) / +0 | -30 / -19 (-19) / +12 | 7 / 7 (7) / +1 | . / . | . / . / . |
| 300 | -12 / -8 (-8, 4) / +3 | 36 / 36 (35, 26) / -0 | -30 / -22 (-22) / +8 | 49 / 49 (49) / +0 | . / . | . / . / . |
| 310 | 4 / 8 (11, 15) / +5 | 37 / 36 (36, 36) / -1 | . / 3 (3) / . | . / 49 (49) / . | . / . | . / . / . |
| 320 | 10 / 12 (14, 11) / +2 | 32 / 31 (26, 32) / -1 | . / 8 (8) / . | . / 48 (48) / . | . / . | . / . / . |

### Hole 18

| along | fairway L: truth / det (2023, 2019-22) / off | fairway R: truth / det (2023, 2019-22) / off | native L: truth / det (lidar) / off | native R: truth / det (lidar) / off | trees L truth/det | trees R truth/det/off |
|---|---|---|---|---|---|---|
| 140 | . / . (., .) / . | . / . (., .) / . | -18 / -2 (-2) / +15 | . / 24 (24) / . | . / . | 40 / 37 / -3 |
| 150 | . / . (., .) / . | . / . (., .) / . | -18 / -8 (-8) / +10 | . / 28 (28) / . | . / . | 36 / 52 / +17 |
| 160 | . / . (., .) / . | . / . (., .) / . | -19 / -10 (-10) / +9 | . / 30 (30) / . | . / . | 34 / 38 / +4 |
| 170 | . / . (., .) / . | . / . (., .) / . | -20 / -10 (-11) / +9 | . / 29 (30) / . | . / . | 36 / 40 / +4 |
| 180 | . / . (., .) / . | . / . (., .) / . | -20 / -12 (-12) / +8 | . / 30 (30) / . | . / . | 40 / 44 / +4 |
| 190 | . / . (., .) / . | . / . (., .) / . | -21 / -14 (-14) / +7 | . / 34 (34) / . | . / . | 39 / 44 / +5 |
| 200 | -3 / -3 (-0, -4) / +0 | 26 / 25 (20, 26) / -1 | -22 / -16 (-16) / +6 | . / 40 (40) / . | . / . | 46 / 49 / +3 |
| 210 | -5 / -6 (-6, -6) / -1 | 28 / 26 (24, 26) / -2 | -23 / -19 (-19) / +4 | . / 41 (41) / . | . / . | 47 / 49 / +2 |
| 220 | -6 / -6 (-6, -7) / -1 | 31 / 27 (23, 28) / -4 | -25 / -19 (-19) / +6 | . / 42 (42) / . | . / . | 46 / 50 / +4 |
| 230 | -6 / -7 (-7, -8) / -1 | 36 / 32 (27, 24) / -4 | -27 / -20 (-20) / +7 | . / . (.) / . | . / . | 48 / 52 / +4 |
| 240 | -8 / -8 (-6, -9) / +0 | 39 / 21 (17, 13) / -18 | -28 / -23 (-23) / +5 | . / 46 (.) / . | . / . | 44 / 54 / +10 |
| 250 | 1 / -0 (4, 10) / -1 | 40 / 36 (18, 12) / -4 | -30 / -26 (-26) / +5 | . / . (.) / . | . / . | 50 / 55 / +5 |
| 260 | 6 / 9 (12, 18) / +2 | 42 / 31 (40, 22) / -11 | -32 / -29 (-29) / +4 | . / . (.) / . | . / . | 54 / 57 / +3 |
| 270 | 2 / 8 (11, 16) / +5 | 42 / 38 (38, 21) / -4 | -34 / -0 (-0) / +34 | . / . (92) / . | . / . | 54 / 61 / +6 |
| 280 | -12 / -10 (2, -12) / +2 | 42 / 40 (40, 15) / -3 | -38 / -34 (-34) / +3 | . / . (.) / . | . / . | 58 / 64 / +7 |
| 290 | -10 / -10 (-8, -11) / +0 | 43 / 40 (40, 42) / -3 | -42 / -37 (-36) / +5 | . / . (.) / . | . / . | 54 / 60 / +5 |
| 300 | -6 / -5 (-4, -6) / +1 | 43 / 40 (41, 33) / -3 | -46 / -40 (-39) / +6 | . / . (.) / . | . / . | 58 / 65 / +7 |
| 310 | -15 / -10 (-8, -12) / +4 | 43 / 40 (39, 37) / -3 | -51 / -44 (-44) / +7 | . / 58 (58) / . | . / . | 54 / 68 / +14 |
| 320 | -26 / -26 (-26, -28) / +0 | 43 / 41 (40, 42) / -2 | -58 / -48 (-48) / +9 | . / 58 (58) / . | . / . | 58 / 71 / +12 |
| 330 | -28 / -29 (-29, -30) / -1 | 42 / 41 (40, 42) / -2 | -60 / -53 (-53) / +7 | . / 60 (60) / . | . / . | 59 / 68 / +10 |
| 340 | -29 / -29 (-28, -30) / -0 | 42 / 41 (42, 42) / -1 | -62 / -56 (-56) / +7 | . / 62 (62) / . | . / . | 58 / 73 / +15 |
| 350 | -31 / -31 (-31, -32) / +0 | 42 / 42 (42, 43) / -0 | . / -56 (-56) / . | . / 63 (63) / . | . / . | 57 / 71 / +14 |
| 360 | -34 / -34 (-34, -35) / +0 | 40 / 40 (40, 41) / +0 | . / -56 (-57) / . | . / 64 (64) / . | . / . | 75 / 73 / -2 |
| 370 | -37 / -38 (-38, -38) / -1 | 37 / 37 (37, 37) / -0 | . / -62 (-62) / . | . / 63 (63) / . | . / . | 74 / 79 / +5 |
| 380 | -40 / -39 (-38, -41) / +1 | 22 / 21 (21, 24) / -1 | . / -58 (-58) / . | . / 63 (64) / . | . / . | 73 / 80 / +7 |
| 390 | -40 / -41 (-40, -42) / -0 | 20 / 19 (19, 20) / -1 | . / -56 (-56) / . | . / 63 (64) / . | . / . | 68 / 82 / +14 |
| 400 | -28 / -36 (-26, -37) / -8 | 24 / 22 (21, 24) / -1 | . / -58 (-58) / . | . / 62 (63) / . | . / -65 | 70 / 89 / +19 |
| 410 | -3 / -2 (-2, -3) / +1 | 28 / 27 (26, 28) / -1 | . / -60 (-60) / . | . / 62 (63) / . | . / . | 69 / 87 / +18 |
| 420 | -7 / -4 (0, -5) / +3 | 32 / 30 (30, 32) / -2 | . / -63 (-63) / . | . / 61 (61) / . | . / . | 68 / . / . |
| 430 | -59 / -59 (-18, -60) / +0 | 36 / 35 (33, 36) / -1 | . / -66 (-66) / . | . / 57 (58) / . | . / . | 67 / . / . |
| 440 | -64 / -62 (-62, -64) / +1 | 37 / 36 (36, 36) / -1 | . / -68 (-69) / . | . / 55 (55) / . | . / . | 69 / . / . |
| 450 | -62 / -61 (-60, -63) / +2 | 35 / 35 (35, 35) / -0 | . / -67 (-68) / . | . / 54 (62) / . | . / . | 70 / . / . |
| 460 | -58 / -58 (-58, -59) / +1 | 32 / 31 (31, 32) / -1 | . / -62 (-62) / . | . / 52 (52) / . | . / -122 | 72 / . / . |
| 470 | -53 / -54 (-53, -54) / -1 | 32 / 31 (30, 32) / -1 | . / -59 (-60) / . | . / 50 (50) / . | . / . | 74 / . / . |
| 480 | -47 / -46 (-46, -45) / +0 | 29 / 28 (27, 29) / -1 | . / -56 (-56) / . | . / 47 (47) / . | . / . | 79 / . / . |
| 490 | -40 / -39 (-39, -40) / +0 | 18 / 18 (16, 19) / -0 | . / -48 (-49) / . | . / 44 (44) / . | . / . | 82 / . / . |
| 500 | -36 / -35 (-34, -36) / +1 | 6 / 6 (5, 6) / -1 | . / -112 (-56) / . | . / 38 (38) / . | . / . | 81 / 68 / -13 |

## Green surrounds: distance (yds) from the green edge to the first feature, 8 directions

Directions in the hole frame (long = past the green along the line from the Back tee). Truth / detected; `.` = none within 40 yds. Narrow ditches are not detected (trust truth water where det is `.`); `sand det` next to a cart path can be the path.


### Hole 10

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 20 / 21 | . / 25 | . / . | . / 13 | . / . |
| long-right | 12 / 11 | . / 31 | 3 / . | . / 35 | . / . |
| right | 8 / 8 | . / . | 2 / . | . / . | . / . |
| short-right | 11 / 10 | . / . | 3 / . | . / . | . / . |
| short | 21 / 22 | . / . | 22 / . | . / . | . / . |
| short-left | 13 / 15 | . / 10 | . / . | 31 / . | . / . |
| left | 11 / 13 | . / . | . / . | 16 / 22 | . / . |
| long-left | 14 / 16 | 19 / 18 | . / . | 24 / 23 | . / . |

### Hole 11

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 17 / 4 | . / . | . / . | . / . | . / . |
| long-right | 10 / 11 | . / 22 | . / . | . / 32 | . / . |
| right | 12 / 12 | . / 12 | . / . | . / 20 | . / . |
| short-right | 15 / 14 | . / 18 | . / . | . / 22 | . / . |
| short | 18 / 19 | . / . | . / . | . / . | . / . |
| short-left | 12 / 10 | . / . | . / . | . / . | . / . |
| left | 13 / 7 | . / . | . / . | . / 38 | . / . |
| long-left | 16 / 3 | . / . | . / . | . / 25 | . / . |

### Hole 12

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 14 / 15 | . / . | 9 / 9 | . / 5 | . / . |
| long-right | 11 / 12 | . / . | . / . | . / 8 | . / . |
| right | 13 / 13 | . / 40 | . / . | . / 18 | . / . |
| short-right | 14 / 15 | . / 6 | . / . | . / . | . / . |
| short | 13 / 15 | . / . | 6 / . | . / . | . / . |
| short-left | 10 / 11 | . / 5 | 5 / 6 | . / . | . / . |
| left | 10 / 13 | . / . | 6 / 7 | . / . | . / . |
| long-left | 15 / 16 | . / . | 5 / 6 | . / . | . / . |

### Hole 13

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 14 / 15 | . / 25 | . / . | . / 9 | . / . |
| long-right | 14 / 16 | . / 20 | 37 / . | . / 7 | . / . |
| right | 13 / 15 | . / . | 8 / . | . / 6 | . / . |
| short-right | 13 / 14 | . / . | 2 / . | . / 2 | . / . |
| short | 19 / 20 | . / . | . / . | . / . | . / . |
| short-left | 11 / 10 | . / . | . / . | . / . | . / . |
| left | 8 / 8 | 6 / 5 | . / . | . / 34 | . / . |
| long-left | 11 / 10 | . / . | . / . | . / 29 | . / . |

### Hole 14

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 17 / 3 | . / . | . / . | . / 15 | 7 / 18 |
| long-right | 12 / 5 | . / . | . / . | . / . | 12 / 22 |
| right | 11 / 12 | . / 28 | . / . | . / 34 | . / . |
| short-right | 16 / 17 | . / 36 | . / . | . / . | . / . |
| short | 16 / 15 | . / . | . / . | . / . | . / . |
| short-left | 11 / 10 | 9 / 7 | . / . | 23 / 21 | . / . |
| left | 11 / 8 | . / . | . / . | . / 35 | 11 / 3 |
| long-left | 15 / 14 | . / . | . / . | . / 4 | 0 / 14 |

### Hole 15

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 20 / 20 | . / . | . / . | . / 6 | . / . |
| long-right | 18 / 17 | . / . | . / . | . / 9 | . / . |
| right | 11 / 10 | . / . | . / . | . / . | . / . |
| short-right | 11 / 9 | 6 / 5 | . / . | . / . | . / . |
| short | 19 / 20 | . / . | . / . | . / . | . / . |
| short-left | 14 / 16 | . / . | . / . | . / 19 | . / . |
| left | 6 / 8 | . / 34 | . / . | . / 19 | . / . |
| long-left | 8 / 10 | . / . | . / . | . / 19 | . / . |

### Hole 16

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 17 / 18 | . / . | 27 / 29 | . / 5 | 0 / 2 |
| long-right | 12 / 13 | . / 32 | . / . | . / . | . / . |
| right | 9 / 10 | . / 38 | . / . | . / . | . / 29 |
| short-right | 18 / 18 | . / 8 | . / . | . / 6 | . / . |
| short | 21 / 22 | . / . | . / . | 37 / . | . / . |
| short-left | 13 / 13 | . / . | 4 / 6 | . / 0 | . / . |
| left | 13 / 13 | . / . | 4 / 4 | . / 0 | . / . |
| long-left | 22 / 21 | . / . | 6 / 8 | . / 2 | . / . |

### Hole 17

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 15 / 15 | . / . | . / . | . / . | 18 / 20 |
| long-right | 14 / 16 | . / 30 | . / . | . / 14 | 5 / 20 |
| right | 10 / 8 | . / . | . / . | . / . | 11 / 17 |
| short-right | 10 / 9 | . / . | . / . | . / . | 13 / 18 |
| short | 14 / 15 | . / . | . / . | . / . | . / . |
| short-left | 14 / 14 | . / . | . / . | . / . | . / . |
| left | 11 / 10 | . / 16 | . / . | . / . | 27 / 27 |
| long-left | 11 / 11 | . / 11 | 39 / . | . / 33 | 15 / 17 |

### Hole 18

| direction | green edge from centre: truth / det | sand: truth / det | water: truth / det | native: truth / det | trees: truth / det |
|---|---|---|---|---|---|
| long | 16 / 18 | . / 39 | . / . | . / 18 | . / . |
| long-right | 11 / 12 | . / 21 | . / . | . / 26 | . / . |
| right | 12 / 13 | 7 / 8 | . / . | . / . | . / . |
| short-right | 21 / 21 | . / . | . / . | . / . | . / . |
| short | 13 / 12 | . / . | 6 / 6 | . / 2 | . / . |
| short-left | 12 / 3 | . / . | 6 / 5 | . / 3 | . / . |
| left | 21 / 21 | . / . | 8 / 9 | . / 4 | . / . |
| long-left | 16 / 15 | . / . | . / . | . / 28 | . / . |

## Bunker / water table: reach and carry from the Back and Middle tees

reach = nearest point, carry = farthest point of the polygon (straight-line yds from the tee marker). Polygons = current truth (OSM / hand); detection check = the same bunker found in NAIP 2023 brightness (IoU, centroid shift) and its own reach / carry.


### Hole 10

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| water | -29 / 185 | 2220 | 59 / 330 | 46 / 310 | 39% of the polygon reads as open water (NIR) |
| sand | 8 / 198 | 43 | 194 / 201 | 174 / 181 | det area 42, IoU 0.56, shift x -1.6 along -0.5; det Back reach/carry 194/201 |
| water | -27 / 223 | 1557 | 143 / 330 | 125 / 310 | 56% of the polygon reads as open water (NIR) |
| sand | -32 / 250 | 43 | 247 / 256 | 228 / 237 | det area 32, IoU 0.48, shift x -1.1 along -0.8; det Back reach/carry 248/255 |
| sand | -60 / 262 | 44 | 265 / 272 | 247 / 253 | det area 42, IoU 0.51, shift x -1.5 along -1.7; det Back reach/carry 264/271 |
| sand | -71 / 276 | 31 | 282 / 288 | 263 / 269 | NOT seen as sand in NAIP 2023 |
| sand | -49 / 279 | 43 | 277 / 288 | 257 / 269 | det area 65, IoU 0.57, shift x -0.1 along -1.2; det Back reach/carry 275/288 |
| sand | -43 / 293 | 29 | 293 / 299 | 274 / 279 | det area 31, IoU 0.41, shift x -1.4 along -1.1; det Back reach/carry 292/298 |

### Hole 11

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| water | -20 / 48 | 176 | 18 / 73 | 15 / 52 | 0% of the polygon reads as open water (NIR) |
| water | 49 / 52 | 5400 | 37 / 240 | 16 / 221 | 77% of the polygon reads as open water (NIR) |
| sand | 52 / 381 | 59 | 380 / 391 | 358 / 369 | det area 93, IoU 0.33, shift x -2.9 along -0.9; det Back reach/carry 377/390 |

### Hole 12

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| water | 24 / 81 | 10319 | 35 / 203 | 31 / 187 | 85% of the polygon reads as open water (NIR) |
| sand | 18 / 118 | 42 | 114 / 123 | 98 / 107 | det area 37, IoU 0.44, shift x -1.8 along -1.5; det Back reach/carry 113/121 |

### Hole 13

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| sand | 34 / 235 | 39 | 233 / 242 | 220 / 229 | det area 55, IoU 0.52, shift x +1.2 along -0.3; det Back reach/carry 232/242 |
| water | 9 / 247 | 12522 | 12 / 595 | 12 / 582 | 73% of the polygon reads as open water (NIR) |
| sand | 26 / 247 | 97 | 242 / 256 | 229 / 243 | det area 141, IoU 0.69, shift x -0.1 along +0.2; det Back reach/carry 240/257 |
| water | -44 / 259 | 2624 | 144 / 350 | 131 / 337 | 70% of the polygon reads as open water (NIR) |
| sand | 14 / 262 | 48 | 258 / 267 | 245 / 254 | det area 73, IoU 0.55, shift x +0.8 along +0.9; det Back reach/carry 257/270 |
| sand | -27 / 394 | 84 | 387 / 402 | 374 / 389 | det area 104, IoU 0.52, shift x +2.2 along +0.6; det Back reach/carry 388/402 |
| sand | -18 / 468 | 44 | 462 / 473 | 449 / 460 | det area 62, IoU 0.43, shift x +1.6 along -0.5; det Back reach/carry 461/473 |
| sand | -9 / 539 | 80 | 533 / 545 | 520 / 532 | det area 72, IoU 0.72, shift x +1.3 along -0.1; det Back reach/carry 533/544 |

### Hole 14

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| sand | 21 / 144 | 42 | 142 / 149 | 126 / 133 | det area 41, IoU 0.48, shift x +1.8 along +0.7; det Back reach/carry 143/150 |
| sand | -18 / 190 | 121 | 180 / 199 | 166 / 185 | det area 62, IoU 0.21, shift x +5.8 along -6.7; det Back reach/carry 178/189 |

### Hole 15

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| sand | -47 / 47 | 123 | 59 / 78 | 50 / 67 | det area 62, IoU 0.21, shift x -5.7 along +7.4; det Back reach/carry 71/81 |
| sand | 18 / 232 | 103 | 226 / 240 | 206 / 220 | det area 145, IoU 0.44, shift x -2.4 along -1.7; det Back reach/carry 223/240 |
| sand | 8 / 240 | 63 | 236 / 243 | 216 / 223 | det area 94, IoU 0.46, shift x -2.9 along -2.4; det Back reach/carry 231/242 |
| sand | -5 / 247 | 82 | 241 / 252 | 221 / 232 | det area 80, IoU 0.55, shift x -1.4 along -0.6; det Back reach/carry 240/251 |
| sand | -9 / 394 | 46 | 389 / 399 | 369 / 379 | det area 43, IoU 0.48, shift x -1.5 along -0.6; det Back reach/carry 388/399 |
| sand | -7 / 413 | 110 | 406 / 421 | 386 / 401 | det area 98, IoU 0.67, shift x -1.6 along -0.0; det Back reach/carry 406/421 |

### Hole 16

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| sand | -28 / 208 | 50 | 207 / 214 | 179 / 185 | det area 82, IoU 0.47, shift x +2.1 along -0.6; det Back reach/carry 204/213 |
| sand | 39 / 229 | 20 | 228 / 235 | 199 / 206 | det area 43, IoU 0.46, shift x -0.0 along -1.2; det Back reach/carry 227/235 |
| sand | 34 / 250 | 55 | 247 / 259 | 218 / 229 | det area 101, IoU 0.55, shift x -0.3 along +0.3; det Back reach/carry 245/259 |
| water | -24 / 324 | 1977 | 308 / 353 | 279 / 325 | 81% of the polygon reads as open water (NIR) |
| sand | 26 / 333 | 16 | 331 / 337 | 302 / 307 | det area 37, IoU 0.28, shift x +1.8 along -1.4; det Back reach/carry 329/337 |
| water | -24 / 353 | 5374 | 308 / 419 | 279 / 391 | 87% of the polygon reads as open water (NIR) |

### Hole 17

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| sand | -52 / 68 | 16 | 83 / 88 | 68 / 72 | det area 37, IoU 0.27, shift x +1.7 along -1.5; det Back reach/carry 80/87 |
| water | -103 / 130 | 3349 | 92 / 269 | 82 / 251 | 93% of the polygon reads as open water (NIR) |
| sand | 6 / 161 | 49 | 156 / 167 | 134 / 145 | det area 46, IoU 0.47, shift x +1.4 along -1.0; det Back reach/carry 155/166 |
| sand | 15 / 170 | 50 | 166 / 176 | 144 / 154 | det area 1, IoU 0.01, shift x +1.2 along -1.8; det Back reach/carry 166/173 |
| sand | -24 / 179 | 70 | 173 / 188 | 152 / 166 | det area 75, IoU 0.61, shift x +0.4 along -0.2; det Back reach/carry 173/187 |
| sand | 18 / 185 | 65 | 180 / 191 | 158 / 169 | NOT seen as sand in NAIP 2023 |

### Hole 18

| kind | x / along (Back frame) | area yd2 | Back: reach / carry | Middle: reach / carry | detection check |
|---|---|---|---|---|---|
| water | 66 / 44 | 2957 | 45 / 118 | 36 / 90 | 0% of the polygon reads as open water (NIR) |
| sand | -44 / 87 | 60 | 93 / 103 | 63 / 71 | det area 69, IoU 0.49, shift x -0.7 along +3.1; det Back reach/carry 95/106 |
| sand | -56 / 96 | 46 | 106 / 116 | 77 / 87 | det area 54, IoU 0.48, shift x -0.4 along +2.0; det Back reach/carry 108/118 |
| sand | -5 / 263 | 95 | 256 / 270 | 214 / 228 | det area 121, IoU 0.63, shift x -1.2 along +1.4; det Back reach/carry 257/271 |
| sand | -5 / 264 | 95 | 256 / 270 | 214 / 228 | det area 121, IoU 0.64, shift x -1.2 along +1.3; det Back reach/carry 257/271 |
| sand | -19 / 298 | 184 | 288 / 308 | 246 / 267 | det area 238, IoU 0.64, shift x -1.1 along +2.5; det Back reach/carry 289/310 |
| sand | -20 / 298 | 182 | 288 / 308 | 246 / 267 | det area 238, IoU 0.64, shift x -1.1 along +2.5; det Back reach/carry 289/310 |
| sand | 29 / 388 | 42 | 383 / 394 | 340 / 352 | det area 53, IoU 0.57, shift x -0.6 along +2.6; det Back reach/carry 385/397 |
| sand | 36 / 394 | 30 | 392 / 399 | 349 / 356 | det area 57, IoU 0.52, shift x -0.3 along +0.4; det Back reach/carry 390/401 |
| sand | 39 / 405 | 104 | 402 / 413 | 360 / 370 | det area 110, IoU 0.00, shift x -6.9 along -12.7; det Back reach/carry 385/401 |
| sand | -13 / 415 | 60 | 407 / 422 | 365 / 380 | det area 89, IoU 0.49, shift x -0.4 along +1.4; det Back reach/carry 409/423 |
| water | -90 / 460 | 4985 | 385 / 542 | 349 / 502 | 68% of the polygon reads as open water (NIR) |
| sand | -25 / 528 | 96 | 522 / 535 | 480 / 493 | det area 87, IoU 0.71, shift x +0.2 along +1.6; det Back reach/carry 523/536 |