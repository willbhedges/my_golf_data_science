# Queenstown Harbor River Course (Queenstown, MD) - osm_back tees

Built 2026-11-03T05:14:11Z. OSM way/1067525665. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 139 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.398 |
| mean_confidence | 0.649 |
| osm_score | 0.851 |

OSM features inside the course: buildings 16, golf=bunker 84, golf=cartpath 1, golf=driving_range 1, golf=fairway 42, golf=green 36, golf=hole 18, golf=lateral_water_hazard 15, golf=path 26, golf=pin 28, golf=rough 1, golf=tee 139, holes_with_handicap 2, holes_with_par 11, trees_polygons 2, water_polygons 15

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 358 / 358 | 325 | 0.64 | check the flags | 46% | 9% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 3 | 157 / 157 | 38 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 422 / 422 | 108 | 0.62 | check the flags | 37% | 20% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 374 / 374 | 203 | 0.57 | needs review | 35% | 0% | 65% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 5 | 559 / 559 | 303 | 0.60 | needs review | 37% | 9% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 348 / 348 | 218 | 0.61 | check the flags | 46% | 5% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 5 | 542 / 542 | 58 | 0.58 | needs review | 24% | 21% | 55% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 240 / 240 | 263 | 0.76 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 414 / 414 | 60 | 0.58 | needs review | 35% | 5% | 60% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 456 / 456 | 239 | 0.63 | check the flags | 34% | 21% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 5 | 564 / 564 | 250 | 0.66 | check the flags | 58% | 2% | 40% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 356 / 356 | 347 | 0.65 | check the flags | 47% | 14% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 3 | 155 / 155 | 286 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 413 / 413 | 47 | 0.63 | check the flags | 50% | 0% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 433 / 433 | 204 | 0.65 | check the flags | 56% | 1% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 199 / 199 | 89 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 367 / 367 | 85 | 0.57 | needs review | 19% | 16% | 65% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 5 | 579 / 579 | 61 | 0.63 | check the flags | 35% | 19% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/1067525665 Queenstown Harbor River Course (Queenstown, MD)
- **osm**: ok: 654 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/queenstown_harbor/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/queenstown_harbor/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 1 polygons (outside 1); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): river 18, #2 18); kept 'river' (named in the request), 18 ways; ignored 18
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
