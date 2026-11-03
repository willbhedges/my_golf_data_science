# Tournament Players Club of Louisiana (Waggaman, LA) - osm_back tees

Built 2026-11-02T23:44:26Z. OSM relation/4260277. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 62 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.463 |
| mean_confidence | 0.677 |
| osm_score | 0.893 |

OSM features inside the course: buildings 7, golf=bunker 97, golf=cartpath 7, golf=clubhouse 1, golf=fairway 20, golf=green 22, golf=hole 18, golf=pin 17, golf=tee 62, golf=water_hazard 5, holes_with_par 18, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 395 | 215 | 0.63 | check the flags | 30% | 28% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 547 / 547 | 230 | 0.65 | check the flags | 37% | 30% | 34% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 176 / 176 | 212 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 466 / 466 | 270 | 0.69 | check the flags | 66% | 9% | 25% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 425 / 425 | 26 | 0.64 | check the flags | 39% | 18% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 498 / 498 | 174 | 0.69 | check the flags | 66% | 5% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 5 | 552 / 552 | 32 | 0.62 | check the flags | 42% | 8% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 370 / 370 | 30 | 0.65 | check the flags | 41% | 20% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 3 | 232 / 232 | 57 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 391 / 391 | 285 | 0.63 | check the flags | 32% | 24% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 5 | 572 / 572 | 206 | 0.63 | check the flags | 39% | 15% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 485 / 485 | 179 | 0.66 | check the flags | 42% | 25% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 398 / 398 | 23 | 0.68 | check the flags | 66% | 0% | 34% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 213 / 213 | 351 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 491 / 491 | 18 | 0.59 | needs review | 31% | 8% | 61% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 4 | 432 / 432 | 182 | 0.67 | check the flags | 47% | 22% | 31% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 209 / 209 | 140 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 5 | 558 / 558 | 18 | 0.69 | check the flags | 70% | 2% | 29% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: relation/4260277 Tournament Players Club of Louisiana (Waggaman, LA)
- **osm**: ok: 315 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/tpc_louisiana/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/tpc_louisiana/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -24 m2 {'cells': 24}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 2 polygons (outside 2); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
