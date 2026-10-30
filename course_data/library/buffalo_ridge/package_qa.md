# Buffalo Ridge Springs Golf Course (Branson, MO) - Buffalo tees

Built 2026-10-30T12:11:35Z. OSM way/399501608. Scorecard: golfify (golfify). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 82 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.521 |
| mean_confidence | 0.862 |
| osm_score | 0.86 |

OSM features inside the course: buildings 2, golf=bunker 88, golf=cartpath 36, golf=fairway 52, golf=green 20, golf=hole 17, golf=lateral_water_hazard 20, golf=rough 5, golf=tee 82, holes_with_par 17, water_lines 9, water_polygons 20

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 578 / 568 | 27 | 0.84 | auto | 68% | 0% | 32% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 471 / 470 | 351 | 0.83 | auto | 41% | 15% | 44% | tee stage: Buffalo tee_centroid |  |
| 3 | 4 | 405 / 405 | 129 | 0.87 | auto | 67% | 0% | 33% | tee stage: Buffalo tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 195 / 195 | 167 | 0.96 | auto | 100% | 0% | 0% | tee stage: Buffalo tee_centroid |  |
| 5 | 4 | 449 / 448 | 23 | 0.82 | auto | 48% | 0% | 51% | tee stage: Buffalo tee_centroid |  |
| 6 | 4 | 353 / 352 | 162 | 0.78 | check the flags | 33% | 21% | 46% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 7 | 3 | 245 / 245 | 339 | 0.93 | auto | 100% | 0% | 0% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 8 | 5 | 524 / 523 | 200 | 0.77 | check the flags | 63% | 7% | 30% | tee stage: Buffalo lidar_pad | tee: tee stage: Buffalo lidar_pad; Buffalo tee on a lidar pad (no OSM box at 524 yds) |
| 9 | 3 | 198 / 198 | 252 | 0.96 | auto | 100% | 0% | 0% | tee stage: Buffalo tee_centroid |  |
| 10 | 4 | 377 / 377 | 288 | 0.87 | auto | 45% | 30% | 25% | tee stage: Buffalo tee_centroid |  |
| 11 | 3 | 158 / 158 | 291 | 0.93 | auto | 100% | 0% | 0% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 12 | 4 | 477 / 478 | 281 | 0.90 | auto | 68% | 10% | 22% | tee stage: Buffalo tee_centroid |  |
| 13 | 4 | 462 / 462 | 135 | 0.83 | auto | 60% | 6% | 34% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 14 | 5 | 615 / 611 | 105 | 0.81 | auto | 42% | 20% | 39% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 15 | 4 | 366 / 365 | 354 | 0.85 | auto | 44% | 22% | 35% | tee stage: Buffalo tee_centroid |  |
| 16 | 4 | 425 / 423 | 55 | 0.80 | check the flags | 51% | 2% | 47% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 17 | 3 | 165 / 165 | 54 | 0.93 | auto | 100% | 0% | 0% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |
| 18 | 5 | 573 / 568 | 285 | 0.82 | auto | 48% | 19% | 34% | tee stage: Buffalo tee_axis | tee: tee stage: Buffalo tee_axis |

## Stages

- **resolve**: ok: way/399501608 Buffalo Ridge Springs Golf Course (Branson, MO)
- **osm**: ok: 484 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 70 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/buffalo_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/buffalo_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace

## Warnings

- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 3 Silver (L) 315 < Silver 333
