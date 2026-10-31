# Edgewood Tahoe Golf Course (Lake Tahoe, NV) - Gold tees

Built 2026-10-31T02:08:49Z. OSM way/63521167. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, Combo, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, Combo, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.528 |
| mean_confidence | 0.836 |
| osm_score | 0.906 |

OSM features inside the course: buildings 9, golf=bunker 66, golf=cartpath 32, golf=fairway 18, golf=green 29, golf=hole 18, golf=rough 23, golf=tee 67, golf=water_hazard 3, holes_with_handicap 18, holes_with_par 18, single_trees 561, trees_polygons 9, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 436 / 437 | 66 | 0.89 | auto | 70% | 5% | 25% | tee stage: Gold tee_centroid |  |
| 2 | 4 | 417 / 418 | 111 | 0.82 | auto | 50% | 0% | 50% | tee stage: Gold tee_centroid |  |
| 3 | 5 | 599 / 599 | 304 | 0.82 | auto | 48% | 0% | 52% | tee stage: Gold tee_centroid |  |
| 4 | 5 | 572 / 573 | 125 | 0.84 | auto | 61% | 10% | 29% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 3 | 220 / 220 | 196 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 6 | 4 | 472 / 473 | 260 | 0.81 | auto | 45% | 1% | 55% | tee stage: Gold tee_centroid |  |
| 7 | 3 | 169 / 158 | 285 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 8 | 4 | 466 / 456 | 172 | 0.75 | check the flags | 45% | 24% | 31% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 466 yds) |
| 9 | 4 | 430 / 430 | 314 | 0.80 | auto | 47% | 10% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 10 | 4 | 441 / 442 | 85 | 0.86 | auto | 60% | 3% | 37% | tee stage: Gold tee_centroid |  |
| 11 | 4 | 407 / 408 | 82 | 0.73 | check the flags | 54% | 2% | 44% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 407 yds) |
| 12 | 3 | 214 / 214 | 9 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 13 | 4 | 434 / 428 | 293 | 0.71 | check the flags | 47% | 0% | 53% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 434 yds) |
| 14 | 4 | 447 / 447 | 216 | 0.82 | auto | 58% | 3% | 39% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 15 | 4 | 462 / 462 | 24 | 0.73 | check the flags | 58% | 13% | 29% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 462 yds) |
| 16 | 5 | 564 / 565 | 294 | 0.84 | auto | 54% | 22% | 24% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 3 | 207 / 207 | 166 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 18 | 5 | 572 / 571 | 185 | 0.78 | check the flags | 42% | 6% | 52% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |

## Stages

- **resolve**: ok: way/63521167 Edgewood Tahoe Golf Course (Lake Tahoe, NV)
- **osm**: ok: 1284 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 83 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/edgewood_tahoe/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/edgewood_tahoe/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, Combo, White, Red
