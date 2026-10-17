# Ellis Golf Course (Cedar Rapids, IA) - Blue tees

Built 2026-10-17T10:44:43Z. OSM way/74271941. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 53 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.277 |
| mean_confidence | 0.813 |
| osm_score | 0.856 |

OSM features inside the course: buildings 9, built_up_landuse 1, golf=bunker 25, golf=cartpath 14, golf=driving_range 1, golf=fairway 21, golf=green 21, golf=hole 18, golf=lateral_water_hazard 2, golf=path 1, golf=tee 53, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, trees_polygons 1, water_lines 9, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 398 | 278 | 0.78 | check the flags | 25% | 11% | 64% | tee stage: Blue tee_centroid |  |
| 2 | 4 | 365 / 366 | 342 | 0.78 | check the flags | 26% | 9% | 65% | tee stage: Blue tee_centroid |  |
| 3 | 5 | 481 / 482 | 261 | 0.82 | auto | 34% | 36% | 30% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 202 / 202 | 192 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 385 / 384 | 66 | 0.80 | auto | 35% | 9% | 56% | tee stage: Blue tee_centroid |  |
| 6 | 4 | 420 / 419 | 246 | 0.68 | check the flags | 32% | 3% | 65% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 420 yds) |
| 7 | 4 | 463 / 465 | 88 | 0.76 | check the flags | 40% | 0% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 150 / 150 | 145 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 534 / 534 | 96 | 0.77 | check the flags | 24% | 10% | 66% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 321 / 321 | 273 | 0.79 | check the flags | 26% | 15% | 58% | tee stage: Blue tee_centroid |  |
| 11 | 3 | 155 / 155 | 168 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 519 / 522 | 132 | 0.83 | auto | 27% | 37% | 36% | tee stage: Blue tee_centroid |  |
| 13 | 4 | 350 / 351 | 127 | 0.78 | check the flags | 10% | 52% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 3 | 155 / 153 | 348 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 15 | 4 | 306 / 307 | 291 | 0.74 | check the flags | 18% | 19% | 63% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 314 / 314 | 308 | 0.77 | check the flags | 25% | 25% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 5 | 569 / 567 | 126 | 0.77 | check the flags | 24% | 10% | 66% | tee stage: Blue tee_centroid |  |
| 18 | 4 | 418 / 418 | 277 | 0.81 | auto | 43% | 22% | 35% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/74271941 Ellis Golf Course (Cedar Rapids, IA)
- **osm**: ok: 1131 features
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tees**: ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for 4 sets; lidar pads: 60 candidate pads near hole starts, 1 placement(s) on one
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/ellis/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/ellis/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 15 polygons (property_line 15); mode replace
