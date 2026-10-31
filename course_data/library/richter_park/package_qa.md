# Richter Park Golf Course (Danbury, CT) - Blue tees

Built 2026-10-30T22:04:59Z. OSM way/43434973. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Gold, Red (L), White (L), Gold (L))).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red (L), White (L), Gold (L)**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 16 |
| greens_found | 18 |
| tee_boxes | 43 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.39 |
| mean_confidence | 0.827 |
| osm_score | 0.85 |

OSM features inside the course: buildings 16, golf=bunker 37, golf=cartpath 28, golf=clubhouse 1, golf=driving_range 1, golf=fairway 20, golf=green 20, golf=hole 16, golf=tee 43, golf=water_hazard 2, holes_with_par 16, water_lines 23, water_polygons 12

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 398 / 398 | 357 | 0.79 | check the flags | 33% | 24% | 43% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 5 | 518 / 516 | 148 | 0.79 | check the flags | 39% | 14% | 47% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 3 | 183 / 183 | 48 | 0.86 | auto | 100% | 0% | 0% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 183 yds) |
| 4 | 4 | 430 / 431 | 280 | 0.74 | check the flags | 45% | 17% | 38% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 430 yds) |
| 5 | 3 | 174 / 174 | 223 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 413 / 413 | 162 | 0.79 | check the flags | 30% | 28% | 42% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 5 | 526 / 526 | 123 | 0.82 | auto | 37% | 35% | 28% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 359 / 359 | 322 | 0.81 | auto | 40% | 26% | 34% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 344 / 344 | 323 | 0.71 | check the flags | 39% | 9% | 52% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 344 yds) |
| 10 | 4 | 382 / 347 | 290 | 0.70 | check the flags | 32% | 31% | 37% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 382 yds) |
| 11 | 4 | 387 / 386 | 56 | 0.86 | auto | 45% | 43% | 12% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 527 / 524 | 259 | 0.82 | auto | 27% | 47% | 26% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 3 | 161 / 155 | 146 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 417 / 416 | 115 | 0.84 | auto | 39% | 42% | 19% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 342 / 342 | 207 | 0.89 | auto | 42% | 42% | 16% | tee stage: Blue tee_centroid |  |
| 16 | 5 | 580 / 579 | 84 | 0.88 | auto | 65% | 25% | 10% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 3 | 165 / 165 | 258 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 438 / 434 | 38 | 0.79 | check the flags | 34% | 24% | 42% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/43434973 Richter Park Golf Course (Danbury, CT)
- **osm**: ok: 627 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 61 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/richter_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/richter_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 15 polygons (outside 15); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red (L), White (L), Gold (L)
- hole 10 Blue: CHECK, walk-back ran onto a building (OSM 791254440) 180 yds behind the line start: capped there (36 yds short of the card)
- hole 10: measured 347 vs card 382 yds for Blue (no OSM tee box at that yardage?)
- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 10 White (L) 160 < Gold 338
