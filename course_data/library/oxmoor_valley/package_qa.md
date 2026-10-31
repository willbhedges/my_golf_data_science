# RTJ Oxmoor Valley Golf (Birmingham, AL) - osm_back tees

Built 2026-10-30T22:16:41Z. OSM way/424825094. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 36 |
| greens_found | 18 |
| tee_boxes | 187 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.58 |
| mean_confidence | 0.689 |
| osm_score | 0.916 |

OSM features inside the course: buildings 7, golf=bunker 96, golf=clubhouse 1, golf=fairway 34, golf=green 36, golf=hole 36, golf=lateral_water_hazard 2, golf=tee 187, golf=water_hazard 7, holes_with_handicap 18, holes_with_par 36, single_trees 181, tees_with_ref 103, trees_polygons 18, water_lines 6, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 434 / 434 | 148 | 0.66 | check the flags | 52% | 10% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 534 / 534 | 132 | 0.68 | check the flags | 66% | 0% | 34% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 5 | 544 / 544 | 55 | 0.68 | check the flags | 64% | 4% | 31% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 388 / 388 | 355 | 0.67 | check the flags | 63% | 0% | 37% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 3 | 179 / 179 | 286 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 445 / 445 | 210 | 0.69 | check the flags | 68% | 5% | 27% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 373 / 373 | 348 | 0.68 | check the flags | 66% | 2% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 176 / 176 | 345 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 419 / 419 | 286 | 0.66 | check the flags | 55% | 9% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 442 / 442 | 183 | 0.62 | check the flags | 43% | 6% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 419 / 419 | 63 | 0.67 | check the flags | 58% | 7% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 5 | 483 / 483 | 175 | 0.70 | check the flags | 67% | 12% | 21% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 3 | 189 / 189 | 43 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 388 / 388 | 352 | 0.68 | check the flags | 57% | 14% | 29% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 406 / 406 | 268 | 0.61 | check the flags | 34% | 14% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 201 / 201 | 229 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 442 / 442 | 7 | 0.67 | check the flags | 59% | 6% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 5 | 591 / 591 | 33 | 0.66 | check the flags | 59% | 3% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/424825094 RTJ Oxmoor Valley Golf (Birmingham, AL)
- **osm**: ok: 989 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/oxmoor_valley/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/oxmoor_valley/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 2 polygons (outside 2); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
