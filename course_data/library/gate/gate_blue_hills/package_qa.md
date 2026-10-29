# Blue Hills Country Club (Kansas City, MO) - Black tees

Built 2026-10-29T20:41:32Z. OSM way/315837565. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 60 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.288 |
| mean_confidence | 0.818 |
| osm_score | 0.844 |

OSM features inside the course: buildings 6, built_up_landuse 1, golf=bunker 59, golf=fairway 22, golf=green 18, golf=hole 17, golf=pin 18, golf=tee 60, golf=water_hazard 1, holes_with_par 17, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 523 / 522 | 359 | 0.83 | auto | 38% | 37% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 419 / 420 | 103 | 0.72 | check the flags | 26% | 35% | 39% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 419 yds) |
| 3 | 4 | 405 / 406 | 266 | 0.81 | auto | 28% | 21% | 51% | tee stage: Black tee_centroid |  |
| 4 | 4 | 446 / 447 | 122 | 0.81 | auto | 24% | 46% | 29% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 197 / 194 | 79 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 567 / 564 | 259 | 0.76 | check the flags | 26% | 18% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 417 / 418 | 103 | 0.79 | check the flags | 34% | 23% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 223 / 223 | 196 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 441 / 442 | 305 | 0.80 | auto | 32% | 33% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 397 / 393 | 152 | 0.80 | check the flags | 29% | 34% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 384 / 383 | 128 | 0.76 | check the flags | 19% | 27% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 188 / 188 | 192 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 5 | 560 / 559 | 303 | 0.78 | check the flags | 30% | 22% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 188 / 188 | 51 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 460 / 460 | 123 | 0.79 | check the flags | 31% | 28% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 456 / 457 | 302 | 0.78 | check the flags | 29% | 23% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 449 / 450 | 186 | 0.79 | check the flags | 31% | 27% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 627 / 626 | 23 | 0.79 | check the flags | 26% | 31% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/315837565 Blue Hills Country Club (Kansas City, MO)
- **osm**: ok: 656 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 9 sets; lidar pads: 52 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 9 tee set(s))
- **imagery**: ok: course_data/packages/gate_blue_hills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/gate_blue_hills/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 22 polygons (outside 22); mode replace
