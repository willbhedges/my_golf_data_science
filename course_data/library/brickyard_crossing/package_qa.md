# Brickyard Crossing Golf Course (Indianapolis, IN) - Gold tees

Built 2026-11-01T20:43:07Z. OSM relation/569616. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Green, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Green, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 19 |
| greens_found | 18 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.534 |
| mean_confidence | 0.836 |
| osm_score | 0.907 |

OSM features inside the course: buildings 6, golf=bunker 82, golf=cartpath 58, golf=fairway 25, golf=green 29, golf=hole 19, golf=pin 18, golf=rough 31, golf=tee 67, golf=water_hazard 5, holes_with_handicap 17, holes_with_par 19, single_trees 297, trees_polygons 7, water_lines 1, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 378 / 377 | 25 | 0.87 | auto | 64% | 4% | 32% | tee stage: Gold tee_centroid |  |
| 2 | 5 | 570 / 569 | 17 | 0.82 | auto | 48% | 16% | 36% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 4 | 369 / 365 | 5 | 0.80 | auto | 44% | 14% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 3 | 215 / 215 | 195 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 4 | 465 / 464 | 165 | 0.83 | auto | 59% | 6% | 35% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 5 | 542 / 541 | 166 | 0.79 | check the flags | 47% | 6% | 47% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 3 | 181 / 181 | 314 | 0.86 | auto | 100% | 0% | 0% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 181 yds) |
| 8 | 4 | 464 / 460 | 9 | 0.88 | auto | 79% | 2% | 18% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 4 | 383 / 382 | 155 | 0.79 | check the flags | 42% | 10% | 49% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 10 | 4 | 353 / 352 | 196 | 0.78 | check the flags | 47% | 0% | 53% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 11 | 4 | 462 / 461 | 20 | 0.92 | auto | 84% | 1% | 15% | tee stage: Gold tee_centroid |  |
| 12 | 5 | 581 / 580 | 16 | 0.83 | auto | 53% | 16% | 30% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 3 | 193 / 193 | 291 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 14 | 4 | 311 / 302 | 203 | 0.65 | check the flags | 22% | 6% | 73% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 311 yds) |
| 15 | 5 | 551 / 553 | 173 | 0.75 | check the flags | 51% | 11% | 38% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 551 yds) |
| 16 | 4 | 465 / 464 | 192 | 0.85 | auto | 58% | 17% | 24% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 3 | 206 / 206 | 188 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 18 | 4 | 491 / 490 | 175 | 0.81 | auto | 50% | 7% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |

## Stages

- **resolve**: ok: relation/569616 Brickyard Crossing Golf Course (Indianapolis, IN)
- **osm**: ok: 1447 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 1/1 holes OSM has no way for (1 to check; segment no, lidar pads 202, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 106 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/brickyard_crossing/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/brickyard_crossing/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 18 polygons (outside 18); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Green, Red
- hole 15: CHECK, shares hole 14's green
- hole 15: placed by v2+structure inference, golfer check (shares hole 14's green and no unused green fits)
- hole 14 Red: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
