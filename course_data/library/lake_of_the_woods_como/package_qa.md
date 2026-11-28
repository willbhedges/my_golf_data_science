# Lake of the Woods Golf Course (Columbia, MO) - Blue tees

Built 2026-11-28T02:50:56Z. OSM way/387184389. Scorecard: file (course_data/library/lake_of_the_woods_como/routed_card.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 48 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.322 |
| mean_confidence | 0.842 |
| osm_score | 0.864 |

OSM features inside the course: buildings 7, golf=bunker 3, golf=cartpath 22, golf=fairway 21, golf=green 18, golf=hole 18, golf=tee 48, golf=water_hazard 2, holes_with_par 18, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 398 / 392 | 164 | 0.80 | auto | 37% | 23% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 3 | 181 / 181 | 233 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 357 / 353 | 286 | 0.75 | check the flags | 18% | 25% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 4 | 298 / 297 | 5 | 0.79 | check the flags | 20% | 40% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 360 / 359 | 10 | 0.81 | auto | 33% | 34% | 34% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 430 / 430 | 160 | 0.83 | auto | 36% | 22% | 42% | tee stage: Blue tee_centroid |  |
| 7 | 3 | 210 / 205 | 310 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 365 / 365 | 130 | 0.83 | auto | 34% | 43% | 22% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 495 / 494 | 351 | 0.82 | auto | 38% | 34% | 28% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 3 | 150 / 150 | 349 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 11 | 5 | 575 / 571 | 92 | 0.84 | auto | 27% | 57% | 15% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 352 / 353 | 262 | 0.85 | auto | 38% | 45% | 17% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 4 | 468 / 467 | 174 | 0.77 | check the flags | 33% | 11% | 56% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 377 / 383 | 32 | 0.85 | auto | 35% | 32% | 33% | tee stage: Blue tee_centroid_capped |  |
| 15 | 4 | 311 / 306 | 73 | 0.83 | auto | 22% | 60% | 18% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 516 / 511 | 228 | 0.84 | auto | 44% | 35% | 21% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 3 | 165 / 170 | 229 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 165 yds) |
| 18 | 4 | 370 / 369 | 347 | 0.84 | auto | 35% | 27% | 37% | tee stage: Blue tee_centroid |  |

## Stages

- **resolve**: ok: way/387184389 Lake of the Woods Golf Course (Columbia, MO)
- **osm**: ok: 253 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/lake_of_the_woods_como/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 25 candidate pads near hole starts (10 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/lake_of_the_woods_como/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/lake_of_the_woods_como/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -232 m2 {'cells': 230}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
- hole 14 Blue: CHECK, tee was put 66 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
