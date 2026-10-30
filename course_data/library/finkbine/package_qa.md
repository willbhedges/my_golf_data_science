# Finkbine Golf Course (Iowa City, IA) - Black tees

Built 2026-10-30T11:57:09Z. OSM way/964660601. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 61 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.37 |
| mean_confidence | 0.822 |
| osm_score | 0.874 |

OSM features inside the course: buildings 13, golf=bunker 71, golf=cartpath 18, golf=clubhouse 1, golf=driving_range 1, golf=fairway 24, golf=green 26, golf=hole 18, golf=rough 5, golf=tee 61, golf=water_hazard 2, holes_with_par 18, single_trees 10, trees_polygons 8, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 415 / 415 | 310 | 0.70 | check the flags | 34% | 29% | 37% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 415 yds) |
| 2 | 5 | 537 / 537 | 315 | 0.85 | auto | 27% | 45% | 27% | tee stage: Black tee_centroid |  |
| 3 | 4 | 394 / 394 | 167 | 0.79 | check the flags | 36% | 21% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 201 / 201 | 51 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 368 / 368 | 223 | 0.79 | check the flags | 35% | 18% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 524 / 525 | 66 | 0.82 | auto | 34% | 20% | 45% | tee stage: Black tee_centroid |  |
| 7 | 4 | 382 / 382 | 346 | 0.83 | auto | 37% | 38% | 25% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 207 / 207 | 143 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 449 / 461 | 130 | 0.79 | check the flags | 40% | 15% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 449 / 449 | 326 | 0.69 | check the flags | 34% | 27% | 38% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 449 yds) |
| 11 | 5 | 562 / 562 | 335 | 0.81 | auto | 32% | 38% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 389 / 389 | 125 | 0.74 | check the flags | 21% | 51% | 28% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 389 yds) |
| 13 | 3 | 199 / 199 | 8 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 199 yds) |
| 14 | 4 | 413 / 407 | 128 | 0.84 | auto | 52% | 22% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 486 / 487 | 296 | 0.88 | auto | 62% | 9% | 29% | tee stage: Black tee_centroid |  |
| 16 | 4 | 398 / 398 | 133 | 0.80 | check the flags | 34% | 25% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 195 / 195 | 32 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 449 / 449 | 204 | 0.81 | auto | 41% | 25% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/964660601 Finkbine Golf Course (Iowa City, IA)
- **osm**: ok: 951 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 27 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/finkbine/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/finkbine/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 7 polygons (property_line 7); mode replace
