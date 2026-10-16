# Elevation: Spirit Hollow tee shots on the USGS 3DEP 1 m DEM

## Data

| | |
|---|---|
| Source | USGS 3DEP, fetched from The National Map `3DEPElevation/ImageServer/exportImage` (best available) on GitHub Actions (`.github/workflows/elevation_fetch.yml`, `fetch_dem.py`) |
| Underlying lidar | **USGS 1 m DEM, project IA_EasternIA_2019_B19** (tile x65y452, published 2022-11); the IL_MidNorth_D22 tile covers the Illinois side of the river only |
| Grid | 1 m, EPSG:32615 (UTM 15N), heights in metres NAVD88, 1800 x 2084 px, course bbox + 200 m, no nodata |
| Files | `spirit_hollow/dem.tif` (float32, DEFLATE, 6.6 MB), `spirit_hollow/dem.npz` (`z_cm` uint16 above `z0_m`, plus `transform`, `epsg`; 4.1 MB), `spirit_hollow/georef.json` (transform, bbox, TNM product list) |
| Range on course | 167.3 to 208.9 m (549 to 685 ft): about 136 ft of relief, mostly creek hollows |
| Accuracy | 3DEP QL2 lidar spec: RMSEz 10 cm or better on open ground. Bare earth, so trees and buildings are removed. Bilinear resampling of 1 m cells. A 1 m DEM resolves tee pads and fairway rolls, but not bunkers' lips exactly. |

The analysis is `holes_elevation.py`, which writes `spirit_hollow_holes.json`. `adjust.py` (with tests in `test_adjust.py`) turns that into model inputs.

## Where the holes are on the ground

The screenshots in `spirit_hollow/course.py` are rotated so each hole points up the screen. Each hole is placed with an **anchor** method:
* **Green**: the centroid of the OSM green polygon at the end of the OSM hole line.
* **Tee**: chosen from the scorecard tees (`course_data/tees/tee_positions.json`) and the OSM tee-box centroids near the start of the line. The one used is whichever has a tee-to-green distance closest to the screenshot's. The screenshot distance comes from trilaterating the green from the app's three "Center" numbers (`course.green_from_app`).
* **Tee line**: the tee-to-green bearing, rotated back by the angle the green sits off the line in the screenshot.

