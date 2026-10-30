# The Falls Golf Club (O'Fallon, MO) - Gold tees

Built 2026-10-30T04:36:59Z. OSM relation/3939928. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.366 |
| mean_confidence | 0.797 |
| osm_score | 0.873 |

OSM features inside the course: buildings 34, golf=bunker 21, golf=cartpath 27, golf=fairway 23, golf=green 19, golf=hole 18, golf=pin 18, golf=rough 3, golf=tee 67, golf=water_hazard 10, holes_with_handicap 18, holes_with_par 18, trees_polygons 6, water_lines 16, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 416 / 413 | 94 | 0.80 | check the flags | 42% | 16% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 2 | 4 | 412 / 420 | 71 | 0.73 | check the flags | 37% | 21% | 42% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 412 yds) |
| 3 | 4 | 388 / 387 | 352 | 0.74 | check the flags | 30% | 36% | 33% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 388 yds) |
| 4 | 3 | 171 / 171 | 271 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 5 | 4 | 419 / 413 | 184 | 0.81 | auto | 44% | 18% | 38% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 5 | 524 / 518 | 290 | 0.78 | check the flags | 32% | 20% | 48% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 4 | 428 / 429 | 289 | 0.78 | check the flags | 39% | 11% | 50% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 8 | 3 | 193 / 190 | 238 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 5 | 491 / 492 | 95 | 0.73 | check the flags | 34% | 29% | 37% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 491 yds) |
| 10 | 4 | 380 / 381 | 102 | 0.75 | check the flags | 39% | 29% | 32% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 380 yds) |
| 11 | 4 | 392 / 391 | 203 | 0.72 | check the flags | 31% | 24% | 45% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 392 yds) |
| 12 | 3 | 181 / 181 | 277 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 4 | 370 / 369 | 189 | 0.67 | check the flags | 46% | 0% | 54% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 370 yds) |
| 14 | 3 | 184 / 179 | 167 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 15 | 5 | 530 / 531 | 270 | 0.67 | check the flags | 34% | 16% | 50% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 530 yds) |
| 16 | 4 | 342 / 348 | 13 | 0.73 | check the flags | 30% | 36% | 34% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 342 yds) |
| 17 | 3 | 178 / 178 | 333 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 18 | 5 | 511 / 511 | 49 | 0.72 | check the flags | 38% | 34% | 29% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 511 yds) |

## Stages

- **resolve**: ok: relation/3939928 The Falls Golf Club (O'Fallon, MO)
- **osm**: ok: 776 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 103 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/the_falls_ofallon/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/the_falls_ofallon/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 51 polygons (outside 51); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red
