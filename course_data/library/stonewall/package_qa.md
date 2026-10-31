# The Arnold Palmer Signature Golf Course at Stonewall Resort (Roanoke, WV) - osm_back tees

Built 2026-10-31T05:28:44Z. OSM way/299335592. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 95 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.47 |
| mean_confidence | 0.672 |
| osm_score | 0.894 |

OSM features inside the course: buildings 1, golf=bunker 42, golf=cartpath 11, golf=fairway 23, golf=green 18, golf=hole 18, golf=rough 72, golf=tee 95, golf=water_hazard 3, holes_with_handicap 18, holes_with_par 18, tees_with_ref 95, trees_polygons 2, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 401 / 401 | 198 | 0.68 | check the flags | 59% | 11% | 30% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 3 | 182 / 182 | 221 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 437 / 437 | 52 | 0.65 | check the flags | 47% | 12% | 41% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 5 | 605 / 605 | 233 | 0.64 | check the flags | 37% | 24% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 432 / 432 | 46 | 0.62 | check the flags | 41% | 8% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 3 | 165 / 165 | 162 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 5 | 581 / 581 | 234 | 0.67 | check the flags | 41% | 30% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 424 / 424 | 325 | 0.61 | check the flags | 44% | 1% | 55% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 393 / 393 | 215 | 0.67 | check the flags | 62% | 2% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 3 | 165 / 165 | 27 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 440 / 440 | 292 | 0.65 | check the flags | 40% | 24% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 5 | 538 / 538 | 285 | 0.62 | check the flags | 41% | 6% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 452 / 452 | 101 | 0.63 | check the flags | 48% | 3% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 321 / 321 | 12 | 0.69 | check the flags | 70% | 2% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 375 / 375 | 152 | 0.66 | check the flags | 56% | 8% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 208 / 208 | 212 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 456 / 456 | 120 | 0.60 | needs review | 26% | 18% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 5 | 568 / 568 | 10 | 0.63 | check the flags | 44% | 8% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/299335592 The Arnold Palmer Signature Golf Course at Stonewall Resort (Roanoke, WV)
- **osm**: ok: 391 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/stonewall/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/stonewall/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
