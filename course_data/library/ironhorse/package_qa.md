# Ironhorse Golf Club (Leawood, KS) - Black tees

Built 2026-10-30T03:31:19Z. OSM way/237531758. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 20 |
| greens_found | 18 |
| tee_boxes | 96 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.445 |
| mean_confidence | 0.844 |
| osm_score | 0.889 |

OSM features inside the course: buildings 4, golf=bunker 48, golf=cartpath 61, golf=clubhouse 1, golf=driving_range 7, golf=fairway 26, golf=green 23, golf=hole 20, golf=lateral_water_hazard 1, golf=pin 18, golf=rough 2, golf=tee 96, golf=water_hazard 1, holes_with_par 18, tees_with_ref 91, trees_polygons 12, water_lines 11, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 405 / 405 | 40 | 0.82 | auto | 58% | 2% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 3 | 211 / 211 | 237 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 425 / 425 | 49 | 0.83 | auto | 51% | 17% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 518 / 519 | 87 | 0.84 | auto | 42% | 17% | 41% | tee stage: Black tee_centroid |  |
| 5 | 3 | 212 / 210 | 70 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 405 / 406 | 276 | 0.81 | auto | 45% | 16% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 340 / 341 | 109 | 0.77 | check the flags | 32% | 14% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 408 / 409 | 277 | 0.81 | auto | 41% | 22% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 5 | 555 / 555 | 246 | 0.87 | auto | 56% | 15% | 29% | tee stage: Black tee_centroid |  |
| 10 | 5 | 555 / 555 | 293 | 0.83 | auto | 43% | 28% | 29% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 371 / 370 | 180 | 0.71 | check the flags | 53% | 8% | 38% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 371 yds) |
| 12 | 3 | 190 / 190 | 300 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 387 / 380 | 4 | 0.81 | auto | 39% | 27% | 33% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 481 / 482 | 284 | 0.85 | auto | 44% | 21% | 35% | tee stage: Black tee_centroid |  |
| 15 | 4 | 372 / 372 | 130 | 0.84 | auto | 27% | 42% | 31% | tee stage: Black tee_centroid |  |
| 16 | 4 | 380 / 379 | 339 | 0.83 | auto | 44% | 30% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 199 / 199 | 165 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 5 | 475 / 1607 | 106 | 0.83 | auto | 48% | 22% | 31% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/237531758 Ironhorse Golf Club (Leawood, KS)
- **osm**: ok: 1521 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 1/1 holes OSM has no way for (0 to check; segment no, lidar pads 561, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 112 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/ironhorse/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/ironhorse/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 34 polygons (outside 34); mode replace

## Warnings

- hole 18: measured 1607 vs card 475 yds for Black (no OSM tee box at that yardage?)
