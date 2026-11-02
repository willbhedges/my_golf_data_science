# A. L. Gustin Golf Course (Columbia, MO) - Black tees

Built 2026-11-02T00:46:32Z. OSM way/449108205. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 52 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.396 |
| mean_confidence | 0.785 |
| osm_score | 0.779 |

OSM features inside the course: buildings 6, golf=bunker 38, golf=cartpath 13, golf=clubhouse 1, golf=fairway 22, golf=green 19, golf=hole 18, golf=tee 52, golf=water_hazard 1, holes_with_par 18, trees_polygons 3, water_lines 5, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 492 / 487 | 201 | 0.75 | check the flags | 35% | 0% | 65% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 3 | 162 / 158 | 171 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 440 / 440 | 221 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 384 / 385 | 94 | 0.81 | auto | 56% | 0% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 201 / 201 | 356 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 418 / 419 | 292 | 0.74 | check the flags | 31% | 0% | 69% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 369 / 364 | 56 | 0.68 | check the flags | 36% | 0% | 64% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 369 yds) |
| 8 | 4 | 376 / 372 | 95 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 338 / 338 | 44 | 0.70 | check the flags | 19% | 0% | 81% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 3 | 205 / 205 | 80 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 424 / 416 | 206 | 0.68 | check the flags | 36% | 0% | 64% | tee stage: Black lidar_pad_capped | tee: tee stage: Black lidar_pad_capped; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee on a lidar pad (no OSM box at 424 yds) |
| 12 | 5 | 518 / 515 | 180 | 0.83 | auto | 66% | 0% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 205 / 205 | 200 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 14 | 4 | 378 / 380 | 352 | 0.71 | check the flags | 47% | 0% | 53% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 378 yds) |
| 15 | 4 | 467 / 467 | 62 | 0.65 | check the flags | 38% | 0% | 62% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee walked back along the hole line (no box at 467 yds) |
| 16 | 4 | 332 / 329 | 224 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 4 | 405 / 405 | 39 | 0.80 | auto | 42% | 0% | 58% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 378 / 377 | 4 | 0.71 | check the flags | 23% | 0% | 77% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/449108205 A. L. Gustin Golf Course (Columbia, MO)
- **osm**: ok: 444 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 47 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/gustin/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/gustin/imagery/dem.tif (18/18 holes)
- **vision**: missing: no vision_any layers for 'gustin' (FileNotFoundError: course_data/vision_any/gustin/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

## Warnings

- hole 11 Black: CHECK, tee was on a road (OSM 278117436): moved 7 yds forward off it
- vision: missing: no vision_any layers for 'gustin' (FileNotFoundError: course_data/vision_any/gustin/raw (not fetched)); add the course to course_data/vision_any/course; trees / long grass come from OSM only
