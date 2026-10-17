# Wakonda Club (Des Moines, IA) - Blue tees

Built 2026-10-17T13:50:45Z. OSM way/102681377. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 55 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.359 |
| mean_confidence | 0.843 |
| osm_score | 0.858 |

OSM features inside the course: buildings 9, golf=bunker 48, golf=cartpath 39, golf=fairway 25, golf=green 26, golf=hole 18, golf=lateral_water_hazard 3, golf=tee 55, holes_with_par 18, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 410 / 410 | 8 | 0.82 | auto | 33% | 20% | 47% | tee stage: Blue tee_centroid |  |
| 2 | 3 | 114 / 114 | 293 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 382 / 382 | 182 | 0.86 | auto | 24% | 52% | 24% | tee stage: Blue tee_centroid |  |
| 4 | 4 | 410 / 409 | 348 | 0.80 | check the flags | 30% | 16% | 55% | tee stage: Blue tee_centroid |  |
| 5 | 5 | 505 / 506 | 101 | 0.79 | check the flags | 30% | 28% | 42% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 399 / 398 | 175 | 0.79 | check the flags | 30% | 30% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 348 / 347 | 189 | 0.80 | auto | 37% | 24% | 39% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 5 | 509 / 510 | 278 | 0.83 | auto | 53% | 16% | 30% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 3 | 169 / 169 | 68 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 429 / 430 | 118 | 0.86 | auto | 57% | 6% | 37% | tee stage: Blue tee_centroid |  |
| 11 | 4 | 396 / 396 | 335 | 0.79 | check the flags | 31% | 9% | 60% | tee stage: Blue tee_centroid |  |
| 12 | 4 | 351 / 351 | 159 | 0.77 | check the flags | 29% | 18% | 53% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 5 | 510 / 509 | 346 | 0.80 | check the flags | 42% | 15% | 43% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 3 | 168 / 168 | 235 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 15 | 5 | 490 / 490 | 163 | 0.79 | check the flags | 30% | 27% | 43% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 422 / 422 | 329 | 0.84 | auto | 52% | 7% | 41% | tee stage: Blue tee_centroid |  |
| 17 | 3 | 158 / 158 | 280 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 301 / 301 | 179 | 0.82 | auto | 27% | 45% | 28% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/102681377 Wakonda Club (Des Moines, IA)
- **osm**: ok: 499 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 59 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/wakonda/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/wakonda/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 9 polygons (property_line 9); mode replace
