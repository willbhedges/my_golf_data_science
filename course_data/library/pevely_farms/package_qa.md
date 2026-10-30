# Pevely Farms Golf Course (Saint Louis, MO) - Black tees

Built 2026-10-30T04:16:22Z. OSM relation/5429230. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 16 |
| tee_boxes | 59 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 15 |
| mean_landing_osm_share | 0.239 |
| mean_confidence | 0.747 |
| osm_score | 0.805 |

OSM features inside the course: buildings 1, built_up_landuse 1, golf=bunker 27, golf=cartpath 22, golf=fairway 23, golf=green 22, golf=hole 18, golf=pin 18, golf=tee 59, holes_with_par 18, trees_polygons 1, water_lines 6, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 446 / 445 | 354 | 0.59 | needs review | 8% | 43% | 50% | tee stage: Black walkback | tee: tee stage: Black walkback; green from the hole-line end (no golf=green polygon); no fairway in the landing zone; Black tee walked back along the hole line (no box at 446 yds) |
| 2 | 5 | 531 / 532 | 244 | 0.74 | check the flags | 34% | 0% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 4 | 277 / 277 | 356 | 0.65 | check the flags | 15% | 13% | 72% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 277 yds) |
| 4 | 4 | 439 / 440 | 83 | 0.73 | check the flags | 29% | 2% | 69% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 199 / 198 | 62 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 398 / 399 | 80 | 0.79 | check the flags | 49% | 2% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 397 / 398 | 282 | 0.82 | auto | 54% | 10% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 217 / 217 | 237 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 5 | 527 / 526 | 179 | 0.58 | needs review | 4% | 10% | 86% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 527 yds) |
| 10 | 4 | 403 / 404 | 292 | 0.70 | check the flags | 0% | 53% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; green from the hole-line end (no golf=green polygon); no fairway in the landing zone |
| 11 | 4 | 401 / 400 | 7 | 0.70 | check the flags | 34% | 29% | 37% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 401 yds) |
| 12 | 5 | 572 / 573 | 273 | 0.76 | check the flags | 29% | 12% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 389 / 385 | 18 | 0.80 | check the flags | 27% | 35% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 145 / 145 | 234 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 358 / 357 | 188 | 0.74 | check the flags | 28% | 6% | 67% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 443 / 441 | 293 | 0.73 | check the flags | 19% | 16% | 65% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 422 / 422 | 163 | 0.78 | check the flags | 30% | 4% | 66% | tee stage: Black tee_centroid |  |
| 18 | 4 | 468 / 469 | 122 | 0.56 | needs review | 0% | 6% | 94% | tee stage: Black walkback | tee: tee stage: Black walkback; no fairway in the landing zone; Black tee walked back along the hole line (no box at 468 yds) |

## Stages

- **resolve**: ok: relation/5429230 Pevely Farms Golf Course (Saint Louis, MO)
- **osm**: ok: 388 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 66 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/pevely_farms/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 16/16 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/pevely_farms/imagery/dem.tif (15/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 35 polygons (outside 35); mode replace
