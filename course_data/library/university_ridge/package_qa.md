# University Ridge Golf Course (Madison, WI) - Black tees

Built 2026-10-31T05:23:03Z. OSM way/23810848. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 84 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.398 |
| mean_confidence | 0.831 |
| osm_score | 0.864 |

OSM features inside the course: buildings 5, golf=bunker 83, golf=cartpath 25, golf=driving_range 1, golf=fairway 24, golf=green 24, golf=hole 18, golf=rough 20, golf=tee 84, golf=water_hazard 5, holes_with_handicap 18, holes_with_par 18, single_trees 9, tees_with_ref 60, trees_polygons 2, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 396 / 396 | 156 | 0.84 | auto | 48% | 8% | 44% | tee stage: Black tee_centroid |  |
| 2 | 5 | 555 / 556 | 106 | 0.68 | check the flags | 45% | 5% | 50% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 555 yds) |
| 3 | 3 | 242 / 243 | 76 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 242 yds) |
| 4 | 4 | 467 / 467 | 340 | 0.84 | auto | 57% | 14% | 29% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 198 / 198 | 31 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 623 / 623 | 223 | 0.81 | auto | 40% | 7% | 53% | tee stage: Black tee_centroid |  |
| 7 | 4 | 429 / 427 | 323 | 0.75 | check the flags | 37% | 0% | 63% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 207 / 207 | 207 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 5 | 587 / 587 | 5 | 0.80 | auto | 47% | 9% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 483 / 484 | 256 | 0.83 | auto | 31% | 47% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 5 | 569 / 570 | 33 | 0.81 | auto | 34% | 32% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 200 / 200 | 288 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 336 / 337 | 94 | 0.83 | auto | 41% | 34% | 25% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 398 / 398 | 160 | 0.87 | auto | 36% | 41% | 23% | tee stage: Black tee_centroid |  |
| 15 | 4 | 352 / 352 | 348 | 0.84 | auto | 30% | 52% | 18% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 5 | 554 / 555 | 47 | 0.70 | check the flags | 38% | 23% | 39% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 554 yds) |
| 17 | 3 | 250 / 251 | 249 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 413 / 412 | 226 | 0.81 | auto | 32% | 36% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/23810848 University Ridge Golf Course (Madison, WI)
- **osm**: ok: 1068 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 11 sets; lidar pads: 93 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 11 tee set(s))
- **imagery**: ok: course_data/packages/university_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/university_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace

## Warnings

- ignored 4 practice / driving-range tee box(es): OSM 772028541, 772028542, 772028544, 772028545
