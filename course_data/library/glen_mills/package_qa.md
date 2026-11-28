# The Golf Course at Glen Mills (Thornbury Township, PA) - Black tees

Built 2026-11-28T04:24:49Z. OSM way/284570622. Scorecard: file (course_data/library/glen_mills/routed_card.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 110 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.385 |
| mean_confidence | 0.824 |
| osm_score | 0.848 |

OSM features inside the course: buildings 2, golf=bunker 104, golf=fairway 18, golf=green 17, golf=hole 17, golf=rough 6, golf=tee 110, golf=water_hazard 1, holes_with_par 17, water_lines 7, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 374 / 372 | 343 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 431 / 430 | 180 | 0.80 | auto | 54% | 0% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 394 / 391 | 268 | 0.82 | auto | 48% | 16% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 572 / 572 | 36 | 0.80 | auto | 46% | 10% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 181 / 181 | 9 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 547 / 548 | 75 | 0.75 | check the flags | 41% | 46% | 13% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 547 yds) |
| 7 | 3 | 221 / 221 | 277 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 325 / 321 | 110 | 0.80 | auto | 33% | 30% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 433 / 428 | 224 | 0.80 | auto | 48% | 9% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 3 | 207 / 209 | 79 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 207 yds) |
| 11 | 4 | 376 / 374 | 36 | 0.84 | auto | 30% | 53% | 18% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 339 / 277 | 35 | 0.72 | check the flags | 22% | 37% | 41% | tee stage: Black lidar_pad_capped | tee: tee stage: Black lidar_pad_capped; Black tee on a lidar pad (no OSM box at 339 yds) |
| 13 | 4 | 453 / 453 | 70 | 0.78 | check the flags | 38% | 10% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 161 / 156 | 92 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 529 / 524 | 228 | 0.75 | check the flags | 21% | 18% | 61% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 156 / 156 | 226 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 5 | 483 / 478 | 212 | 0.81 | auto | 32% | 36% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 464 / 460 | 235 | 0.80 | check the flags | 38% | 20% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/284570622 The Golf Course at Glen Mills (Thornbury Township, PA)
- **osm**: ok: 564 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/glen_mills/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 77 candidate pads near hole starts (20 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/glen_mills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/glen_mills/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -554 m2 {'cells': 529}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 12 Black: CHECK, tee was put 81 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12: measured 277 vs card 339 yds for Black (no OSM tee box at that yardage?)
