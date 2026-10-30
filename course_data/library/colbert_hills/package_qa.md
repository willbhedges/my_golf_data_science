# Colbert Hills Golf Course (Manhattan, KS) - Black/Blue tees

Built 2026-10-30T04:06:11Z. OSM relation/13772939. Scorecard: opengolfapi (opengolfapi). Tee set: word in set name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 17 |
| tee_boxes | 97 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.391 |
| mean_confidence | 0.808 |
| osm_score | 0.813 |

OSM features inside the course: buildings 47, built_up_landuse 3, golf=bunker 90, golf=cartpath 41, golf=driving_range 1, golf=fairway 29, golf=green 17, golf=hole 18, golf=lateral_water_hazard 2, golf=pin 3, golf=rough 21, golf=tee 97, golf=water_hazard 1, holes_with_handicap 18, holes_with_par 18, trees_polygons 4, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 590 / 590 | 157 | 0.57 | needs review | 9% | 0% | 90% | tee stage: Black/Blue walkback | tee: tee stage: Black/Blue walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black/Blue tee walked back along the hole line (no box at 590 yds) |
| 2 | 4 | 412 / 412 | 225 | 0.83 | auto | 44% | 10% | 46% | tee stage: Black/Blue tee_centroid |  |
| 3 | 4 | 416 / 417 | 278 | 0.74 | check the flags | 24% | 12% | 64% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 4 | 4 | 494 / 488 | 316 | 0.75 | check the flags | 35% | 2% | 64% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 5 | 3 | 213 / 213 | 315 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black/Blue tee_centroid |  |
| 6 | 4 | 428 / 428 | 327 | 0.79 | check the flags | 51% | 1% | 48% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 7 | 5 | 600 / 603 | 38 | 0.80 | check the flags | 45% | 12% | 44% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 8 | 3 | 210 / 210 | 104 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black/Blue tee_centroid |  |
| 9 | 4 | 462 / 462 | 128 | 0.79 | check the flags | 36% | 0% | 63% | tee stage: Black/Blue tee_centroid |  |
| 10 | 5 | 614 / 615 | 77 | 0.82 | auto | 46% | 3% | 51% | tee stage: Black/Blue tee_centroid |  |
| 11 | 3 | 230 / 230 | 304 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 12 | 4 | 434 / 435 | 122 | 0.84 | auto | 49% | 12% | 39% | tee stage: Black/Blue tee_centroid |  |
| 13 | 4 | 357 / 352 | 1 | 0.74 | check the flags | 29% | 7% | 64% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 487 / 488 | 266 | 0.82 | auto | 49% | 18% | 33% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 15 | 4 | 375 / 375 | 308 | 0.75 | check the flags | 26% | 15% | 59% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis |
| 16 | 5 | 513 / 514 | 288 | 0.81 | auto | 41% | 3% | 56% | tee stage: Black/Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 237 / 237 | 211 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black/Blue lidar_pad | tee: tee stage: Black/Blue lidar_pad; Black/Blue tee on a lidar pad (no OSM box at 237 yds) |
| 18 | 4 | 453 / 453 | 139 | 0.77 | check the flags | 64% | 0% | 36% | tee stage: Black/Blue tee_axis | tee: tee stage: Black/Blue tee_axis; green from the hole-line end (no golf=green polygon); no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: relation/13772939 Colbert Hills Golf Course (Manhattan, KS)
- **osm**: ok: 1372 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 101 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/colbert_hills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/colbert_hills/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 37 polygons (outside 37); mode replace

## Warnings

- scorecard (opengolfapi): Purple: holes sum to 6432 but the source says 6452 (-20): mixed card versions
