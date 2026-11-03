# Fred Arbanas Golf Course (Kansas City, MO) - Blue tees

Built 2026-11-03T09:11:07Z. OSM way/913710102. Scorecard: file (course_data/library/longview_lake/card_golfify.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Gold, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 87 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.398 |
| mean_confidence | 0.816 |
| osm_score | 0.88 |

OSM features inside the course: buildings 2, golf=bunker 21, golf=cartpath 21, golf=clubhouse 1, golf=driving_range 1, golf=fairway 18, golf=green 27, golf=hole 18, golf=pin 27, golf=tee 87, holes_with_handicap 18, holes_with_par 18, single_trees 102, water_polygons 7

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 387 / 387 | 217 | 0.81 | auto | 38% | 8% | 54% | tee stage: Blue tee_centroid |  |
| 2 | 4 | 376 / 376 | 230 | 0.78 | check the flags | 31% | 6% | 63% | tee stage: Blue tee_centroid |  |
| 3 | 5 | 518 / 518 | 59 | 0.77 | check the flags | 43% | 2% | 55% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 222 / 222 | 39 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 5 | 511 / 511 | 204 | 0.80 | check the flags | 39% | 3% | 58% | tee stage: Blue tee_centroid |  |
| 6 | 4 | 399 / 400 | 67 | 0.73 | check the flags | 28% | 2% | 70% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 3 | 182 / 182 | 315 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 388 / 387 | 355 | 0.82 | auto | 60% | 2% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 369 / 369 | 325 | 0.74 | check the flags | 33% | 2% | 66% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 5 | 548 / 549 | 238 | 0.82 | auto | 47% | 0% | 52% | tee stage: Blue tee_centroid |  |
| 11 | 3 | 203 / 203 | 48 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 403 / 404 | 259 | 0.80 | check the flags | 46% | 8% | 46% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 4 | 457 / 457 | 42 | 0.77 | check the flags | 42% | 3% | 55% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 5 | 519 / 519 | 162 | 0.76 | check the flags | 34% | 9% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 400 / 400 | 332 | 0.81 | auto | 39% | 8% | 54% | tee stage: Blue tee_centroid |  |
| 16 | 3 | 174 / 174 | 281 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 401 / 402 | 94 | 0.76 | check the flags | 35% | 6% | 59% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 422 / 422 | 131 | 0.79 | check the flags | 42% | 12% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/913710102 Fred Arbanas Golf Course (Kansas City, MO)
- **osm**: ok: 520 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/longview_lake/card_golfify.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 60 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/longview_lake/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/longview_lake/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -10054 m2 {'road': 8076, 'cells': 1937}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): #1 18, #2 9); kept the largest group (no name or near point decides: CHECK the course), 18 ways; ignored 9
- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red
