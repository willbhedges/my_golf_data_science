# Annbriar Golf Course (Waterloo, IL) - Black tees

Built 2026-10-30T11:57:30Z. OSM way/1466372251. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 98 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.465 |
| mean_confidence | 0.848 |
| osm_score | 0.864 |

OSM features inside the course: buildings 7, golf=bunker 67, golf=cartpath 48, golf=clubhouse 1, golf=driving_range 1, golf=fairway 21, golf=green 20, golf=hole 18, golf=lateral_water_hazard 3, golf=path 26, golf=pin 18, golf=rough 72, golf=tee 98, golf=water_hazard 3, holes_with_handicap 18, holes_with_par 18, trees_polygons 1, water_lines 2, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 337 / 338 | 72 | 0.77 | check the flags | 41% | 0% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 395 / 394 | 104 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 373 / 374 | 282 | 0.82 | auto | 60% | 1% | 39% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 190 / 191 | 263 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 5 | 496 / 497 | 79 | 0.81 | auto | 46% | 0% | 55% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 378 / 379 | 280 | 0.88 | auto | 65% | 6% | 29% | tee stage: Black tee_centroid |  |
| 7 | 3 | 155 / 155 | 282 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 8 | 4 | 415 / 415 | 196 | 0.83 | auto | 45% | 8% | 47% | tee stage: Black tee_centroid |  |
| 9 | 5 | 475 / 475 | 348 | 0.71 | check the flags | 33% | 19% | 48% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 475 yds) |
| 10 | 4 | 382 / 382 | 348 | 0.82 | auto | 42% | 10% | 47% | tee stage: Black tee_centroid |  |
| 11 | 4 | 404 / 405 | 248 | 0.87 | auto | 46% | 44% | 10% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 353 / 353 | 212 | 0.80 | check the flags | 50% | 5% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 356 / 354 | 73 | 0.79 | check the flags | 49% | 2% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 492 / 492 | 236 | 0.87 | auto | 38% | 39% | 23% | tee stage: Black tee_centroid |  |
| 15 | 3 | 151 / 151 | 136 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 16 | 4 | 446 / 444 | 157 | 0.81 | auto | 44% | 20% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 147 / 147 | 332 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 5 | 572 / 572 | 349 | 0.83 | auto | 42% | 13% | 45% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: way/1466372251 Annbriar Golf Course (Waterloo, IL)
- **osm**: ok: 444 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 104 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/annbriar/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/annbriar/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace
