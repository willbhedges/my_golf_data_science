# Tournament Players Club of Louisiana (Waggaman, LA) - Black tees

Built 2026-11-03T03:34:01Z. OSM relation/4260277. Scorecard: file (course_data/library/tpc_louisiana/card_review.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 62 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.434 |
| mean_confidence | 0.838 |
| osm_score | 0.887 |

OSM features inside the course: buildings 7, golf=bunker 97, golf=cartpath 7, golf=clubhouse 1, golf=fairway 20, golf=green 22, golf=hole 18, golf=pin 17, golf=tee 62, golf=water_hazard 5, holes_with_par 18, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 366 / 366 | 214 | 0.80 | check the flags | 28% | 34% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 5 | 527 / 527 | 230 | 0.80 | auto | 35% | 28% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 167 / 167 | 212 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 465 / 466 | 270 | 0.89 | auto | 66% | 9% | 25% | tee stage: Black tee_centroid |  |
| 5 | 4 | 425 / 424 | 26 | 0.83 | auto | 39% | 19% | 41% | tee stage: Black tee_centroid |  |
| 6 | 4 | 454 / 453 | 173 | 0.85 | auto | 67% | 7% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 5 | 528 / 528 | 33 | 0.77 | check the flags | 41% | 5% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 336 / 336 | 34 | 0.79 | check the flags | 35% | 22% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 3 | 195 / 195 | 55 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 10 | 4 | 375 / 376 | 289 | 0.77 | check the flags | 28% | 23% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 5 | 546 / 545 | 200 | 0.78 | check the flags | 35% | 18% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 470 / 466 | 175 | 0.81 | auto | 42% | 22% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 351 / 350 | 20 | 0.77 | check the flags | 42% | 0% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 192 / 192 | 352 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 457 / 456 | 17 | 0.75 | check the flags | 28% | 10% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 340 / 339 | 189 | 0.84 | auto | 50% | 27% | 23% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 172 / 172 | 137 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 565 / 564 | 18 | 0.85 | auto | 70% | 2% | 28% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/4260277 Tournament Players Club of Louisiana (Waggaman, LA)
- **osm**: ok: 315 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/tpc_louisiana/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 32 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/tpc_louisiana/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/tpc_louisiana/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -24 m2 {'cells': 24}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace
