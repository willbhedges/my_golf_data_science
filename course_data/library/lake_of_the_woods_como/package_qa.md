# Lake of the Woods Golf Course (Columbia, MO) - Blue tees

Built 2026-11-26T07:55:24Z. OSM way/387184389. Scorecard: file (course_data/library/lake_of_the_woods_como/routed_card.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 28 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.298 |
| mean_confidence | 0.799 |
| osm_score | 0.837 |

OSM features inside the course: buildings 7, golf=bunker 3, golf=cartpath 22, golf=fairway 21, golf=green 18, golf=hole 18, golf=tee 28, golf=water_hazard 2, holes_with_par 18, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 398 / 397 | 158 | 0.70 | check the flags | 38% | 24% | 38% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 398 yds) |
| 2 | 3 | 181 / 181 | 233 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 357 / 353 | 286 | 0.75 | check the flags | 18% | 25% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 4 | 298 / 297 | 10 | 0.72 | check the flags | 20% | 41% | 39% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 298 yds) |
| 5 | 4 | 360 / 359 | 3 | 0.73 | check the flags | 32% | 32% | 36% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 360 yds) |
| 6 | 4 | 430 / 430 | 142 | 0.70 | check the flags | 37% | 24% | 39% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 430 yds) |
| 7 | 3 | 210 / 205 | 310 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 365 / 364 | 134 | 0.76 | check the flags | 34% | 44% | 22% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 365 yds) |
| 9 | 5 | 495 / 367 | 345 | 0.80 | check the flags | 38% | 20% | 42% | tee stage: Blue tee_axis_capped | tee: tee stage: Blue tee_axis_capped |
| 10 | 3 | 150 / 150 | 349 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 11 | 5 | 575 / 571 | 94 | 0.84 | auto | 26% | 59% | 15% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 352 / 353 | 262 | 0.85 | auto | 38% | 45% | 17% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 4 | 468 / 467 | 175 | 0.65 | check the flags | 28% | 11% | 61% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 468 yds) |
| 14 | 4 | 377 / 304 | 29 | 0.76 | check the flags | 14% | 17% | 68% | tee stage: Blue tee_centroid_capped |  |
| 15 | 4 | 311 / 306 | 73 | 0.83 | auto | 22% | 60% | 18% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 516 / 516 | 221 | 0.73 | check the flags | 37% | 42% | 21% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 516 yds) |
| 17 | 3 | 165 / 170 | 230 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 165 yds) |
| 18 | 4 | 370 / 369 | 346 | 0.84 | auto | 36% | 29% | 35% | tee stage: Blue tee_centroid |  |

## Stages

- **resolve**: ok: way/387184389 Lake of the Woods Golf Course (Columbia, MO)
- **osm**: ok: 233 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/lake_of_the_woods_como/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 17 candidate pads near hole starts (10 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/lake_of_the_woods_como/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/lake_of_the_woods_como/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -232 m2 {'cells': 230}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 14 polygons (outside 14); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
- hole 9 Blue: CHECK, tee was put 132 yds from this hole's start, at hole 3's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 9 White: CHECK, tee was put 132 yds from this hole's start, at hole 3's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 14 Blue: CHECK, tee was put 108 yds from this hole's start, at hole 17's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 9: measured 367 vs card 495 yds for Blue (no OSM tee box at that yardage?)
- hole 14: measured 304 vs card 377 yds for Blue (no OSM tee box at that yardage?)
