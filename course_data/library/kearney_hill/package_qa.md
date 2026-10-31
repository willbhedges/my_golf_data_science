# Kearney Hill Golf Links (Lexington, KY) - Black tees

Built 2026-10-31T01:46:09Z. OSM way/285529283. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 53 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 8 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.444 |
| mean_confidence | 0.817 |
| osm_score | 0.803 |

OSM features inside the course: buildings 7, golf=bunker 66, golf=cartpath 14, golf=driving_range 1, golf=fairway 19, golf=green 21, golf=hole 18, golf=lateral_water_hazard 3, golf=tee 53, holes_with_handicap 18, holes_with_par 18, single_trees 69, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 435 / 435 | 305 | 0.83 | auto | 40% | 19% | 42% | tee stage: Black tee_centroid |  |
| 2 | 3 | 195 / 195 | 308 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 5 | 470 / 471 | 52 | 0.78 | check the flags | 42% | 6% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 450 / 451 | 272 | 0.76 | check the flags | 40% | 1% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 385 / 386 | 98 | 0.76 | check the flags | 38% | 0% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 350 / 347 | 300 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 5 | 575 / 576 | 123 | 0.80 | check the flags | 48% | 8% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 210 / 210 | 130 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 470 / 470 | 171 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 385 / 385 | 121 | 0.74 | check the flags | 34% | 0% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 390 / 387 | 344 | 0.78 | check the flags | 37% | 11% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 210 / 209 | 330 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 465 / 465 | 181 | 0.78 | check the flags | 41% | 7% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 540 / 538 | 315 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 3 | 190 / 190 | 139 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 415 / 415 | 342 | 0.86 | auto | 73% | 2% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 4 | 430 / 426 | 218 | 0.79 | check the flags | 52% | 0% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 535 / 534 | 135 | 0.76 | check the flags | 39% | 0% | 61% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/285529283 Kearney Hill Golf Links (Lexington, KY)
- **osm**: ok: 341 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 1 sets; lidar pads: 63 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/kearney_hill/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/kearney_hill/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace

## Warnings

- scorecard (opengolfapi): Black: holes sum to 7100 but the source says 7079 (+21): mixed card versions
