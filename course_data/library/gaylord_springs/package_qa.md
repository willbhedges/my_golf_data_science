# Gaylord Springs Golf Links (Nashville, TN) - Black tees

Built 2026-11-26T23:27:50Z. OSM way/499135540. Scorecard: file (course_data/library/gaylord_springs/routed_card.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 86 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.169 |
| mean_confidence | 0.759 |
| osm_score | 0.691 |

OSM features inside the course: buildings 5, golf=bunker 8, golf=fairway 8, golf=green 18, golf=hole 18, golf=tee 86, golf=water_hazard 7, holes_with_par 18, water_polygons 15

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 529 / 528 | 172 | 0.70 | check the flags | 40% | 3% | 57% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 529 yds) |
| 2 | 4 | 441 / 440 | 176 | 0.78 | check the flags | 32% | 21% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 160 / 160 | 160 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 392 / 391 | 349 | 0.69 | check the flags | 12% | 0% | 88% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 444 / 443 | 2 | 0.58 | needs review | 0% | 1% | 99% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no fairway in the landing zone; Black tee on a lidar pad (no OSM box at 444 yds) |
| 6 | 5 | 533 / 461 | 158 | 0.70 | check the flags | 17% | 2% | 81% | tee stage: Black tee_axis_capped | tee: tee stage: Black tee_axis_capped; no fairway in the landing zone |
| 7 | 4 | 455 / 454 | 355 | 0.65 | check the flags | 0% | 0% | 100% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 8 | 3 | 179 / 179 | 341 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 4 | 349 / 348 | 356 | 0.72 | check the flags | 2% | 13% | 85% | tee stage: Black tee_centroid |  |
| 10 | 5 | 505 / 504 | 358 | 0.67 | check the flags | 0% | 11% | 89% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no fairway in the landing zone |
| 11 | 4 | 451 / 450 | 341 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 12 | 5 | 524 / 523 | 158 | 0.68 | check the flags | 10% | 0% | 90% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 13 | 3 | 184 / 184 | 259 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 14 | 4 | 335 / 278 | 152 | 0.80 | auto | 41% | 2% | 57% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 15 | 4 | 392 / 391 | 358 | 0.72 | check the flags | 25% | 0% | 75% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 16 | 4 | 317 / 316 | 338 | 0.70 | check the flags | 4% | 18% | 78% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 210 / 210 | 168 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 442 / 441 | 187 | 0.72 | check the flags | 25% | 2% | 74% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |

## Stages

- **resolve**: ok: way/499135540 Gaylord Springs Golf Links (Nashville, TN)
- **osm**: ok: 335 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/gaylord_springs/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 99 candidate pads near hole starts (20 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/gaylord_springs/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gaylord_springs/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -2702 m2 {'strip': 1369, 'cells': 1285}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: gated: mown / rough separation d' 0.83 < 1.0 (seeds 26259, rough 55057); no fairway filled
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 4 Red: CHECK, tee was put 128 yds from this hole's start, at hole 7's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 6 Black: CHECK, tee was put 75 yds from this hole's start, at hole 9's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 White: CHECK, tee was put 197 yds from this hole's start, at hole 16's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 6: measured 461 vs card 533 yds for Black (no OSM tee box at that yardage?)
- hole 14: measured 278 vs card 335 yds for Black (no OSM tee box at that yardage?)
- no fairway mapped on 11 hole(s) and the NAIP fairway fill did not run: gated: mown / rough separation d' 0.83 < 1.0 (seeds 26259, rough 55057); no fairway filled
