# Mozingo Lake Golf Course (Maryville, MO) - App tees

Built 2026-10-17T04:27:58Z. OSM way/385067034. Scorecard: request (request file yardages). Tee set: name.

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
| mean_landing_osm_share | 0.458 |
| mean_confidence | 0.859 |
| osm_score | 0.892 |

OSM features inside the course: buildings 4, golf=bunker 25, golf=cartpath 23, golf=driving_range 1, golf=fairway 20, golf=green 25, golf=hole 18, golf=rough 22, golf=tee 66, golf=water_hazard 3, holes_with_handicap 16, holes_with_par 18, single_trees 12, tees_with_ref 12, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 371 / 362 | 183 | 0.80 | auto | 35% | 33% | 32% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 2 | 4 | 349 / 350 | 59 | 0.88 | auto | 46% | 36% | 18% | tee stage: App tee_centroid |  |
| 3 | 5 | 517 / 520 | 230 | 0.87 | auto | 49% | 28% | 23% | tee stage: App tee_centroid |  |
| 4 | 4 | 361 / 362 | 79 | 0.81 | auto | 44% | 26% | 30% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 5 | 3 | 182 / 180 | 210 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 6 | 5 | 491 / 492 | 266 | 0.83 | auto | 50% | 25% | 25% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 7 | 4 | 428 / 428 | 36 | 0.82 | auto | 56% | 14% | 30% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 8 | 3 | 187 / 187 | 26 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 9 | 4 | 348 / 346 | 18 | 0.86 | auto | 41% | 34% | 24% | tee stage: App tee_centroid |  |
| 10 | 4 | 392 / 391 | 10 | 0.83 | auto | 47% | 30% | 23% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 11 | 3 | 219 / 220 | 343 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 12 | 5 | 517 / 518 | 265 | 0.81 | auto | 45% | 23% | 32% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 13 | 4 | 394 / 394 | 177 | 0.78 | check the flags | 42% | 11% | 47% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 14 | 5 | 464 / 464 | 187 | 0.83 | auto | 50% | 8% | 42% | tee stage: App tee_centroid |  |
| 15 | 3 | 174 / 176 | 80 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 16 | 4 | 433 / 432 | 13 | 0.84 | auto | 50% | 30% | 19% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 17 | 4 | 344 / 355 | 49 | 0.83 | auto | 31% | 53% | 16% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 18 | 4 | 407 / 407 | 203 | 0.83 | auto | 54% | 21% | 25% | tee stage: App tee_axis | tee: tee stage: App tee_axis |

## Stages

- **resolve**: ok: way/385067034 Mozingo Lake Golf Course (Maryville, MO)
- **osm**: ok: 475 features
- **scorecard**: ok: request (request file yardages)
- **tees**: ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for 1 sets; lidar pads: 41 candidate pads near hole starts, 0 placement(s) on one
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/mozingo_lake/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **elevation**: ok: course_data/packages/mozingo_lake/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: ok: segment gap-fill ariadgolf-v4@43ee2944 (+1 zones on 1 holes, +0 greens, 32 tee candidates)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace
