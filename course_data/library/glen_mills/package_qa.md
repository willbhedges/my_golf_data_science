# The Golf Course at Glen Mills (Thornbury Township, PA) - Black tees

Built 2026-11-26T07:52:16Z. OSM way/284570622. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 15 |
| holes_mapped | 15 |
| greens_found | 15 |
| tee_boxes | 61 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 11 |
| mean_landing_osm_share | 0.438 |
| mean_confidence | 0.843 |
| osm_score | 0.828 |

OSM features inside the course: buildings 2, golf=bunker 104, golf=fairway 18, golf=green 17, golf=hole 15, golf=rough 6, golf=tee 61, holes_with_handicap 8, holes_with_par 15, water_lines 7, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 374 / 371 | 344 | 0.79 | check the flags | 50% | 2% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 431 / 430 | 177 | 0.83 | auto | 65% | 0% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 394 / 390 | 268 | 0.82 | auto | 50% | 16% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 572 / 567 | 33 | 0.82 | auto | 52% | 11% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 181 / 181 | 9 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 6 | 5 | 547 / 548 | 66 | 0.86 | auto | 45% | 42% | 13% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 221 / 221 | 277 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 325 / 321 | 110 | 0.80 | auto | 32% | 32% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 433 / 373 | 227 | 0.80 | auto | 36% | 27% | 38% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap |
| 10 | 3 | 207 / 207 | 9 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 207 yds) |
| 11 | 4 | 376 / 381 | 32 | 0.84 | auto | 30% | 52% | 18% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 339 / 339 | 23 | 0.73 | check the flags | 48% | 8% | 44% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 339 yds) |
| 16 | 3 | 156 / 156 | 226 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 5 | 483 / 478 | 216 | 0.81 | auto | 31% | 36% | 33% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 464 / 461 | 215 | 0.86 | auto | 44% | 42% | 14% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/284570622 The Golf Course at Glen Mills (Thornbury Township, PA)
- **osm**: ok: 492 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 7/10 holes OSM has no way for (3 to check; segment no, lidar pads 279, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 78 candidate pads near hole starts (9 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (15 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/glen_mills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 15/15 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/glen_mills/imagery/dem.tif (15/15 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -483 m2 {'cells': 444}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 10: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 2 Green: CHECK, tee was put 84 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Green (L): CHECK, tee was put 84 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Red: CHECK, tee was put 70 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Red (L): CHECK, tee was put 70 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Red: CHECK, tee was put 66 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Red (L): CHECK, tee was put 66 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Red: CHECK, tee was put 80 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Red (L): CHECK, tee was put 80 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 17 Red: CHECK, tee was put 79 yds from this hole's start, at hole 12's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 17 Red (L): CHECK, tee was put 79 yds from this hole's start, at hole 12's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 Blue: CHECK, tee was put 79 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 White: CHECK, tee was put 105 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 White (L): CHECK, tee was put 105 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 Green: CHECK, tee was put 134 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 Green (L): CHECK, tee was put 134 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 9: measured 373 vs card 433 yds for Black (no OSM tee box at that yardage?)
