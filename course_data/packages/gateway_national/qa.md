# Gateway National Golf Links (Madison, IL) - Back tees

Built 2026-10-17T14:40:18Z. OSM way/782435512. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Blue' not on the card (sets: Back, Champions, Forward, Middle, The Tips)).

**WARNING: requested tee set 'Blue' is not on the card; using 'Back' instead (allow_substitute). Sets on the card: Back, Champions, Forward, Middle, The Tips**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 75 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 0 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.473 |
| mean_confidence | 0.835 |
| osm_score | 0.695 |

OSM features inside the course: buildings 4, golf=bunker 73, golf=cartpath 23, golf=fairway 28, golf=green 20, golf=hole 18, golf=pin 18, golf=rough 1, golf=tee 75, golf=water_hazard 10, holes_with_handicap 18, holes_with_par 18, single_trees 1, water_polygons 11

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 376 / 376 | 318 | 0.80 | auto | 54% | 0% | 46% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 422 / 423 | 237 | 0.85 | auto | 57% | 0% | 42% | tee stage: Back tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 5 | 630 / 630 | 220 | 0.81 | auto | 46% | 0% | 54% | tee stage: Back tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 180 / 180 | 189 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 5 | 4 | 452 / 453 | 80 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 5 | 530 / 531 | 244 | 0.78 | check the flags | 47% | 0% | 53% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 180 / 180 | 61 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 8 | 4 | 408 / 409 | 54 | 0.67 | check the flags | 34% | 0% | 66% | tee stage: Back lidar_pad | tee: tee stage: Back lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Back tee on a lidar pad (no OSM box at 408 yds) |
| 9 | 4 | 390 / 391 | 58 | 0.78 | check the flags | 35% | 0% | 65% | tee stage: Back tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 271 / 272 | 254 | 0.80 | check the flags | 39% | 0% | 61% | tee stage: Back tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 416 / 417 | 236 | 0.81 | auto | 43% | 0% | 57% | tee stage: Back tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 131 / 131 | 269 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 13 | 5 | 533 / 534 | 65 | 0.81 | auto | 57% | 0% | 43% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 3 | 200 / 200 | 74 | 0.93 | auto | 100% | 0% | 0% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis |
| 15 | 4 | 428 / 427 | 250 | 0.79 | check the flags | 51% | 0% | 49% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 354 / 354 | 44 | 0.82 | auto | 50% | 0% | 50% | tee stage: Back tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 195 / 195 | 39 | 0.96 | auto | 100% | 0% | 0% | tee stage: Back tee_centroid |  |
| 18 | 5 | 527 / 533 | 155 | 0.81 | auto | 56% | 0% | 44% | tee stage: Back tee_axis | tee: tee stage: Back tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/782435512 Gateway National Golf Links (Madison, IL)
- **osm**: ok: 455 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 70 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/gateway_national/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/gateway_national/imagery/dem.tif (18/18 holes)
- **vision**: missing: no vision_any layers for 'gateway_national' (FileNotFoundError: course_data/vision_any/gateway_national/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

## Warnings

- requested tee set 'Blue' is not on the card; using 'Back' instead (allow_substitute). Sets on the card: Back, Champions, Forward, Middle, The Tips
- vision: missing: no vision_any layers for 'gateway_national' (FileNotFoundError: course_data/vision_any/gateway_national/raw (not fetched)); add the course to course_da; trees / long grass come from OSM only
