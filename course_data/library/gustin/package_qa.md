# A. L. Gustin Golf Course (Columbia, MO) - Black tees

Built 2026-11-02T13:25:07Z. OSM way/449108205. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 52 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.394 |
| mean_confidence | 0.812 |
| osm_score | 0.879 |

OSM features inside the course: buildings 6, golf=bunker 38, golf=cartpath 13, golf=clubhouse 1, golf=fairway 22, golf=green 19, golf=hole 18, golf=tee 52, golf=water_hazard 1, holes_with_par 18, trees_polygons 3, water_lines 5, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 492 / 487 | 201 | 0.79 | check the flags | 35% | 20% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 3 | 162 / 158 | 171 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 440 / 440 | 221 | 0.81 | auto | 45% | 18% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 384 / 385 | 94 | 0.86 | auto | 56% | 25% | 18% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 201 / 201 | 356 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 418 / 419 | 292 | 0.75 | check the flags | 31% | 6% | 63% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 369 / 364 | 56 | 0.72 | check the flags | 36% | 17% | 46% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 369 yds) |
| 8 | 4 | 376 / 372 | 95 | 0.83 | auto | 50% | 22% | 28% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 338 / 338 | 44 | 0.75 | check the flags | 19% | 26% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 3 | 205 / 205 | 80 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 424 / 416 | 206 | 0.71 | check the flags | 34% | 20% | 46% | tee stage: Black lidar_pad_capped | tee: tee stage: Black lidar_pad_capped; Black tee on a lidar pad (no OSM box at 424 yds) |
| 12 | 5 | 518 / 515 | 180 | 0.81 | auto | 58% | 1% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 205 / 205 | 200 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 14 | 4 | 378 / 380 | 352 | 0.76 | check the flags | 47% | 22% | 31% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 378 yds) |
| 15 | 4 | 399 / 400 | 62 | 0.66 | check the flags | 45% | 14% | 41% | tee stage: Black review (inside OSM tee 591649550) | tee: tee stage: Black review (inside OSM tee 591649550) |
| 16 | 4 | 332 / 329 | 224 | 0.77 | check the flags | 30% | 20% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 405 / 405 | 39 | 0.85 | auto | 42% | 26% | 32% | tee stage: Black tee_centroid |  |
| 18 | 4 | 378 / 377 | 4 | 0.77 | check the flags | 23% | 26% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/449108205 A. L. Gustin Golf Course (Columbia, MO)
- **osm**: ok: 444 features
- **card_overrides**: ok: 1 review fix(es): hole 15 Black: card 467 -> 399 yds (review)
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 15 review (inside OSM tee 591649550); Gold 15 review (inside OSM tee 591649551);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 47 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/gustin/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/gustin/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 8 polygons (outside 8); mode replace
- **agent_layers**: ok: course_data/mapper/gustin (103 zone edits on 14 holes, 0 tee(s) moved, 54 checked)

## Warnings

- hole 11 Black: CHECK, tee was on a road (OSM 278117436): moved 7 yds forward off it
