# RTJ Grand National Golf (Opelika, AL) - osm_back tees

Built 2026-11-03T06:20:00Z. OSM way/328838760. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 150 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.416 |
| mean_confidence | 0.681 |
| osm_score | 0.883 |

OSM features inside the course: buildings 6, golf=bunker 101, golf=cartpath 26, golf=clubhouse 1, golf=driving_range 1, golf=fairway 31, golf=green 54, golf=hole 18, golf=lateral_water_hazard 1, golf=pin 40, golf=tee 150, holes_with_handicap 18, holes_with_par 18, tees_with_colour 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 367 / 367 | 66 | 0.64 | check the flags | 24% | 41% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 556 / 556 | 359 | 0.68 | check the flags | 53% | 23% | 25% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 201 / 201 | 115 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 444 / 444 | 17 | 0.62 | check the flags | 32% | 18% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 451 / 451 | 140 | 0.65 | check the flags | 34% | 34% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 5 | 556 / 556 | 53 | 0.66 | check the flags | 49% | 16% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 468 / 468 | 256 | 0.67 | check the flags | 42% | 29% | 29% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 347 / 347 | 291 | 0.69 | check the flags | 69% | 3% | 29% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 3 | 206 / 206 | 245 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 338 / 338 | 0 | 0.66 | check the flags | 25% | 51% | 24% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 256 / 256 | 317 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 5 | 575 / 575 | 197 | 0.66 | check the flags | 43% | 24% | 34% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 476 / 476 | 200 | 0.62 | check the flags | 36% | 13% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 473 / 473 | 128 | 0.64 | check the flags | 37% | 21% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 5 | 510 / 510 | 212 | 0.67 | check the flags | 39% | 34% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 181 / 181 | 144 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 426 / 426 | 157 | 0.66 | check the flags | 47% | 21% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 472 / 472 | 292 | 0.67 | check the flags | 52% | 16% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/328838760 RTJ Grand National Golf (Opelika, AL)
- **osm**: ok: 728 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/grand_national_links/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/grand_national_links/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 2 polygons (outside 2); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): lake 18, #2 18); kept the course nearest the request's near point (1848 yds vs 3421), 18 ways; ignored 18 + 17 unnumbered golf=hole way(s) in no kept course: OSM 1098809319, 1098809321, 1098809332, 1098809333, 1098809334, 1098809335, 1098809336, 1098809337 ...
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
