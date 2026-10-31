# Crosswater Golf Course (Sunriver, OR) - Black tees

Built 2026-10-31T03:50:24Z. OSM relation/14236725. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 93 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.526 |
| mean_confidence | 0.875 |
| osm_score | 0.805 |

OSM features inside the course: buildings 18, built_up_landuse 1, golf=bunker 89, golf=cartpath 56, golf=fairway 24, golf=green 20, golf=hole 18, golf=pin 18, golf=rough 45, golf=tee 93, golf=water_hazard 3, holes_with_handicap 2, holes_with_par 18, long_grass_polygons 1, single_trees 6, water_lines 1, water_polygons 34

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 371 / 369 | 193 | 0.85 | auto | 42% | 8% | 51% | tee stage: Black tagged |  |
| 2 | 5 | 550 / 542 | 182 | 0.88 | auto | 58% | 0% | 42% | tee stage: Black tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 183 / 177 | 71 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 4 | 4 | 393 / 409 | 212 | 0.84 | auto | 39% | 6% | 55% | tee stage: Black tagged |  |
| 5 | 4 | 447 / 453 | 66 | 0.87 | auto | 50% | 3% | 47% | tee stage: Black tagged |  |
| 6 | 5 | 603 / 592 | 327 | 0.86 | auto | 50% | 0% | 50% | tee stage: Black tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 197 / 195 | 151 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 8 | 4 | 363 / 366 | 4 | 0.90 | auto | 64% | 0% | 36% | tee stage: Black tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 434 / 431 | 312 | 0.84 | auto | 42% | 0% | 57% | tee stage: Black tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 394 / 394 | 113 | 0.84 | auto | 55% | 0% | 45% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 454 / 454 | 4 | 0.81 | auto | 42% | 18% | 39% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 5 | 649 / 647 | 317 | 0.84 | auto | 62% | 10% | 28% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 157 / 158 | 7 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 457 / 458 | 223 | 0.85 | auto | 59% | 1% | 40% | tee stage: Black tee_centroid |  |
| 15 | 4 | 396 / 396 | 164 | 0.80 | auto | 42% | 0% | 57% | tee stage: Black tee_centroid |  |
| 16 | 5 | 569 / 570 | 56 | 0.84 | auto | 66% | 1% | 33% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 232 / 224 | 245 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 424 / 425 | 124 | 0.87 | auto | 65% | 0% | 35% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: relation/14236725 Crosswater Golf Course (Sunriver, OR)
- **osm**: ok: 845 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 47 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/crosswater/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/crosswater/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 28 polygons (outside 28); mode replace

## Warnings

- ignored 1 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 764304886
- hole 4: measured 409 vs card 393 yds for Black (no OSM tee box at that yardage?)
