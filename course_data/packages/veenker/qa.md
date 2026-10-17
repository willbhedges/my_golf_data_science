# Veenker Memorial Golf Course (Ames, IA) - Blue tees

Built 2026-10-17T04:28:14Z. OSM way/44804299. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'White' not on the card (sets: Blue, Gold, Red)).

**WARNING: requested tee set 'White' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, Gold, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 43 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.303 |
| mean_confidence | 0.859 |
| osm_score | 0.861 |

OSM features inside the course: buildings 8, golf=bunker 27, golf=cartpath 5, golf=fairway 30, golf=green 26, golf=hole 18, golf=lateral_water_hazard 2, golf=path 38, golf=rough 1, golf=tee 43, holes_with_handicap 18, holes_with_par 18, water_lines 1, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 435 / 434 | 176 | 0.85 | auto | 37% | 48% | 15% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 334 / 338 | 249 | 0.87 | auto | 18% | 69% | 13% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 333 / 318 | 30 | 0.87 | auto | 22% | 62% | 17% | tee stage: Blue tee_centroid |  |
| 4 | 4 | 349 / 348 | 298 | 0.84 | auto | 35% | 44% | 21% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 402 / 401 | 169 | 0.85 | auto | 31% | 39% | 29% | tee stage: Blue tee_centroid |  |
| 6 | 3 | 210 / 209 | 88 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 5 | 590 / 591 | 66 | 0.77 | check the flags | 24% | 61% | 16% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 590 yds) |
| 8 | 3 | 181 / 174 | 29 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 537 / 538 | 294 | 0.88 | auto | 37% | 47% | 16% | tee stage: Blue tee_centroid |  |
| 10 | 5 | 560 / 568 | 146 | 0.84 | auto | 30% | 55% | 16% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 155 / 155 | 242 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 330 / 331 | 248 | 0.76 | check the flags | 23% | 58% | 19% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 330 yds) |
| 13 | 3 | 160 / 160 | 56 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 416 / 416 | 339 | 0.83 | auto | 26% | 56% | 18% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 420 / 419 | 237 | 0.81 | auto | 35% | 32% | 33% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 544 / 550 | 140 | 0.79 | check the flags | 45% | 40% | 15% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 544 yds) |
| 17 | 3 | 190 / 190 | 118 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 5 | 534 / 533 | 335 | 0.85 | auto | 32% | 56% | 13% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/44804299 Veenker Memorial Golf Course (Ames, IA)
- **osm**: ok: 598 features
- **scorecard**: ok: golfify (golfify)
- **tees**: ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for 3 sets; lidar pads: 36 candidate pads near hole starts, 4 placement(s) on one
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/veenker/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/veenker/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: ok: segment gap-fill ariadgolf-v4@43ee2944 (+3 zones on 2 holes, +0 greens, 18 tee candidates)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 13 polygons (property_line 13); mode replace

## Warnings

- requested tee set 'White' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, Gold, Red
