# Caledonia Golf & Fish Club (Pawleys Island, SC) - Pintail tees

Built 2026-10-31T03:53:50Z. OSM way/342296678. Scorecard: golfify (golfify). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 59 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.496 |
| mean_confidence | 0.86 |
| osm_score | 0.899 |

OSM features inside the course: golf=bunker 83, golf=cartpath 23, golf=fairway 34, golf=green 18, golf=hole 18, golf=pin 18, golf=rough 3, golf=tee 59, golf=water_hazard 5, holes_with_par 18, water_lines 4, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 376 / 377 | 104 | 0.73 | check the flags | 44% | 34% | 22% | tee stage: Pintail walkback | tee: tee stage: Pintail walkback; Pintail tee walked back along the hole line (no box at 376 yds) |
| 2 | 5 | 571 / 569 | 27 | 0.85 | auto | 54% | 26% | 20% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 3 | 3 | 187 / 187 | 28 | 0.82 | auto | 100% | 0% | 0% | tee stage: Pintail walkback | tee: tee stage: Pintail walkback; Pintail tee walked back along the hole line (no box at 187 yds) |
| 4 | 4 | 396 / 397 | 254 | 0.86 | auto | 50% | 35% | 16% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 5 | 4 | 419 / 412 | 263 | 0.85 | auto | 41% | 45% | 14% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 6 | 3 | 157 / 157 | 188 | 0.93 | auto | 100% | 0% | 0% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 7 | 4 | 399 / 390 | 90 | 0.88 | auto | 59% | 31% | 10% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 8 | 5 | 528 / 523 | 255 | 0.84 | auto | 52% | 23% | 25% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 9 | 3 | 118 / 119 | 44 | 0.86 | auto | 100% | 0% | 0% | tee stage: Pintail lidar_pad | tee: tee stage: Pintail lidar_pad; Pintail tee on a lidar pad (no OSM box at 118 yds) |
| 10 | 5 | 553 / 542 | 94 | 0.84 | auto | 54% | 18% | 27% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 11 | 3 | 167 / 167 | 2 | 0.96 | auto | 100% | 0% | 0% | tee stage: Pintail tee_centroid |  |
| 12 | 4 | 405 / 405 | 46 | 0.85 | auto | 43% | 42% | 15% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 13 | 4 | 398 / 385 | 268 | 0.85 | auto | 35% | 52% | 13% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 14 | 4 | 415 / 411 | 277 | 0.87 | auto | 56% | 33% | 11% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 15 | 4 | 462 / 462 | 81 | 0.87 | auto | 55% | 33% | 12% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 16 | 4 | 417 / 414 | 247 | 0.85 | auto | 41% | 41% | 18% | tee stage: Pintail tee_axis | tee: tee stage: Pintail tee_axis |
| 17 | 3 | 175 / 175 | 10 | 0.96 | auto | 100% | 0% | 0% | tee stage: Pintail tee_centroid |  |
| 18 | 4 | 383 / 396 | 179 | 0.79 | check the flags | 62% | 18% | 20% | tee stage: Pintail lidar_pad | tee: tee stage: Pintail lidar_pad; Pintail tee on a lidar pad (no OSM box at 383 yds) |

## Stages

- **resolve**: ok: way/342296678 Caledonia Golf & Fish Club (Pawleys Island, SC)
- **osm**: ok: 444 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 84 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/caledonia/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/caledonia/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 14 polygons (outside 14); mode replace

## Warnings

- ignored 4 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 891729733, 891729734, 1012514187, 1012514188
