# TPC Deere Run (Silvis, IL) - Gold tees

Built 2026-11-03T16:25:48Z. OSM relation/12585470. Scorecard: file (course_data/library/tpc_deere_run/card_review.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 65 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.547 |
| mean_confidence | 0.844 |
| osm_score | 0.895 |

OSM features inside the course: buildings 14, built_up_landuse 1, golf=bunker 79, golf=cartpath 25, golf=clubhouse 1, golf=driving_range 2, golf=fairway 25, golf=green 29, golf=hole 18, golf=rough 4, golf=tee 65, golf=water_hazard 3, holes_with_par 18, single_trees 765, trees_polygons 12, water_lines 4, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 395 | 211 | 0.82 | auto | 55% | 8% | 37% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 2 | 5 | 561 / 561 | 214 | 0.80 | check the flags | 52% | 2% | 46% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 3 | 186 / 186 | 339 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 4 | 454 / 453 | 129 | 0.86 | auto | 70% | 8% | 22% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 4 | 433 / 433 | 353 | 0.78 | check the flags | 40% | 7% | 54% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 4 | 367 / 367 | 309 | 0.85 | auto | 64% | 13% | 24% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 3 | 226 / 226 | 182 | 0.86 | auto | 100% | 0% | 0% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 226 yds) |
| 8 | 4 | 428 / 428 | 359 | 0.87 | auto | 42% | 32% | 26% | tee stage: Gold tee_centroid |  |
| 9 | 4 | 503 / 503 | 142 | 0.78 | check the flags | 42% | 3% | 54% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 10 | 5 | 596 / 596 | 319 | 0.78 | check the flags | 47% | 0% | 53% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 11 | 4 | 432 / 433 | 103 | 0.85 | auto | 68% | 6% | 26% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 12 | 3 | 215 / 215 | 129 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 4 | 424 / 424 | 318 | 0.82 | auto | 59% | 0% | 41% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 361 / 361 | 135 | 0.80 | check the flags | 48% | 6% | 46% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 15 | 4 | 484 / 484 | 182 | 0.82 | auto | 55% | 6% | 39% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 16 | 3 | 157 / 157 | 214 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 5 | 569 / 566 | 30 | 0.83 | auto | 54% | 17% | 29% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 18 | 4 | 476 / 475 | 199 | 0.89 | auto | 70% | 23% | 7% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |

## Stages

- **resolve**: ok: relation/12585470 TPC Deere Run (Silvis, IL)
- **osm**: ok: 1320 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/tpc_deere_run/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 78 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/tpc_deere_run/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/tpc_deere_run/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -57 m2 {'cells': 50}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace
