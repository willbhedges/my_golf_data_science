# Mozingo Lake Golf Course (Maryville, MO) - App tees

Built 2026-10-30T18:49:34Z. OSM way/385067034. Scorecard: request (request file yardages). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 66 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 8 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.458 |
| mean_confidence | 0.822 |
| osm_score | 0.806 |

OSM features inside the course: buildings 4, golf=bunker 25, golf=cartpath 23, golf=driving_range 1, golf=fairway 20, golf=green 25, golf=hole 18, golf=rough 22, golf=tee 66, golf=water_hazard 3, holes_with_handicap 16, holes_with_par 18, single_trees 12, tees_with_ref 12, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 371 / 362 | 183 | 0.77 | check the flags | 35% | 16% | 50% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 2 | 4 | 349 / 350 | 59 | 0.82 | auto | 46% | 10% | 44% | tee stage: App tee_centroid |  |
| 3 | 5 | 517 / 518 | 230 | 0.81 | auto | 49% | 0% | 51% | tee stage: App tee_centroid |  |
| 4 | 4 | 361 / 362 | 79 | 0.76 | check the flags | 44% | 0% | 56% | tee stage: App tee_axis | tee: tee stage: App tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 3 | 182 / 182 | 210 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 6 | 5 | 491 / 492 | 266 | 0.78 | check the flags | 50% | 0% | 50% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 7 | 4 | 428 / 428 | 36 | 0.80 | auto | 56% | 2% | 41% | tee stage: App tee_axis | tee: tee stage: App tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 187 / 187 | 26 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 9 | 4 | 348 / 348 | 18 | 0.79 | check the flags | 41% | 0% | 59% | tee stage: App tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 392 / 391 | 10 | 0.77 | check the flags | 47% | 0% | 53% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 11 | 3 | 219 / 219 | 343 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 12 | 5 | 517 / 518 | 265 | 0.77 | check the flags | 45% | 1% | 54% | tee stage: App tee_axis | tee: tee stage: App tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 4 | 394 / 394 | 177 | 0.77 | check the flags | 42% | 5% | 53% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 14 | 5 | 464 / 463 | 187 | 0.81 | auto | 50% | 0% | 50% | tee stage: App tee_centroid |  |
| 15 | 3 | 174 / 174 | 80 | 0.95 | auto | 100% | 0% | 0% | tee stage: App tee_centroid |  |
| 16 | 4 | 433 / 432 | 13 | 0.78 | check the flags | 50% | 0% | 50% | tee stage: App tee_axis | tee: tee stage: App tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 4 | 344 / 355 | 49 | 0.74 | check the flags | 31% | 4% | 64% | tee stage: App tee_axis | tee: tee stage: App tee_axis |
| 18 | 4 | 407 / 407 | 203 | 0.79 | check the flags | 54% | 0% | 46% | tee stage: App tee_axis | tee: tee stage: App tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/385067034 Mozingo Lake Golf Course (Maryville, MO)
- **osm**: ok: 475 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: request (request file yardages)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture+segment pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture+segment pads, joint chain assignment) for 1 sets; lidar pads: 41 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/mozingo_lake/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/mozingo_lake/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: ok: segment gap-fill ariadgolf-v4@43ee2944 (+1 zones on 1 holes, +0 greens, 32 tee candidates)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace
