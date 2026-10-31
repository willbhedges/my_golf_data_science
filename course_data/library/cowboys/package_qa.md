# Cowboys Golf Club and Grapevine Golf Course (Grapevine, TX) - Web tees

Built 2026-10-31T04:00:23Z. OSM relation/17453587. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Web)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Web**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 161 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.418 |
| mean_confidence | 0.83 |
| osm_score | 0.884 |

OSM features inside the course: buildings 19, built_up_landuse 1, golf=bunker 100, golf=cartpath 37, golf=fairway 48, golf=green 51, golf=hole 18, golf=pin 18, golf=rough 3, golf=tee 161, golf=water_hazard 13, holes_with_par 18, water_lines 8, water_polygons 20

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 533 / 520 | 29 | 0.80 | check the flags | 48% | 8% | 44% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 2 | 4 | 376 / 381 | 23 | 0.81 | auto | 36% | 28% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 3 | 3 | 152 / 147 | 67 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 4 | 4 | 366 / 360 | 353 | 0.85 | auto | 51% | 30% | 19% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 5 | 4 | 479 / 484 | 304 | 0.72 | check the flags | 39% | 15% | 46% | tee stage: Web lidar_pad | tee: tee stage: Web lidar_pad; Web tee on a lidar pad (no OSM box at 479 yds) |
| 6 | 3 | 165 / 165 | 30 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 7 | 4 | 468 / 469 | 77 | 0.82 | auto | 38% | 31% | 31% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 8 | 5 | 520 / 514 | 280 | 0.81 | auto | 38% | 26% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 9 | 4 | 441 / 441 | 53 | 0.71 | check the flags | 47% | 15% | 38% | tee stage: Web walkback | tee: tee stage: Web walkback; Web tee walked back along the hole line (no box at 441 yds) |
| 10 | 4 | 361 / 361 | 56 | 0.82 | auto | 34% | 21% | 45% | tee stage: Web tee_centroid |  |
| 11 | 4 | 439 / 431 | 207 | 0.81 | auto | 42% | 23% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 12 | 4 | 441 / 439 | 19 | 0.80 | check the flags | 40% | 18% | 42% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 13 | 5 | 600 / 590 | 193 | 0.84 | auto | 45% | 30% | 25% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 14 | 4 | 333 / 331 | 186 | 0.80 | check the flags | 34% | 24% | 42% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 15 | 3 | 158 / 158 | 279 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 16 | 4 | 455 / 449 | 194 | 0.81 | auto | 46% | 18% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 3 | 194 / 194 | 237 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 18 | 5 | 519 / 506 | 175 | 0.80 | auto | 49% | 8% | 43% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |

## Stages

- **resolve**: ok: relation/17453587 Cowboys Golf Club and Grapevine Golf Course (Grapevine, TX)
- **osm**: ok: 1438 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 1 sets; lidar pads: 94 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/cowboys/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/cowboys/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 8 polygons (outside 8); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Web
