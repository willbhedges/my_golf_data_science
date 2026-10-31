# TPC Sawgrass (Ponte Vedra Beach, FL) - Web tees

Built 2026-10-30T22:28:18Z. OSM relation/1783123. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Tpc, Web, Blue, B-W Blended, White, W-G Blended, Green)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Tpc, Web, Blue, B-W Blended, White, W-G Blended, Green**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 34 |
| greens_found | 18 |
| tee_boxes | 117 |
| tees_with_colour | 2 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.499 |
| mean_confidence | 0.838 |
| osm_score | 0.843 |

OSM features inside the course: buildings 4, golf=bunker 154, golf=cartpath 103, golf=driving_range 2, golf=fairway 49, golf=green 60, golf=hole 34, golf=lateral_water_hazard 13, golf=pin 36, golf=rough 20, golf=tee 117, golf=water_hazard 19, holes_with_handicap 30, holes_with_par 34, long_grass_polygons 1, single_trees 1, tees_with_colour 2, tees_with_ref 18, tree_rows 2, trees_polygons 1, water_polygons 35

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 558 / 556 | 183 | 0.80 | check the flags | 38% | 20% | 42% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 2 | 3 | 171 / 171 | 107 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 3 | 4 | 354 / 354 | 226 | 0.77 | check the flags | 40% | 5% | 55% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 4 | 4 | 403 / 403 | 126 | 0.78 | check the flags | 43% | 4% | 53% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 5 | 3 | 158 / 157 | 172 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 6 | 4 | 445 / 445 | 286 | 0.90 | auto | 71% | 6% | 23% | tee stage: Web tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 326 / 326 | 327 | 0.77 | check the flags | 29% | 20% | 52% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 8 | 5 | 503 / 501 | 352 | 0.83 | auto | 52% | 15% | 33% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 9 | 4 | 436 / 435 | 350 | 0.84 | auto | 66% | 0% | 34% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 408 / 407 | 8 | 0.89 | auto | 56% | 23% | 21% | tee stage: Web tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 229 / 228 | 188 | 0.82 | auto | 100% | 0% | 0% | tee stage: Web walkback | tee: tee stage: Web walkback; Web tee walked back along the hole line (no box at 229 yds) |
| 12 | 4 | 363 / 363 | 245 | 0.82 | auto | 56% | 6% | 38% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 4 | 409 / 392 | 50 | 0.83 | auto | 55% | 15% | 30% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 14 | 3 | 203 / 202 | 341 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 15 | 4 | 402 / 401 | 337 | 0.79 | check the flags | 37% | 17% | 46% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 16 | 5 | 559 / 557 | 197 | 0.80 | auto | 52% | 4% | 44% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 5 | 499 / 498 | 160 | 0.80 | auto | 51% | 6% | 43% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 18 | 4 | 421 / 420 | 340 | 0.85 | auto | 53% | 29% | 19% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |

## Stages

- **resolve**: ok: relation/1783123 TPC Sawgrass (Ponte Vedra Beach, FL)
- **osm**: ok: 1484 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 0 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/tpc_sawgrass/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/tpc_sawgrass/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 57 polygons (outside 57); mode replace

## Warnings

- ignored 2 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1455229994, 1455229999
- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Tpc, Web, Blue, B-W Blended, White, W-G Blended, Green
- hole 11 Tpc: CHECK, walk-back moved the back tee 350 yds up the hole line to fit the card: kept at the line start (card hole may not be this OSM hole)
- hole 11 Web: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 11 Blue: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 11 B-W Blended: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 11 White: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 11 W-G Blended: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 11 Green: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 13: measured 392 vs card 409 yds for Web (no OSM tee box at that yardage?)
