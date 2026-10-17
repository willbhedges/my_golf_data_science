# Coldwater Golf Links (Ames, IA) - Blue tees

Built 2026-10-17T18:14:34Z. OSM way/44807109. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 75 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 4 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.502 |
| mean_confidence | 0.82 |
| osm_score | 0.758 |

OSM features inside the course: buildings 4, golf=bunker 41, golf=cartpath 8, golf=fairway 23, golf=green 19, golf=hole 18, golf=lateral_water_hazard 1, golf=path 11, golf=rough 32, golf=tee 75, golf=water_hazard 3, holes_with_par 18, tees_with_ref 1, trees_polygons 2, water_lines 2, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 307 / 308 | 280 | 0.80 | check the flags | 50% | 3% | 46% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 425 / 425 | 34 | 0.69 | check the flags | 35% | 7% | 58% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 425 yds) |
| 3 | 5 | 510 / 510 | 224 | 0.88 | auto | 70% | 0% | 30% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 4 | 371 / 371 | 20 | 0.83 | auto | 52% | 0% | 48% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 3 | 185 / 185 | 95 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 6 | 4 | 418 / 419 | 280 | 0.68 | check the flags | 48% | 0% | 52% | tee stage: Blue walkback | tee: tee stage: Blue walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Blue tee walked back along the hole line (no box at 418 yds) |
| 7 | 5 | 505 / 500 | 98 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 139 / 139 | 211 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 139 yds) |
| 9 | 4 | 371 / 371 | 184 | 0.87 | auto | 78% | 0% | 22% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 396 / 396 | 339 | 0.77 | check the flags | 43% | 0% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 147 / 147 | 119 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 12 | 4 | 328 / 329 | 86 | 0.79 | check the flags | 51% | 0% | 49% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 4 | 413 / 420 | 281 | 0.81 | auto | 56% | 0% | 44% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 5 | 476 / 476 | 100 | 0.77 | check the flags | 39% | 4% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 417 / 416 | 186 | 0.79 | check the flags | 49% | 2% | 49% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 3 | 170 / 170 | 277 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 17 | 4 | 395 / 379 | 360 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 433 / 433 | 205 | 0.80 | check the flags | 53% | 0% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/44807109 Coldwater Golf Links (Ames, IA)
- **osm**: ok: 686 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 74 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/coldwater/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/coldwater/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 6 polygons (property_line 6); mode replace

## Warnings

- hole 17: measured 379 vs card 395 yds for Blue (no OSM tee box at that yardage?)
