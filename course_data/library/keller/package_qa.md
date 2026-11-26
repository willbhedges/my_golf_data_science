# Keller Golf Course (Saint Paul, MN) - osm_back tees

Built 2026-11-26T11:01:41Z. OSM way/242402746. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 22 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.298 |
| mean_confidence | 0.663 |
| osm_score | 0.821 |

OSM features inside the course: buildings 2, golf=bunker 34, golf=cartpath 22, golf=driving_range 1, golf=fairway 18, golf=green 19, golf=hole 18, golf=pin 18, golf=tee 22, golf=water_hazard 3, holes_with_handicap 18, holes_with_par 18, trees_polygons 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 334 / 334 | 162 | 0.59 | needs review | 27% | 12% | 61% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 4 | 329 / 329 | 351 | 0.62 | check the flags | 19% | 40% | 40% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 188 / 188 | 360 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 5 | 479 / 479 | 182 | 0.65 | check the flags | 33% | 31% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 327 / 327 | 291 | 0.60 | check the flags | 26% | 20% | 55% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 351 / 351 | 8 | 0.63 | check the flags | 34% | 22% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 401 / 401 | 3 | 0.69 | check the flags | 49% | 34% | 18% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 136 / 136 | 188 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 318 / 318 | 126 | 0.62 | check the flags | 26% | 30% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 338 / 338 | 82 | 0.67 | check the flags | 26% | 56% | 18% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 5 | 477 / 477 | 183 | 0.63 | check the flags | 34% | 23% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 3 | 154 / 154 | 185 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 342 / 342 | 355 | 0.67 | check the flags | 50% | 20% | 31% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 367 / 367 | 359 | 0.64 | check the flags | 26% | 39% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 337 / 337 | 210 | 0.62 | check the flags | 26% | 27% | 47% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 152 / 152 | 298 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 386 / 386 | 14 | 0.65 | check the flags | 30% | 38% | 32% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 287 / 287 | 255 | 0.58 | needs review | 14% | 24% | 62% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/242402746 Keller Golf Course (Saint Paul, MN)
- **osm**: ok: 1043 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/keller/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/keller/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 16 polygons (outside 16); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
