# Ed Oliver Golf Club (Wilmington, DE) - Black tees

Built 2026-10-30T21:35:04Z. OSM way/82787084. Scorecard: allsquare (allsquare). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 31 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.352 |
| mean_confidence | 0.803 |
| osm_score | 0.857 |

OSM features inside the course: buildings 4, golf=bunker 39, golf=fairway 19, golf=green 19, golf=hole 18, golf=tee 31, holes_with_par 18, single_trees 135, tree_rows 10, trees_polygons 2, water_lines 2, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 388 / 389 | 100 | 0.75 | check the flags | 29% | 9% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 369 / 369 | 119 | 0.78 | check the flags | 42% | 5% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 447 / 447 | 211 | 0.72 | check the flags | 30% | 28% | 42% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 447 yds) |
| 4 | 5 | 527 / 527 | 306 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 210 / 210 | 291 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 510 / 510 | 130 | 0.79 | check the flags | 39% | 13% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 360 / 360 | 295 | 0.82 | auto | 36% | 32% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 388 / 387 | 311 | 0.79 | check the flags | 38% | 14% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 3 | 148 / 148 | 358 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 362 / 351 | 97 | 0.77 | check the flags | 30% | 18% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 380 / 374 | 111 | 0.81 | auto | 38% | 28% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 290 / 290 | 211 | 0.74 | check the flags | 29% | 3% | 68% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 143 / 143 | 354 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 382 / 383 | 287 | 0.75 | check the flags | 31% | 8% | 61% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 352 / 346 | 296 | 0.75 | check the flags | 31% | 6% | 63% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 355 / 355 | 36 | 0.83 | auto | 34% | 26% | 40% | tee stage: Black tee_centroid |  |
| 17 | 3 | 179 / 179 | 127 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 400 / 400 | 235 | 0.67 | check the flags | 40% | 6% | 55% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 400 yds) |

## Stages

- **resolve**: ok: way/82787084 Ed Oliver Golf Club (Wilmington, DE)
- **osm**: ok: 528 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 18/18 holes OSM has no way for (2 to check; segment no, lidar pads 135, perception scene no)
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 39 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/ed_oliver/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/ed_oliver/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace

## Warnings

- hole 1: placed by v2+structure inference, golfer check (ambiguous (49% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (95% of the posterior))
