# Ellis Golf Course (Cedar Rapids, IA) - Blue tees

Built 2026-10-17T10:12:30Z. OSM way/74271941. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 53 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 2 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.313 |
| mean_confidence | 0.792 |
| osm_score | 0.691 |

OSM features inside the course: buildings 9, built_up_landuse 1, golf=bunker 25, golf=cartpath 14, golf=driving_range 1, golf=fairway 21, golf=green 21, golf=hole 18, golf=lateral_water_hazard 2, golf=path 1, golf=tee 53, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, trees_polygons 1, water_lines 9, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 398 | 278 | 0.76 | check the flags | 25% | 0% | 75% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 365 / 366 | 342 | 0.76 | check the flags | 26% | 0% | 74% | tee stage: Blue tee_centroid |  |
| 3 | 5 | 481 / 482 | 261 | 0.74 | check the flags | 34% | 0% | 66% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 202 / 202 | 192 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 385 / 384 | 66 | 0.78 | check the flags | 35% | 0% | 65% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 420 / 419 | 246 | 0.67 | check the flags | 32% | 0% | 68% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Blue tee on a lidar pad (no OSM box at 420 yds) |
| 7 | 4 | 463 / 465 | 88 | 0.76 | check the flags | 40% | 0% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 150 / 150 | 145 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 534 / 534 | 96 | 0.75 | check the flags | 24% | 0% | 76% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 321 / 321 | 273 | 0.76 | check the flags | 26% | 0% | 74% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 155 / 155 | 168 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 519 / 522 | 132 | 0.76 | check the flags | 27% | 0% | 73% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 4 | 350 / 351 | 127 | 0.82 | auto | 60% | 0% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 3 | 155 / 153 | 348 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 15 | 4 | 306 / 307 | 291 | 0.70 | check the flags | 18% | 0% | 82% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 314 / 314 | 308 | 0.72 | check the flags | 25% | 0% | 75% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 5 | 569 / 567 | 126 | 0.75 | check the flags | 24% | 0% | 76% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 418 / 418 | 277 | 0.77 | check the flags | 43% | 0% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/74271941 Ellis Golf Course (Cedar Rapids, IA)
- **osm**: ok: 1131 features
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tees**: ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for 4 sets; lidar pads: 60 candidate pads near hole starts, 1 placement(s) on one
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/ellis/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/ellis/imagery/dem.tif (18/18 holes)
- **vision**: missing: no vision_any layers for 'ellis' (FileNotFoundError: course_data/vision_any/ellis/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

## Warnings

- vision: missing: no vision_any layers for 'ellis' (FileNotFoundError: course_data/vision_any/ellis/raw (not fetched)); add the course to course_data/vision_any/courses.; trees / long grass come from OSM only