Par 3s use the Black tee (the golfer's tee) and the tee-to-green line.

As a cross-check, the imagery engineer's screenshot-to-NAIP image registration (`course_data/imagery/spirit_hollow/traced_registration.json`) agrees with the anchor on 12 of 16 tee holes. On those, the tee is within about 13 yd and the bearing within about 2 deg. The exceptions:
* 2B and 2F: the registration slid about 100 yd down the creek (its gradient correlation is about 0.04).
* 9B: 49 yd.
* 17: 30 yd.
* 4, 11 and 13: bearing differs by 6 to 13 deg.

The anchor method is used for all of these. It matches the app's tee-to-green distance within a few yards on every hole except these three:
* 2B (26 yd): the Gold tee there is a low-confidence walk-back, because the back box isn't in OSM.
* 10 (14 yd).
* 4 (11 yd).

**Treat 2B as low confidence.**

| Hole | Tee used | app vs map tee->green (yd) | ECC registration: tee offset / bearing diff |
|---|---|---|---|
| 1 | osm_tee_923964594 (osm_tee_centroid) | 396 / 397 | 9 yd / -0.3 deg |
| 2B | Gold (walkback) | 576 / 602 | 108 yd / -5.1 deg |
| 2F | Black (tee_axis) | 500 / 499 | 99 yd / +11.6 deg |
| 4 | osm_tee_923974657 (osm_tee_centroid) | 518 / 529 | 7 yd / -9.4 deg |
| 5 | osm_tee_923958976 (osm_tee_centroid) | 396 / 394 | 3 yd / +0.2 deg |
| 6 | osm_tee_923976293 (osm_tee_centroid) | 406 / 409 | 3 yd / +0.9 deg |
| 8 | osm_tee_923979073 (osm_tee_centroid) | 372 / 373 | 6 yd / -1.2 deg |
| 9B | Gold (tee_axis) | 359 / 358 | 49 yd / -7.4 deg |
| 9F | osm_tee_923980730 (osm_tee_centroid) | 340 / 340 | 2 yd / +0.3 deg |
| 10 | osm_tee_923984304 (osm_tee_centroid) | 499 / 513 | 11 yd / -0.6 deg |
| 11 | Gold (tee_axis) | 348 / 344 | 1 yd / +5.9 deg |
| 13 | Black (tee_centroid) | 402 / 402 | 5 yd / -13.4 deg |
| 14 | osm_tee_923991717 (osm_tee_centroid) | 406 / 409 | 3 yd / -0.5 deg |
| 16 | osm_tee_923991718 (osm_tee_centroid) | 388 / 394 | 13 yd / +1.7 deg |
| 17 | Black (tee_axis) | 451 / 447 | 30 yd / -3.9 deg |
| 18 | osm_tee_923993470 (osm_tee_centroid) | 492 / 497 | 8 yd / -0.9 deg |
| 7 | Black (tee_axis) | 159 / 152 | n/a |
| 12 | Black (tee_axis) | 177 / 186 | n/a |
| 15 | Black (tee_axis) | 134 / 148 | n/a |

## Per-hole results

Conventions:
* The tee-to-270 and tee-to-green columns are elevation differences, where + means uphill. "Tee -> 270" is the mean over ±10 yd laterally at 270 yd.
* Along grade: + means the ground rises away from the tee (an upslope landing).
* Cross grade: + means the ground rises to the golfer's right, so the ball kicks left.
* Carry delta: how much farther (+) or shorter the ball flies before it comes down through the real ground profile, compared with flat ground.
* Roll factor and extra_roll are for the Driver: its 25 yd of flat roll times the factor, minus 25.
* Side kick: + means the ball drifts right during the run-out.

| Hole | Par | Bearing (deg T) | Tee elev (ft) | Tee -> 270 (ft) | Tee -> green (ft) | Landing slope 240-320 along / cross (%) | Carry delta Driver / 2W / 4W (yd) | Roll factor (Driver) | extra_roll (yd) | Side kick, Driver (yd) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 155 | 658 | -46 | -65 | -4.5 / +3.4 | +19 / +17 / +14 | 1.46 | +11 | -11 |
| 2B | 5 | 260 | 616 | -33 | -41 | +7.8 / +9.0 | +10 / +11 / +10 | 0.48 | -13 | -4 |
| 2F | 5 | 247 | 575 | +13 | -0 | +4.6 / +10.4 | -6 / -4 / -3 | 0.74 | -6 | -10 |
| 4 | 5 | 350 | 638 | +17 | +22 | +3.3 / -4.2 | -7 / -6 / -5 | 0.88 | -3 | +6 |
| 5 | 4 | 15 | 669 | +6 | +8 | +1.2 / -0.2 | -3 / -2 / -2 | 0.88 | -3 | +0 |
| 6 | 4 | 93 | 678 | -12 | -24 | -2.5 / +2.5 | +5 / +5 / +4 | 1.20 | +5 | -6 |
| 8 | 4 | 262 | 652 | +13 | +14 | -0.3 / +4.2 | -6 / -5 / -4 | 0.98 | -0 | -7 |
| 9B | 4 | 72 | 665 | -19 | -40 | -2.1 / -4.7 | +8 / +7 / +6 | 1.14 | +3 | +10 |
| 9F | 4 | 79 | 665 | -24 | -41 | +0.4 / -6.8 | +10 / +9 / +7 | 0.60 | -10 | +5 |
| 10 | 5 | 34 | 619 | -28 | -17 | +0.6 / +2.8 | +11 / +10 / +9 | 0.94 | -2 | -4 |
| 11 | 4 | 60 | 605 | +6 | +12 | -1.1 / -7.0 | -2 / -2 / -2 | 1.45 | +11 | +22 |
| 13 | 4 | 196 | 629 | -35 | -31 | -3.3 / +0.1 | +15 / +13 / +11 | 1.76 | +19 | -0 |
| 14 | 4 | 202 | 640 | -59 | -51 | -0.8 / -3.6 | +22 / +20 / +18 | 1.24 | +6 | +9 |
| 16 | 4 | 88 | 645 | -12 | +10 | +2.0 / -5.6 | +5 / +4 / +4 | 0.65 | -9 | +4 |
| 17 | 4 | 215 | 647 | -2 | +2 | +1.0 / -9.4 | +1 / +1 / +0 | 0.83 | -4 | +11 |
| 18 | 5 | 330 | 642 | -65 | -57 | +3.2 / -2.8 | +24 / +22 / +20 | 0.50 | -12 | +1 |
| 7 | 3 | 193 | 658 | - | +8 | green surface +3.0 / +0.5 | plays +2 yd (iron) | - | - | - |
| 12 | 3 | 222 | 664 | - | -6 | green surface +1.5 / -1.7 | plays -2 yd (iron) | - | - | - |
| 15 | 3 | 345 | 628 | - | -6 | green surface +2.4 / +2.1 | plays -2 yd (iron) | - | - | - |

Full detail is in `spirit_hollow_holes.json`. It includes the elevations at 240, 270 and 300 yd, plane fits for the 200-240, 240-280 and 280-320 yd zones, the fall-line direction, and a 10-yd profile (centre line and ±10 yd mean) out to the green.

**Notable holes:**
* **18**: the biggest drop, 65 ft from tee to landing. The drive carries about 24 yd farther, but it lands short of a rise at about 310-330 yd that kills the run (roll ×0.5).
* **14**: 59 ft down, giving about +22 yd of carry on a nearly flat landing.
* **1**: 46 ft down, and the landing keeps falling (-4.5%). That gives +19 yd of carry and about +11 yd of extra roll, with a left kick off a +3% cross slope.
* **13**: 35 ft down onto a -3% downslope: +15 yd of carry and the most extra run (+19 yd).
* **2B** (low confidence): 33 ft down into a hollow at 230-270 yd, then a steep face (about +15%) at 280-300 yd. The driver flies into that face and stops (roll ×0.5).
* **Uphill holes**: 4 (+17 ft at 270, so -7 yd of carry), 8 (+13 ft, -6 yd) and 2F (+13 ft, -6 yd, onto a +4.6% upslope with roll ×0.74).
* **Strong side slopes**: 17 (-9.4%, ball kicks right about 11 yd), 2F (+10%, kicks left about 10 yd), 11 (-7%, about 20 yd right because the driver runs down off a crest) and 9F/9B (about -5 to -7%, kicks right).
* **Par 3s**: within ±8 ft, so ±2 yd. Hole 7 plays about 2 yd longer (uphill), and 12 and 15 play about 2 yd shorter.

## Physics (sources in the `adjust.py` docstring)

**Carry.** A 2-D ball flight with drag, Magnus lift and spin decay is fitted to the TrackMan PGA Tour averages:
* Driver: 167 mph, 10.9 deg launch, 2686 rpm, giving 275 yd carry, a 32 yd apex and a 38 deg landing angle.
* 3-wood: lands at 43 deg.
* 5-wood: lands at 47 deg.

The fit reproduces the driver exactly and the fairway woods within about 3 yd and 2 deg. Each model club keeps its own launch and spin, and its ball speed is solved so that it gives the model's flat carry. The ball is then flown onto the actual ground profile.

The geometry gives dCarry ≈ dh / tan(landing angle):
* Driver: about **0.42 yd per ft** (1 yd per 2.3 ft).
* 4-wood: about 0.33 yd per ft.
* The often-quoted "1 yd per yard (3 ft)" rule is the steeper-descending fairway-wood and iron case.
* A rule of 1 yd per 10 ft is far too small for driving.

Uphill costs more than downhill gives. At 30 ft, the driver loses 14 yd uphill but gains only 12 yd downhill: going down, the ball keeps steepening as it falls further, and going up, it meets the slope earlier.

**Roll.**
* Run-out is modelled as rolling against resistance μ = 0.15 (fairway stimp about 4 ft) plus the along grade s, so roll scales by μ/(μ+s). This is Penner's rolling-ball model.
* The first bounce is steeper relative to an upslope, so it keeps less forward speed. This is modelled with a factor of (cos(θ+α)/cos θ)².
* An upslope kills roll and a downslope adds it. The factor is clipped to 0.25-3.0.
* The grade is taken per club where that club actually lands and runs.

**Side kick.** A cross grade c accelerates the ball sideways during the run-out. The drift is roll × c / (μ + s) toward the low side, capped at 0.6 × roll. This is an upper bound for firm, dry fairways. In soft conditions, scale it by about 0.5.

## How the strategy model should apply them

The model's club tuple is `(carry, total, width, depth)`, and `simulate()` gives each ball `total - carry + extra_roll` yd of roll.

```python
from course_data.elevation.adjust import adjustments, apply_to_club
adj = adjustments("18")               # keys as course.HOLES / PAR3: 1, "2B", ..., "18" (str or int)
for club, tup in CLUBS.items():       # per hole, per club
    a = adj["clubs"][club]
    carry, total, width, depth = apply_to_club(tup, a)   # carry += carry_delta; roll *= roll_factor
    # aim: shift the aim point by -a["lateral_kick_yds"] (or add it to the landing spot before roll)
```

* **Per-club, preferred:** pass `carry + carry_delta_yds` and `carry + carry_delta + (total - carry) × roll_factor`. Leave `width` and `depth` unchanged.
* **Minimal:** keep the club table, set `HOLES[k]["extra_roll"] = adj["extra_roll_yds"]` (Driver-based), and add `carry_delta_yds` to every ball's carry. `extra_roll` alone cannot represent the carry change. A carry change matters, because carrying a hazard and the lie both depend on where the ball lands, not just its total.
* **Side kick:** add `lateral_kick_yds` to the lateral position at the end of the roll, for balls that land in the fairway. Rough already keeps only `ROUGH_ROLL` of the run.
* **Par 3s:** `plays_like_delta_yds` is the iron "plays like" change to the green, about ±2 yd at this course.
* **Regenerating:** run `python course_data/elevation/holes_elevation.py`, then `python course_data/elevation/adjust.py` to print the table. If the screenshot registrations improve, run `holes_elevation.py --geometry ecc`.
