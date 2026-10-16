# Veenker Memorial Golf Course (Ames, IA) - Blue tees

Built 2026-10-16T19:42:31Z. OSM way/44804299. Scorecard: golfify (golfify). Tee set: fallback: longest set (tee set 'White' not on the card (sets: Blue, Gold, Red, Gold (Gold), Red (Red))).

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 43 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 1 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.287 |
| mean_confidence | 0.788 |
| osm_score | 0.673 |

OSM features inside the course: buildings 8, golf=bunker 27, golf=cartpath 5, golf=fairway 30, golf=green 26, golf=hole 18, golf=lateral_water_hazard 2, golf=path 38, golf=rough 1, golf=tee 43, holes_with_handicap 18, holes_with_par 18, water_lines 1, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 435 / 435 | 176 | 0.75 | check the flags | 36% | 0% | 64% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 334 / 338 | 248 | 0.74 | check the flags | 18% | 0% | 82% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 333 / 318 | 32 | 0.76 | check the flags | 25% | 0% | 75% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 4 | 349 / 348 | 298 | 0.75 | check the flags | 35% | 0% | 65% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 402 / 401 | 167 | 0.77 | check the flags | 30% | 0% | 70% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 3 | 210 / 209 | 88 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 5 | 590 / 572 | 66 | 0.72 | check the flags | 26% | 0% | 74% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 181 / 174 | 29 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 537 / 538 | 294 | 0.79 | check the flags | 37% | 0% | 63% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 560 / 536 | 148 | 0.73 | check the flags | 29% | 0% | 71% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 155 / 155 | 242 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 330 / 317 | 245 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 3 | 160 / 159 | 56 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 416 / 415 | 336 | 0.71 | check the flags | 21% | 0% | 79% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 420 / 419 | 230 | 0.72 | check the flags | 24% | 0% | 76% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 5 | 544 / 544 | 130 | 0.63 | check the flags | 30% | 0% | 70% | tee stage: Blue walkback | tee: tee stage: Blue walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 190 / 184 | 109 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 5 | 534 / 532 | 335 | 0.74 | check the flags | 31% | 0% | 69% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/44804299 Veenker Memorial Golf Course (Ames, IA)
- **osm**: ok: 598 features
- **scorecard**: ok: golfify (golfify)
- **tees**: ok: tees/place_tee.py for 5 sets on the card yardages
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/veenker/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/veenker/imagery/dem.tif (18/18 holes)
- **vision**: failed: IndexError: list index out of range

## Warnings

- tee set 'White' not on the card (sets: Blue, Gold, Red, Gold (Gold), Red (Red)); using the longest set 'Blue' instead
- hole 7: measured 572 vs card 590 yds for Blue (no OSM tee box at that yardage?)
- hole 10: measured 536 vs card 560 yds for Blue (no OSM tee box at that yardage?)
