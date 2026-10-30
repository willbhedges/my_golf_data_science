# St Andrews Golf Club (Overland Park, KS) - Black tees

Built 2026-10-30T03:26:24Z. OSM way/68744841. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 55 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.318 |
| mean_confidence | 0.828 |
| osm_score | 0.864 |

OSM features inside the course: buildings 4, golf=bunker 18, golf=cartpath 20, golf=driving_range 2, golf=fairway 16, golf=green 32, golf=hole 18, golf=pin 18, golf=tee 55, golf=water_hazard 2, holes_with_handicap 18, holes_with_par 18, single_trees 5, water_lines 4, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 560 / 559 | 183 | 0.79 | check the flags | 43% | 12% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 354 / 354 | 346 | 0.82 | auto | 40% | 12% | 48% | tee stage: Black tee_centroid |  |
| 3 | 4 | 343 / 343 | 157 | 0.84 | auto | 26% | 58% | 15% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 161 / 161 | 40 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 330 / 330 | 213 | 0.73 | check the flags | 16% | 19% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 3 | 178 / 179 | 285 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 5 | 524 / 523 | 5 | 0.84 | auto | 32% | 35% | 33% | tee stage: Black tee_centroid |  |
| 8 | 4 | 384 / 385 | 117 | 0.78 | check the flags | 33% | 19% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 386 / 378 | 330 | 0.78 | check the flags | 29% | 22% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 5 | 577 / 577 | 126 | 0.72 | check the flags | 31% | 25% | 44% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 577 yds) |
| 11 | 4 | 384 / 384 | 261 | 0.82 | auto | 38% | 32% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 168 / 168 | 94 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 328 / 328 | 178 | 0.83 | auto | 26% | 53% | 20% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 178 / 178 | 342 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 15 | 5 | 498 / 498 | 71 | 0.83 | auto | 37% | 40% | 24% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 419 / 419 | 330 | 0.64 | check the flags | 32% | 3% | 65% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 419 yds) |
| 17 | 3 | 193 / 193 | 117 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 397 / 398 | 279 | 0.78 | check the flags | 30% | 25% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/68744841 St Andrews Golf Club (Overland Park, KS)
- **osm**: ok: 767 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 74 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/st_andrews_op/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/st_andrews_op/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace
