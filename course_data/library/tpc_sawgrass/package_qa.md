# TPC Sawgrass (Ponte Vedra Beach, FL) - Web tees

Built 2026-11-03T06:47:33Z. OSM relation/1783123. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Tpc, Web, Blue, B-W Blended, White, W-G Blended, Green)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Tpc, Web, Blue, B-W Blended, White, W-G Blended, Green**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 116 |
| tees_with_colour | 2 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.443 |
| mean_confidence | 0.841 |
| osm_score | 0.889 |

OSM features inside the course: buildings 4, golf=bunker 154, golf=cartpath 104, golf=driving_range 2, golf=fairway 49, golf=green 59, golf=hole 18, golf=lateral_water_hazard 13, golf=pin 36, golf=rough 19, golf=tee 116, golf=water_hazard 19, holes_with_handicap 18, holes_with_par 18, long_grass_polygons 1, single_trees 1, tees_with_colour 2, tees_with_ref 18, tree_rows 2, trees_polygons 1, water_polygons 35

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 558 / 553 | 324 | 0.82 | auto | 51% | 16% | 33% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 2 | 3 | 171 / 170 | 177 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 3 | 4 | 354 / 354 | 232 | 0.83 | auto | 26% | 37% | 38% | tee stage: Web tee_centroid |  |
| 4 | 4 | 403 / 397 | 160 | 0.76 | check the flags | 33% | 8% | 59% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 5 | 3 | 158 / 158 | 341 | 0.86 | auto | 100% | 0% | 0% | tee stage: Web lidar_pad | tee: tee stage: Web lidar_pad; Web tee on a lidar pad (no OSM box at 158 yds) |
| 6 | 4 | 445 / 444 | 204 | 0.84 | auto | 67% | 3% | 30% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 7 | 4 | 326 / 325 | 16 | 0.81 | auto | 38% | 29% | 33% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 8 | 5 | 503 / 501 | 192 | 0.87 | auto | 33% | 44% | 23% | tee stage: Web tee_centroid |  |
| 9 | 4 | 436 / 436 | 98 | 0.87 | auto | 62% | 4% | 34% | tee stage: Web tee_centroid |  |
| 10 | 4 | 408 / 408 | 62 | 0.83 | auto | 38% | 37% | 25% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 11 | 3 | 229 / 229 | 78 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 12 | 4 | 363 / 362 | 4 | 0.83 | auto | 35% | 40% | 25% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 13 | 4 | 409 / 409 | 51 | 0.84 | auto | 66% | 4% | 30% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 14 | 3 | 203 / 185 | 294 | 0.86 | auto | 100% | 0% | 0% | tee stage: Web lidar_pad | tee: tee stage: Web lidar_pad; Web tee on a lidar pad (no OSM box at 203 yds) |
| 15 | 4 | 402 / 401 | 315 | 0.76 | check the flags | 40% | 32% | 28% | tee stage: Web lidar_pad | tee: tee stage: Web lidar_pad; Web tee on a lidar pad (no OSM box at 402 yds) |
| 16 | 5 | 559 / 557 | 207 | 0.81 | auto | 40% | 22% | 38% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 5 | 499 / 498 | 163 | 0.80 | auto | 40% | 20% | 40% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 18 | 4 | 421 / 420 | 340 | 0.85 | auto | 53% | 29% | 19% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |

## Stages

- **resolve**: ok: relation/1783123 TPC Sawgrass (Ponte Vedra Beach, FL)
- **osm**: ok: 1484 features
- **renumber**: ok: OSM hole refs -> card holes 1->12, 2->8, 3->14, 5->9, 6->3, 7->13, 8->11, 9->1, 11->16, 12->7, 13->2, 14->6, 16->17, 17->5
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 99 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/tpc_sawgrass/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/tpc_sawgrass/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole way names: stadium 18, valley 18); kept 'stadium' (named in the request), 18 ways; ignored 18
- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Tpc, Web, Blue, B-W Blended, White, W-G Blended, Green
- OSM hole numbering differs from the card: OSM hole refs -> card holes 1->12, 2->8, 3->14, 5->9, 6->3, 7->13, 8->11, 9->1, 11->16, 12->7, 13->2, 14->6, 16->17, 17->5 (CHECK)
- hole 14: measured 185 vs card 203 yds for Web (no OSM tee box at that yardage?)
