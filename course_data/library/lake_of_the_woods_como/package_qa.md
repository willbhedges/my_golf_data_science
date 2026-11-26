# Lake of the Woods Golf Course (Columbia, MO) - osm_back tees

Built 2026-11-26T06:29:43Z. OSM way/387184389. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 27 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.221 |
| mean_confidence | 0.659 |
| osm_score | 0.819 |

OSM features inside the course: buildings 7, golf=bunker 3, golf=cartpath 22, golf=fairway 21, golf=green 18, golf=hole 18, golf=tee 27, golf=water_hazard 2, holes_with_par 18, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 276 / 276 | 158 | 0.62 | check the flags | 19% | 36% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 3 | 121 / 121 | 235 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 328 / 328 | 286 | 0.57 | needs review | 11% | 24% | 65% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 208 / 208 | 7 | 0.54 | needs review | 7% | 14% | 79% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 256 / 256 | 4 | 0.63 | check the flags | 20% | 41% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 315 / 315 | 140 | 0.66 | check the flags | 26% | 50% | 24% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 3 | 128 / 128 | 307 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 265 / 265 | 138 | 0.61 | check the flags | 12% | 46% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 5 | 367 / 367 | 345 | 0.63 | check the flags | 37% | 20% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 3 | 147 / 147 | 349 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 5 | 491 / 491 | 91 | 0.70 | check the flags | 31% | 60% | 9% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 331 / 331 | 262 | 0.67 | check the flags | 34% | 44% | 22% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 320 / 320 | 175 | 0.62 | check the flags | 22% | 36% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 277 / 277 | 33 | 0.53 | needs review | 0% | 20% | 80% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 283 / 283 | 73 | 0.65 | check the flags | 15% | 60% | 24% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 5 | 426 / 426 | 224 | 0.69 | check the flags | 40% | 46% | 15% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 103 / 103 | 219 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 370 / 370 | 347 | 0.65 | check the flags | 35% | 28% | 37% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/387184389 Lake of the Woods Golf Course (Columbia, MO)
- **osm**: ok: 232 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/lake_of_the_woods_como/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/lake_of_the_woods_como/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -232 m2 {'cells': 230}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 11 polygons (outside 11); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
