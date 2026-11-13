# Gateway National, holes 1-9: second-pass feature detection (specialist F1)

Status: **CHECKPOINT 1 (02:59 UTC Fri)** - the independent measurement of the hole 8 and hole 9 edges the integrator
changed on Nov 13. Holes 1-7, bunker table, greens, tees: in progress (next checkpoints replace this file).
Machine-applicable edits: `features_1_9.json` (same folder, same schema as `features_10_18.json`).

5-line summary for the manager:
1. **Hole 8 right, inside the dogleg: the two mapped native bands are mown rough.** Unmown ground starts 13-26 yds
   further right than mapped at 250-290 (lidar Dec 2020 + Sentinel-2 Nov 2024 / 2025 / 2026 agree). MUST APPLY.
2. Hole 8 unmown square inside the bend: position confirmed, 6-9 yds larger on its east side; whether it is standing
   now is NOT settled (confidence 0.55).
3. Hole 8 fairway left edge is 3-7 yds inside the mapped line at 240-290 (the Driver side).
4. **Hole 9 both integrator edits confirmed**: right "fescue" band is mown (no lidar height, NDVI > 0.72 out to the
   trees); left inner edge within 1-4 yds of the new line at 270-340, and the new line is 3-10 yds too close to play
   at 250-265.
5. Hole 9 trees right: the mapped tree zone (2014 canopy + 3 m) is 3-9 yds closer to play than the Dec 2020 crown
   edge at 180-345 (median 4). Conservative; tree polygons come with the next checkpoint.

Frame: x = yds right of the Back tee -> aim line of `render/frames.json`, along = yds from the Back tee.
"detected - mapped" offsets; the mapped values are read from `truth/package.json` as of commit bad105749.

## Evidence and method (short)

* NAIP 2023-08-19 at native 0.3 m and 2016 / 2018 / 2019 / 2020 / 2021 / 2022 at 0.6 m, all rectified into each
  hole's frame at 3 px / yd (years co-registered: residual shifts <= 0.8 m). Per-year gradient-boosted classifier
  (fairway / green / rough / native / trees / water / sand / bare) trained on eroded interiors of the map; then the
  fairway edge is re-measured per 5-yd station as the half-height crossing of a raw-band LDA score (the classifier
  alone sits ~1.5 yds inside the true edge because of its texture windows). Median and spread over 7 years.
* Lidar height above ground on 0.5 m cells (F2's grids): Dec 2023 on holes 1-2 (mown 0.023 m, native 0.13-0.22 m:
  clean), Dec 2020 on 3-9 (mown 0.004 m, native 0.01-0.05 m: weak; swath stripes on 6-7). "lidar unmown" = first
  sustained (>= 3 yds) 3-yd mean height >= 0.02-0.025 m (2020) or 0.07 m (2023) outward from the fairway edge.
* Sentinel-2 NDVI, 10 m: Nov 8 + 10 2026, Nov 2025 (4 dates), Nov 2024 (2), summer 2026 (4).
  Mown turf stays 0.80-0.87 in November; standing native 0.50-0.69.
* Trees: lidar height >= 2.5 m (Dec 2020 / Dec 2023) against the mapped zone (2014 canopy + 3 m buffer).

## Hole 8 (par 4, 408)

Fairway (mapped = OSM), 7-year measurement:

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

Left edge: measured 2-5 yds inside the mapped line at 200-250 and 3-7 at 250-290 (the diagonal edge after the
corner; perpendicular to the edge that is 2-5 yds). Right edge: within 1 yd at 200-250, 3 yds inside at 260.
Uncertainty +/-1.5 yds (sd over years 0.3-1.6; 260 L is +/-3).

Right side, from the fairway edge outwards (x, yds):

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

* "mapped native" starts at the fairway edge + 0-10 yds because two bands overlap there: `fescue before the trees
  right` (x +25..+45, 220-345) and `unmown ground inside the dogleg`.
* Lidar (Dec 2020) finds no standing grass until 41-49 at 220-255 (= the brush at the foot of the trees), then
  34 / 28 / 21 / 8 / -7 at 260 / 270 / 280 / 290 / 300. Sentinel-2 Nov 2026 (NDVI < 0.72) puts the same line at
  44 / 36 / 29 / 14 / 2 / -7 at 250 / 260 / 270 / 280 / 290 / 300. They agree within 0-6 yds.
