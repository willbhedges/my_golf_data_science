# George Wright Golf Course (Hyde Park, MA) - Blue tees

Built 2026-10-31T01:57:42Z. OSM way/29830747. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 37 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.418 |
| mean_confidence | 0.849 |
| osm_score | 0.87 |

OSM features inside the course: buildings 5, built_up_landuse 1, golf=bunker 42, golf=cartpath 26, golf=fairway 20, golf=green 18, golf=hole 17, golf=tee 37, golf=water_hazard 10, holes_with_handicap 17, holes_with_par 17, trees_polygons 1, water_lines 1, water_polygons 15

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 377 / 377 | 10 | 0.85 | auto | 38% | 30% | 32% | tee stage: Blue tee_centroid |  |
| 2 | 4 | 321 / 321 | 5 | 0.82 | auto | 34% | 40% | 26% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 5 | 515 / 518 | 212 | 0.82 | auto | 32% | 43% | 25% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 165 / 165 | 118 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 412 / 412 | 188 | 0.89 | auto | 70% | 20% | 10% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 395 / 389 | 20 | 0.85 | auto | 38% | 48% | 14% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 400 / 400 | 17 | 0.85 | auto | 47% | 34% | 20% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 185 / 186 | 168 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 185 yds) |
| 9 | 4 | 453 / 453 | 179 | 0.86 | auto | 49% | 38% | 14% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 4 | 462 / 462 | 235 | 0.77 | check the flags | 50% | 24% | 26% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 462 yds) |
| 11 | 4 | 362 / 362 | 23 | 0.80 | check the flags | 25% | 37% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 412 / 413 | 122 | 0.80 | check the flags | 41% | 16% | 43% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 4 | 390 / 391 | 296 | 0.82 | auto | 43% | 24% | 33% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 3 | 191 / 191 | 133 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 5 | 510 / 511 | 105 | 0.81 | auto | 46% | 13% | 41% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 340 / 340 | 331 | 0.83 | auto | 39% | 37% | 24% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 3 | 170 / 169 | 321 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 380 / 381 | 312 | 0.87 | auto | 34% | 47% | 20% | tee stage: Blue tee_centroid |  |

## Stages

- **resolve**: ok: way/29830747 George Wright Golf Course (Hyde Park, MA)
- **osm**: ok: 1805 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 89 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/george_wright/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/george_wright/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 8 polygons (outside 8); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
