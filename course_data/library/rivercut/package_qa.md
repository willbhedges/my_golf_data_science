# Rivercut Golf Course (Springfield, MO) - Black tees

Built 2026-10-30T04:23:54Z. OSM relation/5981089. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 73 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.42 |
| mean_confidence | 0.818 |
| osm_score | 0.842 |

OSM features inside the course: buildings 8, golf=bunker 59, golf=cartpath 16, golf=clubhouse 1, golf=fairway 20, golf=green 18, golf=hole 17, golf=tee 73, golf=water_hazard 9, holes_with_par 17, water_lines 16, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 375 / 374 | 198 | 0.74 | check the flags | 33% | 0% | 67% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 3 | 204 / 204 | 69 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 415 / 415 | 36 | 0.80 | check the flags | 42% | 16% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 346 / 346 | 222 | 0.78 | check the flags | 34% | 17% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 5 | 511 / 511 | 240 | 0.79 | check the flags | 42% | 12% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 3 | 176 / 176 | 287 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 5 | 569 / 568 | 50 | 0.77 | check the flags | 38% | 6% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 443 / 443 | 231 | 0.77 | check the flags | 39% | 7% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 473 / 473 | 42 | 0.79 | check the flags | 50% | 2% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 611 / 611 | 245 | 0.81 | auto | 42% | 21% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 385 / 384 | 200 | 0.81 | auto | 52% | 8% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 409 / 409 | 317 | 0.77 | check the flags | 39% | 6% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 465 / 465 | 55 | 0.81 | auto | 42% | 21% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 435 / 435 | 21 | 0.83 | auto | 53% | 19% | 29% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 3 | 146 / 146 | 234 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 345 / 337 | 11 | 0.71 | check the flags | 41% | 8% | 51% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 345 yds) |
| 17 | 3 | 243 / 243 | 96 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 544 / 543 | 153 | 0.80 | auto | 42% | 18% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/5981089 Rivercut Golf Course (Springfield, MO)
- **osm**: ok: 421 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 130 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/rivercut/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/rivercut/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 20 polygons (outside 20); mode replace
