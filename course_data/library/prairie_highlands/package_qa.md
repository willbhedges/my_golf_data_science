# Prairie Highlands Golf Course (Olathe, KS) - Black tees

Built 2026-10-30T03:25:25Z. OSM relation/11701165. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 74 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.424 |
| mean_confidence | 0.84 |
| osm_score | 0.856 |

OSM features inside the course: buildings 9, golf=bunker 58, golf=cartpath 29, golf=fairway 21, golf=green 19, golf=hole 18, golf=pin 18, golf=rough 15, golf=tee 74, golf=water_hazard 3, holes_with_par 18, trees_polygons 2, water_lines 9, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 425 / 424 | 343 | 0.80 | auto | 41% | 1% | 58% | tee stage: Black tee_centroid |  |
| 2 | 4 | 417 / 418 | 66 | 0.81 | auto | 44% | 0% | 56% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 409 / 410 | 99 | 0.79 | check the flags | 50% | 1% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 585 / 584 | 185 | 0.78 | check the flags | 41% | 8% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 227 / 227 | 285 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 6 | 4 | 377 / 377 | 225 | 0.77 | check the flags | 38% | 5% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 457 / 456 | 156 | 0.84 | auto | 47% | 14% | 39% | tee stage: Black tee_centroid |  |
| 8 | 3 | 165 / 165 | 210 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 5 | 570 / 567 | 352 | 0.80 | check the flags | 40% | 17% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 392 / 392 | 212 | 0.81 | auto | 31% | 39% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 400 / 388 | 192 | 0.79 | check the flags | 45% | 4% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 5 | 553 / 550 | 5 | 0.78 | check the flags | 41% | 8% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 395 / 394 | 4 | 0.83 | auto | 50% | 3% | 47% | tee stage: Black tee_centroid |  |
| 14 | 3 | 201 / 201 | 152 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 15 | 5 | 537 / 537 | 340 | 0.86 | auto | 49% | 21% | 30% | tee stage: Black tee_centroid |  |
| 16 | 3 | 181 / 181 | 346 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 17 | 4 | 340 / 340 | 161 | 0.81 | auto | 45% | 0% | 55% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 435 / 434 | 158 | 0.78 | check the flags | 32% | 3% | 65% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: relation/11701165 Prairie Highlands Golf Course (Olathe, KS)
- **osm**: ok: 719 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 69 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/prairie_highlands/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/prairie_highlands/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 24 polygons (outside 24); mode replace
