# Gateway National, holes 1-9: second-pass feature detection (specialist F1)

Status: **CHECKPOINT 2 (Fri Nov 13, ~03:25 UTC): all nine holes - must-apply edits for landing areas and par 3s. Further refinement, if any, replaces this file**. Machine-applicable edits, bunker / hazard table and the measured fairway edges:
`features_1_9.json` (same folder; schema of `features_10_18.json` plus `priority`, `hazards[]`,
`measured_fairway_edges`). Mapped values are read from `truth/package.json` as of commit bad105749 (the
integrator's Nov 13 02:43 map).

## 5-line summary

1. **Hole 8 inside the dogleg (right): mapped fescue is mown rough for 13-26 yds, and the trees are 10-40 yds closer
   than mapped from 265 yds on.** Both change what a Driver through the corner costs.
2. **Holes 5 right, 6 right + left, 2 left: mapped native sits on mown rough** (5 R: 17-27 yds of rough before the
   fescue, mapped 0-14; 6 R: 4-18 yds more; 6 L: rough runs to the tree row; 2 L: 10-13 yds of rough, mapped 1-7).
   **Hole 2 right: unmapped fescue beyond the cart path from 39-48 R (250-320).**
3. **Hole 1: fescue is 3-6 yds closer than mapped on both sides at 260-350** (right: only 4-9 yds of rough at
   320-350). Hole 3 right: the "fescue strip" is a bare track; trees as mapped.
4. **Par 3s.** 7: the ground short of the green (105-157 yds, 8 L .. 15 R) is regrown thicket, not rough; right of
   the right-hand bunkers is mown (was fescue); the Middle marker belongs on the strip tee 7 yds right, 4 yds back
   (159 yds, not 155). 4: unmapped fescue mound back-right of the green.
5. Fairways (OSM) are right to +/-1-3 yds everywhere (exception: 8 left, 3-7 yds inside at 240-290); bunkers and
   greens are right to 1-3 yds; water edges to 1-2 yds; tees on or within 3 yds of a pad except hole 7. **Hole 9:
   both integrator edits confirmed.** Not settled: whether hole 8's unmown square is standing fescue (confidence 0.5).

Frame: x = yds right of the Back tee -> aim line of `render/frames.json`, along = yds from the Back tee. Par 3s
(4, 7): Back tee -> green centre. **Hole 2: `frames.json["2"]` still holds the old (wrong) tee; my hole-2 numbers use
the hand Back tee [-90.1434917, 38.663402] -> aim [-90.1454657, 38.6618048]; use `polygon_ll`.** Offsets are
detected - mapped.

## Evidence

| source | date | used for |
|---|---|---|
| NAIP 0.3 m RGBN (native resolution, Planetary Computer) | 2023-08-19 | mowing lines, sand, water, greens, tees, canopy |
| NAIP 0.6 m | 2016-06, 2018-10, 2019-09, 2020-07, 2021-06, 2022-06 | year-to-year agreement of every edge (co-registered: shifts <= 0.8 m) |
| USGS lidar, 0.5 m height above ground (F2's grids) | Dec 2023 (holes 1, 2, first 200 yds of 3), ~27 pts/m2 | standing grass (mown 0.02-0.03 m, native 0.13-0.22 m), trees |
| same | Dec 2020 (rest), ~8 pts/m2 | weak for grass (mown 0.004 m, native 0.01-0.05 m; swath stripes on 6, 7), fair for trees (misses thin crowns) |
| Sentinel-2 L2A NDVI, 10 m | 26 clear dates Oct 2025 - Nov 10 2026 | present / absent now, and the autumn TREND |
| 2014 lidar (`raw/hag.tif`) | 2014 | change only |

Newer lidar: the 2023 flight (IL_10CountyNRCS_D23) stops at UTM northing 4282838; south of it the newest is Dec 2020.
NAIP 2023 is the newest NAIP. NAIP 2023 sits within 0.5 m of the Dec 2023 lidar intensity image (phase correlation),
so it is the position reference; the OSM polygons are offset from it by 1-2 yds in places (see bunkers / greens).

## Method

1. Each hole's sources rectified into its frame at 3 px / yd (`naip_*`, lidar height, S2).
2. Per NAIP year, a gradient-boosted classifier (fairway / green / rough / native / trees / water / sand / bare) on
   bands, NDVI and 2- and 7-yd texture, trained on eroded interiors of the map over holes 1-9 (so a wrong edge does
   not teach it the wrong line). Its fairway edge sits ~1.5 yds inside the true one (texture windows), so:
3. **Fairway edge** per 5-yd station and year = half-height crossing of a raw-band LDA score (fairway vs rough)
   within 6 yds of the classifier edge; reported = median over the years, sd = 1.48 MAD (typically 0.2-0.8 yd).
4. **Native inner edge** per station = first sustained (>= 3 yds) standing height in the lidar outward from the
   fairway edge; cross-checked with the NAIP classifier ("not mown turf", 7-year consensus) and the S2 Nov 2026
   NDVI < 0.72 line. Where they disagreed the Sentinel-2 autumn series decided:
   **mown rough rises from ~0.6-0.75 in September to 0.80-0.87 in November; standing native falls steadily to
   0.42-0.62** (no native block on 1-9 shows the sudden drop a cut would give: all were standing on Nov 10).
5. **Trees** = lidar >= 2.5 m (closed 1.5 yds), accepted only where the NAIP 2023 canopy agrees.
6. **Sand** = 3-year classifier vote, outline refined at half height of (brightness - 60 NDVI) on NAIP 2023.
   **Greens** = half-height contour of a green-vs-surround LDA score. **Water** = NIR / NDWI in four years.
7. Every overlay looked at; rejected artefacts: cart paths and dried-out summer rough classified as "bare / native"
   by the photo classifier (holes 5, 6, 8, 9 right), lidar spikes at bunker faces, the 2020 lidar's missing thin
   crowns (hole 9 right: I first read the tree line as 3-9 yds further out; the 2023 canopy says the map is right).

Uncertainty of a detected line: fairway +/-1.5 yds; native +/-2 yds on holes 1-2 (2023 lidar), +/-4 yds on 3-9;
trees +/-3 yds; bunkers, greens +/-1.5 yds; S2-only lines (6 right) +/-6 yds.

## MUST APPLY (ranked by likely effect on club / aim)

| # | hole | feature | offset (detected - mapped) | conf. |
|---|---|---|---|---|
| 1 | 8 | right side inside the dogleg: two native bands are mown rough; unmown brush starts at 44 / 34 / 28 / 21 / 8 at 250 / 260 / 270 / 280 / 290 | native 19 / 13 / 18 / 26 / 16 yds further right | 0.85 (220-260), 0.7 (265-290) |
| 2 | 8 | trees inside the dogleg: canopy edge 31 / 27 / 17 / 11 / 7 / 2 / -4 / -13 at 270 / 280 / 290 / 300 / 310 / 320 / 330 / 340 | 10-40 yds closer than mapped from 265 on | 0.85 |
| 3 | 5 | right: band "between the rough and the cart path" is mown; fescue starts at 64 / 58 / 54 / 51 / 49 / 47 / 46 / 41 at 200 / 240 / 250 / 260 / 270 / 280 / 290 / 300 | 17-27 yds more rough | 0.8 |
| 4 | 2 | left beyond the pond: inner edge -35 / -31 / -27 / -26 / -26 / -27 at 290 ... 340 | 7 / 6 / 5 / 6 / 9 / 11 yds further left (mapped band touches the fairway at 330-345) | 0.9 |
| 5 | 2 | right: NEW fescue beyond the cart path from 40 / 39 / 41 / 44 / 48 at 250 / 270 / 290 / 300 / 320 | unmapped | 0.85 |
| 6 | 7 | par 3: thicket short of the green, 105-157 yds, 8 L .. 15 R (edge 3 yds short of the green front on the line) | unmapped (the 2014 tree zone beside it is the same regrowth now) | 0.7 |
| 7 | 7 | par 3: right of the bunkers (18-35 R, 150-188) is mown; fescue long from 196 | native edge 17 yds further right | 0.65 |
| 8 | 7 | Middle tee marker: on the strip tee at (8, 17) | 7 yds right, 3.6 yds back: 159.0 yds (mapped 155.2, card 160) | 0.75 |
| 9 | 6 | right: fescue from 52 / 57 / 60 / 64 / 66 / 66 / 64 / 58 at 240 ... 310 (between the two paths at 150-230: from 41-48) | 4-18 yds further right at 240-310 | 0.6 |
| 10 | 6 | left: the native band (x -48..-30, 255-345) is mown rough up to the tree row (-43 / -38 / -35 / -33 at 260 / 280 / 300 / 320) | 5-13 yds more rough at 260-300 | 0.75 |
| 11 | 1 | right fescue: 30 / 29 / 28 / 30 / 30 / 28 / 29 / 30 at 280 ... 350; 25 at 200-220 | 3-6 yds closer (integrator lead 5-8: confirmed, slightly less) | 0.85 |
| 12 | 1 | left prairie: -48 / -45 / -43 / -43 / -41 / -41 / -39 / -37 / -37 at 260 ... 340 | 3-6 yds closer; 5-7 yds further away at 150-230 | 0.85 |
| 13 | 4 | par 3: NEW fescue mound back-right of the green (x 7..29, 179-206) | unmapped | 0.75 |
| 14 | 3 | right: the "fescue strip" (x 20-32) is a bare track; brush / trees from 25-29 (230-270) and 31-36 (280-350) | 5-8 yds more playable ground at 240-290, 10-12 at 300-350 | 0.65 |

## MINOR

* 9 left native inner edge at 250-265: -27 / -30 / -30 / -24 (map -24 / -22 / -20 / -18): 3-10 yds further from play.
* 9: mapped bunker left at 198-206 yds (x -32..-27) does not exist (grass on NAIP 2021-2023): remove.
* 8: unmown square inside the bend is 6-9 yds larger on its east side (polygon in the json); state unresolved.
* 8: fairway left edge 3-7 yds inside the mapped line at 240-290 (rough strip polygon in the json).
* 5 left native inner edge: 4-5 yds closer than mapped at 180-220 (-26; mapped -30 ... -33), 3-6 further at 280-300.
* 6: stale 2014 tree blob at (x -45..-33, 258-278): no tree on NAIP 2022 / 2023.
* 4: unmown ridge short-left of the bunkers (132-160 yds, 19-46 L), confidence 0.6.
* 2: brush strip between the cart path and the trees right at 155-215 (36-50 R).
* 7: Forward marker 21 yds right / 5 back (on the strip, 145.4 yds); Back marker 4 yds back (179.8).
* 4, 7 (and all greens): mapped outline 1-2 yds inside the visible surface; polygons for 4 and 7 in the json.
* Bunkers: 1 (all four) mapped 2-4 yds long of the sand; 2, 3 mapped ~1.5 yds right; 7, 8, 9 mapped ~1.7 yds left.
  Detected outlines in `hazards[]`.
* 3 left: lidar puts the standing prairie at -50 ... -58 at 200-260 (mapped -44, the cart path edge): 5-10 yds more
  mown ground beyond the path; no effect.

## Bunker table (carry / reach in yds from the Back and Middle tee markers of package.json)

"reach" = nearest sand, "carry to clear" = farthest sand, measured from the tee marker to the detected outline.

| hole | bunker (side of the hole line, x range) | role | Back: reach / carry to clear | Middle: reach / carry to clear | detected along | mapped along | note |
|---|---|---|---|---|---|---|---|
| 1 | R 5..12 | tee shot | 236 / 243 | 214 / 221 | 235-243 | 236-245 |  |
| 1 | R 15..29 | tee shot | 237 / 256 | 215 / 234 | 236-254 | 238-256 | mapped polygon +2 yds along |
| 1 | L -9..-2 | greenside | 346 / 356 | 324 / 334 | 346-356 | 349-358 | mapped polygon +2 yds along |
| 1 | L -18..-11 | greenside | 357 / 368 | 335 / 346 | 357-368 | 360-370 | mapped polygon +4 yds along |
| 2 | R 27..36 | tee shot | 221 / 236 | 200 / 215 | 219-234 | 220-234 |  |
| 2 | R 18..26 | tee shot | 235 / 245 | 215 / 225 | 234-244 | 234-244 |  |
| 2 | R 27..33 | greenside | 392 / 400 | 372 / 379 | 391-399 | 392-399 |  |
| 2 | R 37..46 | greenside | 402 / 414 | 381 / 393 | 400-412 | 400-412 |  |
| 3 | R 14..28 | tee shot | 274 / 285 | 210 / 221 | 273-284 | 273-284 |  |
| 3 | L -13..-7 | second shot | 468 / 475 | 404 / 411 | 468-474 | 469-474 | mapped +2 yds across |
| 3 | L -8..7 | second shot | 474 / 485 | 410 / 421 | 474-485 | 476-484 | mapped polygon +2 yds along mapped +4 yds across |
| 3 | L 7..16 | second shot | 484 / 491 | 420 / 427 | 484-491 | 486-490 | mapped polygon +2 yds along mapped +3 yds across |
| 3 | R 45..53 | greenside | 594 / 600 | 530 / 537 | 592-598 | 592-598 |  |
| 3 | R 58..64 | greenside | 598 / 610 | 535 / 547 | 596-607 | 598-607 | mapped polygon +2 yds along mapped +2 yds across |
| 4 | L -7..0 | greenside | 137 / 150 | 111 / 124 | 137-150 | 138-149 |  |
| 4 | L -18..-7 | greenside | 150 / 171 | 125 / 146 | 150-170 | 150-170 |  |
| 5 | L -25..-7 | tee shot | 233 / 255 | 203 / 224 | 233-254 | 233-253 |  |
| 5 | R -2..10 | greenside | 423 / 443 | 392 / 411 | 423-442 | 422-442 |  |
| 6 | L -40..-13 | tee shot | 228 / 249 | 199 / 220 | 228-246 | 230-247 | mapped polygon +2 yds along |
| 6 | L -18..0 | second shot | 422 / 445 | 392 / 415 | 421-445 | 422-444 | mapped +3 yds across |
| 6 | R 5..14 | second shot | 477 / 495 | 447 / 464 | 477-494 | 477-495 |  |
| 6 | R 4..17 | greenside | 493 / 508 | 462 / 477 | 492-508 | 494-507 |  |
| 6 | R 1..10 | greenside | 517 / 529 | 487 / 499 | 517-529 | 518-529 |  |
| 6 | L -24..-17 | greenside | 539 / 548 | 509 / 518 | 538-548 | 539-547 | mapped +2 yds across |
| 7 | R 23..29 | greenside | 150 / 156 | 129 / 135 | 148-154 | 148-154 |  |
| 7 | R 17..23 | greenside | 170 / 180 | 149 / 159 | 168-179 | 170-178 |  |
| 8 | L -40..-28 | tee shot | 218 / 229 | 187 / 198 | 215-226 | 216-226 | mapped -2 yds across |
| 8 | R -6..5 | tee shot | 267 / 276 | 237 / 246 | 267-276 | 267-276 |  |
| 8 | C -101..-93 | greenside | 363 / 372 | 332 / 341 | 350-359 | 350-359 |  |
| 8 | R -94..-87 | greenside | 380 / 387 | 349 / 356 | 370-376 | 370-376 |  |
| 9 | L -46..-42 | tee shot | 174 / 179 | 143 / 148 | 169-174 | 169-174 | mapped -3 yds across |
| 9 | R 19..26 | tee shot | 234 / 242 | 204 / 213 | 233-241 | 233-241 |  |
| 9 | R 25..35 | tee shot | 239 / 249 | 211 / 221 | 238-247 | 239-247 | mapped -2 yds across |
| 9 | C 10..18 | greenside | 353 / 361 | 323 / 332 | 353-361 | 353-360 |  |

Not in the table (detector merged or missed them; mapped polygons are fine, +/-2 yds): hole 6's chain of four more
bunkers right of centre at 447-474 and 518-529 yds (second / third shot). Hole 7's large bunker 40-67 L (164-183) is
28 yds left of the green edge.

Hole 7 after the tee fix: Middle reach / carry of the right-hand bunkers becomes 152 / 162 (pin-high one) and
132 / 138 (short-right one).

## Per hole

### Hole 1 (par 4, 376)

Fairway (OSM) vs 7-year measurement:

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 150 | -34.7 | -33.4 | 1.3 | 0.6 (7) | 15.2 | 14.4 | -0.8 | 0.0 (7) |
| 160 | -37.7 | -35.9 | 1.8 | 0.4 (7) | 14.3 | 13.7 | -0.6 | 0.7 (5) |
| 170 | -41.5 | -40.1 | 1.4 | 0.4 (7) | 13.7 | 13.3 | -0.4 | 0.7 (6) |
| 180 | -45.3 | -43.5 | 1.8 | 0.4 (7) | 13.2 | 13.1 | -0.1 | 0.3 (7) |
| 190 | -47.9 | -46.5 | 1.5 | 0.4 (7) | 12.6 | 13.4 | 0.8 | 0.3 (7) |
| 200 | -49.6 | -48.2 | 1.4 | 0.5 (7) | 14.0 | 13.2 | -0.8 | 0.5 (6) |
| 210 | -48.6 | -46.2 | 2.4 | 0.2 (7) | 13.4 | 13.5 | 0.1 | 0.3 (7) |
| 220 | -45.1 | -42.9 | 2.2 | 0.2 (6) | 11.5 | 10.0 | -1.5 | 0.2 (6) |
| 230 | -42.9 | -41.4 | 1.6 | 0.2 (7) | 2.8 | 1.8 | -1.0 | 0.4 (7) |
| 240 | -42.1 | -39.6 | 2.6 | 0.3 (7) | 0.4 | -0.6 | -1.0 | 0.4 (7) |
| 250 | -39.3 | -36.9 | 2.3 | 0.4 (7) | 7.2 | 4.5 | -2.7 | 0.8 (6) |
| 260 | -35.9 | -33.7 | 2.2 | 0.2 (7) | 17.7 | 17.3 | -0.3 | 0.4 (6) |
| 270 | -34.5 | -32.6 | 1.8 | 0.4 (7) | 20.4 | 19.9 | -0.5 | 0.2 (7) |
| 280 | -32.2 | -30.3 | 1.8 | 0.4 (7) | 21.4 | 20.7 | -0.6 | 0.3 (7) |
| 290 | -28.2 | -26.2 | 2.0 | 0.3 (6) | 22.3 | 20.9 | -1.3 | 0.2 (7) |
| 300 | -29.4 | -28.0 | 1.4 | 0.5 (7) | 19.5 | 15.8 | -3.7 | 0.2 (7) |
| 310 | -29.8 | -29.1 | 0.7 | 0.2 (7) | 10.6 | 10.8 | 0.2 | 0.3 (7) |
| 320 | -28.8 | -27.5 | 1.3 | 0.2 (6) | 21.2 | 20.7 | -0.5 | 0.2 (7) |
| 330 | -28.3 | -27.0 | 1.4 | 0.1 (7) | 24.2 | 23.8 | -0.4 | 0.5 (7) |
| 340 | -27.1 | -27.8 | -0.7 | 0.2 (5) | 25.6 | 24.6 | -0.9 | 0.2 (7) |

Mapped fairway is 1.5-2.5 yds too wide on the left and within 1 yd on the right (exceptions: 3-4 yds at the notch
behind the 240 bunkers and at 300). No edit.

Left (2023 lidar):

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 140 | -31 | -43 | - | -43 | -39 | -44 | - |
| 150 | -33 | -44 | - | -49 | -44 | -48 | - |
| 160 | -36 | -47 | - | -53 | -47 | -51 | - |
| 170 | -40 | -49 | - | -57 | -50 | -53 | - |
| 180 | -44 | -51 | - | -59 | -53 | -67 | - |
| 190 | -46 | -54 | - | -61 | -55 | -67 | - |
| 200 | -48 | -56 | - | -62 | -57 | -66 | - |
| 210 | -46 | -55 | - | -61 | -55 | -64 | - |
| 220 | -43 | -54 | - | -61 | -51 | -60 | - |
| 230 | -41 | -53 | - | -57 | -50 | -56 | - |
| 240 | -40 | -53 | - | -53 | -47 | -53 | - |
| 250 | -37 | -52 | - | -51 | -44 | -49 | - |
| 260 | -34 | -51 | - | -48 | -42 | -47 | - |
| 270 | -33 | -50 | - | -45 | -40 | -44 | - |
| 280 | -30 | -49 | - | -44 | -38 | -41 | - |
| 290 | -26 | -47 | - | -43 | -37 | -39 | - |
| 300 | -28 | -46 | - | -41 | -36 | -37 | - |
| 310 | -29 | -45 | - | -41 | -37 | -35 | - |
| 320 | -28 | -43 | - | -39 | -38 | -33 | - |
| 330 | -27 | -42 | - | -37 | -37 | -33 | - |
| 340 | -28 | -41 | - | -37 | -36 | -38 | - |
| 350 | 4 | - | - | -35 | -29 | -37 | - |

Right (2023 lidar; 240-250 = bunker faces, ignore):

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 140 | 14 | 28 | - | 25 | 25 | 23 | - |
| 150 | 14 | 28 | - | 25 | 24 | 25 | - |
| 160 | 14 | 28 | - | 32 | 27 | 29 | - |
| 170 | 13 | 28 | - | 34 | 30 | 30 | - |
| 180 | 13 | 28 | - | 30 | 29 | 29 | - |
| 190 | 13 | 28 | - | 28 | 27 | 28 | - |
| 200 | 13 | 28 | - | 25 | 19 | 26 | - |
| 210 | 14 | 29 | - | 24 | 21 | 24 | - |
| 220 | 10 | 29 | - | 24 | 21 | 26 | - |
| 230 | 2 | 30 | - | 27 | 26 | 28 | - |
| 240 | -1 | 31 | - | 2 | 13 | 21 | - |
| 250 | 4 | 31 | - | 13 | 29 | 43 | - |
| 260 | 17 | 32 | - | 36 | 37 | 39 | - |
| 270 | 20 | 32 | - | 33 | 32 | 31 | - |
| 280 | 21 | 33 | - | 30 | 30 | 23 | - |
| 290 | 21 | 33 | - | 29 | 28 | 22 | - |
| 300 | 16 | 33 | - | 27 | 28 | 22 | - |
| 310 | 11 | 34 | - | 30 | 29 | 25 | 87 |
| 320 | 21 | 34 | - | 30 | 30 | 24 | - |
| 330 | 24 | 34 | - | 28 | 28 | 25 | - |
| 340 | 25 | 35 | - | 29 | 28 | 26 | - |
| 350 | 27 | - | - | 30 | 30 | 28 | - |

Verdict: both native edges re-traced from the Dec 2023 lidar (+/-2 yds). S2 2026: both blocks fall from 0.83-0.89
(June) to 0.48-0.55 (Nov 10): standing. Bunkers: mapped polygons 2-4 yds long of the sand (236-254 / 235-243 measured;
238-256 / 237-245 mapped). Tees: Back on its pad (x -8..5, -8..11); Middle at the back edge of its pad (15-33);
Champions / Tips pad (20..31, -29..-13): the Tips point is 3-4 yds behind it; Forward 2 yds off its pad (77-96).

### Hole 2 (par 4, 422) - own frame, see above

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 160 | -3.7 | -4.9 | -1.3 | 1.1 (7) | 18.5 | 17.3 | -1.2 | 0.4 (7) |
| 170 | -8.0 | -10.0 | -2.0 | 0.9 (7) | 19.2 | 18.3 | -0.9 | 0.5 (7) |
| 180 | -12.4 | -14.7 | -2.3 | 0.8 (7) | 19.9 | 18.9 | -1.0 | 0.8 (7) |
| 190 | -15.7 | -17.7 | -2.0 | 0.6 (7) | 21.3 | 20.1 | -1.2 | 0.8 (7) |
| 200 | -19.1 | -20.6 | -1.6 | 0.6 (7) | 22.3 | 21.7 | -0.6 | 0.5 (7) |
| 210 | -25.2 | -26.7 | -1.5 | 0.6 (6) | 23.7 | 22.4 | -1.3 | 0.8 (7) |
| 220 | -28.8 | -30.7 | -1.9 | 0.2 (3) | 24.5 | 23.8 | -0.7 | 0.5 (7) |
| 230 | -24.8 | -27.9 | -3.1 | 0.7 (4) | 23.0 | 21.3 | -1.7 | 0.6 (7) |
| 240 | -23.5 | -26.4 | -2.9 | 0.8 (5) | 16.5 | 14.3 | -2.2 | 0.5 (6) |
| 250 | -23.8 | -25.8 | -2.0 | 1.0 (7) | 13.5 | 11.6 | -1.8 | 2.0 (6) |
| 260 | -24.4 | -26.6 | -2.2 | 1.5 (7) | 21.8 | 20.4 | -1.5 | 1.0 (7) |
| 270 | -25.4 | -27.4 | -2.0 | 1.3 (6) | 27.2 | 26.8 | -0.3 | 0.3 (7) |
| 280 | -23.3 | -24.3 | -1.0 | 0.9 (7) | 28.9 | 28.1 | -0.7 | 0.7 (7) |
| 290 | -19.8 | -21.9 | -2.1 | 0.5 (7) | 29.7 | 29.2 | -0.5 | 0.3 (7) |
| 300 | -16.4 | -18.0 | -1.6 | 1.4 (7) | 29.7 | 29.2 | -0.4 | 0.5 (7) |
| 310 | -13.2 | -15.0 | -1.8 | 1.2 (7) | 31.4 | 31.0 | -0.4 | 0.7 (7) |
| 320 | -12.7 | -15.1 | -2.4 | 1.2 (7) | 35.3 | 34.9 | -0.3 | 0.9 (7) |
| 330 | -12.2 | -15.5 | -3.3 | 0.7 (7) | 39.2 | 39.1 | -0.1 | 0.5 (7) |
| 340 | -11.7 | -14.6 | -3.0 | 1.5 (7) | 43.3 | 42.3 | -1.0 | 0.4 (6) |

Fairway: mapped left edge 1.5-3 yds inside the measured one (fairway slightly wider left), right within 1.5.

Left:

| along | fairway edge | mapped native | mapped water | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 |
|---|---|---|---|---|---|---|
| 160 | -5 | - | -11 | -9 | -7 | -8 |
| 170 | -10 | - | -16 | - | -12 | -14 |
| 180 | -15 | - | -19 | -21 | -16 | -16 |
| 190 | -18 | - | -22 | -21 | -21 | -32 |
| 200 | -21 | - | -26 | -25 | -24 | -37 |
| 210 | -27 | - | -35 | -33 | -29 | -38 |
| 220 | -31 | - | -36 | -35 | -32 | -39 |
| 230 | -28 | - | -33 | -32 | -31 | -45 |
| 240 | -26 | - | -32 | -31 | -29 | -41 |
| 250 | -26 | - | -31 | -31 | -28 | -42 |
| 260 | -27 | - | -35 | -35 | -32 | -44 |
| 270 | -27 | -35 | -42 | -38 | -34 | -46 |
| 280 | -24 | -32 | - | - | -42 | -52 |
| 290 | -22 | -28 | - | -35 | -35 | -44 |
| 300 | -18 | -25 | - | -31 | -30 | -38 |
| 310 | -15 | -22 | - | -27 | -27 | -33 |
| 320 | -15 | -20 | - | -26 | -25 | -30 |
| 330 | -16 | -17 | - | -26 | -24 | -30 |
| 340 | -15 | -16 | - | -27 | -24 | -30 |
| 350 | -12 | -39 | - | -25 | -24 | -28 |

Right:

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 160 | 17 | - | 47 | 36 | 29 | 24 | 48 |
| 170 | 18 | - | 47 | 38 | 31 | 26 | 48 |
| 180 | 19 | - | 50 | 41 | 34 | 28 | 52 |
| 190 | 20 | - | 54 | 45 | 37 | 31 | 56 |
| 200 | 22 | - | 58 | 34 | 39 | 35 | 59 |
| 210 | 22 | - | 59 | 51 | 42 | 38 | 60 |
| 220 | 24 | - | 61 | 36 | 28 | 41 | 62 |
| 230 | 21 | - | 58 | 32 | 37 | 34 | 59 |
| 240 | 14 | - | 58 | 24 | 27 | 23 | 58 |
| 250 | 12 | - | 54 | 40 | 21 | 26 | 55 |
| 260 | 20 | - | 51 | 39 | 31 | 26 | 55 |
| 270 | 27 | - | 88 | 39 | 31 | 28 | 87 |
| 280 | 28 | - | 67 | 39 | 33 | 29 | 93 |
| 290 | 29 | - | 69 | 41 | 35 | 32 | 74 |
| 300 | 29 | - | 72 | 44 | 39 | 36 | 77 |
| 310 | 31 | - | 74 | 46 | 40 | 38 | 79 |
| 320 | 35 | - | 77 | 48 | 44 | 40 | 81 |
| 330 | 39 | - | - | 52 | 45 | 43 | - |
| 340 | 42 | - | - | 55 | 49 | 48 | - |
| 350 | 44 | - | - | 57 | 51 | 53 | - |

* Pond: mapped edge = NIR water edge in 2020-2022 within 1 yd at every station 100-270; in Aug 2023 the water was
  2-5 yds lower. Bank vegetation starts 0-3 yds in front of the water. Fine.
* Left beyond the pond (290-345): fescue block (lidar 0.22 m, S2 0.56 and falling) starts 10-13 yds left of the
  fairway; the mapped band (drawn in the old frame) reaches the fairway edge. Must apply.
* Right: fescue beyond the cart path at 250-350, S2 NDVI 0.42 on Nov 10. Must apply. Trees right: mapped within
  2 yds of the 2023 lidar at 160-260.
* Tees (true Back pad): Back on its pad (x -12..6, -8..8); Middle on its pad (-2..10, 18-38); Forward on the front
  edge of its pad (17..26, 90-105); Champions / Tips at the back edge of theirs (-36..-27, -45..-30).

### Hole 3 (par 5, 630)

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 200 | -22.0 | -22.3 | -0.3 | 1.0 (6) | -0.2 | -5.0 | -4.8 | 1.7 (7) |
| 210 | -26.9 | -27.7 | -0.8 | 0.6 (7) | 6.9 | 5.4 | -1.5 | 1.0 (7) |
| 220 | -27.9 | -29.4 | -1.5 | 0.5 (7) | 9.2 | 8.8 | -0.4 | 0.5 (7) |
| 230 | -28.3 | -30.2 | -1.9 | 0.9 (7) | 12.8 | 12.1 | -0.8 | 0.6 (7) |
| 240 | -28.0 | -30.8 | -2.8 | 0.7 (7) | 13.7 | 13.0 | -0.7 | 0.5 (7) |
| 250 | -28.7 | -30.1 | -1.4 | 0.2 (7) | 14.0 | 13.1 | -1.0 | 0.1 (7) |
| 260 | -28.3 | -29.0 | -0.6 | 0.5 (7) | 14.0 | 13.0 | -1.0 | 0.3 (7) |
| 270 | -27.2 | -28.1 | -0.8 | 0.3 (7) | 12.1 | 10.0 | -2.1 | 0.6 (6) |
| 280 | -25.2 | -28.1 | -2.9 | 0.3 (7) | 10.7 | 9.6 | -1.1 | 0.2 (7) |
| 290 | -23.4 | -25.8 | -2.4 | 0.5 (7) | 16.5 | 14.8 | -1.7 | 0.6 (6) |
| 300 | -22.5 | -24.3 | -1.8 | 0.4 (7) | 22.3 | 21.1 | -1.1 | 0.2 (7) |
| 310 | -22.7 | -23.5 | -0.8 | 0.3 (7) | 23.4 | 22.2 | -1.3 | 0.6 (7) |
| 320 | -22.3 | -23.4 | -1.1 | 0.4 (7) | 22.8 | 21.9 | -0.9 | 0.5 (7) |
| 330 | -21.4 | -23.1 | -1.7 | 0.3 (7) | 21.6 | 21.1 | -0.6 | 0.7 (7) |
| 340 | -21.5 | -23.2 | -1.7 | 0.7 (7) | 21.7 | 20.5 | -1.2 | 0.5 (7) |

Fairway: mapped within 1-3 yds both sides (left edge 1-3 yds inside the measured one).

Right:

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 200 | -5 | 20 | 24 | 19 | 10 | 26 | 25 |
| 210 | 5 | 20 | 26 | 21 | 16 | 13 | 26 |
| 220 | 9 | 20 | 32 | 22 | 17 | 14 | - |
| 230 | 12 | 20 | 30 | 25 | 20 | 18 | 32 |
| 240 | 13 | 20 | 30 | 28 | 20 | 34 | 32 |
| 250 | 13 | 20 | 32 | 29 | 18 | 23 | 34 |
| 260 | 13 | 21 | 32 | 28 | 23 | 20 | 36 |
| 270 | 10 | 21 | 32 | 29 | 11 | 17 | 40 |
| 280 | 10 | 21 | 32 | 31 | 12 | 14 | 44 |
| 290 | 15 | 21 | 32 | 32 | 19 | 16 | 37 |
| 300 | 21 | 22 | 32 | 33 | 24 | 25 | - |
| 310 | 22 | 23 | 32 | 34 | 28 | 27 | - |
| 320 | 22 | 23 | 32 | 34 | 29 | 29 | 47 |
| 330 | 21 | 22 | 32 | 33 | 27 | 30 | 47 |
| 340 | 21 | 22 | 32 | 36 | 28 | 31 | 47 |
| 350 | 22 | - | 42 | 35 | 30 | 33 | 44 |

The mapped fescue strip (20-32) is a bare / worn track along the tree line on NAIP 2023 and 2022; standing
vegetation (lidar) starts at 25-29 (230-270) and 31-36 (280-350) = the brush and trees. S2 cannot resolve a 9-yd
strip next to an industrial yard (0.68-0.72, flat). Confidence 0.65. Trees and OB as mapped (+/-3).
Left: prairie beyond the cart path as mapped (+/-5; lidar -50..-58 at 200-260, -40..-48 at 270-350).
Tees: Back on its pad (x -7..4, -7..10); Middle on the long pad (49-87); Forward and Champions / Tips on faint pads.

### Hole 4 (par 3, 180)

* Green: mapped x -19..17, 161-190; visible surface -19.5..17, 160.5-190.5 (IoU 0.88). The lobe left of it
  (x -34..-18, 163-188) is fairway-height apron, as mapped.
* Bunkers: front-left -17.5..-6.6 at 150-171 and -7.2..0.4 at 137-150 (mapped within 1-1.5 yds).
* **New: fescue mound back-right** (x 7..29, 179-206): NAIP texture 7.9, S2 Nov 0.59 / 0.55 / 0.66 (2026 / 25 / 24),
  falling since September. Begins 3 yds from the green's back-right edge.
* Short-left ridge (132-160, 19-46 L): unmown, confidence 0.6. Left beyond 45 L: unmown (25+ yds from the green).
* Right: mown rough to the cart path (27-36 R), trees beyond it, as mapped. Tees: all four markers on pads.

### Hole 5 (par 4, 452)

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 180 | 2.5 | 4.7 | 2.2 | 1.4 (7) | 34.7 | 33.8 | -0.9 | 0.4 (7) |
| 190 | -2.7 | -3.1 | -0.4 | 0.6 (6) | 37.0 | 36.1 | -1.0 | 0.1 (7) |
| 200 | -5.8 | -6.5 | -0.8 | 0.4 (6) | 38.0 | 36.6 | -1.4 | 0.2 (7) |
| 210 | -7.3 | -7.2 | 0.0 | 0.4 (7) | 37.8 | 37.7 | -0.1 | 0.4 (7) |
| 220 | -2.5 | -3.0 | -0.5 | 0.3 (7) | 37.7 | 37.6 | -0.1 | 0.4 (6) |
| 230 | -4.8 | -1.4 | 3.4 | 0.1 (6) | 36.4 | 36.3 | -0.1 | 0.3 (6) |
| 240 | -3.7 | -1.6 | 2.1 | 0.1 (7) | 34.2 | 34.0 | -0.2 | 0.4 (7) |
| 250 | -5.5 | -5.0 | 0.5 | 1.0 (6) | 30.7 | 32.0 | 1.3 | 0.1 (6) |
| 260 | -18.8 | -15.2 | 3.7 | 0.5 (6) | 28.9 | 29.5 | 0.6 | 0.1 (7) |
| 270 | -24.8 | -23.9 | 0.9 | 0.4 (5) | 26.1 | 27.3 | 1.3 | 0.3 (6) |
| 280 | -25.1 | -24.9 | 0.2 | 0.6 (6) | 22.4 | 24.1 | 1.7 | 0.5 (7) |
| 290 | -22.7 | -23.0 | -0.3 | 0.8 (7) | 19.4 | 20.4 | 1.0 | 0.5 (5) |
| 300 | -20.5 | -21.4 | -0.9 | 0.3 (7) | 17.6 | 18.5 | 0.9 | 0.3 (6) |
| 310 | -20.7 | -21.3 | -0.6 | 0.3 (6) | 17.0 | 18.1 | 1.1 | 0.1 (7) |
| 320 | -21.1 | -21.2 | -0.1 | 0.7 (6) | 16.7 | 16.9 | 0.2 | 0.7 (7) |
| 330 | -20.3 | -19.1 | 1.2 | 0.4 (7) | 15.9 | 17.5 | 1.7 | 0.9 (6) |
| 340 | -17.9 | -17.0 | 1.0 | 0.8 (6) | 16.3 | 18.2 | 2.0 | 0.2 (5) |

Fairway within 1-2 yds (left edge 2-4 yds inside the mapped line at 230-260 by the bunker).

Right:

| along | fairway edge | mapped native | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 |
|---|---|---|---|---|---|
| 180 | 34 | 35 | 65 | 36 | 56 |
| 190 | 36 | 37 | 74 | 51 | 61 |
| 200 | 37 | 38 | - | 38 | 62 |
| 210 | 38 | 39 | 65 | 40 | 63 |
| 220 | 38 | 39 | 62 | 48 | 62 |
| 230 | 36 | 37 | 63 | 47 | 60 |
| 240 | 34 | 35 | 58 | 45 | 57 |
| 250 | 32 | 33 | 53 | 46 | 55 |
| 260 | 30 | 33 | 51 | 43 | 53 |
| 270 | 27 | 33 | 49 | 41 | 52 |
| 280 | 24 | 33 | 47 | 39 | 50 |
| 290 | 20 | 33 | 46 | 36 | 49 |
| 300 | 19 | 34 | 39 | 33 | 44 |
| 310 | 18 | 34 | 41 | 31 | 34 |
| 320 | 17 | 34 | 37 | 30 | 34 |
| 330 | 18 | 34 | 36 | 30 | 33 |
| 340 | 18 | 34 | 43 | 30 | 36 |
| 350 | 18 | - | 37 | 31 | 38 |

Left:

| along | fairway edge | mapped native | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 |
|---|---|---|---|---|---|
| 180 | 5 | -30 | -25 | -18 | -17 |
| 190 | -3 | -30 | -26 | -19 | -18 |
| 200 | -7 | -30 | -27 | -21 | -19 |
| 210 | -7 | -32 | -26 | -22 | -19 |
| 220 | -3 | -33 | -30 | -25 | -20 |
| 230 | -1 | -35 | -6 | -3 | -16 |
| 240 | -2 | -36 | -36 | -4 | -6 |
| 250 | -5 | -38 | -11 | -11 | -20 |
| 260 | -15 | -38 | -37 | -32 | -30 |
| 270 | -24 | -39 | -37 | -35 | -31 |
| 280 | -25 | -39 | -45 | -38 | -35 |
| 290 | -23 | -40 | -53 | -42 | -38 |
| 300 | -21 | -40 | -53 | -36 | -36 |
| 310 | -21 | -40 | -43 | -32 | -31 |
| 320 | -21 | -40 | -43 | -33 | -36 |
| 330 | -19 | -40 | -41 | -36 | -39 |
| 340 | -17 | -40 | -41 | -36 | -38 |
| 350 | -16 | - | -41 | -36 | -37 |

Right: the mapped band at 32-45 is mown (S2: 0.70 in Sept rising to 0.87 on Nov 8-10; lidar flat); the real fescue
is the strip between the two cart paths (S2 0.56, falling). Left: the strip between 5 and 6 is standing (0.62).
Tees: Back, Middle, Champions on pads; Tips 1 yd behind its pad; Forward on its pad.

### Hole 6 (par 5, 530)

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 160 | -14.1 | -16.3 | -2.2 | 0.6 (7) | 22.5 | 21.3 | -1.2 | 0.3 (7) |
| 170 | -14.3 | -15.6 | -1.3 | 0.5 (7) | 24.2 | 23.5 | -0.6 | 0.3 (7) |
| 180 | -13.3 | -16.0 | -2.6 | 1.0 (7) | 25.7 | 24.7 | -0.9 | 0.4 (7) |
| 190 | -12.2 | -15.3 | -3.2 | 0.3 (7) | 26.0 | 24.2 | -1.8 | 0.5 (7) |
| 200 | -11.9 | -14.9 | -3.0 | 0.8 (7) | 24.0 | 23.5 | -0.5 | 0.4 (7) |
| 210 | -12.1 | -14.0 | -1.9 | 0.4 (7) | 24.5 | 24.1 | -0.4 | 0.3 (7) |
| 220 | -10.9 | -13.5 | -2.6 | 0.4 (7) | 27.0 | 25.5 | -1.5 | 0.4 (7) |
| 230 | -8.1 | -9.2 | -1.2 | 0.5 (6) | 30.2 | 28.8 | -1.5 | 0.6 (7) |
| 240 | -9.5 | -9.2 | 0.3 | 1.4 (7) | 32.0 | 30.9 | -1.1 | 0.6 (7) |
| 250 | -21.3 | -22.6 | -1.3 | 0.5 (7) | 33.0 | 31.6 | -1.3 | 0.5 (6) |
| 260 | -23.3 | -23.3 | 0.0 | 0.7 (7) | 32.6 | 31.0 | -1.6 | 0.6 (7) |
| 270 | -21.5 | -22.9 | -1.4 | 0.2 (7) | 30.4 | 29.6 | -0.8 | 0.4 (7) |
| 280 | -22.1 | -22.6 | -0.6 | 1.3 (7) | 28.8 | 28.6 | -0.2 | 0.6 (7) |
| 290 | -22.2 | -23.6 | -1.4 | 0.8 (7) | 29.3 | 28.2 | -1.1 | 0.6 (7) |
| 300 | -21.6 | -21.4 | 0.2 | 0.8 (7) | 28.9 | 28.6 | -0.3 | 0.8 (7) |
| 310 | -18.9 | -19.9 | -1.0 | 0.7 (7) | 27.9 | 26.4 | -1.5 | 0.6 (7) |
| 320 | -16.3 | -16.2 | 0.1 | 0.3 (6) | 21.5 | 21.0 | -0.5 | 0.4 (7) |
| 330 | -12.3 | -12.5 | -0.1 | 0.5 (7) | 14.8 | 12.8 | -2.0 | 0.8 (5) |

Fairway: left edge 1-3 yds outside the mapped line at 160-220, right within 1.5.

Left:

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 250 | -23 | - | -52 | -53 | -25 | -31 | -55 |
| 260 | -23 | -30 | -35 | -43 | -26 | -41 | -53 |
| 270 | -23 | -30 | -33 | -39 | -30 | -40 | -51 |
| 280 | -23 | -30 | -42 | -38 | -34 | -38 | -48 |
| 290 | -24 | -30 | -36 | -36 | -28 | -36 | -44 |
| 300 | -21 | -30 | -32 | -35 | -28 | -35 | -41 |
| 310 | -20 | -30 | -32 | -36 | -23 | -32 | -39 |
| 320 | -16 | -30 | -32 | -33 | -20 | -32 | -35 |
| 330 | -12 | -30 | -28 | -30 | -18 | -25 | -31 |

Right (lidar unusable; "S2" = NDVI < 0.72 edge, contaminated by the cart path at 150-230):

| along | fairway edge | mapped native | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 |
|---|---|---|---|---|
| 150 | 12 | 48 | 22 | 28 |
| 160 | 21 | 48 | 28 | 30 |
| 170 | 24 | 48 | 28 | 31 |
| 180 | 25 | 48 | 29 | 32 |
| 190 | 24 | 48 | 31 | 33 |
| 200 | 23 | 48 | 34 | 34 |
| 210 | 24 | 48 | 36 | 35 |
| 220 | 25 | 48 | 40 | 38 |
| 230 | 29 | 48 | 43 | 43 |
| 240 | 31 | 48 | 47 | 47 |
| 250 | 32 | 48 | 49 | 50 |
| 260 | 31 | 48 | 49 | 57 |
| 270 | 30 | 48 | 54 | 60 |
| 280 | 29 | 48 | 42 | 71 |
| 290 | 28 | 48 | 43 | 68 |
| 300 | 29 | 48 | 43 | 66 |
| 310 | 26 | 48 | 39 | 58 |
| 320 | 21 | 48 | 32 | 53 |
| 330 | 13 | 48 | 24 | 50 |

* Right: rough between the fairway and the path at 250-300 (x 36-50): S2 0.57 (Sept) -> 0.83 (Nov) = mown. Beyond
  the path: 0.67 -> 0.59 = standing. Between the two paths at 160-225: 0.64 -> 0.56 = standing.
* Left: mapped native rectangle: 0.66 -> 0.81 = mown. The tree row behind it is right in the map (photo canopy edge
  -43 / -35 / -30 at 280 / 300 / 320) except the stale blob at 258-278.

### Hole 7 (par 3, 180)

* Tee: one strip tee for Back / Middle / Forward, corners (-7,-15), (3,-17), (23,40), (11,42); divot clusters at
  (1..5, -5..0), (4..12, 10..22), (10..14, 25..32). Mapped Middle (0.9, 20.6) is 3 yds left of the strip and
  measures 155.2 yds; on the strip at card distance it is (8, 17) = 159.0. Mapped Forward (-8, 36) is in the long
  grass 20 yds left of the strip. Champions / Tips on their own round pads (195.6 / 198.6 yds; card 200 / 204).
* Green: mapped x -12..10.6, 160-191; visible surface -12..12.5, 159.5-192.
* Bunkers right: 16.8..22.7 at 168-179 (mapped 15.2..21.1) and 23.2..28.7 at 148-154 (mapped 21.7..27.0): the
  mapped polygons are 1.6 yds left.
* **Short of the green**: 2018-19 tall growth; 2020-21 cut to stubble; 2022-23 regrown; S2 2026 0.82 -> 0.69 and
  falling: standing thicket from ~105 to 157 yds, 8 L .. 15 R, and it continues left into the mapped (2014) tree
  zone, where only one tree is left (-28, 128). The fairway approach is right of it (18-38 R, 110-150).
* **Right of the bunkers** (24-33 R): S2 0.65 -> 0.82 = mown; the mapped native polygon starts at 18 R. Native from
  ~35-38 R. **Long**: mown to 192-196, standing growth and trees from 196 (S2 0.78 -> 0.67).

### Hole 8 (par 4, 408)

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 190 | -22.5 | -21.0 | 1.5 | 2.1 (7) | 23.5 | 20.3 | -3.2 | 1.9 (6) |
| 200 | -28.7 | -26.2 | 2.5 | 0.8 (6) | 26.6 | 27.4 | 0.8 | 0.2 (7) |
| 210 | -32.4 | -29.1 | 3.2 | 1.3 (5) | 26.8 | 27.6 | 0.8 | 0.5 (6) |
| 220 | -28.2 | -26.9 | 1.2 | 1.1 (3) | 25.7 | 26.8 | 1.1 | 0.4 (7) |
| 230 | -27.8 | -25.8 | 2.1 | 1.6 (7) | 23.8 | 24.0 | 0.2 | 0.3 (6) |
| 240 | -37.3 | -34.8 | 2.6 | 0.5 (7) | 18.5 | 18.8 | 0.3 | 0.2 (7) |
| 250 | -44.8 | -40.1 | 4.8 | 0.6 (7) | 15.3 | 15.4 | 0.1 | 0.2 (7) |
| 260 | -57.5 | -50.0 | 7.5 | 3.4 (7) | 5.8 | 2.3 | -3.5 | 1.8 (6) |
| 270 | -71.2 | -67.6 | 3.6 | 0.7 (6) | -11.6 | -11.2 | 0.4 | 0.6 (7) |
| 280 | -84.2 | -81.9 | 2.2 | 2.6 (7) | -13.5 | -11.7 | 1.8 | 0.6 (7) |
| 290 | -62.5 | -56.3 | 6.2 | 0.7 (6) | -19.5 | -18.4 | 1.1 | 0.4 (7) |
| 300 | -50.2 | -48.9 | 1.2 | 0.3 (7) | -26.7 | -25.1 | 1.6 | 1.3 (6) |

Right side:

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 200 | 27 | - | 30 | 37 | 34 | 73 | 48 |
| 205 | 28 | - | 49 | 42 | 42 | 70 | 52 |
| 210 | 28 | - | 49 | 46 | 41 | 71 | 55 |
| 215 | 27 | - | 50 | 46 | 33 | 79 | 54 |
| 220 | 27 | 28 | 50 | 49 | 34 | 80 | 54 |
| 225 | 25 | 27 | 50 | 44 | 33 | 78 | 53 |
| 230 | 24 | 25 | 51 | 49 | 31 | 78 | 55 |
| 235 | 21 | 25 | 52 | 46 | 23 | 83 | 53 |
| 240 | 19 | 25 | 54 | 49 | 21 | 85 | 53 |
| 245 | 17 | 25 | 56 | 48 | 22 | 85 | 52 |
| 250 | 15 | 25 | 56 | 44 | 22 | 44 | 49 |
| 255 | 10 | 24 | 50 | 41 | 16 | 39 | 48 |
| 260 | 2 | 21 | 48 | 33 | 5 | 36 | 51 |
| 265 | -9 | 16 | 54 | 34 | -7 | 33 | 63 |
| 270 | -11 | 10 | 53 | 28 | -9 | 29 | 39 |
| 275 | -11 | 3 | 52 | 29 | -9 | 24 | 39 |
| 280 | -12 | -5 | 50 | 20 | -10 | 14 | 42 |
| 285 | -15 | -6 | 19 | 24 | -9 | 7 | 43 |
| 290 | -18 | -8 | 17 | 9 | -15 | 2 | 21 |
| 295 | -21 | -10 | 16 | -6 | -17 | -3 | 19 |
| 300 | -25 | -12 | 20 | -7 | -20 | -7 | 14 |

See the must-apply list. S2 series for the band x 28..44, 222-255: 0.72 (Sept) -> 0.85 (Nov 10), like hole 9's right
rough (0.67 -> 0.87) and unlike native (-> 0.42-0.62). Trees: the Dec 2020 lidar outline and the 2023 canopy agree
within 2-3 yds along the whole inside of the dogleg; the mapped zone has only the main edge at 47-65 and one blob.
Square inside the bend: S2 0.75-0.82 all autumn (neither rising like rough nor falling like fescue), lidar mostly
short, photo 2023 clearly unmown: thick green grass, probably not dormant fescue. Confidence 0.5 either way.

### Hole 9 (par 4, 390)

| along | mapped L | measured L | dL | sd L (n yrs) | mapped R | measured R | dR | sd R (n yrs) |
|---|---|---|---|---|---|---|---|---|
| 140 | -26.4 | -26.2 | 0.3 | 0.7 (7) | 16.5 | 16.0 | -0.5 | 1.4 (7) |
| 150 | -27.2 | -27.1 | 0.1 | 1.0 (6) | 20.5 | 19.9 | -0.6 | 0.3 (7) |
| 160 | -31.3 | -30.4 | 0.9 | 1.0 (5) | 23.0 | 23.0 | 0.0 | 0.8 (7) |
| 170 | -31.1 | -30.0 | 1.2 | 0.7 (7) | 24.8 | 25.1 | 0.2 | 1.0 (7) |
| 180 | -28.8 | -26.7 | 2.1 | 0.1 (7) | 26.6 | 25.9 | -0.7 | 0.1 (7) |
| 190 | -25.5 | -25.0 | 0.5 | 0.3 (7) | 27.7 | 27.7 | -0.1 | 0.3 (7) |
| 200 | -22.7 | -21.7 | 1.0 | 0.2 (7) | 29.4 | 28.5 | -0.9 | 0.3 (7) |
| 210 | -18.6 | -17.6 | 1.0 | 0.4 (7) | 30.0 | 29.4 | -0.6 | 0.4 (7) |
| 220 | -16.1 | -15.3 | 0.7 | 0.6 (7) | 26.2 | 26.0 | -0.2 | 0.9 (6) |
| 230 | -16.7 | -16.0 | 0.7 | 0.4 (7) | 15.8 | 14.6 | -1.2 | 0.4 (6) |
| 240 | -19.2 | -19.0 | 0.2 | 0.4 (7) | 9.6 | 10.9 | 1.3 | 0.1 (7) |
| 250 | -20.2 | -19.3 | 0.9 | 0.3 (6) | 13.7 | 15.1 | 1.5 | 0.7 (6) |
| 260 | -15.8 | -14.5 | 1.4 | 0.5 (7) | 22.5 | 24.0 | 1.5 | 0.4 (6) |
| 270 | -11.4 | -10.2 | 1.2 | 0.4 (7) | 26.2 | 27.7 | 1.5 | 0.3 (6) |
| 280 | -9.6 | -8.6 | 1.1 | 0.4 (7) | 28.1 | 29.2 | 1.1 | 0.5 (7) |
| 290 | -7.2 | -6.8 | 0.4 | 0.4 (7) | 28.1 | 28.8 | 0.7 | 0.9 (4) |
| 300 | -6.1 | -5.5 | 0.6 | 0.6 (7) | 17.2 | 18.4 | 1.2 | 1.2 (7) |

Fairway accurate (+/-1.5).

Left:

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 240 | -19 | -33 | - | -34 | -31 | -28 | - |
| 245 | -20 | -33 | - | -36 | -33 | -29 | - |
| 250 | -19 | -24 | - | -35 | -27 | -29 | - |
| 255 | -17 | -22 | - | -36 | -34 | -28 | - |
| 260 | -14 | -20 | - | -34 | -33 | -25 | - |
| 265 | -12 | -18 | - | -29 | -29 | -19 | - |
| 270 | -10 | -18 | - | -20 | -15 | -13 | - |
| 275 | -10 | -18 | - | -16 | -16 | -11 | - |
| 280 | -9 | -18 | - | -19 | -12 | -10 | - |
| 285 | -7 | -19 | - | -18 | -12 | -9 | - |
| 290 | -7 | -20 | - | -19 | -18 | -10 | - |
| 295 | -6 | -21 | - | -21 | -20 | -11 | - |
| 300 | -5 | -22 | - | -23 | -20 | -13 | - |
| 305 | -4 | -23 | - | -27 | -20 | -14 | - |
| 320 | 17 | -27 | - | -32 | -12 | -19 | - |
| 325 | 13 | -27 | - | -35 | -13 | -21 | - |
| 330 | 7 | -28 | - | -31 | -20 | -21 | - |
| 335 | 7 | -28 | - | -32 | -20 | -22 | - |
| 340 | 9 | - | - | -31 | 8 | -22 | - |
| 345 | 16 | - | - | -27 | 10 | -20 | - |

Right:

| along | fairway edge | mapped native | mapped trees | lidar unmown | NAIP 7-yr unmown | S2 Nov-26 NDVI<0.72 | lidar trees (new) |
|---|---|---|---|---|---|---|---|
| 180 | 26 | - | 37 | 51 | 35 | 66 | 55 |
| 185 | 27 | - | 42 | 47 | 35 | 69 | 49 |
| 190 | 28 | - | 43 | 47 | 34 | 70 | 50 |
| 195 | 28 | - | 40 | 44 | 35 | 70 | 46 |
| 200 | 29 | - | 39 | 43 | 36 | 71 | 44 |
| 205 | 29 | - | 41 | 48 | 36 | 71 | 49 |
| 210 | 29 | - | 40 | 44 | 38 | 72 | 46 |
| 215 | 28 | - | 40 | 45 | 39 | 70 | 47 |
| 220 | 26 | - | 43 | 49 | 31 | 66 | 52 |
| 225 | 21 | - | 44 | 49 | 41 | 62 | 52 |
| 230 | 15 | - | 44 | 48 | 23 | 60 | 49 |
| 235 | 11 | - | 44 | 48 | 26 | 62 | 49 |
| 240 | 11 | - | 46 | 49 | 16 | 64 | 51 |
| 245 | 12 | - | 45 | 51 | 34 | 64 | 53 |
| 250 | 15 | - | 48 | 51 | 29 | 63 | 55 |
| 255 | 18 | - | 49 | 53 | 31 | 62 | 56 |
| 260 | 24 | - | 48 | 52 | 33 | 62 | 56 |
| 265 | 27 | - | 47 | 52 | 36 | 64 | 53 |
| 270 | 28 | - | 51 | 54 | 38 | 65 | 57 |
| 275 | 29 | - | 51 | 54 | 41 | 65 | 57 |
| 280 | 29 | - | 51 | 55 | 44 | 63 | 56 |
| 285 | 30 | - | 53 | 54 | 42 | 63 | 58 |
| 290 | 29 | - | 53 | 56 | 41 | 63 | 57 |
| 295 | 23 | - | 51 | 55 | 45 | 63 | 58 |
| 300 | 18 | - | 49 | 52 | 41 | 61 | 58 |
| 305 | 12 | - | 47 | 52 | 41 | 59 | 53 |
| 320 | 29 | - | 51 | 53 | 36 | 57 | 54 |
| 325 | 33 | - | 53 | 53 | 36 | 58 | 55 |
| 330 | 36 | - | 55 | 56 | 39 | 60 | - |
| 335 | 39 | - | 54 | 58 | 42 | 61 | 63 |
| 340 | 40 | - | 55 | 57 | 44 | 62 | 59 |
| 345 | 41 | - | 55 | 58 | 45 | 64 | 62 |

* Left inner edge: integrator's Nov 13 line confirmed within 1-4 yds at 270-340; 3-10 yds too close at 250-265.
  Block S2 0.75 -> 0.54: standing.
* Right: no standing grass between the fairway and the trees (lidar first height = the tree line; S2 0.67 -> 0.87).
  Removal of the right fescue band confirmed (0.9). "NAIP unmown" at 23-45 = dried summer rough + cart path.
* Trees right: the mapped zone matches the 2023 canopy edge within 1-2 yds at 180-300 (40-41 at 200, 43 at 220,
  50 at 240-260, 52 at 290). The Dec 2020 lidar (>= 2.5 m) reads 3-9 yds further out because it misses thin
  crowns; **no change** (this corrects item 5 of my checkpoint 1).
* Tees: Back, Middle, Forward, Champions on pads; Tips 1 yd behind the Champions pad.

## Greens (all nine)

| hole | mapped x / along | detected x / along | IoU | mean radial diff (3-yr median) |
|---|---|---|---|---|
| 1 | -7..20 / 355-389 | -6..20 / 351-388 | 0.84 | +0.6 |
| 2 | 9..33 / 400-433 | 8..32 / 397-434 | 0.80 | +2.2 |
| 3 | 39..68 / 611-639 | 36..67 / 609-640 | 0.80 | +1.9 |
| 4 | -19..17 / 161-190 | -22..16 / 161-191 | 0.88 | +0.9 |
| 5 | -23..1 / 436-469 | -23..2 / 435-472 | 0.87 | +2.2 |
| 6 | -20..6 / 513-548 | -22..5 / 504-550 | 0.76 | +1.8 |
| 7 | -12..11 / 160-191 | -12..15 / 160-194 | 0.82 | +2.2 |
| 8 | -124..-101 / 352-387 | -123..-99 / 350-389 | 0.80 | +1.6 |
| 9 | 7..38 / 372-404 | 8..42 / 371-408 | 0.81 | +1.3 |

Detected outlines include 1-3 yds of close-cut collar in places (1 front, 6 front); read the table as "mapped
outline is 1-2 yds inside the visible surface", not as an edit list.

## Not resolved

* Hole 8 unmown square: standing fescue or thick green grass (above).
* Hole 3 right strip: bare track vs thin fescue (too narrow for S2; lidar 2020 flat).
* Native edges on 3-9 rest on the weak Dec 2020 lidar plus S2 at 10 m: +/-4 yds (6 right +/-6).
* Collar widths: not measurable at 0.3 m with confidence (collar ring ~1-2 yds).
* Tree lines beyond 350 yds and second-shot corridors of 3 and 6: not reviewed beyond the bunker table.
* Whether any native is cut between Nov 10 and the tournament: none was cut by Nov 10 (S2), in 2025 none by Nov 15.

## Methods: what worked, what did not

* Worked: 2023 lidar height for native (holes 1-2); the S2 autumn NDVI trend (rising = mown, falling = standing)
  as the tie-breaker everywhere else; raw-band half-height edges for fairways (sd 0.2-0.8 yd over 7 years);
  multi-year NAIP for "was it ever cut" (hole 7 thicket).
* Did not: photo classifier for native on unirrigated rough (tan in August = "native"); Dec 2020 lidar for grass
  height and for thin tree crowns; automatic tee-pad segmentation (pads read by eye); S2 level alone next to paths.
