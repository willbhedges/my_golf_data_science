# Sycamore Ridge Golf Club (Spring Hill, KS) - Black tees

Built 2026-11-02T23:15:54Z. OSM way/151985223. Scorecard: file (course_data/library/sycamore_ridge/card_review.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 99 |
| tees_with_colour | 89 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.421 |
| mean_confidence | 0.872 |
| osm_score | 0.854 |

OSM features inside the course: buildings 4, golf=bunker 45, golf=cartpath 47, golf=driving_range 1, golf=fairway 30, golf=green 25, golf=hole 18, golf=pin 18, golf=rough 1, golf=tee 99, golf=water_hazard 5, holes_with_handicap 18, holes_with_par 18, tees_with_colour 89, trees_polygons 3, water_lines 5, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 467 / 468 | 178 | 0.66 | check the flags | 45% | 14% | 41% | tee stage: Black review (inside OSM tee 930492853) | tee: tee stage: Black review (inside OSM tee 930492853) |
| 2 | 5 | 544 / 544 | 256 | 0.89 | auto | 43% | 26% | 31% | tee stage: Black tagged |  |
| 3 | 4 | 351 / 349 | 266 | 0.89 | auto | 34% | 37% | 29% | tee stage: Black tagged |  |
| 4 | 3 | 226 / 226 | 171 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 5 | 4 | 413 / 408 | 164 | 0.89 | auto | 42% | 28% | 30% | tee stage: Black tagged |  |
| 6 | 4 | 390 / 384 | 7 | 0.80 | auto | 46% | 11% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 5 | 600 / 596 | 50 | 0.88 | auto | 38% | 26% | 35% | tee stage: Black tagged |  |
| 8 | 3 | 195 / 193 | 355 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 9 | 4 | 466 / 466 | 49 | 0.66 | check the flags | 38% | 19% | 43% | tee stage: Black card_box | tee: tee stage: Black card_box |
| 10 | 4 | 457 / 456 | 41 | 0.85 | auto | 46% | 0% | 54% | tee stage: Black tagged |  |
| 11 | 5 | 566 / 564 | 11 | 0.85 | auto | 44% | 5% | 50% | tee stage: Black tagged |  |
| 12 | 3 | 230 / 230 | 73 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 13 | 4 | 331 / 329 | 179 | 0.75 | check the flags | 36% | 2% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 3 | 176 / 176 | 323 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 15 | 5 | 548 / 547 | 179 | 0.88 | auto | 55% | 0% | 45% | tee stage: Black tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 381 / 381 | 244 | 0.86 | auto | 49% | 1% | 50% | tee stage: Black tagged |  |
| 17 | 3 | 215 / 215 | 335 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 18 | 5 | 525 / 530 | 144 | 0.82 | auto | 30% | 10% | 60% | tee stage: Black tagged |  |

## Stages

- **resolve**: ok: way/151985223 Sycamore Ridge Golf Club (Spring Hill, KS)
- **osm**: ok: 495 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **hole_renumber**: ok: hole 1 -> 10; hole 2 -> 11; hole 3 -> 12; hole 4 -> 13; hole 5 -> 14; hole 6 -> 15; hole 7 -> 16; hole 8 -> 17; hole 9 -> 18; hole 10 -> 1; hole 11 -> 2; hole 12 -> 3; hole 13 -> 4; hole 14 -> 5; hole 15 -> 6; hole 16 -> 7; hole 17 -> 8; hole 18 -> 9
- **scorecard**: ok: file (course_data/library/sycamore_ridge/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 1 review (inside OSM tee 930492853);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 102 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/sycamore_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/sycamore_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace
