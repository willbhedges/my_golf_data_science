# Mozingo Lake Golf Course (Maryville, MO) - App tees

Built 2026-10-16T23:34:35Z. OSM way/385067034. Scorecard: request (request file yardages). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 66 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.451 |
| mean_confidence | 0.832 |
| osm_score | 0.89 |

OSM features inside the course: buildings 4, golf=bunker 25, golf=cartpath 23, golf=driving_range 1, golf=fairway 20, golf=green 25, golf=hole 18, golf=rough 22, golf=tee 66, golf=water_hazard 3, holes_with_handicap 16, holes_with_par 18, single_trees 12, tees_with_ref 12, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 371 / 361 | 183 | 0.77 | check the flags | 34% | 17% | 48% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 2 | 4 | 349 / 350 | 59 | 0.85 | auto | 46% | 24% | 30% | tee stage: App tee_centroid |  |
| 3 | 5 | 517 / 513 | 230 | 0.78 | check the flags | 48% | 2% | 50% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 4 | 4 | 361 / 362 | 79 | 0.78 | check the flags | 44% | 7% | 49% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 5 | 3 | 182 / 174 | 210 | 0.92 | auto | 100% | 0% | 0% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 6 | 5 | 491 / 487 | 266 | 0.79 | check the flags | 50% | 3% | 47% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 7 | 4 | 428 / 427 | 36 | 0.81 | auto | 57% | 4% | 39% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 8 | 3 | 187 / 184 | 26 | 0.92 | auto | 100% | 0% | 0% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 9 | 4 | 348 / 346 | 18 | 0.81 | auto | 41% | 12% | 47% | tee stage: App tee_centroid |  |
| 10 | 4 | 392 / 393 | 10 | 0.80 | auto | 47% | 15% | 38% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 11 | 3 | 219 / 220 | 343 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 12 | 5 | 517 / 516 | 265 | 0.77 | check the flags | 45% | 4% | 51% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 13 | 4 | 394 / 393 | 177 | 0.83 | auto | 43% | 36% | 22% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 14 | 5 | 464 / 464 | 187 | 0.83 | auto | 50% | 9% | 41% | tee stage: App tee_centroid |  |
| 15 | 3 | 174 / 176 | 80 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 16 | 4 | 433 / 431 | 13 | 0.81 | auto | 50% | 17% | 33% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 17 | 4 | 344 / 326 | 47 | 0.77 | check the flags | 22% | 33% | 45% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 18 | 4 | 407 / 399 | 203 | 0.83 | auto | 55% | 2% | 43% | tee stage: App tee_centroid |  |

## Stages

- **resolve**: ok: way/385067034 Mozingo Lake Golf Course (Maryville, MO)
- **osm**: ok: 475 features
- **scorecard**: ok: request (request file yardages)
- **tees**: ok: tees/place_tee.py for 1 sets on the card yardages
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/mozingo_lake/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **elevation**: ok: course_data/packages/mozingo_lake/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised)

## Warnings

- hole 17: measured 326 vs card 344 yds for App (no OSM tee box at that yardage?)
