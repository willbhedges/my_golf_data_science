# Gamble Sands Golf Course (Brewster, WA) - Back tees

Built 2026-11-26T17:18:10Z. OSM way/876550790. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Medal, Back, Regular, Intermediate, Forward, Sands, Intermediate (F))).

**WARNING: requested tee set 'Black' is not on the card; using 'Back' instead (allow_substitute). Sets on the card: Medal, Back, Regular, Intermediate, Forward, Sands, Intermediate (F)**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 18 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.726 |
| mean_confidence | 0.865 |
| osm_score | 0.888 |

OSM features inside the course: buildings 4, golf=bunker 69, golf=cartpath 44, golf=driving_range 1, golf=fairway 13, golf=green 18, golf=hole 18, golf=lateral_water_hazard 1, golf=rough 7, golf=tee 18, holes_with_par 18, water_lines 1, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 397 / 397 | 230 | 0.76 | check the flags | 62% | 23% | 15% | tee stage: Back walkback | tee: tee stage: Back walkback; Back tee walked back along the hole line (no box at 397 yds) |
| 2 | 4 | 297 / 303 | 304 | 0.87 | auto | 62% | 24% | 14% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 3 | 5 | 623 / 623 | 157 | 0.90 | auto | 87% | 4% | 8% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 4 | 3 | 161 / 161 | 199 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 5 | 4 | 483 / 484 | 100 | 0.90 | auto | 77% | 14% | 9% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 6 | 3 | 230 / 230 | 32 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 7 | 5 | 456 / 457 | 193 | 0.78 | check the flags | 71% | 16% | 13% | tee stage: Back walkback | tee: tee stage: Back walkback; Back tee walked back along the hole line (no box at 456 yds) |
| 8 | 4 | 305 / 306 | 286 | 0.91 | auto | 78% | 4% | 18% | tee stage: Back tee_centroid |  |
| 9 | 4 | 380 / 380 | 141 | 0.75 | check the flags | 47% | 36% | 17% | tee stage: Back walkback | tee: tee stage: Back walkback; Back tee walked back along the hole line (no box at 380 yds) |
| 10 | 3 | 132 / 137 | 79 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 11 | 4 | 402 / 403 | 45 | 0.79 | check the flags | 83% | 6% | 10% | tee stage: Back walkback | tee: tee stage: Back walkback; Back tee walked back along the hole line (no box at 402 yds) |
| 12 | 4 | 296 / 297 | 48 | 0.86 | auto | 51% | 36% | 14% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 13 | 5 | 538 / 538 | 331 | 0.89 | auto | 78% | 8% | 14% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 14 | 4 | 393 / 393 | 6 | 0.79 | check the flags | 87% | 1% | 12% | tee stage: Back walkback | tee: tee stage: Back walkback; Back tee walked back along the hole line (no box at 393 yds) |
| 15 | 4 | 453 / 454 | 226 | 0.93 | auto | 86% | 3% | 12% | tee stage: Back tee_centroid |  |
| 16 | 3 | 193 / 199 | 252 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 17 | 4 | 411 / 411 | 337 | 0.87 | auto | 72% | 9% | 19% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 18 | 5 | 514 / 514 | 7 | 0.77 | check the flags | 76% | 9% | 16% | tee stage: Back walkback | tee: tee stage: Back walkback; Back tee walked back along the hole line (no box at 514 yds) |

## Stages

- **resolve**: ok: way/876550790 Gamble Sands Golf Course (Okanogan County, WA)
- **osm**: ok: 333 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 2 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/gamble_sands/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gamble_sands/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -5933 m2 {'strip': 5933}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace
- **native_auto**: ok: 14 holes, sides 1 both, 2 both, 3 both, 5 both, 7 both, 8 both, 9 both, 11 both, 12 both, 13 both, 14 both, 15 both, 17 both, 18 both

## Warnings

- ignored 14 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1551387389, 1551387397, 1551387400, 1551387403, 1551387406, 1551387409, 1551387412, 1551387415
- requested tee set 'Black' is not on the card; using 'Back' instead (allow_substitute). Sets on the card: Medal, Back, Regular, Intermediate, Forward, Sands, Intermediate (F)
- hole 1 Medal: CHECK, tee was on a building (OSM 1091039587): moved 5 yds forward off it
- hole 6 Medal: CHECK, tee was on a green (OSM 946566256): moved 5 yds forward off it
- hole 6 Forward: CHECK, tee was put 120 yds from this hole's start, at hole 7's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- scorecard (golfify): 3 hole(s) where a longer set is shorter than the next set: 12 Back 296 < Sands 306, 3 Sands 519 < Regular 591, 17 Sands 393 < Regular 411
