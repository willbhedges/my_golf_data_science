# The National Golf Club (Parkville, MO) - osm_back tees

Built 2026-10-17T17:00:57Z. OSM relation/2630633. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 17 |
| holes_mapped | 17 |
| greens_found | 17 |
| tee_boxes | 90 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 1 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.426 |
| mean_confidence | 0.624 |
| osm_score | 0.686 |

OSM features inside the course: buildings 22, built_up_landuse 1, golf=bunker 83, golf=cartpath 30, golf=fairway 22, golf=green 21, golf=hole 17, golf=path 1, golf=pin 2, golf=rough 3, golf=tee 90, holes_with_handicap 2, holes_with_par 2, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 287 / 287 | 198 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 5 | 496 / 496 | 219 | 0.61 | check the flags | 44% | 0% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 5 | 661 / 661 | 94 | 0.53 | needs review | 21% | 0% | 79% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 0% of the landing zone |
| 4 | 4 | 427 / 427 | 268 | 0.61 | check the flags | 47% | 0% | 53% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 5 | 492 / 492 | 306 | 0.66 | check the flags | 66% | 0% | 34% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 419 / 419 | 358 | 0.57 | needs review | 32% | 0% | 68% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 323 / 323 | 253 | 0.59 | needs review | 40% | 0% | 60% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 211 / 211 | 339 | 0.76 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 5 | 531 / 531 | 315 | 0.56 | needs review | 29% | 0% | 71% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 590 / 590 | 197 | 0.62 | check the flags | 51% | 0% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 5 | 500 / 500 | 69 | 0.62 | check the flags | 54% | 0% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 5 | 526 / 526 | 5 | 0.62 | check the flags | 51% | 0% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 3 | 162 / 162 | 194 | 0.76 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 454 / 454 | 132 | 0.59 | needs review | 40% | 0% | 60% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 5 | 482 / 482 | 165 | 0.61 | check the flags | 49% | 0% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 4 | 448 / 448 | 345 | 0.58 | needs review | 39% | 0% | 61% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 594 / 594 | 145 | 0.57 | needs review | 34% | 0% | 66% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: relation/2630633 The National Golf Club (Parkville, MO)
- **osm**: ok: 885 features
- **routing**: ok: v2+structure (mapped_nocard, lam 2.0, structure on osm) placed 15/16 holes OSM has no way for (12 to check; segment no, lidar pads 624, perception scene no)
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (17 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/national_kc/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/national_kc/imagery/dem.tif (17/17 holes)
- **vision**: missing: no vision_any layers for 'national_kc' (FileNotFoundError: course_data/vision_any/national_kc/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

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
- vision: missing: no vision_any layers for 'national_kc' (FileNotFoundError: course_data/vision_any/national_kc/raw (not fetched)); add the course to course_data/vision_; trees / long grass come from OSM only
