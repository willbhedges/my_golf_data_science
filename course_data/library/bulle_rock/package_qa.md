# Bulle Rock Golf Club (Havre de Grace, MD) - Black tees

Built 2026-10-31T01:46:26Z. OSM way/70804218. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 64 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.451 |
| mean_confidence | 0.819 |
| osm_score | 0.876 |

OSM features inside the course: buildings 5, golf=bunker 130, golf=cartpath 7, golf=fairway 20, golf=green 20, golf=hole 18, golf=pin 18, golf=tee 64, holes_with_par 18, trees_polygons 4, water_lines 6, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 358 / 358 | 240 | 0.78 | check the flags | 42% | 8% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 5 | 572 / 571 | 157 | 0.83 | auto | 52% | 19% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 177 / 177 | 92 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 417 / 408 | 128 | 0.73 | check the flags | 50% | 5% | 45% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 417 yds) |
| 5 | 4 | 483 / 480 | 241 | 0.81 | auto | 49% | 13% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 413 / 413 | 50 | 0.79 | check the flags | 30% | 28% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 202 / 202 | 334 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 5 | 546 / 546 | 335 | 0.82 | auto | 49% | 0% | 51% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 4 | 478 / 478 | 341 | 0.84 | auto | 62% | 8% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 393 / 393 | 156 | 0.77 | check the flags | 42% | 0% | 58% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 5 | 665 / 664 | 171 | 0.82 | auto | 47% | 2% | 50% | tee stage: Black tee_centroid |  |
| 12 | 3 | 190 / 190 | 61 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 476 / 476 | 322 | 0.81 | auto | 41% | 5% | 55% | tee stage: Black tee_centroid |  |
| 14 | 4 | 372 / 371 | 354 | 0.84 | auto | 49% | 8% | 43% | tee stage: Black tee_centroid |  |
| 15 | 5 | 529 / 529 | 249 | 0.78 | check the flags | 31% | 6% | 63% | tee stage: Black tee_centroid |  |
| 16 | 4 | 425 / 419 | 40 | 0.73 | check the flags | 36% | 25% | 39% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 425 yds) |
| 17 | 3 | 194 / 203 | 310 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 194 yds) |
| 18 | 4 | 485 / 484 | 202 | 0.72 | check the flags | 50% | 2% | 48% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 485 yds) |

## Stages

- **resolve**: ok: way/70804218 Bulle Rock Golf Club (Havre de Grace, MD)
- **osm**: ok: 909 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 10 sets; lidar pads: 105 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 10 tee set(s))
- **imagery**: ok: course_data/packages/bulle_rock/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/bulle_rock/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace
