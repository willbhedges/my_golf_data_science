# Pasatiempo Golf Course (Santa Cruz, CA) - Middle tees

Built 2026-10-30T22:08:16Z. OSM relation/13921737. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: White/Green Combo, Middle, Forward)).

**WARNING: requested tee set 'Black' is not on the card; using 'Middle' instead (allow_substitute). Sets on the card: White/Green Combo, Middle, Forward**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 34 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.368 |
| mean_confidence | 0.857 |
| osm_score | 0.868 |

OSM features inside the course: buildings 4, built_up_landuse 2, golf=bunker 92, golf=cartpath 25, golf=fairway 21, golf=green 21, golf=hole 18, golf=pin 18, golf=rough 22, golf=tee 34, holes_with_par 18, single_trees 76, water_lines 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 440 / 428 | 166 | 0.79 | check the flags | 38% | 14% | 48% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 2 | 4 | 420 / 419 | 162 | 0.81 | auto | 44% | 20% | 35% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 3 | 3 | 195 / 195 | 338 | 0.93 | auto | 100% | 0% | 0% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 4 | 4 | 358 / 357 | 180 | 0.84 | auto | 44% | 17% | 39% | tee stage: Middle tee_centroid |  |
| 5 | 3 | 174 / 174 | 355 | 0.96 | auto | 100% | 0% | 0% | tee stage: Middle tee_centroid |  |
| 6 | 5 | 516 / 515 | 350 | 0.85 | auto | 43% | 40% | 18% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 7 | 4 | 335 / 334 | 163 | 0.86 | auto | 43% | 27% | 30% | tee stage: Middle tee_centroid |  |
| 8 | 3 | 162 / 162 | 344 | 0.96 | auto | 100% | 0% | 0% | tee stage: Middle tee_centroid |  |
| 9 | 5 | 473 / 472 | 335 | 0.82 | auto | 46% | 19% | 35% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 10 | 4 | 440 / 441 | 295 | 0.82 | auto | 37% | 32% | 31% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 11 | 4 | 379 / 379 | 41 | 0.84 | auto | 9% | 62% | 28% | tee stage: Middle tee_centroid |  |
| 12 | 4 | 373 / 372 | 213 | 0.81 | auto | 29% | 20% | 51% | tee stage: Middle tee_centroid |  |
| 13 | 5 | 485 / 484 | 352 | 0.82 | auto | 47% | 21% | 31% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |
| 14 | 4 | 384 / 383 | 180 | 0.71 | check the flags | 40% | 27% | 33% | tee stage: Middle walkback | tee: tee stage: Middle walkback; Middle tee walked back along the hole line (no box at 384 yds) |
| 15 | 3 | 120 / 120 | 16 | 0.96 | auto | 100% | 0% | 0% | tee stage: Middle tee_centroid |  |
| 16 | 4 | 365 / 362 | 171 | 0.85 | auto | 26% | 47% | 27% | tee stage: Middle tee_centroid |  |
| 17 | 4 | 363 / 364 | 90 | 0.85 | auto | 32% | 40% | 28% | tee stage: Middle tee_centroid |  |
| 18 | 3 | 143 / 143 | 116 | 0.93 | auto | 100% | 0% | 0% | tee stage: Middle tee_axis | tee: tee stage: Middle tee_axis |

## Stages

- **resolve**: ok: relation/13921737 Pasatiempo Golf Course (Santa Cruz, CA)
- **osm**: ok: 859 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 51 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/pasatiempo/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/pasatiempo/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 26 polygons (outside 26); mode replace

## Warnings

- card consensus: opengolfapi: set order: 'Gold/White_Combo' is longer than 'Gold/White Combo' on 5 of 5 holes with several OSM tees: names may be swapped
- requested tee set 'Black' is not on the card; using 'Middle' instead (allow_substitute). Sets on the card: White/Green Combo, Middle, Forward
- scorecard (golfify): 9 hole(s) where a longer set is shorter than the next set: 1 Middle 440 < Forward 457, 2 Forward 376 < White/Green Combo 384, 4 Forward 343 < White/Green Combo 359, 5 Forward 156 < White/Green Combo 170
