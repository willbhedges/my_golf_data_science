# TPC Sawgrass (Ponte Vedra Beach, FL) - The Players tees

Built 2026-11-03T09:27:58Z. OSM relation/1783123. Scorecard: file (course_data/library/tpc_sawgrass/card_review.json). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 116 |
| tees_with_colour | 2 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.467 |
| mean_confidence | 0.834 |
| osm_score | 0.893 |

OSM features inside the course: buildings 4, golf=bunker 154, golf=cartpath 104, golf=driving_range 2, golf=fairway 49, golf=green 59, golf=hole 18, golf=lateral_water_hazard 13, golf=pin 36, golf=rough 19, golf=tee 116, golf=water_hazard 19, holes_with_handicap 18, holes_with_par 18, long_grass_polygons 1, single_trees 1, tees_with_colour 2, tees_with_ref 18, tree_rows 2, trees_polygons 1, water_polygons 35

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 424 / 423 | 1 | 0.82 | auto | 38% | 31% | 31% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 2 | 5 | 555 / 553 | 199 | 0.74 | check the flags | 27% | 44% | 29% | tee stage: The Players lidar_pad | tee: tee stage: The Players lidar_pad; The Players tee on a lidar pad (no OSM box at 555 yds) |
| 3 | 3 | 182 / 182 | 284 | 0.93 | auto | 100% | 0% | 0% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 4 | 4 | 387 / 386 | 160 | 0.79 | check the flags | 32% | 9% | 59% | tee stage: The Players tee_centroid |  |
| 5 | 4 | 469 / 469 | 98 | 0.83 | auto | 62% | 2% | 36% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 6 | 4 | 413 / 413 | 234 | 0.73 | check the flags | 45% | 31% | 24% | tee stage: The Players walkback | tee: tee stage: The Players walkback; The Players tee walked back along the hole line (no box at 413 yds) |
| 7 | 4 | 450 / 450 | 53 | 0.85 | auto | 69% | 5% | 26% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 8 | 3 | 236 / 236 | 78 | 0.93 | auto | 100% | 0% | 0% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 9 | 5 | 601 / 595 | 316 | 0.76 | check the flags | 50% | 20% | 30% | tee stage: The Players lidar_pad | tee: tee stage: The Players lidar_pad; The Players tee on a lidar pad (no OSM box at 601 yds) |
| 10 | 4 | 419 / 419 | 62 | 0.84 | auto | 40% | 38% | 22% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 11 | 5 | 573 / 571 | 207 | 0.83 | auto | 37% | 23% | 40% | tee stage: The Players tee_centroid |  |
| 12 | 4 | 365 / 364 | 16 | 0.74 | check the flags | 39% | 26% | 34% | tee stage: The Players lidar_pad | tee: tee stage: The Players lidar_pad; The Players tee on a lidar pad (no OSM box at 365 yds) |
| 13 | 3 | 183 / 182 | 177 | 0.93 | auto | 100% | 0% | 0% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 14 | 4 | 485 / 483 | 204 | 0.83 | auto | 64% | 0% | 36% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 15 | 4 | 470 / 469 | 308 | 0.83 | auto | 42% | 34% | 24% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 16 | 5 | 537 / 531 | 163 | 0.82 | auto | 42% | 25% | 33% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 17 | 3 | 141 / 141 | 328 | 0.93 | auto | 100% | 0% | 0% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |
| 18 | 4 | 462 / 461 | 340 | 0.86 | auto | 66% | 14% | 19% | tee stage: The Players tee_axis | tee: tee stage: The Players tee_axis |

## Stages

- **resolve**: ok: relation/1783123 TPC Sawgrass (Ponte Vedra Beach, FL)
- **osm**: ok: 1484 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/tpc_sawgrass/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 99 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/tpc_sawgrass/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/tpc_sawgrass/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole way names: stadium 18, valley 18); kept 'stadium' (named in the request), 18 ways; ignored 18
