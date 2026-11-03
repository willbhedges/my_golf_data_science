# Seneca Golf Course (Louisville, KY) - Blue tees

Built 2026-11-03T05:55:30Z. OSM way/59714994. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Yellow, Green, Red, Pink, Orange)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Yellow, Green, Red, Pink, Orange**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 86 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.36 |
| mean_confidence | 0.796 |
| osm_score | 0.815 |

OSM features inside the course: buildings 10, golf=bunker 23, golf=cartpath 25, golf=clubhouse 1, golf=driving_range 2, golf=fairway 28, golf=green 30, golf=hole 18, golf=pin 10, golf=tee 86, holes_with_handicap 18, holes_with_par 18, tees_with_ref 83, trees_polygons 3, water_lines 1, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 426 / 424 | 310 | 0.75 | check the flags | 37% | 0% | 63% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 412 / 411 | 340 | 0.78 | check the flags | 37% | 11% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 5 | 586 / 587 | 280 | 0.79 | check the flags | 41% | 12% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 217 / 217 | 144 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 217 yds) |
| 5 | 4 | 463 / 463 | 147 | 0.77 | check the flags | 39% | 4% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 397 / 396 | 350 | 0.75 | check the flags | 34% | 0% | 66% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 5 | 564 / 563 | 189 | 0.79 | check the flags | 42% | 9% | 49% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 149 / 149 | 177 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 320 / 320 | 141 | 0.76 | check the flags | 23% | 21% | 56% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 5 | 577 / 576 | 317 | 0.70 | check the flags | 19% | 0% | 81% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 390 / 390 | 56 | 0.82 | auto | 60% | 4% | 37% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 346 / 346 | 203 | 0.76 | check the flags | 32% | 8% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 3 | 213 / 213 | 19 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 438 / 437 | 188 | 0.74 | check the flags | 31% | 3% | 66% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 5 | 565 / 565 | 42 | 0.74 | check the flags | 32% | 0% | 68% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 3 | 206 / 206 | 140 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 399 / 400 | 287 | 0.78 | check the flags | 44% | 5% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 442 / 442 | 235 | 0.76 | check the flags | 34% | 9% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/59714994 Seneca Golf Course (Louisville, KY)
- **osm**: ok: 1558 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 43 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/seneca/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/seneca/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): #1 18, #2 9); kept the largest group (no name or near point decides: CHECK the course), 18 ways; ignored 9
- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Yellow, Green, Red, Pink, Orange
