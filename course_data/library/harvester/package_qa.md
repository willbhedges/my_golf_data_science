# The Harvester Golf Club (Rhodes, IA) - Black tees

Built 2026-10-30T11:51:02Z. OSM way/325314320. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 60 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.47 |
| mean_confidence | 0.799 |
| osm_score | 0.794 |

OSM features inside the course: buildings 11, built_up_landuse 1, golf=bunker 102, golf=cartpath 44, golf=fairway 27, golf=green 23, golf=hole 18, golf=lateral_water_hazard 3, golf=path 9, golf=rough 25, golf=tee 60, golf=water_hazard 1, holes_with_par 18, water_lines 13, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 425 / 423 | 14 | 0.77 | check the flags | 39% | 5% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 360 / 361 | 357 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 195 / 195 | 133 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 195 yds) |
| 4 | 5 | 575 / 575 | 210 | 0.77 | check the flags | 43% | 1% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 370 / 364 | 76 | 0.77 | check the flags | 44% | 0% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 5 | 560 / 561 | 268 | 0.70 | check the flags | 55% | 0% | 45% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee walked back along the hole line (no box at 560 yds) |
| 7 | 4 | 405 / 398 | 177 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 225 / 226 | 194 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 465 / 464 | 354 | 0.80 | check the flags | 52% | 1% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 470 / 464 | 343 | 0.77 | check the flags | 44% | 0% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 385 / 385 | 199 | 0.76 | check the flags | 37% | 1% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 410 / 410 | 200 | 0.81 | auto | 38% | 7% | 55% | tee stage: Black tee_centroid |  |
| 13 | 4 | 390 / 409 | 96 | 0.77 | check the flags | 44% | 0% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 3 | 230 / 230 | 104 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 230 yds) |
| 15 | 5 | 650 / 651 | 268 | 0.83 | auto | 50% | 3% | 47% | tee stage: Black tee_centroid |  |
| 16 | 4 | 480 / 497 | 100 | 0.80 | auto | 54% | 0% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 180 / 176 | 35 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 565 / 565 | 344 | 0.77 | check the flags | 82% | 0% | 18% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 565 yds) |

## Stages

- **resolve**: ok: way/325314320 The Harvester Golf Club (Marshall County, IA)
- **osm**: ok: 436 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 67 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/harvester/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/harvester/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 12 polygons (property_line 12); mode replace

## Warnings

- hole 13: measured 409 vs card 390 yds for Black (no OSM tee box at that yardage?)
- hole 16: measured 497 vs card 480 yds for Black (no OSM tee box at that yardage?)
