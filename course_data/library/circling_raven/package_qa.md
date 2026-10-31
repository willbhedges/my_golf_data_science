# Circling Raven Golf Course (Worley, ID) - Gold tees

Built 2026-10-30T21:58:31Z. OSM relation/13691362. Scorecard: allsquare (allsquare). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Red, Green)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red, Green**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 13 |
| greens_found | 18 |
| tee_boxes | 76 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.448 |
| mean_confidence | 0.81 |
| osm_score | 0.791 |

OSM features inside the course: buildings 4, golf=bunker 47, golf=cartpath 36, golf=clubhouse 1, golf=fairway 35, golf=green 18, golf=hole 13, golf=pin 17, golf=rough 48, golf=tee 76, golf=water_hazard 1, holes_with_par 13, single_trees 79, trees_polygons 25, water_lines 1, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 513 / 513 | 6 | 0.72 | check the flags | 48% | 0% | 52% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 513 yds) |
| 2 | 4 | 395 / 398 | 70 | 0.80 | check the flags | 39% | 2% | 60% | tee stage: Gold tee_centroid |  |
| 3 | 3 | 217 / 218 | 277 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 4 | 406 / 413 | 76 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 5 | 574 / 570 | 263 | 0.83 | auto | 63% | 0% | 37% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 4 | 387 / 388 | 302 | 0.78 | check the flags | 34% | 1% | 65% | tee stage: Gold tee_centroid |  |
| 7 | 3 | 212 / 212 | 295 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 8 | 4 | 386 / 381 | 139 | 0.70 | check the flags | 38% | 9% | 53% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 386 yds) |
| 9 | 4 | 474 / 472 | 139 | 0.82 | auto | 48% | 0% | 52% | tee stage: Gold tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 336 / 332 | 67 | 0.76 | check the flags | 30% | 11% | 59% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 11 | 4 | 446 / 440 | 89 | 0.78 | check the flags | 46% | 2% | 52% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 12 | 5 | 581 / 581 | 194 | 0.62 | check the flags | 23% | 4% | 73% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 581 yds) |
| 13 | 3 | 253 / 253 | 130 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 14 | 4 | 397 / 395 | 94 | 0.76 | check the flags | 41% | 0% | 59% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 426 / 426 | 196 | 0.83 | auto | 58% | 7% | 35% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 16 | 3 | 192 / 188 | 211 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 5 | 559 / 560 | 314 | 0.84 | auto | 54% | 2% | 44% | tee stage: Gold tee_centroid |  |
| 18 | 4 | 435 / 436 | 303 | 0.81 | auto | 54% | 2% | 44% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |

## Stages

- **resolve**: ok: relation/13691362 Circling Raven Golf Course (Worley, ID)
- **osm**: ok: 563 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 93 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/circling_raven/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/circling_raven/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 18 polygons (outside 18); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red, Green
