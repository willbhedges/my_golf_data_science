# Pine Dunes Resort & Golf Club (Frankston, TX) - Gold tees

Built 2026-10-17T18:01:19Z. OSM none/0. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 45 |
| tees_with_colour | 18 |
| holes_with_trees_or_long_grass_in_landing_zone | 0 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.398 |
| mean_confidence | 0.869 |
| osm_score | 0.68 |

OSM features inside the course: buildings 4, golf=bunker 87, golf=cartpath 15, golf=clubhouse 1, golf=driving_range 2, golf=fairway 22, golf=green 21, golf=hole 18, golf=lateral_water_hazard 1, golf=rough 1, golf=tee 45, golf=water_hazard 5, holes_with_par 18, single_trees 4, tees_with_colour 18, water_lines 1, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 391 / 386 | 250 | 0.80 | auto | 29% | 0% | 71% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 348 / 341 | 324 | 0.81 | auto | 31% | 0% | 69% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 160 / 154 | 68 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 4 | 4 | 463 / 445 | 142 | 0.81 | auto | 33% | 0% | 67% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 5 | 501 / 494 | 11 | 0.86 | auto | 50% | 0% | 50% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 3 | 254 / 250 | 16 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 7 | 4 | 443 / 439 | 97 | 0.90 | auto | 63% | 0% | 37% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 4 | 389 / 387 | 252 | 0.80 | check the flags | 28% | 0% | 72% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 5 | 551 / 552 | 205 | 0.82 | auto | 35% | 0% | 65% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 439 / 433 | 10 | 0.83 | auto | 41% | 0% | 59% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 5 | 605 / 602 | 65 | 0.85 | auto | 47% | 0% | 53% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 204 / 201 | 116 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 13 | 4 | 426 / 425 | 271 | 0.84 | auto | 44% | 0% | 56% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 434 / 430 | 94 | 0.86 | auto | 50% | 0% | 50% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 344 / 335 | 275 | 0.81 | auto | 31% | 0% | 69% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 3 | 178 / 176 | 295 | 1.00 | auto | 100% | 0% | 0% | tee stage: Gold tagged |  |
| 17 | 4 | 475 / 474 | 152 | 0.83 | auto | 41% | 0% | 59% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 512 / 501 | 208 | 0.81 | auto | 34% | 0% | 66% | tee stage: Gold tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: none/0 Pine Dunes Resort & Golf Club (Frankston, TX)
- **osm**: ok: 287 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: failed: MemoryError: Unable to allocate 1.53 TiB for an array with shape (2, 324001, 324001) and data type int64
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/pine_dunes/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/pine_dunes/imagery/dem.tif (18/18 holes)
- **vision**: missing: no vision_any layers for 'pine_dunes' (FileNotFoundError: course_data/vision_any/pine_dunes/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

## Warnings

- hole 4: measured 445 vs card 463 yds for Gold (no OSM tee box at that yardage?)
- vision: missing: no vision_any layers for 'pine_dunes' (FileNotFoundError: course_data/vision_any/pine_dunes/raw (not fetched)); add the course to course_data/vision_an; trees / long grass come from OSM only
