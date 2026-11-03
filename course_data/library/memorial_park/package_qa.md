# Memorial Park Golf Course (Houston, TX) - osm_back tees

Built 2026-11-03T09:42:08Z. OSM relation/13729803. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 51 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.338 |
| mean_confidence | 0.653 |
| osm_score | 0.852 |

OSM features inside the course: buildings 10, golf=bunker 21, golf=cartpath 30, golf=clubhouse 1, golf=driving_range 1, golf=fairway 19, golf=green 23, golf=hole 18, golf=lateral_water_hazard 8, golf=path 3, golf=pin 18, golf=tee 51, holes_with_par 18, tees_with_ref 12, trees_polygons 8, water_lines 4, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 499 / 499 | 221 | 0.59 | needs review | 29% | 9% | 62% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 3 | 151 / 151 | 179 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 5 | 580 / 580 | 344 | 0.58 | needs review | 23% | 14% | 63% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 483 / 483 | 167 | 0.59 | needs review | 27% | 14% | 59% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 440 / 440 | 323 | 0.63 | check the flags | 45% | 7% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 441 / 441 | 143 | 0.61 | check the flags | 38% | 8% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 3 | 206 / 206 | 70 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 5 | 591 / 591 | 16 | 0.59 | needs review | 25% | 14% | 61% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 3 | 180 / 180 | 13 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 433 / 433 | 303 | 0.60 | needs review | 32% | 9% | 59% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 217 / 217 | 158 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 486 / 486 | 330 | 0.61 | check the flags | 28% | 18% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 390 / 390 | 205 | 0.62 | check the flags | 27% | 26% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 5 | 517 / 517 | 190 | 0.60 | check the flags | 32% | 12% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 3 | 137 / 137 | 153 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 5 | 545 / 545 | 339 | 0.64 | check the flags | 46% | 8% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 403 / 403 | 171 | 0.64 | check the flags | 54% | 0% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 485 / 485 | 67 | 0.60 | check the flags | 31% | 14% | 55% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: relation/13729803 Memorial Park Golf Course (Houston, TX)
- **osm**: ok: 832 features
- **card_order**: reject: card did not match the mapped holes: the OSM holes 1-18 walk as a round (longest green-to-next-tee 186 yds), and in that order the card's par or length is off on 6 holes (3, 8, 9, 13, 14, 18); card not used
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/memorial_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/memorial_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -1614 m2 {'road': 539, 'strip': 340, 'cells': 679}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- card did not match the mapped holes: the OSM holes 1-18 walk as a round (longest green-to-next-tee 186 yds), and in that order the card's par or length is off on 6 holes (3, 8, 9, 13, 14, 18); card not used (golfify: golfify) (CHECK)
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
