# Leatherstocking Golf Course (Cooperstown, NY) - Blue tees

Built 2026-10-31T03:36:25Z. OSM relation/19437352. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red, White (L), Red (L))).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red, White (L), Red (L)**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 46 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.371 |
| mean_confidence | 0.805 |
| osm_score | 0.846 |

OSM features inside the course: buildings 3, golf=bunker 102, golf=clubhouse 2, golf=fairway 21, golf=green 18, golf=hole 17, golf=lateral_water_hazard 1, golf=path 29, golf=pin 18, golf=rough 2, golf=tee 46, golf=water_hazard 1, holes_with_par 17, single_trees 76, trees_polygons 1, water_lines 4, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 340 / 340 | 352 | 0.72 | check the flags | 25% | 1% | 74% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 392 / 392 | 12 | 0.76 | check the flags | 34% | 8% | 58% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 3 | 210 / 209 | 316 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 210 yds) |
| 4 | 5 | 513 / 512 | 187 | 0.86 | auto | 49% | 20% | 30% | tee stage: Blue tee_centroid |  |
| 5 | 4 | 396 / 396 | 189 | 0.77 | check the flags | 36% | 10% | 54% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 362 / 361 | 356 | 0.77 | check the flags | 37% | 8% | 55% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 404 / 403 | 0 | 0.77 | check the flags | 38% | 6% | 56% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 375 / 375 | 331 | 0.83 | auto | 35% | 23% | 42% | tee stage: Blue tee_centroid |  |
| 9 | 3 | 186 / 186 | 344 | 0.82 | auto | 100% | 0% | 0% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 186 yds) |
| 10 | 4 | 384 / 380 | 355 | 0.72 | check the flags | 22% | 5% | 72% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 5 | 560 / 559 | 171 | 0.84 | auto | 46% | 15% | 39% | tee stage: Blue tee_centroid |  |
| 12 | 3 | 137 / 137 | 160 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 13 | 4 | 342 / 342 | 168 | 0.80 | check the flags | 34% | 9% | 57% | tee stage: Blue tee_centroid |  |
| 14 | 4 | 285 / 285 | 351 | 0.75 | check the flags | 14% | 14% | 73% | tee stage: Blue tee_centroid |  |
| 15 | 5 | 467 / 459 | 177 | 0.79 | check the flags | 45% | 6% | 49% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 366 / 366 | 183 | 0.82 | auto | 48% | 0% | 52% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 182 / 182 | 51 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 5 | 515 / 515 | 226 | 0.71 | check the flags | 56% | 2% | 42% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 515 yds) |

## Stages

- **resolve**: ok: relation/19437352 Leatherstocking Golf Course (Cooperstown, NY)
- **osm**: ok: 482 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 42 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/leatherstocking/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/leatherstocking/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 16 polygons (outside 16); mode replace

## Warnings

- ignored 1 practice / driving-range tee box(es): OSM 1421068530
- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red, White (L), Red (L)
