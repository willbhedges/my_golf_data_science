# Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO) - Web tees

Built 2026-10-30T04:13:44Z. OSM way/393079215. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Web)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Web**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 64 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.464 |
| mean_confidence | 0.833 |
| osm_score | 0.879 |

OSM features inside the course: buildings 60, golf=bunker 53, golf=cartpath 42, golf=clubhouse 4, golf=fairway 24, golf=green 20, golf=hole 18, golf=lateral_water_hazard 1, golf=rough 36, golf=tee 64, golf=water_hazard 8, holes_with_handicap 18, holes_with_par 18, single_trees 1, water_polygons 9

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 430 / 429 | 204 | 0.81 | auto | 45% | 16% | 39% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 2 | 4 | 386 / 385 | 163 | 0.81 | auto | 43% | 20% | 37% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 3 | 3 | 206 / 206 | 24 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 4 | 4 | 432 / 427 | 11 | 0.79 | check the flags | 48% | 1% | 50% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 446 / 445 | 339 | 0.85 | auto | 41% | 24% | 35% | tee stage: Web tee_centroid |  |
| 6 | 4 | 344 / 339 | 279 | 0.85 | auto | 37% | 47% | 16% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 7 | 3 | 152 / 145 | 328 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 8 | 4 | 416 / 415 | 106 | 0.82 | auto | 47% | 18% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 9 | 5 | 514 / 513 | 147 | 0.74 | check the flags | 40% | 26% | 35% | tee stage: Web lidar_pad | tee: tee stage: Web lidar_pad; Web tee on a lidar pad (no OSM box at 514 yds) |
| 10 | 4 | 423 / 424 | 65 | 0.74 | check the flags | 47% | 17% | 36% | tee stage: Web lidar_pad | tee: tee stage: Web lidar_pad; Web tee on a lidar pad (no OSM box at 423 yds) |
| 11 | 3 | 202 / 202 | 129 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 12 | 4 | 408 / 402 | 45 | 0.79 | check the flags | 43% | 8% | 49% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 13 | 4 | 437 / 431 | 273 | 0.82 | auto | 56% | 4% | 40% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 14 | 5 | 559 / 560 | 256 | 0.88 | auto | 78% | 4% | 18% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 15 | 4 | 273 / 272 | 184 | 0.70 | check the flags | 14% | 4% | 82% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 16 | 3 | 206 / 206 | 221 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 4 | 376 / 376 | 47 | 0.83 | auto | 54% | 12% | 33% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 18 | 5 | 516 / 515 | 329 | 0.83 | auto | 58% | 7% | 35% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |

## Stages

- **resolve**: ok: way/393079215 Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO)
- **osm**: ok: 562 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 1 sets; lidar pads: 81 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/old_kinderhook/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2016)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2016
- **elevation**: ok: course_data/packages/old_kinderhook/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 21 polygons (outside 21); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Web
