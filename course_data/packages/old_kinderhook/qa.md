# Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO) - Championship tees

Built 2026-11-03T06:52:34Z. OSM way/393079215. Scorecard: request (request file yardages). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 66 |
| tees_with_colour | 2 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.486 |
| mean_confidence | 0.83 |
| osm_score | 0.869 |

OSM features inside the course: buildings 60, golf=bunker 53, golf=cartpath 42, golf=clubhouse 4, golf=fairway 24, golf=green 20, golf=hole 18, golf=lateral_water_hazard 1, golf=rough 36, golf=tee 66, golf=water_hazard 8, holes_with_handicap 18, holes_with_par 18, single_trees 1, tees_with_colour 2, tees_with_ref 2, water_polygons 9

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 430 / 429 | 204 | 0.81 | auto | 45% | 16% | 39% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 2 | 4 | 386 / 385 | 163 | 0.81 | auto | 43% | 20% | 37% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 3 | 3 | 206 / 206 | 24 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 4 | 4 | 432 / 427 | 11 | 0.79 | check the flags | 48% | 1% | 51% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 446 / 445 | 339 | 0.85 | auto | 41% | 24% | 35% | tee stage: Championship tee_centroid |  |
| 6 | 4 | 344 / 340 | 279 | 0.85 | auto | 38% | 47% | 15% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 7 | 3 | 152 / 147 | 328 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 8 | 4 | 416 / 415 | 106 | 0.82 | auto | 47% | 18% | 36% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 9 | 5 | 514 / 506 | 140 | 0.68 | check the flags | 38% | 33% | 30% | tee stage: Championship review (inside OSM tee 822641041) | tee: tee stage: Championship review (inside OSM tee 822641041) |
| 10 | 4 | 423 / 421 | 64 | 0.82 | auto | 48% | 17% | 35% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 11 | 3 | 202 / 202 | 129 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 12 | 4 | 408 / 403 | 45 | 0.79 | check the flags | 44% | 8% | 48% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 13 | 4 | 437 / 433 | 273 | 0.81 | auto | 56% | 5% | 40% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 14 | 5 | 559 / 560 | 256 | 0.88 | auto | 78% | 4% | 18% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 15 | 4 | 402 / 405 | 186 | 0.64 | check the flags | 45% | 0% | 55% | tee stage: Championship review (inside OSM tee -2) | tee: tee stage: Championship review (inside OSM tee -2); no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 3 | 206 / 206 | 221 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 17 | 4 | 376 / 376 | 47 | 0.83 | auto | 54% | 12% | 33% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 18 | 5 | 516 / 515 | 329 | 0.83 | auto | 58% | 7% | 35% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |

## Stages

- **resolve**: ok: way/393079215 Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO)
- **osm**: ok: 564 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: request (request file yardages)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Championship 9 review (inside OSM tee 822641041), 15 review (inside OSM tee -2);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 1 sets; lidar pads: 81 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/old_kinderhook/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2016)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2016
- **elevation**: ok: course_data/packages/old_kinderhook/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -1325 m2 {'road': 593, 'cells': 683}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 22 polygons (outside 22); mode replace
