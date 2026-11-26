# Brown Deer Golf Club (Coralville, IA) - osm_back tees

Built 2026-11-26T09:27:00Z. OSM way/191258543. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 17 |
| tee_boxes | 62 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.304 |
| mean_confidence | 0.663 |
| osm_score | 0.837 |

OSM features inside the course: buildings 5, built_up_landuse 2, golf=bunker 38, golf=cartpath 21, golf=clubhouse 1, golf=driving_range 1, golf=fairway 17, golf=green 19, golf=hole 18, golf=lateral_water_hazard 10, golf=path 1, golf=tee 62, golf=water_hazard 2, holes_with_par 18, trees_polygons 7, water_lines 2, water_polygons 12

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 551 / 551 | 352 | 0.63 | check the flags | 50% | 6% | 44% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 555 / 555 | 334 | 0.65 | check the flags | 52% | 4% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 323 / 323 | 331 | 0.60 | needs review | 32% | 9% | 59% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 5 | 501 / 501 | 109 | 0.61 | check the flags | 42% | 2% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 3 | 177 / 177 | 194 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 284 / 284 | 144 | 0.61 | check the flags | 35% | 9% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 469 / 469 | 145 | 0.67 | check the flags | 23% | 55% | 22% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 4 | 487 / 487 | 175 | 0.61 | check the flags | 6% | 52% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 3 | 116 / 116 | 27 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 5 | 357 / 357 | 209 | 0.60 | check the flags | 21% | 28% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 4 | 351 / 351 | 130 | 0.64 | check the flags | 23% | 42% | 35% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 3 | 208 / 208 | 310 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 258 / 258 | 287 | 0.60 | needs review | 21% | 26% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 95 / 95 | 19 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 5 | 478 / 478 | 353 | 0.60 | check the flags | 28% | 17% | 55% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 4 | 272 / 272 | 152 | 0.64 | check the flags | 13% | 58% | 29% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 169 / 169 | 95 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 304 / 304 | 62 | 0.64 | check the flags | 49% | 4% | 47% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/191258543 Brown Deer Golf Club (Coralville, IA)
- **osm**: ok: 544 features
- **card_order**: reject: card did not match the mapped holes: the OSM holes 1-18 walk as a round (longest green-to-next-tee 257 yds), and in that order the card's par or length is off on 8 holes (1, 6, 7, 8, 9, 10, 16, 18); card not used
- **routing**: not needed: OSM has a golf=hole way for every hole
- **green_overrides**: ok: hole 1: green moved 184 yds, line re-drawn start -> green
- **card_overrides**: ok: yardage_overrides on 1 hole(s) not applied: no card (lengths are measured)
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/brown_deer/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/brown_deer/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -1 m2 {'cells': 1}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 31 polygons (property_line 31); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- card did not match the mapped holes: the OSM holes 1-18 walk as a round (longest green-to-next-tee 257 yds), and in that order the card's par or length is off on 8 holes (1, 6, 7, 8, 9, 10, 16, 18); card not used (golfify: golfify) (CHECK)
- review override: yardage_overrides on 1 hole(s) not applied: no card (lengths are measured)
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
