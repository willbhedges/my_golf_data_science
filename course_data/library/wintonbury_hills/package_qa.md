# Wintonbury Hills Golf Course (Bloomfield, CT) - Black tees

Built 2026-10-30T21:25:31Z. OSM way/296554921. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 48 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 9 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.493 |
| mean_confidence | 0.825 |
| osm_score | 0.837 |

OSM features inside the course: buildings 5, golf=bunker 80, golf=cartpath 9, golf=fairway 17, golf=green 19, golf=hole 18, golf=lateral_water_hazard 1, golf=pin 18, golf=rough 22, golf=tee 48, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, single_trees 327, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 377 / 375 | 38 | 0.76 | check the flags | 39% | 0% | 61% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 365 / 365 | 52 | 0.71 | check the flags | 45% | 0% | 55% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee on a lidar pad (no OSM box at 365 yds) |
| 3 | 3 | 163 / 163 | 29 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 163 yds) |
| 4 | 5 | 526 / 523 | 172 | 0.81 | auto | 53% | 6% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 333 / 333 | 339 | 0.76 | check the flags | 40% | 0% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 430 / 430 | 186 | 0.82 | auto | 61% | 2% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 255 / 255 | 326 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 5 | 564 / 563 | 188 | 0.70 | check the flags | 42% | 0% | 58% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee on a lidar pad (no OSM box at 564 yds) |
| 9 | 3 | 190 / 190 | 347 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 412 / 410 | 22 | 0.78 | check the flags | 44% | 1% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 443 / 434 | 49 | 0.82 | auto | 59% | 0% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 168 / 168 | 37 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 5 | 551 / 543 | 173 | 0.84 | auto | 52% | 22% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 455 / 449 | 357 | 0.85 | auto | 60% | 13% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 427 / 424 | 349 | 0.85 | auto | 53% | 27% | 21% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 408 / 407 | 227 | 0.80 | auto | 45% | 12% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 230 / 230 | 198 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 414 / 412 | 202 | 0.78 | check the flags | 46% | 0% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/296554921 Wintonbury Hills Golf Course (Bloomfield, CT)
- **osm**: ok: 741 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 9 sets; lidar pads: 56 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 9 tee set(s))
- **imagery**: ok: course_data/packages/wintonbury_hills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/wintonbury_hills/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace
