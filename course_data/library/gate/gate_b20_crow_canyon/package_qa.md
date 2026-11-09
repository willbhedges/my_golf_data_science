# Crow Canyon Country Club (Danville, CA) - Black tees

Built 2026-11-09T21:34:03Z. OSM relation/3132092. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 46 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.287 |
| mean_confidence | 0.843 |
| osm_score | 0.857 |

OSM features inside the course: buildings 1, built_up_landuse 1, golf=bunker 54, golf=cartpath 2, golf=fairway 24, golf=green 19, golf=hole 18, golf=pin 18, golf=tee 46, golf=water_hazard 5, holes_with_par 18, water_lines 4, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 371 / 371 | 39 | 0.80 | check the flags | 27% | 36% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 5 | 570 / 568 | 115 | 0.82 | auto | 36% | 36% | 28% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 405 / 400 | 298 | 0.81 | auto | 32% | 37% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 172 / 172 | 214 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 325 / 325 | 214 | 0.81 | auto | 9% | 47% | 44% | tee stage: Black tee_centroid |  |
| 6 | 3 | 200 / 195 | 324 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 380 / 379 | 326 | 0.85 | auto | 28% | 63% | 9% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 168 / 168 | 39 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 403 / 401 | 135 | 0.82 | auto | 24% | 50% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 345 / 344 | 16 | 0.81 | auto | 29% | 39% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 370 / 370 | 307 | 0.88 | auto | 27% | 57% | 16% | tee stage: Black tee_centroid |  |
| 12 | 3 | 148 / 145 | 16 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 5 | 523 / 518 | 124 | 0.77 | check the flags | 33% | 49% | 18% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 523 yds) |
| 14 | 4 | 348 / 349 | 88 | 0.83 | auto | 19% | 47% | 34% | tee stage: Black tee_centroid |  |
| 15 | 4 | 340 / 340 | 134 | 0.82 | auto | 21% | 57% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 180 / 170 | 296 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad_capped | tee: tee stage: Black lidar_pad_capped; Black tee on a lidar pad (no OSM box at 180 yds) |
| 17 | 4 | 403 / 403 | 302 | 0.71 | check the flags | 27% | 42% | 30% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 403 yds) |
| 18 | 4 | 401 / 401 | 233 | 0.86 | auto | 60% | 5% | 35% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: relation/3132092 Crow Canyon Country Club (Danville, CA)
- **osm**: ok: 1363 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 114 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/gate_b20_crow_canyon/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/gate_b20_crow_canyon/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -1371 m2 {'cells': 1330}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 40 polygons (outside 40); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 9 Red: CHECK, tee was on a building (OSM 1416772510): moved 41 yds forward off it
- hole 9 Gold: CHECK, tee was on a building (OSM 1416772510): moved 41 yds forward off it
- hole 16 Black: CHECK, tee was on a building (OSM 1175985504): moved 5 yds forward off it
