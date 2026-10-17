# Veenker Memorial Golf Course (Ames, IA) - Blue tees

Built 2026-10-17T00:46:59Z. OSM way/44804299. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'White' not on the card (sets: Blue, Gold, Red)).

**WARNING: requested tee set 'White' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, Gold, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 43 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.305 |
| mean_confidence | 0.818 |
| osm_score | 0.861 |

OSM features inside the course: buildings 8, golf=bunker 27, golf=cartpath 5, golf=fairway 30, golf=green 26, golf=hole 18, golf=lateral_water_hazard 2, golf=path 38, golf=rough 1, golf=tee 43, holes_with_handicap 18, holes_with_par 18, water_lines 1, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 435 / 434 | 176 | 0.77 | check the flags | 37% | 9% | 54% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; imagery-model sand where OSM has none (segment gap-fill; check on the map) |
| 2 | 4 | 334 / 338 | 249 | 0.82 | auto | 18% | 41% | 41% | tee stage: Blue tee_centroid | imagery-model sand where OSM has none (segment gap-fill; check on the map) |
| 3 | 4 | 333 / 318 | 30 | 0.80 | auto | 22% | 28% | 50% | tee stage: Blue tee_centroid |  |
| 4 | 4 | 349 / 348 | 298 | 0.79 | check the flags | 35% | 22% | 42% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 402 / 401 | 169 | 0.81 | auto | 32% | 20% | 48% | tee stage: Blue tee_centroid |  |
| 6 | 3 | 210 / 209 | 88 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 5 | 590 / 591 | 66 | 0.70 | check the flags | 24% | 26% | 50% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 590 yds) |
| 8 | 3 | 181 / 174 | 29 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 537 / 538 | 294 | 0.81 | auto | 37% | 12% | 51% | tee stage: Blue tee_centroid |  |
| 10 | 5 | 560 / 568 | 146 | 0.78 | check the flags | 30% | 26% | 45% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 155 / 155 | 242 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 330 / 331 | 248 | 0.68 | check the flags | 26% | 14% | 60% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 330 yds) |
| 13 | 3 | 160 / 160 | 56 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 416 / 416 | 339 | 0.79 | check the flags | 26% | 34% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 420 / 419 | 237 | 0.79 | check the flags | 35% | 20% | 45% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 544 / 550 | 140 | 0.76 | check the flags | 45% | 24% | 31% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 544 yds) |
| 17 | 3 | 190 / 190 | 118 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 5 | 534 / 533 | 335 | 0.77 | check the flags | 32% | 16% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/44804299 Veenker Memorial Golf Course (Ames, IA)
- **osm**: ok: 598 features
- **scorecard**: ok: golfify (golfify)
- **tees**: ok: tees/place_tee.place_course_sets (joint, ordered back to front, green centroid) for 3 sets; lidar pads: 36 candidate pads near hole starts, 4 placement(s) on one
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/veenker/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **elevation**: ok: course_data/packages/veenker/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised)
- **segment**: ok: segment gap-fill ariadgolf-v4@43ee2944 (+3 zones on 2 holes, +0 greens, 18 tee candidates)

## Warnings

- requested tee set 'White' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, Gold, Red
