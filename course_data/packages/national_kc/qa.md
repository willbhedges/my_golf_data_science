# The National Golf Club (Parkville, MO) - Black tees

Built 2026-10-17T17:43:27Z. OSM relation/2630633. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 87 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.35 |
| mean_confidence | 0.639 |
| osm_score | 0.828 |

OSM features inside the course: buildings 22, built_up_landuse 1, golf=bunker 83, golf=cartpath 30, golf=fairway 22, golf=green 21, golf=hole 18, golf=path 1, golf=pin 2, golf=rough 3, golf=tee 87, holes_with_handicap 2, holes_with_par 18, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 287 / 287 | 198 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 496 / 496 | 219 | 0.62 | check the flags | 43% | 7% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 5 | 661 / 661 | 94 | 0.56 | needs review | 21% | 14% | 65% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 427 / 427 | 268 | 0.61 | check the flags | 30% | 26% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 5 | 492 / 492 | 306 | 0.67 | check the flags | 47% | 31% | 22% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 419 / 419 | 358 | 0.57 | needs review | 32% | 4% | 64% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 323 / 323 | 253 | 0.59 | needs review | 40% | 3% | 57% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 211 / 211 | 339 | 0.76 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 5 | 531 / 531 | 315 | 0.61 | check the flags | 29% | 26% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 5 | 590 / 590 | 197 | 0.65 | check the flags | 27% | 47% | 26% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 5 | 500 / 500 | 69 | 0.61 | check the flags | 26% | 34% | 40% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 5 | 526 / 526 | 5 | 0.65 | check the flags | 40% | 31% | 29% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 3 | 162 / 162 | 194 | 0.76 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 454 / 454 | 132 | 0.64 | check the flags | 38% | 31% | 31% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 5 | 482 / 482 | 165 | 0.63 | check the flags | 44% | 17% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 448 / 448 | 345 | 0.59 | needs review | 39% | 1% | 60% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 594 / 594 | 145 | 0.57 | needs review | 34% | 2% | 64% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: relation/2630633 The National Golf Club (Parkville, MO)
- **osm**: ok: 885 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 16/16 holes OSM has no way for (2 to check; segment no, lidar pads 624, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 123 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/national_kc/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/national_kc/imagery/dem.tif (17/17 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 35 polygons (outside 35); mode replace

## Warnings

- hole 3: placed by v2+structure inference, golfer check (ambiguous (30% of the posterior))
- hole 4: placed by v2+structure inference, golfer check (ambiguous (39% of the posterior))
- hole 5: placed by v2+structure inference, golfer check (ambiguous (29% of the posterior))
- hole 8: placed by v2+structure inference, golfer check (ambiguous (38% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (36% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (27% of the posterior))
- hole 12: placed by v2+structure inference, golfer check (ambiguous (27% of the posterior))
- hole 13: placed by v2+structure inference, golfer check (ambiguous (27% of the posterior))
- hole 15: placed by v2+structure inference, golfer check (ambiguous (27% of the posterior))
- hole 16: placed by v2+structure inference, golfer check (ambiguous (28% of the posterior))
- hole 17: placed by v2+structure inference, golfer check (ambiguous (82% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (80% of the posterior))
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
