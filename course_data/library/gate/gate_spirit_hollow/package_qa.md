# Spirit Hollow Golf Course (Burlington, IA) - Black tees

Built 2026-10-29T21:19:17Z. OSM relation/13353211. Scorecard: file (course_data/tees/scorecard.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 103 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.34 |
| mean_confidence | 0.805 |
| osm_score | 0.811 |

OSM features inside the course: buildings 7, golf=bunker 50, golf=cartpath 4, golf=driving_range 1, golf=fairway 20, golf=green 25, golf=hole 18, golf=lateral_water_hazard 11, golf=path 30, golf=rough 34, golf=tee 103, holes_with_par 18, water_lines 16, water_polygons 14

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 391 / 391 | 153 | 0.77 | check the flags | 22% | 30% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 5 | 507 / 508 | 262 | 0.76 | check the flags | 25% | 21% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 148 / 148 | 3 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 532 / 531 | 342 | 0.76 | check the flags | 35% | 6% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 384 / 384 | 12 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 408 / 409 | 94 | 0.73 | check the flags | 29% | 0% | 71% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 154 / 154 | 193 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 383 / 384 | 264 | 0.78 | check the flags | 34% | 15% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 365 / 368 | 78 | 0.78 | check the flags | 22% | 32% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 5 | 502 / 501 | 30 | 0.80 | auto | 53% | 1% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 338 / 336 | 64 | 0.75 | check the flags | 26% | 11% | 63% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 186 / 186 | 223 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 409 / 409 | 180 | 0.75 | check the flags | 35% | 2% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 393 / 393 | 208 | 0.76 | check the flags | 36% | 7% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 3 | 145 / 144 | 344 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 378 / 379 | 96 | 0.76 | check the flags | 32% | 10% | 58% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 445 / 445 | 217 | 0.77 | check the flags | 38% | 6% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 521 / 521 | 333 | 0.82 | auto | 40% | 12% | 48% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: relation/13353211 Spirit Hollow Golf Course (Des Moines County, IA)
- **osm**: ok: 406 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/tees/scorecard.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 69 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/gate_spirit_hollow/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/gate_spirit_hollow/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 21 polygons (property_line 21); mode replace
