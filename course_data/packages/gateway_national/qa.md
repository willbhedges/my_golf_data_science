# Gateway National Golf Links (Madison, IL) - Back tees

Built 2026-11-03T21:30:48Z. OSM way/782435512. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Blue' not on the card (sets: Back, Champions, Forward, Middle, The Tips)).

**WARNING: requested tee set 'Blue' is not on the card; using 'Back' instead (allow_substitute). Sets on the card: Back, Champions, Forward, Middle, The Tips**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 75 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.473 |
| mean_confidence | 0.881 |
| osm_score | 0.895 |

OSM features inside the course: buildings 4, golf=bunker 73, golf=cartpath 23, golf=fairway 28, golf=green 20, golf=hole 18, golf=pin 18, golf=rough 1, golf=tee 75, golf=water_hazard 10, holes_with_handicap 18, holes_with_par 18, single_trees 1, water_polygons 11

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 376 / 376 | 318 | 0.85 | auto | 54% | 26% | 21% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 2 | 4 | 422 / 423 | 237 | 0.89 | auto | 57% | 22% | 20% | tee stage: Back tee_centroid |  |
| 3 | 5 | 630 / 630 | 220 | 0.88 | auto | 44% | 35% | 21% | tee stage: Back tee_centroid |  |
| 4 | 3 | 180 / 180 | 189 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 5 | 4 | 452 / 453 | 80 | 0.84 | auto | 45% | 34% | 22% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 6 | 5 | 530 / 531 | 244 | 0.84 | auto | 47% | 31% | 22% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 7 | 3 | 180 / 180 | 61 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 8 | 4 | 408 / 412 | 56 | 0.84 | auto | 34% | 50% | 17% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 9 | 4 | 390 / 391 | 58 | 0.83 | auto | 35% | 26% | 39% | tee stage: Back tee_centroid |  |
| 10 | 4 | 271 / 272 | 254 | 0.85 | auto | 39% | 28% | 32% | tee stage: Back tee_centroid |  |
| 11 | 4 | 416 / 417 | 236 | 0.87 | auto | 43% | 30% | 27% | tee stage: Back tee_centroid |  |
| 12 | 3 | 131 / 131 | 269 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 13 | 5 | 533 / 534 | 65 | 0.84 | auto | 57% | 17% | 26% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 14 | 3 | 200 / 200 | 74 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 15 | 4 | 428 / 427 | 250 | 0.85 | auto | 50% | 32% | 18% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 16 | 4 | 354 / 354 | 44 | 0.88 | auto | 50% | 27% | 23% | tee stage: Back tee_centroid |  |
| 17 | 3 | 195 / 195 | 39 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 18 | 5 | 527 / 522 | 155 | 0.86 | auto | 58% | 24% | 18% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |

## Stages

- **resolve**: ok: way/782435512 Gateway National Golf Links (Madison, IL)
- **osm**: ok: 455 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 70 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/gateway_national/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gateway_national/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -1034 m2 {'road': 1033, 'cells': 1}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace
- **native_auto**: ok: 13 holes, sides 1 both, 2 both, 3 both, 5 both, 6 both, 8 both, 9 L, 10 both, 11 both, 13 both, 15 both, 16 both, 18 L

## Warnings

- requested tee set 'Blue' is not on the card; using 'Back' instead (allow_substitute). Sets on the card: Back, Champions, Forward, Middle, The Tips
