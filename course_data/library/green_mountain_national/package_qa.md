# Green Mountain National Golf Course (Killington, VT) - Black tees

Built 2026-10-31T04:38:49Z. OSM way/570014047. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 70 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.434 |
| mean_confidence | 0.86 |
| osm_score | 0.887 |

OSM features inside the course: buildings 9, golf=bunker 43, golf=cartpath 24, golf=clubhouse 1, golf=driving_range 1, golf=fairway 25, golf=green 20, golf=hole 18, golf=rough 1, golf=tee 70, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, trees_polygons 19, water_lines 6, water_polygons 7

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 513 / 513 | 9 | 0.85 | auto | 37% | 33% | 30% | tee stage: Black tee_centroid |  |
| 2 | 4 | 412 / 412 | 26 | 0.78 | check the flags | 40% | 8% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 402 / 403 | 117 | 0.81 | auto | 49% | 14% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 439 / 439 | 135 | 0.87 | auto | 45% | 31% | 24% | tee stage: Black tee_centroid | green not visible on the NAIP 2021 imagery (NDVI -0.167 vs 0.117 on the course's other greens: bare soil / construction); the outline is OSM's |
| 5 | 3 | 183 / 183 | 298 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 183 yds) |
| 6 | 5 | 510 / 513 | 299 | 0.84 | auto | 44% | 34% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 151 / 151 | 340 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 361 / 354 | 234 | 0.79 | check the flags | 39% | 16% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 449 / 449 | 197 | 0.87 | auto | 40% | 37% | 23% | tee stage: Black tee_centroid |  |
| 10 | 4 | 423 / 423 | 11 | 0.85 | auto | 41% | 25% | 35% | tee stage: Black tee_centroid |  |
| 11 | 4 | 385 / 385 | 185 | 0.87 | auto | 55% | 13% | 32% | tee stage: Black tee_centroid |  |
| 12 | 4 | 394 / 394 | 354 | 0.87 | auto | 44% | 32% | 24% | tee stage: Black tee_centroid |  |
| 13 | 3 | 173 / 173 | 158 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 356 / 356 | 339 | 0.83 | auto | 44% | 29% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 466 / 466 | 27 | 0.84 | auto | 41% | 22% | 38% | tee stage: Black tee_centroid |  |
| 16 | 4 | 374 / 374 | 38 | 0.86 | auto | 44% | 26% | 30% | tee stage: Black tee_centroid |  |
| 17 | 3 | 204 / 204 | 174 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 394 / 394 | 203 | 0.85 | auto | 45% | 21% | 34% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: way/570014047 Green Mountain National Golf Course (Killington, VT)
- **osm**: ok: 292 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 99 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/green_mountain_national/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 17/18 greens visible as turf on NAIP 2021; NOT visible: holes 4
- **elevation**: ok: course_data/packages/green_mountain_national/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- greens of holes 4 are not visible as turf on the NAIP 2021 imagery (bare soil / construction / dead turf): pick another NAIP year (imagery/naip_years.py)
