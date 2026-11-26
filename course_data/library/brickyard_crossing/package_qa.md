# Brickyard Crossing Golf Course (Indianapolis, IN) - Gold tees

Built 2026-11-26T17:16:07Z. OSM relation/569616. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Green, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Green, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.554 |
| mean_confidence | 0.855 |
| osm_score | 0.911 |

OSM features inside the course: buildings 6, golf=bunker 82, golf=cartpath 58, golf=fairway 25, golf=green 29, golf=hole 18, golf=pin 18, golf=rough 31, golf=tee 67, golf=water_hazard 5, holes_with_handicap 16, holes_with_par 18, single_trees 297, trees_polygons 7, water_lines 1, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 378 / 377 | 25 | 0.88 | auto | 64% | 6% | 30% | tee stage: Gold tee_centroid |  |
| 2 | 5 | 570 / 569 | 17 | 0.83 | auto | 48% | 23% | 29% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 4 | 369 / 365 | 5 | 0.81 | auto | 44% | 20% | 36% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 3 | 215 / 215 | 195 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 4 | 465 / 464 | 165 | 0.84 | auto | 59% | 11% | 30% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 5 | 542 / 541 | 166 | 0.80 | auto | 47% | 11% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 3 | 181 / 181 | 314 | 0.86 | auto | 100% | 0% | 0% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 181 yds) |
| 8 | 4 | 464 / 460 | 9 | 0.88 | auto | 79% | 5% | 16% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 4 | 383 / 382 | 155 | 0.80 | check the flags | 42% | 14% | 44% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 10 | 4 | 353 / 352 | 196 | 0.78 | check the flags | 47% | 0% | 52% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 11 | 4 | 462 / 461 | 20 | 0.93 | auto | 84% | 4% | 13% | tee stage: Gold tee_centroid |  |
| 12 | 5 | 581 / 580 | 16 | 0.84 | auto | 53% | 18% | 28% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 3 | 193 / 193 | 291 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 14 | 4 | 311 / 312 | 94 | 0.83 | auto | 45% | 27% | 28% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 15 | 5 | 551 / 545 | 183 | 0.83 | auto | 53% | 14% | 33% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 16 | 4 | 465 / 464 | 192 | 0.85 | auto | 58% | 21% | 21% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 3 | 206 / 206 | 188 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 18 | 4 | 491 / 490 | 177 | 0.81 | auto | 52% | 7% | 40% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |

## Stages

- **resolve**: ok: relation/569616 Brickyard Crossing Golf Course (Indianapolis, IN)
- **osm**: ok: 1447 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 1/1 holes OSM has no way for (0 to check; segment no, lidar pads 202, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 89 candidate pads near hole starts (20 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/brickyard_crossing/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/brickyard_crossing/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -32776 m2 {'road': 31562, 'strip': 568, 'cells': 624}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 16 polygons (outside 16); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- ignored 1 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 696812937
- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Green, Red
- hole 2 White: CHECK, tee was put 77 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Green: CHECK, tee was put 97 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 4 Green: CHECK, tee was put 63 yds from this hole's start, at hole 13's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 4 Red: CHECK, tee was put 110 yds from this hole's start, at hole 13's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Green: CHECK, tee was put 87 yds from this hole's start, at hole 6's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Red: CHECK, tee was put 97 yds from this hole's start, at hole 6's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 15 Green: CHECK, tee was put 84 yds from this hole's start, at hole 4's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
