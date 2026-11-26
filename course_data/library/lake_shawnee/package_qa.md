# Lake Shawnee Golf Course (Topeka, KS) - Blue tees

Built 2026-11-26T16:00:51Z. OSM relation/2053245. Scorecard: file (course_data/library/lake_shawnee/routed_card.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red, Gold)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red, Gold**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 82 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.115 |
| mean_confidence | 0.822 |
| osm_score | 0.761 |

OSM features inside the course: buildings 4, golf=bunker 4, golf=cartpath 14, golf=clubhouse 1, golf=fairway 5, golf=green 18, golf=hole 18, golf=tee 82, golf=water_hazard 2, holes_with_par 18, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 348 / 349 | 259 | 0.78 | check the flags | 2% | 60% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 369 / 369 | 6 | 0.80 | auto | 18% | 50% | 31% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 353 / 353 | 124 | 0.82 | auto | 1% | 67% | 33% | tee stage: Blue tee_centroid |  |
| 4 | 3 | 148 / 148 | 42 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 5 | 5 | 474 / 474 | 330 | 0.77 | check the flags | 0% | 62% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 3 | 179 / 179 | 8 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 419 / 415 | 108 | 0.75 | check the flags | 0% | 52% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 391 / 390 | 312 | 0.78 | check the flags | 0% | 62% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 625 / 620 | 137 | 0.79 | check the flags | 0% | 71% | 29% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 4 | 364 / 364 | 206 | 0.79 | check the flags | 25% | 17% | 58% | tee stage: Blue tee_centroid |  |
| 11 | 4 | 412 / 407 | 225 | 0.78 | check the flags | 35% | 17% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 429 / 429 | 207 | 0.71 | check the flags | 41% | 25% | 34% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 429 yds) |
| 13 | 3 | 156 / 156 | 250 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 14 | 4 | 338 / 338 | 40 | 0.75 | check the flags | 0% | 50% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 3 | 199 / 200 | 79 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 515 / 509 | 359 | 0.78 | check the flags | 0% | 62% | 38% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 3 | 183 / 183 | 173 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 455 / 450 | 39 | 0.78 | check the flags | 28% | 28% | 45% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: relation/2053245 Lake Shawnee Golf Course (Shawnee County, KS)
- **osm**: ok: 559 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/lake_shawnee/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 53 candidate pads near hole starts (5 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/lake_shawnee/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/lake_shawnee/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: ok: 9/9 hole(s) without a mapped fairway filled from NAIP (d' 1.69; gated: none)
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red, Gold
- hole 11 Gold: CHECK, tee was put 155 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
