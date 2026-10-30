# Adams Pointe Golf Course (Blue Springs, MO) - osm_back tees

Built 2026-10-30T00:33:29Z. OSM way/371984147. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 70 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.428 |
| mean_confidence | 0.656 |
| osm_score | 0.843 |

OSM features inside the course: buildings 5, golf=bunker 30, golf=cartpath 22, golf=fairway 23, golf=green 20, golf=hole 18, golf=path 8, golf=pin 18, golf=rough 4, golf=tee 70, golf=water_hazard 7, holes_with_handicap 18, holes_with_par 18, trees_polygons 1, water_lines 4, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 345 / 345 | 167 | 0.59 | needs review | 29% | 10% | 62% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 5 | 578 / 578 | 166 | 0.61 | check the flags | 39% | 7% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 420 / 420 | 84 | 0.61 | check the flags | 36% | 11% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 3 | 194 / 194 | 249 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 354 / 354 | 14 | 0.65 | check the flags | 45% | 17% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 415 / 415 | 53 | 0.67 | check the flags | 47% | 22% | 31% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 418 / 418 | 219 | 0.60 | check the flags | 40% | 1% | 58% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 239 / 239 | 340 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 5 | 489 / 489 | 329 | 0.61 | check the flags | 36% | 12% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 5 | 506 / 506 | 220 | 0.64 | check the flags | 51% | 4% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 383 / 383 | 248 | 0.62 | check the flags | 42% | 5% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 3 | 187 / 187 | 250 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 362 / 362 | 249 | 0.64 | check the flags | 53% | 1% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 5 | 546 / 546 | 76 | 0.60 | check the flags | 35% | 7% | 58% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 417 / 417 | 76 | 0.61 | check the flags | 44% | 0% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 420 / 420 | 310 | 0.62 | check the flags | 46% | 1% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 219 / 219 | 149 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 446 / 446 | 340 | 0.65 | check the flags | 55% | 1% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/371984147 Adams Pointe Golf Course (Blue Springs, MO)
- **osm**: ok: 1475 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/adams_pointe/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/adams_pointe/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 14 polygons (outside 14); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
