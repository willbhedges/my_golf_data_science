# Pine Dunes Resort & Golf Club (Frankston, TX) - Gold tees

Built 2026-10-17T19:14:29Z. OSM none/0. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 45 |
| tees_with_colour | 18 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.398 |
| mean_confidence | 0.915 |
| osm_score | 0.88 |

OSM features inside the course: buildings 4, golf=bunker 87, golf=cartpath 15, golf=clubhouse 1, golf=driving_range 2, golf=fairway 22, golf=green 21, golf=hole 18, golf=lateral_water_hazard 1, golf=rough 1, golf=tee 45, golf=water_hazard 5, holes_with_par 18, single_trees 4, tees_with_colour 18, water_lines 1, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 391 / 386 | 250 | 0.89 | auto | 29% | 46% | 25% | tee stage: Gold tagged |  |
| 2 | 4 | 348 / 341 | 324 | 0.84 | auto | 31% | 16% | 53% | tee stage: Gold tagged |  |
| 3 | 3 | 160 / 154 | 68 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 4 | 4 | 463 / 445 | 142 | 0.88 | auto | 33% | 33% | 34% | tee stage: Gold tagged |  |
| 5 | 5 | 501 / 494 | 11 | 0.92 | auto | 50% | 32% | 18% | tee stage: Gold tagged |  |
| 6 | 3 | 254 / 250 | 16 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 7 | 4 | 443 / 439 | 97 | 0.93 | auto | 63% | 18% | 19% | tee stage: Gold tagged |  |
| 8 | 4 | 389 / 387 | 252 | 0.88 | auto | 28% | 41% | 30% | tee stage: Gold tagged |  |
| 9 | 5 | 551 / 552 | 205 | 0.89 | auto | 35% | 35% | 30% | tee stage: Gold tagged |  |
| 10 | 4 | 439 / 433 | 10 | 0.90 | auto | 41% | 32% | 28% | tee stage: Gold tagged |  |
| 11 | 5 | 605 / 602 | 65 | 0.88 | auto | 47% | 13% | 40% | tee stage: Gold tagged |  |
| 12 | 3 | 204 / 201 | 116 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 13 | 4 | 426 / 425 | 271 | 0.87 | auto | 44% | 12% | 43% | tee stage: Gold tagged |  |
| 14 | 4 | 434 / 430 | 94 | 0.90 | auto | 50% | 21% | 30% | tee stage: Gold tagged |  |
| 15 | 4 | 344 / 335 | 275 | 0.88 | auto | 31% | 34% | 34% | tee stage: Gold tagged |  |
| 16 | 3 | 178 / 176 | 295 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 17 | 4 | 475 / 474 | 152 | 0.90 | auto | 41% | 33% | 26% | tee stage: Gold tagged |  |
| 18 | 5 | 512 / 501 | 208 | 0.91 | auto | 34% | 48% | 18% | tee stage: Gold tagged |  |

## Stages

- **resolve**: ok: none/0 Pine Dunes Resort & Golf Club (Frankston, TX)
- **osm**: ok: 287 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 0 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/pine_dunes/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/pine_dunes/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace

## Warnings

- hole 4: measured 445 vs card 463 yds for Gold (no OSM tee box at that yardage?)
