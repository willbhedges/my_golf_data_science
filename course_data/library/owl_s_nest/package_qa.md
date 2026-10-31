# Owl's Nest Resort Golf Course (Thornton, NH) - Black tees

Built 2026-10-31T02:10:55Z. OSM relation/17154512. Scorecard: club_site (club_site). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 68 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.341 |
| mean_confidence | 0.82 |
| osm_score | 0.854 |

OSM features inside the course: buildings 59, built_up_landuse 3, golf=bunker 60, golf=cartpath 36, golf=driving_range 1, golf=fairway 26, golf=green 20, golf=hole 18, golf=lateral_water_hazard 4, golf=rough 2, golf=tee 68, holes_with_par 18, single_trees 88, trees_polygons 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 395 | 175 | 0.77 | check the flags | 30% | 17% | 53% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 433 / 434 | 278 | 0.83 | auto | 45% | 8% | 46% | tee stage: Black tee_centroid |  |
| 3 | 4 | 435 / 435 | 154 | 0.83 | auto | 44% | 10% | 45% | tee stage: Black tee_centroid |  |
| 4 | 5 | 543 / 539 | 317 | 0.77 | check the flags | 41% | 4% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 192 / 192 | 58 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 338 / 338 | 164 | 0.77 | check the flags | 41% | 0% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 207 / 207 | 38 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 8 | 4 | 375 / 375 | 354 | 0.84 | auto | 32% | 34% | 34% | tee stage: Black tee_centroid |  |
| 9 | 5 | 534 / 535 | 116 | 0.68 | check the flags | 36% | 16% | 49% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 534 yds) |
| 10 | 3 | 152 / 152 | 232 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 349 / 349 | 173 | 0.80 | auto | 25% | 40% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 4 | 408 / 409 | 91 | 0.77 | check the flags | 22% | 31% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 5 | 499 / 501 | 167 | 0.79 | check the flags | 36% | 20% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 208 / 208 | 317 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 280 / 280 | 173 | 0.78 | check the flags | 24% | 30% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 465 / 465 | 355 | 0.80 | auto | 31% | 17% | 53% | tee stage: Black tee_centroid |  |
| 17 | 5 | 514 / 515 | 261 | 0.83 | auto | 39% | 19% | 42% | tee stage: Black tee_centroid |  |
| 18 | 4 | 357 / 357 | 346 | 0.74 | check the flags | 31% | 0% | 69% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/17154512 Owl's Nest Resort Golf Course (Thornton, NH)
- **osm**: ok: 745 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: club_site (club_site)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 78 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/owl_s_nest/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/owl_s_nest/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 29 polygons (outside 29); mode replace
