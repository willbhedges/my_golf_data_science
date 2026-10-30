# Swope Memorial Golf Course (Kansas City, MO) - Blue tees

Built 2026-10-30T00:46:44Z. OSM way/68196001. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 53 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.366 |
| mean_confidence | 0.823 |
| osm_score | 0.873 |

OSM features inside the course: buildings 1, golf=bunker 42, golf=cartpath 8, golf=clubhouse 1, golf=fairway 21, golf=green 19, golf=hole 18, golf=pin 18, golf=tee 53, holes_with_handicap 18, holes_with_par 18, tees_with_ref 50, trees_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 372 / 373 | 113 | 0.76 | check the flags | 30% | 11% | 58% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 317 / 316 | 172 | 0.75 | check the flags | 24% | 18% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 267 / 267 | 224 | 0.75 | check the flags | 16% | 9% | 75% | tee stage: Blue tee_centroid |  |
| 4 | 4 | 368 / 369 | 68 | 0.69 | check the flags | 44% | 12% | 44% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 368 yds) |
| 5 | 5 | 451 / 451 | 316 | 0.80 | auto | 40% | 22% | 39% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 3 | 172 / 171 | 96 | 0.82 | auto | 100% | 0% | 0% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 172 yds) |
| 7 | 4 | 330 / 330 | 198 | 0.72 | check the flags | 8% | 22% | 70% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 167 / 167 | 16 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 477 / 478 | 290 | 0.87 | auto | 53% | 16% | 31% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 384 / 385 | 106 | 0.81 | auto | 34% | 35% | 31% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 4 | 361 / 361 | 154 | 0.81 | auto | 31% | 19% | 50% | tee stage: Blue tee_centroid |  |
| 12 | 5 | 504 / 503 | 192 | 0.86 | auto | 60% | 6% | 34% | tee stage: Blue tee_centroid |  |
| 13 | 3 | 235 / 235 | 1 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 14 | 4 | 416 / 416 | 228 | 0.87 | auto | 70% | 11% | 18% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 349 / 350 | 81 | 0.83 | auto | 33% | 28% | 40% | tee stage: Blue tee_centroid |  |
| 16 | 3 | 134 / 134 | 81 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 17 | 5 | 566 / 565 | 2 | 0.82 | auto | 41% | 12% | 47% | tee stage: Blue tee_centroid |  |
| 18 | 4 | 404 / 405 | 276 | 0.77 | check the flags | 27% | 21% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/68196001 Swope Memorial Golf Course (Kansas City, MO)
- **osm**: ok: 251 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 46 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/swope_memorial/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/swope_memorial/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
