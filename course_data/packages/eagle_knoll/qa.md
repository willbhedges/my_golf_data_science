# Eagle Knoll Golf Club (Hartsburg, MO) - Back tees

Built 2026-10-17T18:14:40Z. OSM way/389825776. Scorecard: golfify (golfify). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 65 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.426 |
| mean_confidence | 0.845 |
| osm_score | 0.857 |

OSM features inside the course: buildings 1, golf=bunker 41, golf=cartpath 14, golf=fairway 19, golf=green 19, golf=hole 17, golf=tee 65, golf=water_hazard 3, holes_with_handicap 17, holes_with_par 17, single_trees 3, trees_polygons 4, water_lines 4, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 366 / 361 | 191 | 0.84 | auto | 58% | 13% | 29% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 2 | 3 | 151 / 150 | 288 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 3 | 4 | 397 / 398 | 243 | 0.85 | auto | 49% | 13% | 38% | tee stage: Back tee_centroid |  |
| 4 | 4 | 399 / 405 | 16 | 0.77 | check the flags | 37% | 6% | 57% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 5 | 4 | 465 / 466 | 282 | 0.85 | auto | 39% | 26% | 35% | tee stage: Back tee_centroid |  |
| 6 | 3 | 138 / 138 | 48 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 7 | 5 | 475 / 476 | 121 | 0.81 | auto | 40% | 24% | 35% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 8 | 4 | 407 / 406 | 169 | 0.74 | check the flags | 32% | 0% | 67% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 9 | 5 | 510 / 508 | 33 | 0.75 | check the flags | 31% | 8% | 62% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 10 | 4 | 405 / 405 | 322 | 0.89 | auto | 39% | 47% | 14% | tee stage: Back tee_centroid |  |
| 11 | 4 | 441 / 440 | 154 | 0.75 | check the flags | 31% | 7% | 62% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 12 | 3 | 180 / 180 | 350 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 13 | 5 | 546 / 546 | 287 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 265 / 261 | 85 | 0.78 | check the flags | 19% | 40% | 42% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 15 | 4 | 447 / 445 | 330 | 0.90 | auto | 80% | 13% | 7% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 16 | 3 | 158 / 158 | 75 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 17 | 5 | 489 / 489 | 130 | 0.86 | auto | 57% | 23% | 19% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 18 | 4 | 428 / 428 | 143 | 0.81 | auto | 35% | 30% | 34% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |

## Stages

- **resolve**: ok: way/389825776 Eagle Knoll Golf Club (Hartsburg, MO)
- **osm**: ok: 229 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 45 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/eagle_knoll/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/eagle_knoll/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 2 polygons (outside 2); mode replace
