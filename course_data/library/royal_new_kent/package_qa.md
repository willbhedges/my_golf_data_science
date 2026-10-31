# Royal New Kent Golf Club (Providence Forge, VA) - Black tees

Built 2026-10-31T04:54:14Z. OSM relation/6209148. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 89 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 9 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.452 |
| mean_confidence | 0.827 |
| osm_score | 0.819 |

OSM features inside the course: buildings 8, built_up_landuse 1, golf=bunker 112, golf=cartpath 23, golf=clubhouse 1, golf=fairway 39, golf=green 20, golf=hole 18, golf=lateral_water_hazard 2, golf=path 5, golf=pin 1, golf=rough 52, golf=tee 89, holes_with_handicap 2, holes_with_par 18, single_trees 12, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 378 / 378 | 356 | 0.80 | check the flags | 39% | 1% | 61% | tee stage: Black tee_centroid |  |
| 2 | 5 | 512 / 512 | 270 | 0.82 | auto | 42% | 10% | 48% | tee stage: Black tee_centroid |  |
| 3 | 3 | 160 / 160 | 175 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 381 / 392 | 170 | 0.75 | check the flags | 34% | 4% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 5 | 541 / 537 | 198 | 0.76 | check the flags | 36% | 3% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 392 / 391 | 2 | 0.82 | auto | 47% | 0% | 53% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 173 / 173 | 347 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 386 / 386 | 11 | 0.76 | check the flags | 38% | 2% | 61% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 337 / 338 | 100 | 0.80 | auto | 41% | 0% | 59% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 537 / 538 | 58 | 0.77 | check the flags | 67% | 0% | 33% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee on a lidar pad (no OSM box at 537 yds) |
| 11 | 4 | 378 / 377 | 302 | 0.78 | check the flags | 37% | 16% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 176 / 176 | 24 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 334 / 337 | 98 | 0.81 | auto | 53% | 9% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 330 / 329 | 355 | 0.75 | check the flags | 32% | 3% | 64% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 3 | 208 / 208 | 101 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 16 | 4 | 442 / 441 | 186 | 0.84 | auto | 54% | 0% | 46% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 5 | 509 / 510 | 230 | 0.81 | auto | 46% | 13% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 386 / 387 | 253 | 0.88 | auto | 69% | 0% | 31% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: relation/6209148 Royal New Kent Golf Club (New Kent County, VA)
- **osm**: ok: 888 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 84 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/royal_new_kent/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/royal_new_kent/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 16 polygons (outside 16); mode replace

## Warnings

- ignored 1 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1442108863
- hole 10 Invicta: CHECK, tee was on a building (OSM 734612343): moved 17 yds forward off it
- hole 10 Gold: CHECK, tee was on a building (OSM 734612343): moved 9 yds forward off it
