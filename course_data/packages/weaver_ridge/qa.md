# WeaverRidge Golf Club (Peoria, IL) - Black tees

Built 2026-11-09T22:15:10Z. OSM way/749257217. Scorecard: file (course_data/library/weaver_ridge/card_review.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 82 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.466 |
| mean_confidence | 0.834 |
| osm_score | 0.865 |

OSM features inside the course: buildings 183, golf=bunker 78, golf=cartpath 46, golf=clubhouse 1, golf=driving_range 1, golf=fairway 24, golf=green 19, golf=hole 18, golf=rough 1, golf=tee 82, golf=water_hazard 8, holes_with_par 18, water_lines 3, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 540 / 536 | 274 | 0.80 | check the flags | 52% | 2% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 391 / 391 | 157 | 0.79 | check the flags | 37% | 2% | 62% | tee stage: Black tee_centroid |  |
| 3 | 5 | 519 / 520 | 276 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 182 / 181 | 23 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 387 / 363 | 102 | 0.71 | check the flags | 69% | 4% | 27% | tee stage: Black review (inside OSM tee 749315882) | tee: tee stage: Black review (inside OSM tee 749315882) |
| 6 | 4 | 388 / 388 | 10 | 0.81 | auto | 38% | 7% | 54% | tee stage: Black tee_centroid |  |
| 7 | 4 | 435 / 436 | 84 | 0.83 | auto | 43% | 13% | 44% | tee stage: Black tee_centroid |  |
| 8 | 3 | 194 / 194 | 173 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 381 / 381 | 189 | 0.79 | check the flags | 33% | 7% | 60% | tee stage: Black tee_centroid |  |
| 10 | 4 | 418 / 418 | 180 | 0.85 | auto | 36% | 32% | 32% | tee stage: Black tee_centroid |  |
| 11 | 5 | 489 / 484 | 221 | 0.84 | auto | 52% | 22% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 228 / 229 | 275 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 432 / 427 | 38 | 0.80 | check the flags | 47% | 9% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 406 / 406 | 210 | 0.82 | auto | 38% | 31% | 31% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 458 / 459 | 294 | 0.82 | auto | 59% | 4% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 401 / 402 | 83 | 0.80 | auto | 55% | 0% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 187 / 183 | 84 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 556 / 554 | 58 | 0.85 | auto | 49% | 29% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/749257217 WeaverRidge Golf Club (Peoria, IL)
- **osm**: ok: 822 features
- **card_overrides**: ok: 1 review fix(es): hole 16 Black: card 439 -> 401 yds (review)
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/weaver_ridge/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 5 review (inside OSM tee 749315882);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 72 candidate pads near hole starts (8 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/weaver_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/weaver_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -6325 m2 {'strip': 987, 'road': 3807, 'cells': 1452}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 10 polygons (outside 10); mode replace
- **native_auto**: none: course gate shut: 4% of sides >= 0.675 (< 25%)

## Warnings

- hole 5: measured 363 vs card 387 yds for Black (no OSM tee box at that yardage?)
