# Paa-Ko Ridge Golf Club (Sandia Park, NM) - osm_back tees

Built 2026-10-31T02:02:44Z. OSM relation/3585731. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 24 |
| greens_found | 18 |
| tee_boxes | 132 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.439 |
| mean_confidence | 0.674 |
| osm_score | 0.888 |

OSM features inside the course: buildings 3, golf=bunker 119, golf=cartpath 27, golf=clubhouse 1, golf=fairway 34, golf=green 28, golf=hole 24, golf=pin 27, golf=rough 85, golf=tee 132, golf=water_hazard 4, holes_with_handicap 1, holes_with_par 24, tees_with_colour 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 428 / 428 | 266 | 0.61 | check the flags | 38% | 9% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 4 | 397 / 397 | 264 | 0.60 | check the flags | 30% | 14% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 5 | 603 / 603 | 250 | 0.65 | check the flags | 52% | 6% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 3 | 186 / 186 | 306 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 5 | 539 / 539 | 32 | 0.64 | check the flags | 32% | 28% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 326 / 326 | 36 | 0.63 | check the flags | 38% | 14% | 47% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 492 / 492 | 157 | 0.66 | check the flags | 47% | 18% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 271 / 271 | 108 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 474 / 474 | 74 | 0.62 | check the flags | 43% | 5% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 5 | 566 / 566 | 23 | 0.65 | check the flags | 41% | 23% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 459 / 459 | 246 | 0.64 | check the flags | 50% | 7% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 442 / 442 | 336 | 0.64 | check the flags | 50% | 5% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 3 | 221 / 221 | 268 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 5 | 615 / 615 | 275 | 0.63 | check the flags | 50% | 0% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 3 | 198 / 198 | 77 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 5 | 562 / 562 | 108 | 0.66 | check the flags | 57% | 6% | 37% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 253 / 253 | 110 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 501 / 501 | 103 | 0.65 | check the flags | 43% | 19% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: relation/3585731 Paa-Ko Ridge Golf Club (Sandia Park, NM)
- **osm**: ok: 620 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/paa_ko_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/paa_ko_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 17 polygons (outside 17); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
