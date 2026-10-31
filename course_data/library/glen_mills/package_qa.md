# The Golf Course at Glen Mills (Thornbury Township, PA) - Black tees

Built 2026-10-31T03:48:56Z. OSM way/284570622. Scorecard: golfify (golfify). Tee set: name.

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
| mean_landing_osm_share | 0.443 |
| mean_confidence | 0.828 |
| osm_score | 0.829 |

OSM features inside the course: buildings 2, golf=bunker 104, golf=fairway 18, golf=green 17, golf=hole 15, golf=rough 6, golf=tee 61, holes_with_handicap 8, holes_with_par 15, water_lines 7, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 374 / 371 | 344 | 0.79 | check the flags | 50% | 1% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 431 / 430 | 177 | 0.83 | auto | 65% | 0% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 394 / 387 | 268 | 0.81 | auto | 50% | 13% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 572 / 572 | 44 | 0.73 | check the flags | 49% | 8% | 43% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 572 yds) |
| 5 | 3 | 181 / 181 | 9 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 6 | 5 | 547 / 540 | 66 | 0.83 | auto | 42% | 34% | 24% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 221 / 221 | 277 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 325 / 321 | 110 | 0.80 | check the flags | 32% | 28% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 433 / 430 | 218 | 0.73 | check the flags | 48% | 8% | 44% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 433 yds) |
| 10 | 3 | 207 / 207 | 9 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 207 yds) |
| 11 | 4 | 376 / 382 | 32 | 0.83 | auto | 29% | 48% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 339 / 339 | 23 | 0.72 | check the flags | 48% | 6% | 46% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 339 yds) |
| 16 | 3 | 156 / 156 | 226 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 5 | 483 / 475 | 216 | 0.80 | auto | 31% | 33% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 464 / 461 | 215 | 0.85 | auto | 44% | 41% | 16% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/284570622 The Golf Course at Glen Mills (Thornbury Township, PA)
- **osm**: ok: 492 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 7/10 holes OSM has no way for (3 to check; segment no, lidar pads 279, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 87 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (15 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/glen_mills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 15/15 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/glen_mills/imagery/dem.tif (15/15 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace

## Warnings

- hole 10: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
