# Tournament Club of Iowa (Polk City, IA) - osm_back tees

Built 2026-10-30T12:32:53Z. OSM relation/1507320. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 72 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.319 |
| mean_confidence | 0.662 |
| osm_score | 0.833 |

OSM features inside the course: buildings 3, golf=bunker 26, golf=cartpath 53, golf=clubhouse 1, golf=driving_range 1, golf=fairway 23, golf=green 26, golf=hole 18, golf=tee 72, golf=water_hazard 4, holes_with_handicap 18, holes_with_par 18, single_trees 6, water_lines 4, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 270 / 270 | 343 | 0.61 | check the flags | 42% | 1% | 57% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 4 | 294 / 294 | 289 | 0.60 | needs review | 3% | 48% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 377 / 377 | 270 | 0.65 | check the flags | 14% | 58% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 5 | 473 / 473 | 104 | 0.63 | check the flags | 28% | 32% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 256 / 256 | 206 | 0.56 | needs review | 10% | 22% | 67% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 3 | 173 / 173 | 135 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 3 | 154 / 154 | 126 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 5 | 553 / 553 | 89 | 0.65 | check the flags | 57% | 0% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 396 / 396 | 276 | 0.65 | check the flags | 57% | 0% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 485 / 485 | 32 | 0.61 | check the flags | 30% | 17% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 322 / 322 | 344 | 0.58 | needs review | 27% | 7% | 66% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 3 | 142 / 142 | 247 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 5 | 547 / 547 | 315 | 0.66 | check the flags | 42% | 28% | 30% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 162 / 162 | 229 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 5 | 416 / 416 | 157 | 0.62 | check the flags | 29% | 27% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 4 | 357 / 357 | 161 | 0.61 | check the flags | 24% | 25% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 158 / 158 | 50 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 388 / 388 | 171 | 0.63 | check the flags | 50% | 0% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: relation/1507320 Tournament Club of Iowa (Polk City, IA)
- **osm**: ok: 1058 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/tournament_club_iowa/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/tournament_club_iowa/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 22 polygons (property_line 22); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
