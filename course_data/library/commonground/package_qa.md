# CommonGround Golf Course (Aurora, CO) - Black tees

Built 2026-10-30T21:34:37Z. OSM way/113046166. Scorecard: allsquare (allsquare). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 50 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 9 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.624 |
| mean_confidence | 0.844 |
| osm_score | 0.863 |

OSM features inside the course: buildings 15, golf=bunker 80, golf=cartpath 63, golf=fairway 24, golf=green 20, golf=hole 18, golf=lateral_water_hazard 1, golf=pin 18, golf=rough 5, golf=tee 50, golf=water_hazard 2, holes_with_handicap 8, holes_with_par 18, single_trees 145, tees_with_ref 47, water_lines 7, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 489 / 488 | 179 | 0.69 | check the flags | 62% | 5% | 33% | tee stage: Black texture_pad | tee: tee stage: Black texture_pad; Black tee on an imagery-detected pad (texture; no OSM box at 489 yds) |
| 2 | 3 | 144 / 144 | 283 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 5 | 586 / 587 | 253 | 0.82 | auto | 56% | 9% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 424 / 434 | 311 | 0.90 | auto | 88% | 0% | 11% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 489 / 488 | 346 | 0.87 | auto | 78% | 0% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 3 | 188 / 188 | 119 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 7 | 5 | 545 / 545 | 142 | 0.82 | auto | 62% | 0% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 355 / 351 | 16 | 0.82 | auto | 62% | 0% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 376 / 376 | 39 | 0.82 | auto | 57% | 3% | 39% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 437 / 437 | 226 | 0.66 | check the flags | 52% | 0% | 48% | tee stage: Black texture_pad | tee: tee stage: Black texture_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee on an imagery-detected pad (texture; no OSM box at 437 yds) |
| 11 | 5 | 529 / 530 | 302 | 0.85 | auto | 67% | 6% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 219 / 219 | 258 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 417 / 416 | 156 | 0.83 | auto | 66% | 0% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 3 | 229 / 229 | 4 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 505 / 504 | 166 | 0.82 | auto | 62% | 0% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 476 / 473 | 48 | 0.83 | auto | 57% | 8% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 243 / 243 | 190 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 568 / 564 | 6 | 0.77 | check the flags | 42% | 2% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/113046166 CommonGround Golf Course (Aurora, CO)
- **osm**: ok: 1035 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 17 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/commonground/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/commonground/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace

## Warnings

- scorecard (allsquare): 1 hole(s) where a longer set is shorter than the next set: 11 Black 529 < Black/Gold 539