* Region means: band x +30..+44 at 225-255: lidar 3 % of cells > 0.05 m (fairway 1 %, reference native left of 8:
  24 %), NDVI Nov 2026 / 2025 / 2024 = 0.84 / 0.76 / 0.82 (fairway 0.84 / 0.85 / 0.86; native 0.66 / 0.63 / 0.69).
  Band at 272-284, x 0..+20: lidar 2 %, NDVI 0.76 / 0.67 / 0.76 (10 m pixels mixed with the brush line).
* The NAIP classifier calls this ground "bare / native" in every summer image (tan, textured): it is unirrigated
  rough that browns out in summer and is green and short in November / December. The photo misleads here; the
  two late-season sources decide. **Verdict: mown rough to the brush line. Confidence 0.8 at 220-260, 0.65 at
  265-290. Edge uncertainty +/-4 yds.**
* Trees: Dec 2020 crown edge 48-55 at 200-260 (mapped 49-56: fine), **39-43 at 270-285 (mapped 50-53: trees
  10-12 yds closer)**, 21 / 19 / 14 at 290 / 295 / 300 (mapped 17 / 16 / 20: fine).

Unmown square inside the bend (integrator's Nov 13 polygon, x -88..-57, 302-337):
* NAIP 2023 0.3 m: tufted block with a straight worn north-east edge from (-48, 316) to (-72, 335) and a south tip
  at (-67, 298). Mapped polygon is right on the west / north and 6-9 yds short on the east (x -57 vs -48 at 316).
* Is it standing now? NAIP 2023 texture 7.4 (native 7.2, fairway 1.7): unmown in Aug 2023, also darker / rougher in
  2021. But lidar Dec 2020: 9 % of cells > 0.05 m (native 24 %, fairway 1 %), and NDVI Nov 2026 0.78 median, 0.57
  minimum (30-yd block = mixed pixels). **Not resolved: keep as native, confidence 0.55.** If Driver at 46 L only
  wins because of how this block is priced, say so on the page.

## Hole 9 (par 4, 390)

Fairway (OSM) is accurate: measured - mapped within +/-1.5 yds on both edges at 140-310, sd over years 0.1-1.0
(table in the next checkpoint).

Left side (native strip between 9 and the pond):

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

* Integrator's new inner edge: -24 / -18 / -18 / -22 / -27 / -28 at 250 / 265 / 280 / 300 / 320 / 340.
* 270-300: lidar -20 / -19 / -19 / -23, NAIP -15 / -12 / -18 / -20, S2 -13 / -10 / -10 / -13: **confirmed, +/-3 yds**
  (lidar = standing height; NAIP and S2 also catch the worn, bare strip in front of it).
* 320-340: lidar -31 ... -32 (map -27 / -28): map 3-4 yds on the safe side. Fine.
* 250-265: lidar -35 / -36 / -34 / -29, NAIP -27 / -34 / -33 / -29, S2 -29 / -28 / -25 / -19; map -24 / -22 / -20 /
  -18: **map is 3-10 yds too close to play here** (suggested -27 / -30 / -30 / -24; minor: fairway edge is -19 ... -12).
* The Nov 9 line (-14 ... -22 at 290-340) was indeed an overshoot.

Right side:

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

* No standing grass between the fairway and the trees: lidar first height at 43-58 = the tree line itself; S2 Nov
  2026 stays above 0.72 out to 57-72. The NAIP classifier's "unmown" at 23-45 is the pale, dried-out rough and the
  cart path (path at x 51-57 from 230 on). **Removal of the right fescue band confirmed, confidence 0.9.**
* Trees: mapped zone starts 3-9 yds closer to play than the Dec 2020 crown edge (>= 2.5 m): 39 vs 44 at 200,
  43 vs 52 at 220, 48 vs 55 at 250, 51 vs 57 at 270, 53 vs 57 at 290, 49 vs 58 at 300. The 2023 photo crowns sit
  2-4 yds inside the lidar edge at 200-220 (leaf-on, relief displacement), so the truth is in between: **mapped
  trees ~2-5 yds too close; conservative for a Driver aimed 19 R.** Crown edge uncertainty +/-3 yds.

## Not done yet (next checkpoints)

Holes 1-7 station tables; fairway edits; bunker carry / reach table; greens, collars and par-3 surrounds (4, 7);
tee pads (first look: every set's marker on holes 1, 2, 3 sits on or within 3 yds of a visible pad); tree polygons
from the 2020 / 2023 lidar; water edges.
