# Sycamore Ridge Golf Club (Spring Hill, KS) - osm_back tees

Built 2026-10-30T03:39:13Z. OSM way/151985223. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 99 |
| tees_with_colour | 89 |
| holes_with_trees_or_long_grass_in_landing_zone | 9 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.408 |
| mean_confidence | 0.676 |
| osm_score | 0.818 |

OSM features inside the course: buildings 4, golf=bunker 45, golf=cartpath 47, golf=driving_range 1, golf=fairway 30, golf=green 25, golf=hole 17, golf=pin 18, golf=rough 1, golf=tee 99, golf=water_hazard 5, holes_with_handicap 17, holes_with_par 17, tees_with_colour 89, trees_polygons 3, water_lines 5, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 450 / 450 | 41 | 0.62 | check the flags | 46% | 0% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 5 | 558 / 558 | 11 | 0.62 | check the flags | 44% | 4% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 228 / 228 | 73 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 316 / 316 | 178 | 0.58 | needs review | 31% | 3% | 66% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 3 | 171 / 171 | 323 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 5 | 545 / 545 | 179 | 0.65 | check the flags | 56% | 0% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 377 / 377 | 244 | 0.62 | check the flags | 47% | 1% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 209 / 209 | 335 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 5 | 538 / 538 | 144 | 0.59 | needs review | 30% | 10% | 60% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 463 / 463 | 178 | 0.64 | check the flags | 46% | 13% | 41% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 5 | 541 / 541 | 256 | 0.66 | check the flags | 42% | 27% | 31% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 344 / 344 | 266 | 0.66 | check the flags | 33% | 37% | 30% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 3 | 222 / 222 | 171 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 399 / 399 | 147 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 375 / 375 | 7 | 0.64 | check the flags | 46% | 13% | 41% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 5 | 581 / 581 | 50 | 0.64 | check the flags | 34% | 26% | 40% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 188 / 188 | 355 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 416 / 416 | 49 | 0.62 | check the flags | 34% | 17% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/151985223 Sycamore Ridge Golf Club (Spring Hill, KS)
- **osm**: ok: 495 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/sycamore_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/sycamore_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
