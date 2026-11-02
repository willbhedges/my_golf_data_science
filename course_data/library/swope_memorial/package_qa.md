# Swope Memorial Golf Course (Kansas City, MO) - Green tees

Built 2026-11-02T06:23:16Z. OSM way/68196001. Scorecard: file (course_data/library/swope_memorial/card_review.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 53 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.357 |
| mean_confidence | 0.82 |
| osm_score | 0.871 |

OSM features inside the course: buildings 1, golf=bunker 42, golf=cartpath 8, golf=clubhouse 1, golf=fairway 21, golf=green 19, golf=hole 18, golf=pin 18, golf=tee 53, holes_with_par 18, tees_with_ref 50, trees_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 390 / 391 | 98 | 0.77 | check the flags | 37% | 7% | 56% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 2 | 4 | 321 / 320 | 172 | 0.75 | check the flags | 26% | 15% | 59% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 3 | 4 | 339 / 338 | 245 | 0.77 | check the flags | 30% | 16% | 54% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 4 | 3 | 176 / 175 | 68 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 5 | 5 | 475 / 470 | 317 | 0.80 | auto | 36% | 25% | 39% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 6 | 4 | 406 / 406 | 131 | 0.82 | auto | 30% | 23% | 47% | tee stage: Green tee_centroid |  |
| 7 | 3 | 177 / 177 | 191 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 8 | 4 | 273 / 273 | 1 | 0.74 | check the flags | 18% | 4% | 78% | tee stage: Green tee_centroid |  |
| 9 | 4 | 371 / 372 | 286 | 0.79 | check the flags | 31% | 25% | 45% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 10 | 4 | 384 / 385 | 106 | 0.81 | auto | 34% | 35% | 31% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 11 | 4 | 375 / 370 | 154 | 0.79 | check the flags | 34% | 19% | 46% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 12 | 5 | 533 / 527 | 197 | 0.74 | check the flags | 55% | 6% | 40% | tee stage: Green lidar_pad | tee: tee stage: Green lidar_pad; Green tee on a lidar pad (no OSM box at 533 yds) |
| 13 | 3 | 229 / 229 | 1 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 14 | 4 | 426 / 421 | 228 | 0.87 | auto | 69% | 13% | 18% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 15 | 4 | 347 / 348 | 81 | 0.83 | auto | 32% | 29% | 39% | tee stage: Green tee_centroid |  |
| 16 | 3 | 127 / 129 | 81 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 17 | 5 | 562 / 562 | 2 | 0.79 | check the flags | 41% | 12% | 48% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 18 | 4 | 413 / 409 | 276 | 0.77 | check the flags | 28% | 22% | 51% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |

## Stages

- **resolve**: ok: way/68196001 Swope Memorial Golf Course (Kansas City, MO)
- **osm**: ok: 251 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/swope_memorial/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 46 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/swope_memorial/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/swope_memorial/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace
