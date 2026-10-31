# Jimmie Austin Golf Club (Norman, OK) - I tees

Built 2026-10-31T03:50:22Z. OSM way/315995643. Scorecard: golfify (golfify). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 85 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.402 |
| mean_confidence | 0.835 |
| osm_score | 0.88 |

OSM features inside the course: buildings 7, golf=bunker 99, golf=cartpath 63, golf=clubhouse 1, golf=driving_range 1, golf=fairway 81, golf=green 28, golf=hole 18, golf=pin 18, golf=tee 85, golf=water_hazard 2, holes_with_par 18, trees_polygons 3, water_lines 5, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 461 / 461 | 167 | 0.76 | check the flags | 45% | 26% | 30% | tee stage: I lidar_pad | tee: tee stage: I lidar_pad; I tee on a lidar pad (no OSM box at 461 yds) |
| 2 | 3 | 171 / 171 | 168 | 0.93 | auto | 100% | 0% | 0% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 3 | 4 | 329 / 328 | 188 | 0.80 | check the flags | 46% | 9% | 45% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 4 | 4 | 445 / 445 | 80 | 0.80 | check the flags | 39% | 18% | 43% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 5 | 5 | 625 / 615 | 218 | 0.80 | auto | 47% | 10% | 43% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 6 | 3 | 180 / 180 | 263 | 0.93 | auto | 100% | 0% | 0% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 7 | 4 | 424 / 421 | 19 | 0.85 | auto | 54% | 23% | 23% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 8 | 5 | 583 / 582 | 12 | 0.87 | auto | 37% | 40% | 23% | tee stage: I tee_centroid |  |
| 9 | 4 | 420 / 426 | 351 | 0.81 | auto | 52% | 7% | 41% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 10 | 4 | 319 / 320 | 270 | 0.78 | check the flags | 35% | 17% | 48% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 11 | 4 | 440 / 441 | 94 | 0.83 | auto | 42% | 14% | 44% | tee stage: I tee_centroid |  |
| 12 | 3 | 182 / 178 | 101 | 0.93 | auto | 100% | 0% | 0% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 13 | 5 | 592 / 591 | 160 | 0.85 | auto | 33% | 38% | 30% | tee stage: I tee_centroid |  |
| 14 | 4 | 441 / 440 | 151 | 0.78 | check the flags | 33% | 18% | 49% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 15 | 3 | 260 / 259 | 351 | 0.93 | auto | 100% | 0% | 0% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 16 | 4 | 423 / 422 | 179 | 0.78 | check the flags | 32% | 20% | 48% | tee stage: I tee_axis | tee: tee stage: I tee_axis |
| 17 | 4 | 483 / 482 | 2 | 0.81 | auto | 37% | 9% | 54% | tee stage: I tee_centroid |  |
| 18 | 5 | 586 / 582 | 334 | 0.80 | check the flags | 30% | 31% | 39% | tee stage: I tee_axis | tee: tee stage: I tee_axis |

## Stages

- **resolve**: ok: way/315995643 Jimmie Austin Golf Club (Norman, OK)
- **osm**: ok: 1179 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 97 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/jimmie_austin/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/jimmie_austin/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace
