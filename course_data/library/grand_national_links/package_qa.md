# RTJ Grand National Golf (Opelika, AL) - Purple tees

Built 2026-11-03T09:19:05Z. OSM way/328838760. Scorecard: file (course_data/library/grand_national_links/card_review.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Purple, Orange, White, Teal)).

**WARNING: requested tee set 'Black' is not on the card; using 'Purple' instead (allow_substitute). Sets on the card: Purple, Orange, White, Teal**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 150 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.409 |
| mean_confidence | 0.85 |
| osm_score | 0.882 |

OSM features inside the course: buildings 6, golf=bunker 101, golf=cartpath 26, golf=clubhouse 1, golf=driving_range 1, golf=fairway 31, golf=green 54, golf=hole 18, golf=lateral_water_hazard 1, golf=pin 40, golf=tee 150, holes_with_handicap 18, holes_with_par 18, tees_with_colour 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 423 / 423 | 68 | 0.69 | check the flags | 30% | 32% | 38% | tee stage: Purple walkback | tee: tee stage: Purple walkback; Purple tee walked back along the hole line (no box at 423 yds) |
| 2 | 5 | 556 / 555 | 359 | 0.88 | auto | 53% | 22% | 25% | tee stage: Purple tee_centroid |  |
| 3 | 3 | 206 / 206 | 115 | 0.93 | auto | 100% | 0% | 0% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 4 | 4 | 425 / 424 | 12 | 0.82 | auto | 31% | 24% | 45% | tee stage: Purple tee_centroid |  |
| 5 | 4 | 456 / 455 | 140 | 0.81 | auto | 36% | 33% | 32% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 6 | 5 | 544 / 545 | 52 | 0.82 | auto | 48% | 19% | 33% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 7 | 4 | 472 / 473 | 256 | 0.82 | auto | 42% | 28% | 30% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 8 | 4 | 345 / 345 | 291 | 0.88 | auto | 69% | 2% | 29% | tee stage: Purple tee_centroid |  |
| 9 | 3 | 204 / 204 | 245 | 0.96 | auto | 100% | 0% | 0% | tee stage: Purple tee_centroid |  |
| 10 | 4 | 363 / 362 | 2 | 0.82 | auto | 30% | 45% | 25% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 11 | 3 | 260 / 260 | 317 | 0.93 | auto | 100% | 0% | 0% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 12 | 5 | 575 / 574 | 197 | 0.85 | auto | 43% | 23% | 34% | tee stage: Purple tee_centroid |  |
| 13 | 4 | 418 / 423 | 198 | 0.76 | check the flags | 14% | 35% | 51% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 14 | 4 | 467 / 467 | 127 | 0.80 | check the flags | 38% | 20% | 42% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 15 | 5 | 516 / 515 | 212 | 0.82 | auto | 39% | 32% | 29% | tee stage: Purple tee_axis | tee: tee stage: Purple tee_axis |
| 16 | 3 | 181 / 181 | 144 | 0.96 | auto | 100% | 0% | 0% | tee stage: Purple tee_centroid |  |
| 17 | 4 | 429 / 428 | 157 | 0.86 | auto | 47% | 20% | 33% | tee stage: Purple tee_centroid |  |
| 18 | 4 | 471 / 472 | 292 | 0.86 | auto | 52% | 16% | 32% | tee stage: Purple tee_centroid |  |

## Stages

- **resolve**: ok: way/328838760 RTJ Grand National Golf (Opelika, AL)
- **osm**: ok: 728 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/grand_national_links/card_review.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 0 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/grand_national_links/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/grand_national_links/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 2 polygons (outside 2); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): lake 18, #2 18); kept the course nearest the request's near point (1848 yds vs 3421), 18 ways; ignored 18 + 17 unnumbered golf=hole way(s) in no kept course: OSM 1098809319, 1098809321, 1098809332, 1098809333, 1098809334, 1098809335, 1098809336, 1098809337 ...
- requested tee set 'Black' is not on the card; using 'Purple' instead (allow_substitute). Sets on the card: Purple, Orange, White, Teal
