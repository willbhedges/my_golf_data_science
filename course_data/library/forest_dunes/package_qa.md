# Forest Dunes Course (South Branch Township, MI) - osm_back tees

Built 2026-11-01T22:16:54Z. OSM way/1536953640. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 77 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.469 |
| mean_confidence | 0.689 |
| osm_score | 0.865 |

OSM features inside the course: buildings 2, golf=bunker 126, golf=cartpath 23, golf=fairway 20, golf=green 19, golf=hole 18, golf=lateral_water_hazard 2, golf=rough 37, golf=tee 77, golf=water_hazard 1, holes_with_handicap 1, holes_with_par 18, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 400 / 400 | 135 | 0.65 | check the flags | 43% | 22% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 4 | 450 / 450 | 204 | 0.67 | check the flags | 39% | 34% | 27% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 197 / 197 | 42 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 405 / 405 | 72 | 0.65 | check the flags | 35% | 32% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 5 | 606 / 606 | 124 | 0.65 | check the flags | 48% | 13% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 366 / 366 | 306 | 0.67 | check the flags | 46% | 24% | 30% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 5 | 536 / 536 | 335 | 0.70 | check the flags | 39% | 51% | 10% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 436 / 436 | 279 | 0.69 | check the flags | 42% | 40% | 18% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 3 | 204 / 204 | 310 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 434 / 434 | 92 | 0.67 | check the flags | 64% | 0% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 186 / 186 | 159 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 395 / 395 | 127 | 0.70 | check the flags | 44% | 41% | 14% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 374 / 374 | 29 | 0.69 | check the flags | 54% | 28% | 19% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 466 / 466 | 2 | 0.65 | check the flags | 53% | 4% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 5 | 559 / 559 | 210 | 0.66 | check the flags | 48% | 20% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 228 / 228 | 234 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 309 / 309 | 303 | 0.62 | check the flags | 47% | 0% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 532 / 532 | 269 | 0.65 | check the flags | 55% | 2% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/1536953640 Forest Dunes Course (South Branch Township, MI)
- **osm**: ok: 449 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/forest_dunes/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/forest_dunes/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 3 polygons (outside 3); mode replace

## Warnings

- ignored 10 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1528336302, 1528336303, 1528336304, 1528336305, 1528336306, 1528336307, 1528336308, 1528336309
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
