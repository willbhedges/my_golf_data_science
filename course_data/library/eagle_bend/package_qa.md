# Eagle Bend Golf Course (Lawrence, KS) - Blue tees

Built 2026-11-21T16:22:39Z. OSM way/151983193. Scorecard: file (course_data/library/eagle_bend/card_fix.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 74 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.344 |
| mean_confidence | 0.812 |
| osm_score | 0.855 |

OSM features inside the course: buildings 9, golf=bunker 23, golf=cartpath 24, golf=clubhouse 1, golf=driving_range 1, golf=fairway 24, golf=green 20, golf=hole 18, golf=pin 18, golf=tee 74, golf=water_hazard 4, holes_with_par 18, water_lines 7, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 397 / 398 | 99 | 0.79 | check the flags | 41% | 12% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 344 / 345 | 77 | 0.77 | check the flags | 30% | 16% | 54% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 5 | 545 / 544 | 359 | 0.78 | check the flags | 37% | 13% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 140 / 140 | 272 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 5 | 4 | 368 / 367 | 185 | 0.77 | check the flags | 34% | 13% | 53% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 439 / 440 | 275 | 0.81 | auto | 47% | 13% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 5 | 540 / 536 | 295 | 0.78 | check the flags | 32% | 21% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 147 / 147 | 303 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 9 | 4 | 410 / 409 | 175 | 0.76 | check the flags | 24% | 22% | 53% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 4 | 396 / 397 | 85 | 0.79 | check the flags | 40% | 13% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 4 | 366 / 367 | 91 | 0.74 | check the flags | 31% | 0% | 69% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 139 / 139 | 162 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 5 | 527 / 528 | 285 | 0.76 | check the flags | 38% | 2% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 368 / 369 | 250 | 0.80 | check the flags | 34% | 8% | 57% | tee stage: Blue tee_centroid |  |
| 15 | 4 | 320 / 321 | 81 | 0.73 | check the flags | 24% | 5% | 71% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 430 / 431 | 256 | 0.80 | check the flags | 37% | 23% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 3 | 175 / 175 | 183 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 5 | 491 / 491 | 320 | 0.76 | check the flags | 34% | 9% | 58% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/151983193 Eagle Bend Golf Course (Lawrence, KS)
- **osm**: ok: 266 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/eagle_bend/card_fix.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 50 candidate pads near hole starts (8 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/eagle_bend/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/eagle_bend/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -368 m2 {'cells': 366}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace
- **native_auto**: skipped: the mapper layer (agent_layers) wins
- **agent_layers**: ok: course_data/mapper/eagle_bend (41 zone edits on 10 holes, 0 tee(s) moved, 72 checked)
