# Troon North Golf Club (Scottsdale, AZ) - Black tees

Built 2026-11-03T15:54:37Z. OSM relation/1389558. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 117 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.421 |
| mean_confidence | 0.872 |
| osm_score | 0.784 |

OSM features inside the course: golf=bunker 119, golf=cartpath 9, golf=fairway 48, golf=green 37, golf=hole 18, golf=pin 36, golf=rough 25, golf=tee 117, golf=water_hazard 4, holes_with_handicap 18, holes_with_par 18, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 444 / 445 | 267 | 0.88 | auto | 38% | 44% | 17% | tee stage: Black tee_centroid |  |
| 2 | 3 | 172 / 172 | 8 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 5 | 556 / 551 | 243 | 0.83 | auto | 48% | 24% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 420 / 417 | 287 | 0.90 | auto | 63% | 35% | 2% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 464 / 463 | 199 | 0.91 | auto | 57% | 30% | 12% | tee stage: Black tee_centroid |  |
| 6 | 4 | 306 / 304 | 70 | 0.86 | auto | 36% | 52% | 12% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 205 / 205 | 65 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 408 / 408 | 119 | 0.87 | auto | 36% | 62% | 2% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 5 | 530 / 531 | 79 | 0.88 | auto | 48% | 50% | 2% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 396 / 394 | 84 | 0.85 | auto | 42% | 41% | 17% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 5 | 512 / 513 | 110 | 0.84 | auto | 39% | 42% | 19% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 4 | 426 / 427 | 256 | 0.83 | auto | 35% | 38% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 222 / 222 | 94 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 570 / 570 | 251 | 0.85 | auto | 32% | 54% | 14% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 299 / 298 | 2 | 0.82 | auto | 29% | 28% | 43% | tee stage: Black tee_centroid |  |
| 16 | 3 | 244 / 240 | 303 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 495 / 496 | 275 | 0.83 | auto | 37% | 37% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 370 / 370 | 44 | 0.82 | auto | 47% | 21% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/1389558 Troon North Golf Club (Scottsdale, AZ)
- **osm**: ok: 2446 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 146 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/troon_north/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/troon_north/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 34 polygons (outside 34); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole way names: Pinnacle Course 18, Monument Course 18); kept 'Monument Course' (named in the request), 18 ways; ignored 18
- ignored 4 practice / driving-range tee box(es): OSM 1120331229, 1120331230, 1120331231, 1120331233
- ignored 10 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 731646897, 733110749, 733121972, 733123625, 733127369, 733131640, 733132163, 733132458
