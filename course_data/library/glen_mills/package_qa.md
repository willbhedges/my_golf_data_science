# The Golf Course at Glen Mills (Thornbury Township, PA) - Black tees

Built 2026-11-26T17:12:16Z. OSM way/284570622. Scorecard: file (course_data/library/glen_mills/routed_card.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 56 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.37 |
| mean_confidence | 0.834 |
| osm_score | 0.845 |

OSM features inside the course: buildings 2, golf=bunker 104, golf=fairway 18, golf=green 17, golf=hole 17, golf=rough 6, golf=tee 56, holes_with_par 17, water_lines 7, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 374 / 372 | 343 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 431 / 430 | 180 | 0.80 | auto | 54% | 0% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 394 / 390 | 268 | 0.82 | auto | 48% | 16% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 572 / 567 | 35 | 0.80 | check the flags | 46% | 9% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 181 / 296 | 4 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid_capped |  |
| 6 | 5 | 547 / 548 | 73 | 0.79 | check the flags | 42% | 44% | 13% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 547 yds) |
| 7 | 3 | 221 / 221 | 277 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 325 / 321 | 110 | 0.80 | auto | 32% | 30% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 433 / 374 | 229 | 0.79 | check the flags | 34% | 21% | 44% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap |
| 10 | 3 | 207 / 206 | 69 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 376 / 381 | 29 | 0.84 | auto | 31% | 50% | 19% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 339 / 339 | 1 | 0.84 | auto | 6% | 85% | 8% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 453 / 453 | 72 | 0.71 | check the flags | 38% | 10% | 52% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 453 yds) |
| 14 | 3 | 161 / 156 | 92 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 529 / 524 | 228 | 0.75 | check the flags | 24% | 18% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 156 / 156 | 226 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 5 | 483 / 488 | 196 | 0.81 | auto | 37% | 31% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 464 / 463 | 223 | 0.80 | auto | 40% | 21% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/284570622 The Golf Course at Glen Mills (Thornbury Township, PA)
- **osm**: ok: 502 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/glen_mills/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 77 candidate pads near hole starts (16 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/glen_mills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/glen_mills/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -575 m2 {'cells': 527}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 8 polygons (outside 8); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 2 White: CHECK, tee was put 95 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 White (L): CHECK, tee was put 95 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Green: CHECK, tee was put 135 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Green (L): CHECK, tee was put 135 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Red: CHECK, tee was put 172 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Red (L): CHECK, tee was put 172 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Black: CHECK, tee was put 118 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Blue: CHECK, tee was put 128 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 White: CHECK, tee was put 137 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 White (L): CHECK, tee was put 137 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Green: CHECK, tee was put 161 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Green (L): CHECK, tee was put 161 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Red: CHECK, tee was put 196 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5 Red (L): CHECK, tee was put 196 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Red: CHECK, tee was put 66 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Red (L): CHECK, tee was put 66 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Green: CHECK, tee was put 96 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Green (L): CHECK, tee was put 96 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Red: CHECK, tee was put 134 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Red (L): CHECK, tee was put 134 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 17 Green: CHECK, tee was put 95 yds from this hole's start, at hole 12's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 17 Green (L): CHECK, tee was put 95 yds from this hole's start, at hole 12's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 17 Red: CHECK, tee was put 114 yds from this hole's start, at hole 12's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 17 Red (L): CHECK, tee was put 114 yds from this hole's start, at hole 12's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 Blue: CHECK, tee was put 82 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 White: CHECK, tee was put 109 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 White (L): CHECK, tee was put 109 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 5: measured 296 vs card 181 yds for Black (no OSM tee box at that yardage?)
- hole 9: measured 374 vs card 433 yds for Black (no OSM tee box at that yardage?)
