# Harbour Town Golf Links (Hilton Head Island, SC) - Heritage tees

Built 2026-11-01T22:44:08Z. OSM relation/4813858. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Heritage, Blue, White, Gold, Green)).

**WARNING: requested tee set 'Black' is not on the card; using 'Heritage' instead (allow_substitute). Sets on the card: Heritage, Blue, White, Gold, Green**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 44 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.4 |
| mean_confidence | 0.829 |
| osm_score | 0.88 |

OSM features inside the course: buildings 4, golf=bunker 75, golf=cartpath 42, golf=fairway 31, golf=green 31, golf=hole 18, golf=lateral_water_hazard 10, golf=pin 18, golf=rough 6, golf=tee 44, golf=water_hazard 7, holes_with_par 18, single_trees 8, water_polygons 19

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 414 / 410 | 123 | 0.80 | auto | 22% | 46% | 32% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 2 | 5 | 544 / 515 | 148 | 0.71 | check the flags | 26% | 46% | 28% | tee stage: Heritage walkback_capped | tee: tee stage: Heritage walkback_capped; Heritage tee walked back along the hole line (no box at 544 yds) |
| 3 | 4 | 465 / 464 | 224 | 0.76 | check the flags | 44% | 30% | 27% | tee stage: Heritage lidar_pad | tee: tee stage: Heritage lidar_pad; Heritage tee on a lidar pad (no OSM box at 465 yds) |
| 4 | 3 | 194 / 193 | 187 | 0.93 | auto | 100% | 0% | 0% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 5 | 5 | 561 / 561 | 76 | 0.75 | check the flags | 42% | 24% | 34% | tee stage: Heritage lidar_pad | tee: tee stage: Heritage lidar_pad; Heritage tee on a lidar pad (no OSM box at 561 yds) |
| 6 | 4 | 419 / 418 | 327 | 0.86 | auto | 55% | 28% | 17% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 7 | 3 | 216 / 216 | 234 | 0.93 | auto | 100% | 0% | 0% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 8 | 4 | 467 / 429 | 340 | 0.72 | check the flags | 29% | 48% | 23% | tee stage: Heritage walkback_capped | tee: tee stage: Heritage walkback_capped; Heritage tee walked back along the hole line (no box at 467 yds) |
| 9 | 4 | 326 / 326 | 326 | 0.78 | check the flags | 27% | 24% | 48% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 10 | 4 | 435 / 434 | 197 | 0.79 | check the flags | 51% | 0% | 48% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 11 | 4 | 432 / 431 | 169 | 0.82 | auto | 44% | 25% | 31% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 12 | 4 | 426 / 426 | 222 | 0.82 | auto | 34% | 39% | 26% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 13 | 4 | 372 / 372 | 250 | 0.84 | auto | 42% | 39% | 19% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 14 | 3 | 188 / 188 | 28 | 0.96 | auto | 100% | 0% | 0% | tee stage: Heritage tee_centroid |  |
| 15 | 5 | 584 / 584 | 52 | 0.89 | auto | 67% | 25% | 8% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 16 | 4 | 420 / 419 | 334 | 0.74 | check the flags | 0% | 95% | 4% | tee stage: Heritage walkback | tee: tee stage: Heritage walkback; no fairway in the landing zone; Heritage tee walked back along the hole line (no box at 420 yds) |
| 17 | 3 | 198 / 204 | 246 | 0.93 | auto | 100% | 0% | 0% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |
| 18 | 4 | 470 / 469 | 18 | 0.88 | auto | 76% | 10% | 14% | tee stage: Heritage tee_axis | tee: tee stage: Heritage tee_axis |

## Stages

- **resolve**: ok: relation/4813858 Harbour Town Golf Links (Hilton Head Island, SC)
- **osm**: ok: 684 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 2/2 holes OSM has no way for (0 to check; segment no, lidar pads 251, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 47 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/harbour_town/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/harbour_town/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 48 polygons (outside 48); mode replace

## Warnings

- ignored 6 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 722552383, 722552391, 1238650436, 1238650437, 1238650440, 1238650441
- requested tee set 'Black' is not on the card; using 'Heritage' instead (allow_substitute). Sets on the card: Heritage, Blue, White, Gold, Green
- hole 2 Heritage: CHECK, walk-back ran onto a road (OSM 347307270) 20 yds behind the line start: capped there (28 yds short of the card)
- hole 8 Heritage: CHECK, walk-back ran onto a green (OSM 713709018) 48 yds behind the line start: capped there (37 yds short of the card)
- hole 2: measured 515 vs card 544 yds for Heritage (no OSM tee box at that yardage?)
- hole 8: measured 429 vs card 467 yds for Heritage (no OSM tee box at that yardage?)
- scorecard (opengolfapi): Heritage: holes sum to 7131 but the source says 7099 (+32): mixed card versions
- scorecard (opengolfapi): Blue: holes sum to 6642 but the source says 6681 (-39): mixed card versions
- scorecard (opengolfapi): White: holes sum to 6103 but the source says 6253 (-150): mixed card versions
- scorecard (opengolfapi): Gold: holes sum to 5478 but the source says 5867 (-389): mixed card versions
- scorecard (opengolfapi): Green: holes sum to 4760 but the source says 5084 (-324): mixed card versions
