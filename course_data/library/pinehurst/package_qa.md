# Pinehurst No. 2 (Pinehurst, NC) - osm_back tees

Built 2026-11-01T22:22:04Z. OSM way/1358696570. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 3 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.614 |
| mean_confidence | 0.666 |
| osm_score | 0.831 |

OSM features inside the course: buildings 7, golf=bunker 126, golf=cartpath 67, golf=fairway 34, golf=green 24, golf=hole 18, golf=tee 3, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, trees_polygons 11, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 401 / 401 | 45 | 0.62 | check the flags | 56% | 2% | 42% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 2 | 4 | 476 / 476 | 27 | 0.64 | check the flags | 64% | 3% | 33% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 3 | 4 | 387 / 387 | 69 | 0.64 | check the flags | 61% | 8% | 31% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 4 | 4 | 544 / 544 | 74 | 0.67 | check the flags | 62% | 2% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 5 | 583 / 583 | 258 | 0.63 | check the flags | 56% | 10% | 34% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 6 | 3 | 205 / 205 | 260 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 393 / 393 | 196 | 0.62 | check the flags | 60% | 0% | 40% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 8 | 5 | 486 / 486 | 124 | 0.62 | check the flags | 55% | 6% | 38% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 9 | 3 | 161 / 161 | 11 | 0.73 | check the flags | 100% | 0% | 0% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 10 | 5 | 693 / 693 | 186 | 0.70 | check the flags | 67% | 10% | 22% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 380 / 380 | 236 | 0.63 | check the flags | 64% | 0% | 36% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 12 | 4 | 517 / 517 | 41 | 0.63 | check the flags | 50% | 0% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 379 / 379 | 277 | 0.60 | check the flags | 54% | 0% | 46% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 14 | 4 | 530 / 530 | 87 | 0.69 | check the flags | 72% | 0% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 3 | 211 / 211 | 322 | 0.73 | check the flags | 100% | 0% | 0% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 16 | 5 | 533 / 533 | 353 | 0.68 | check the flags | 79% | 0% | 21% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 17 | 3 | 205 / 205 | 157 | 0.73 | check the flags | 100% | 0% | 0% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 18 | 4 | 445 / 445 | 243 | 0.62 | check the flags | 60% | 0% | 40% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |

## Stages

- **resolve**: ok: way/1358696570 Pinehurst No. 2 (Pinehurst, NC)
- **osm**: ok: 1113 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/pinehurst/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/pinehurst/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 17 polygons (outside 17); mode replace

## Warnings

- hole refs: kept the '2' holes (named in the request) (18 ways, refs as plain numbers)
- ignored 39 golf=hole way(s) of another course / practice area by ref: 1 - #1, 1 - #4, 1 - #5, 1 - TC, 10 - #4, 11 - #4, 12 - #4, 13, 13 - #4, 14 - #4, 15, 15 - #4 ...
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
