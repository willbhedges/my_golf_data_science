# Torrey Pines South Course (La Jolla, CA) - Black tees

Built 2026-10-30T21:54:28Z. OSM way/35679036. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 84 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.357 |
| mean_confidence | 0.826 |
| osm_score | 0.871 |

OSM features inside the course: buildings 5, golf=bunker 82, golf=cartpath 28, golf=fairway 18, golf=green 18, golf=hole 18, golf=pin 18, golf=tee 84, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, single_trees 196, tees_with_colour 1, tees_with_ref 1, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 451 / 451 | 235 | 0.79 | check the flags | 34% | 3% | 63% | tee stage: Black tee_centroid |  |
| 2 | 4 | 389 / 388 | 167 | 0.80 | auto | 39% | 4% | 57% | tee stage: Black tee_centroid |  |
| 3 | 3 | 201 / 195 | 203 | 1.00 | auto | 100% | 0% | 0% | tee stage: Black tagged |  |
| 4 | 4 | 490 / 489 | 353 | 0.78 | check the flags | 46% | 0% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 454 / 453 | 166 | 0.79 | check the flags | 34% | 3% | 63% | tee stage: Black tee_centroid |  |
| 6 | 5 | 564 / 563 | 20 | 0.82 | auto | 39% | 11% | 50% | tee stage: Black tee_centroid |  |
| 7 | 4 | 462 / 461 | 185 | 0.79 | check the flags | 32% | 8% | 59% | tee stage: Black tee_centroid |  |
| 8 | 3 | 177 / 177 | 70 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 5 | 615 / 613 | 175 | 0.80 | check the flags | 32% | 29% | 39% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 454 / 453 | 183 | 0.70 | check the flags | 33% | 13% | 54% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 454 yds) |
| 11 | 3 | 225 / 225 | 250 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 12 | 4 | 505 / 505 | 289 | 0.78 | check the flags | 32% | 5% | 63% | tee stage: Black tee_centroid |  |
| 13 | 5 | 621 / 622 | 123 | 0.80 | check the flags | 36% | 7% | 57% | tee stage: Black tee_centroid |  |
| 14 | 4 | 437 / 436 | 343 | 0.79 | check the flags | 35% | 6% | 59% | tee stage: Black tee_centroid |  |
| 15 | 4 | 517 / 516 | 350 | 0.78 | check the flags | 28% | 8% | 64% | tee stage: Black tee_centroid |  |
| 16 | 3 | 227 / 227 | 228 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 443 / 442 | 40 | 0.78 | check the flags | 42% | 7% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 570 / 568 | 348 | 0.82 | auto | 38% | 13% | 50% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: way/35679036 Torrey Pines South Course (La Jolla, CA)
- **osm**: ok: 995 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 71 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/torrey_pines/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/torrey_pines/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 8 polygons (outside 8); mode replace

## Warnings

- ignored 8 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 892086600, 892086601, 892086603, 892086604, 892086607, 902999850, 903003227, 903006041
