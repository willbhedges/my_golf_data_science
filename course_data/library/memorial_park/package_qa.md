# Memorial Park Golf Course (Houston, TX) - Blue tees

Built 2026-11-03T11:06:20Z. OSM relation/13729803. Scorecard: file (course_data/library/memorial_park/card_review.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Gold, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 51 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.327 |
| mean_confidence | 0.807 |
| osm_score | 0.85 |

OSM features inside the course: buildings 10, golf=bunker 21, golf=cartpath 30, golf=clubhouse 1, golf=driving_range 1, golf=fairway 19, golf=green 23, golf=hole 18, golf=lateral_water_hazard 8, golf=path 3, golf=pin 18, golf=tee 51, holes_with_par 18, tees_with_ref 12, trees_polygons 8, water_lines 4, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 522 / 521 | 221 | 0.75 | check the flags | 28% | 12% | 59% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 3 | 167 / 165 | 174 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 5 | 587 / 586 | 344 | 0.74 | check the flags | 22% | 15% | 63% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 4 | 490 / 489 | 167 | 0.75 | check the flags | 25% | 14% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 440 / 440 | 323 | 0.83 | auto | 46% | 7% | 47% | tee stage: Blue tee_centroid |  |
| 6 | 4 | 443 / 443 | 143 | 0.81 | auto | 38% | 8% | 54% | tee stage: Blue tee_centroid |  |
| 7 | 3 | 216 / 216 | 70 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 5 | 625 / 619 | 16 | 0.72 | check the flags | 19% | 9% | 72% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 3 | 202 / 201 | 13 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 4 | 456 / 456 | 303 | 0.76 | check the flags | 31% | 9% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 237 / 237 | 158 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 496 / 495 | 330 | 0.77 | check the flags | 29% | 19% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 4 | 406 / 405 | 205 | 0.77 | check the flags | 24% | 27% | 49% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 5 | 529 / 528 | 190 | 0.76 | check the flags | 29% | 14% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 3 | 155 / 155 | 153 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 576 / 575 | 344 | 0.67 | check the flags | 53% | 3% | 44% | tee stage: Blue texture_pad | tee: tee stage: Blue texture_pad; Blue tee on an imagery-detected pad (texture; no OSM box at 576 yds) |
| 17 | 4 | 414 / 413 | 171 | 0.80 | auto | 55% | 0% | 45% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 503 / 500 | 67 | 0.75 | check the flags | 26% | 12% | 62% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: relation/13729803 Memorial Park Golf Course (Houston, TX)
- **osm**: ok: 832 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/memorial_park/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 42 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/memorial_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/memorial_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -1712 m2 {'road': 539, 'strip': 367, 'cells': 737}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 10 polygons (outside 10); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red
