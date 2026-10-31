# Sharon Woods Golf Course (Sharonville, OH) - Green tees

Built 2026-10-31T04:17:10Z. OSM way/31875338. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Green, Blue, White, Gray, Yellow, Orange, White (L), Gray (L), Yellow (L), Orange (L))).

**WARNING: requested tee set 'Black' is not on the card; using 'Green' instead (allow_substitute). Sets on the card: Green, Blue, White, Gray, Yellow, Orange, White (L), Gray (L), Yellow (L), Orange (L)**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 31 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.354 |
| mean_confidence | 0.78 |
| osm_score | 0.857 |

OSM features inside the course: buildings 10, golf=bunker 30, golf=cartpath 13, golf=fairway 20, golf=green 18, golf=hole 18, golf=tee 31, golf=water_hazard 1, holes_with_par 18, trees_polygons 11, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 371 / 371 | 213 | 0.71 | check the flags | 42% | 10% | 49% | tee stage: Green lidar_pad | tee: tee stage: Green lidar_pad; Green tee on a lidar pad (no OSM box at 371 yds) |
| 2 | 3 | 170 / 169 | 298 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 3 | 4 | 468 / 458 | 117 | 0.78 | check the flags | 31% | 21% | 48% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 4 | 4 | 458 / 459 | 81 | 0.81 | auto | 38% | 26% | 35% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 5 | 4 | 408 / 404 | 258 | 0.80 | auto | 32% | 31% | 37% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 6 | 4 | 293 / 293 | 360 | 0.76 | check the flags | 19% | 27% | 53% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 7 | 4 | 390 / 391 | 235 | 0.79 | check the flags | 34% | 4% | 62% | tee stage: Green tee_centroid |  |
| 8 | 3 | 221 / 222 | 288 | 0.86 | auto | 100% | 0% | 0% | tee stage: Green lidar_pad | tee: tee stage: Green lidar_pad; Green tee on a lidar pad (no OSM box at 221 yds) |
| 9 | 5 | 535 / 541 | 80 | 0.72 | check the flags | 34% | 21% | 45% | tee stage: Green lidar_pad | tee: tee stage: Green lidar_pad; Green tee on a lidar pad (no OSM box at 535 yds) |
| 10 | 4 | 375 / 375 | 32 | 0.78 | check the flags | 72% | 0% | 28% | tee stage: Green lidar_pad | tee: tee stage: Green lidar_pad; Green tee on a lidar pad (no OSM box at 375 yds) |
| 11 | 3 | 232 / 232 | 118 | 0.82 | auto | 100% | 0% | 0% | tee stage: Green walkback | tee: tee stage: Green walkback; Green tee walked back along the hole line (no box at 232 yds) |
| 12 | 4 | 328 / 328 | 170 | 0.72 | check the flags | 52% | 14% | 34% | tee stage: Green walkback | tee: tee stage: Green walkback; Green tee walked back along the hole line (no box at 328 yds) |
| 13 | 3 | 181 / 181 | 188 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 14 | 4 | 405 / 405 | 27 | 0.67 | check the flags | 28% | 22% | 50% | tee stage: Green walkback | tee: tee stage: Green walkback; Green tee walked back along the hole line (no box at 405 yds) |
| 15 | 4 | 434 / 433 | 194 | 0.69 | check the flags | 30% | 30% | 40% | tee stage: Green walkback | tee: tee stage: Green walkback; Green tee walked back along the hole line (no box at 434 yds) |
| 16 | 5 | 532 / 533 | 292 | 0.69 | check the flags | 29% | 14% | 57% | tee stage: Green lidar_pad | tee: tee stage: Green lidar_pad; Green tee on a lidar pad (no OSM box at 532 yds) |
| 17 | 4 | 356 / 357 | 75 | 0.83 | auto | 27% | 36% | 37% | tee stage: Green tee_centroid |  |
| 18 | 4 | 431 / 430 | 290 | 0.75 | check the flags | 26% | 12% | 62% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |

## Stages

- **resolve**: ok: way/31875338 Sharon Woods Golf Course (Sharonville, OH)
- **osm**: ok: 488 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 10 sets; lidar pads: 39 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 10 tee set(s))
- **imagery**: ok: course_data/packages/sharon_woods/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/sharon_woods/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Green' instead (allow_substitute). Sets on the card: Green, Blue, White, Gray, Yellow, Orange, White (L), Gray (L), Yellow (L), Orange (L)
- hole 17 Orange: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 17 Orange (L): CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- scorecard (golfify): 3 hole(s) where a longer set is shorter than the next set: 1 Blue 320 < White 341, 7 Blue 375 < White 405, 14 Blue 360 < White 378
