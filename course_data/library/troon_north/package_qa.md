# Troon North Golf Club (Scottsdale, AZ) - Black tees

Built 2026-11-03T04:14:14Z. OSM relation/1389558. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 117 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.362 |
| mean_confidence | 0.818 |
| osm_score | 0.844 |

OSM features inside the course: golf=bunker 119, golf=cartpath 9, golf=fairway 48, golf=green 37, golf=hole 18, golf=pin 36, golf=rough 25, golf=tee 117, golf=water_hazard 4, holes_with_handicap 18, holes_with_par 18, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 444 / 445 | 267 | 0.88 | auto | 38% | 44% | 17% | tee stage: Black tee_centroid |  |
| 2 | 3 | 172 / 172 | 8 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 5 | 556 / 417 | 311 | 0.75 | check the flags | 46% | 40% | 14% | tee stage: Black walkback_capped | tee: tee stage: Black walkback_capped; Black tee walked back along the hole line (no box at 556 yds) |
| 4 | 4 | 420 / 416 | 86 | 0.81 | auto | 40% | 25% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 464 / 460 | 79 | 0.81 | auto | 40% | 24% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 306 / 306 | 313 | 0.66 | check the flags | 20% | 32% | 48% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 306 yds) |
| 7 | 3 | 205 / 200 | 156 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 408 / 409 | 95 | 0.86 | auto | 37% | 34% | 29% | tee stage: Black tee_centroid |  |
| 9 | 5 | 530 / 531 | 93 | 0.89 | auto | 52% | 28% | 20% | tee stage: Black tee_centroid |  |
| 10 | 4 | 396 / 390 | 194 | 0.76 | check the flags | 32% | 7% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 5 | 512 / 507 | 35 | 0.79 | check the flags | 38% | 19% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 426 / 427 | 292 | 0.85 | auto | 41% | 23% | 36% | tee stage: Black tee_centroid |  |
| 13 | 3 | 222 / 222 | 141 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 222 yds) |
| 14 | 5 | 570 / 570 | 251 | 0.85 | auto | 32% | 54% | 14% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 299 / 300 | 265 | 0.76 | check the flags | 16% | 34% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 244 / 238 | 3 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 244 yds) |
| 17 | 4 | 495 / 467 | 262 | 0.79 | check the flags | 54% | 32% | 14% | tee stage: Black lidar_pad_capped | tee: tee stage: Black lidar_pad_capped; Black tee on a lidar pad (no OSM box at 495 yds) |
| 18 | 4 | 370 / 370 | 250 | 0.69 | check the flags | 22% | 24% | 54% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 370 yds) |

## Stages

- **resolve**: ok: relation/1389558 Troon North Golf Club (Scottsdale, AZ)
- **osm**: ok: 2446 features
- **renumber**: ok: OSM hole refs -> card holes 3->12, 5->9, 7->5, 8->7, 9->15, 12->8, 15->3
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 133 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/troon_north/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/troon_north/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 32 polygons (outside 32); mode replace

## Warnings

- ignored 4 practice / driving-range tee box(es): OSM 1120331229, 1120331230, 1120331231, 1120331233
- ignored 28 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 731646897, 733110749, 733121972, 733123625, 733127369, 733131640, 733132163, 733132458
- OSM hole numbering differs from the card: OSM hole refs -> card holes 3->12, 5->9, 7->5, 8->7, 9->15, 12->8, 15->3 (CHECK)
- hole 15 Silver: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 15 Copper: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 15 Jade: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 3 Black: CHECK, walk-back ran onto a road (OSM 802802204) 58 yds behind the line start: capped there (139 yds short of the card)
- hole 3 Gold: CHECK, walk-back ran onto a road (OSM 802802204) 58 yds behind the line start: capped there (127 yds short of the card)
- hole 3 Silver: CHECK, tee was on a building (OSM 1204281411): moved 9 yds forward off it
- hole 3 Copper: CHECK, tee was on a building (OSM 1204281415): moved 9 yds forward off it
- hole 3 Jade: CHECK, tee was on a building (OSM 1204281414): moved 23 yds forward off it
- hole 17 Black: CHECK, tee was on a building (OSM 1214124310): moved 29 yds forward off it
- hole 3: measured 417 vs card 556 yds for Black (no OSM tee box at that yardage?)
- hole 17: measured 467 vs card 495 yds for Black (no OSM tee box at that yardage?)
