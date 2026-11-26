# Harbour Town Golf Links (Hilton Head Island, SC) - Heritage tees

Built 2026-11-26T19:06:28Z. OSM relation/4813858. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Heritage, Blue, White, Gold, Green)).

**WARNING: requested tee set 'Black' is not on the card; using 'Heritage' instead (allow_substitute). Sets on the card: Heritage, Blue, White, Gold, Green**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 38 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.434 |
| mean_confidence | 0.842 |
| osm_score | 0.887 |

OSM features inside the course: buildings 4, golf=bunker 75, golf=cartpath 42, golf=fairway 31, golf=green 31, golf=hole 18, golf=lateral_water_hazard 10, golf=pin 18, golf=rough 6, golf=tee 38, golf=water_hazard 7, holes_with_par 18, single_trees 8, water_polygons 19

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 414 / 410 | 123 | 0.81 | auto | 22% | 50% | 27% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 2 | 5 | 544 / 515 | 148 | 0.75 | check the flags | 26% | 68% | 6% | tee stage: Heritage walkback_capped | tee: tee stage: Heritage walkback_capped; Heritage tee walked back along the hole line (no box at 544 yds) |
| 3 | 4 | 465 / 464 | 224 | 0.78 | check the flags | 44% | 38% | 18% | tee stage: Heritage lidar_pad | tee: tee stage: Heritage lidar_pad; Heritage tee on a lidar pad (no OSM box at 465 yds) |
| 4 | 3 | 194 / 193 | 187 | 0.93 | auto | 100% | 0% | 0% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 5 | 5 | 561 / 561 | 76 | 0.75 | check the flags | 42% | 27% | 31% | tee stage: Heritage lidar_pad | tee: tee stage: Heritage lidar_pad; Heritage tee on a lidar pad (no OSM box at 561 yds) |
| 6 | 4 | 419 / 418 | 327 | 0.86 | auto | 55% | 30% | 15% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 7 | 3 | 216 / 216 | 234 | 0.86 | auto | 100% | 0% | 0% | tee stage: Heritage lidar_pad | tee: tee stage: Heritage lidar_pad; Heritage tee on a lidar pad (no OSM box at 216 yds) |
| 8 | 4 | 467 / 466 | 3 | 0.84 | auto | 34% | 50% | 16% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 9 | 4 | 326 / 326 | 326 | 0.81 | auto | 27% | 40% | 32% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 10 | 4 | 435 / 434 | 197 | 0.80 | check the flags | 51% | 1% | 48% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 11 | 4 | 432 / 431 | 169 | 0.84 | auto | 44% | 33% | 23% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 12 | 4 | 426 / 426 | 222 | 0.83 | auto | 34% | 44% | 22% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 13 | 4 | 372 / 372 | 250 | 0.85 | auto | 42% | 43% | 15% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 14 | 3 | 188 / 188 | 28 | 0.96 | auto | 100% | 0% | 0% | tee stage: Heritage tee_centroid |  |
| 15 | 5 | 584 / 584 | 52 | 0.82 | auto | 67% | 26% | 7% | tee stage: Heritage lidar_pad | tee: tee stage: Heritage lidar_pad; Heritage tee on a lidar pad (no OSM box at 584 yds) |
| 16 | 4 | 420 / 419 | 351 | 0.83 | auto | 42% | 14% | 44% | tee stage: Heritage tee_centroid |  |
| 17 | 3 | 198 / 203 | 246 | 0.93 | auto | 100% | 0% | 0% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 18 | 4 | 470 / 469 | 18 | 0.89 | auto | 76% | 12% | 12% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |

## Stages

- **resolve**: ok: relation/4813858 Harbour Town Golf Links (Hilton Head Island, SC)
- **osm**: ok: 684 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 33 candidate pads near hole starts (13 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/harbour_town/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/harbour_town/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -3233 m2 {'strip': 2038, 'road': 519, 'cells': 647}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 47 polygons (outside 47); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- ignored 4 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1238650436, 1238650437, 1238650440, 1238650441
- requested tee set 'Black' is not on the card; using 'Heritage' instead (allow_substitute). Sets on the card: Heritage, Blue, White, Gold, Green
- hole 2 Heritage: CHECK, walk-back ran onto a road (OSM 347307270) 20 yds behind the line start: capped there (28 yds short of the card)
- hole 3 Blue: CHECK, tee was put 87 yds from this hole's start, at hole 7's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 3 White: CHECK, tee was put 122 yds from this hole's start, at hole 7's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2: measured 515 vs card 544 yds for Heritage (no OSM tee box at that yardage?)
- scorecard (opengolfapi): Heritage: holes sum to 7131 but the source says 7099 (+32): mixed card versions
- scorecard (opengolfapi): Blue: holes sum to 6642 but the source says 6681 (-39): mixed card versions
- scorecard (opengolfapi): White: holes sum to 6103 but the source says 6253 (-150): mixed card versions
- scorecard (opengolfapi): Gold: holes sum to 5478 but the source says 5867 (-389): mixed card versions
- scorecard (opengolfapi): Green: holes sum to 4760 but the source says 5084 (-324): mixed card versions
