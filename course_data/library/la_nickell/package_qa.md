# L.A. Nickell Golf Course (Columbia, MO) - Blue tees

Built 2026-10-30T03:59:02Z. OSM way/387047950. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 40 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.283 |
| mean_confidence | 0.775 |
| osm_score | 0.843 |

OSM features inside the course: buildings 7, golf=cartpath 12, golf=clubhouse 1, golf=fairway 22, golf=green 20, golf=hole 17, golf=tee 40, golf=water_hazard 3, holes_with_par 17, water_lines 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 372 / 365 | 164 | 0.74 | check the flags | 24% | 13% | 63% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 369 / 364 | 135 | 0.76 | check the flags | 28% | 18% | 54% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 385 / 385 | 316 | 0.78 | check the flags | 41% | 10% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 224 / 227 | 276 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Blue texture_pad | tee: tee stage: Blue texture_pad; Blue tee on an imagery-detected pad (texture; no OSM box at 224 yds) |
| 5 | 4 | 325 / 313 | 165 | 0.76 | check the flags | 20% | 28% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 3 | 196 / 196 | 43 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 7 | 5 | 500 / 507 | 150 | 0.77 | check the flags | 31% | 19% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 392 / 391 | 329 | 0.76 | check the flags | 30% | 15% | 55% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 379 / 378 | 336 | 0.68 | check the flags | 30% | 23% | 47% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 379 yds) |
| 10 | 4 | 384 / 383 | 190 | 0.67 | check the flags | 30% | 21% | 49% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 384 yds) |
| 11 | 3 | 174 / 174 | 280 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 526 / 525 | 2 | 0.68 | check the flags | 30% | 25% | 44% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 526 yds) |
| 13 | 4 | 376 / 375 | 174 | 0.72 | check the flags | 28% | 30% | 41% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 376 yds) |
| 14 | 3 | 194 / 194 | 26 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 377 / 377 | 315 | 0.78 | check the flags | 32% | 18% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 328 / 329 | 73 | 0.81 | auto | 19% | 55% | 26% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 407 / 397 | 98 | 0.71 | check the flags | 18% | 8% | 74% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 427 / 426 | 199 | 0.70 | check the flags | 35% | 28% | 37% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 427 yds) |

## Stages

- **resolve**: ok: way/387047950 L.A. Nickell Golf Course (Columbia, MO)
- **osm**: ok: 367 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 28 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/la_nickell/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/la_nickell/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 10 polygons (outside 10); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
