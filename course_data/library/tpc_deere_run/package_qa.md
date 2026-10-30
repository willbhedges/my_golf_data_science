# TPC Deere Run (Silvis, IL) - osm_back tees

Built 2026-10-30T12:23:41Z. OSM relation/12585470. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 65 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.518 |
| mean_confidence | 0.678 |
| osm_score | 0.904 |

OSM features inside the course: buildings 14, built_up_landuse 1, golf=bunker 79, golf=cartpath 25, golf=clubhouse 1, golf=driving_range 2, golf=fairway 25, golf=green 29, golf=hole 18, golf=rough 4, golf=tee 65, golf=water_hazard 3, holes_with_par 18, single_trees 765, trees_polygons 12, water_lines 4, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 356 / 356 | 213 | 0.63 | check the flags | 42% | 11% | 47% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 549 / 549 | 214 | 0.64 | check the flags | 54% | 2% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 158 / 158 | 339 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 440 / 440 | 130 | 0.70 | check the flags | 71% | 8% | 21% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 415 / 415 | 353 | 0.60 | check the flags | 35% | 7% | 58% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 361 / 361 | 309 | 0.69 | check the flags | 63% | 12% | 25% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 3 | 177 / 177 | 178 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 317 / 317 | 8 | 0.59 | needs review | 37% | 0% | 63% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 350 / 350 | 137 | 0.68 | check the flags | 58% | 14% | 27% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 5 | 465 / 465 | 325 | 0.69 | check the flags | 65% | 6% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 317 / 317 | 102 | 0.66 | check the flags | 56% | 5% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 3 | 131 / 131 | 132 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 326 / 326 | 309 | 0.62 | check the flags | 36% | 15% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 273 / 273 | 136 | 0.62 | check the flags | 46% | 2% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 370 / 370 | 186 | 0.67 | check the flags | 56% | 11% | 33% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 121 / 121 | 219 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 5 | 427 / 427 | 19 | 0.66 | check the flags | 55% | 10% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 324 / 324 | 194 | 0.66 | check the flags | 50% | 13% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: relation/12585470 TPC Deere Run (Silvis, IL)
- **osm**: ok: 1320 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/tpc_deere_run/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/tpc_deere_run/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
