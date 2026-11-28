# Gaylord Springs Golf Links (Nashville, TN) - Black tees

Built 2026-11-28T02:50:45Z. OSM way/499135540. Scorecard: file (course_data/library/gaylord_springs/routed_card.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 83 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 9 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.147 |
| mean_confidence | 0.801 |
| osm_score | 0.715 |

OSM features inside the course: buildings 5, golf=bunker 8, golf=fairway 8, golf=green 18, golf=hole 18, golf=tee 83, golf=water_hazard 8, holes_with_par 18, water_polygons 16

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 529 / 528 | 182 | 0.77 | check the flags | 41% | 4% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 441 / 440 | 178 | 0.76 | check the flags | 31% | 12% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 160 / 160 | 147 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 392 / 386 | 332 | 0.86 | auto | 43% | 43% | 14% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no fairway in the landing zone |
| 5 | 4 | 444 / 443 | 6 | 0.74 | check the flags | 0% | 44% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 533 / 532 | 154 | 0.76 | check the flags | 2% | 54% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 455 / 454 | 351 | 0.76 | check the flags | 0% | 55% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 179 / 179 | 333 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 349 / 346 | 12 | 0.70 | check the flags | 0% | 60% | 40% | tee stage: Black lidar_pad_capped | tee: tee stage: Black lidar_pad_capped; Black tee on a lidar pad (no OSM box at 349 yds) |
| 10 | 5 | 505 / 504 | 357 | 0.78 | check the flags | 0% | 64% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 451 / 450 | 338 | 0.78 | check the flags | 28% | 60% | 12% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee on a lidar pad (no OSM box at 451 yds) |
| 12 | 5 | 524 / 523 | 168 | 0.66 | check the flags | 5% | 0% | 95% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 13 | 3 | 184 / 184 | 259 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 14 | 4 | 335 / 334 | 164 | 0.71 | check the flags | 15% | 10% | 75% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 392 / 391 | 358 | 0.80 | auto | 23% | 44% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 317 / 316 | 345 | 0.70 | check the flags | 4% | 4% | 92% | tee stage: Black tee_centroid |  |
| 17 | 3 | 210 / 210 | 168 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 442 / 441 | 184 | 0.83 | auto | 12% | 75% | 13% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/499135540 Gaylord Springs Golf Links (Nashville, TN)
- **osm**: ok: 332 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/gaylord_springs/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 94 candidate pads near hole starts (21 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/gaylord_springs/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gaylord_springs/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -2965 m2 {'strip': 1376, 'cells': 1520}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: ok: 8/10 hole(s) without a mapped fairway filled from NAIP (d' 1.02; gated: 4, 12)
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 4 Red: CHECK, tee was put 81 yds from this hole's start, at hole 3's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 9 Black: CHECK, tee was on a road (OSM 19483708): moved 7 yds forward off it
