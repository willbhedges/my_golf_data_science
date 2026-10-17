# Wakonda Club (Des Moines, IA) - Blue tees

Built 2026-10-17T09:11:53Z. OSM way/102681377. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 55 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 0 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.381 |
| mean_confidence | 0.813 |
| osm_score | 0.676 |

OSM features inside the course: buildings 9, golf=bunker 48, golf=cartpath 39, golf=fairway 25, golf=green 26, golf=hole 18, golf=lateral_water_hazard 3, golf=tee 55, holes_with_par 18, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 410 / 408 | 8 | 0.78 | check the flags | 32% | 0% | 68% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 3 | 114 / 113 | 293 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 382 / 384 | 182 | 0.79 | check the flags | 36% | 0% | 64% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 2% of the landing zone |
| 4 | 4 | 410 / 410 | 348 | 0.77 | check the flags | 29% | 0% | 71% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 5 | 505 / 506 | 101 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 399 / 398 | 175 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 348 / 347 | 189 | 0.75 | check the flags | 37% | 0% | 63% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 5 | 509 / 510 | 278 | 0.80 | check the flags | 53% | 0% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 0% of the landing zone |
| 9 | 3 | 169 / 168 | 68 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 429 / 427 | 118 | 0.84 | auto | 56% | 0% | 44% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 396 / 397 | 335 | 0.77 | check the flags | 31% | 0% | 69% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 4 | 351 / 351 | 159 | 0.73 | check the flags | 29% | 0% | 71% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 5 | 510 / 509 | 346 | 0.77 | check the flags | 42% | 0% | 58% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 3 | 168 / 168 | 235 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 15 | 5 | 490 / 490 | 163 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 422 / 421 | 329 | 0.83 | auto | 52% | 0% | 48% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 158 / 158 | 280 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 301 / 301 | 179 | 0.73 | check the flags | 27% | 0% | 73% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 1% of the landing zone |

## Stages

- **resolve**: ok: way/102681377 Wakonda Club (Des Moines, IA)
- **osm**: ok: 499 features
- **scorecard**: ok: golfify (golfify)
- **tees**: ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for 5 sets; lidar pads: 59 candidate pads near hole starts, 0 placement(s) on one
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/wakonda/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/wakonda/imagery/dem.tif (18/18 holes)
- **vision**: missing: no vision_any layers for 'wakonda' (FileNotFoundError: course_data/vision_any/wakonda/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

## Warnings

- vision: missing: no vision_any layers for 'wakonda' (FileNotFoundError: course_data/vision_any/wakonda/raw (not fetched)); add the course to course_data/vision_any/cour; trees / long grass come from OSM only
