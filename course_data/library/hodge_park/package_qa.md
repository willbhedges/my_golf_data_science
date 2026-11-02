# Hodge Park Golf Course (Kansas City, MO) - osm_back tees

Built 2026-11-01T21:02:03Z. OSM way/195221873. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 16 |
| greens_found | 17 |
| tee_boxes | 35 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.317 |
| mean_confidence | 0.627 |
| osm_score | 0.824 |

OSM features inside the course: buildings 2, golf=bunker 3, golf=cartpath 20, golf=clubhouse 1, golf=fairway 22, golf=green 18, golf=hole 16, golf=tee 35, holes_with_par 16, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 516 / 516 | 13 | 0.61 | check the flags | 33% | 12% | 55% | tee stage: review | tee: tee stage: review |
| 2 | 4 | 446 / 446 | 339 | 0.67 | check the flags | 30% | 46% | 24% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 1189 / 1189 | 338 | 0.77 | check the flags | 100% | 0% | 0% | tee stage: review (snapped 2 yds to OSM tee 279486929) | tee: tee stage: review (snapped 2 yds to OSM tee 279486929) |
| 4 | 4 | 350 / 350 | 147 | 0.64 | check the flags | 30% | 31% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 247 / 247 | 354 | 0.63 | check the flags | 46% | 5% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 295 / 295 | 145 | 0.62 | check the flags | 42% | 6% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 3 | 169 / 169 | 108 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 401 / 401 | 146 | 0.49 | needs review | 0% | 1% | 99% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no fairway in the landing zone |
| 9 | 4 | 276 / 276 | 13 | 0.62 | check the flags | 14% | 43% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 390 / 390 | 7 | 0.68 | check the flags | 44% | 34% | 22% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 215 / 215 | 109 | 0.43 | needs review | 0% | 0% | 100% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon) |
| 12 | 4 | 364 / 364 | 277 | 0.57 | needs review | 18% | 15% | 67% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 294 / 294 | 203 | 0.63 | check the flags | 47% | 3% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 412 / 412 | 167 | 0.69 | check the flags | 67% | 5% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 332 / 332 | 360 | 0.58 | needs review | 30% | 3% | 67% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 141 / 141 | 128 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 448 / 448 | 222 | 0.53 | needs review | 3% | 13% | 84% | tee stage: review (snapped 4 yds to OSM tee 279487481) | tee: tee stage: review (snapped 4 yds to OSM tee 279487481) |
| 18 | 4 | 385 / 385 | 201 | 0.60 | check the flags | 36% | 5% | 59% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/195221873 Hodge Park Golf Course (Kansas City, MO)
- **osm**: ok: 560 features
- **routing**: ok: pathroute_v2 (mapped_nocard) placed 16/16 holes OSM has no way for (4 to check; segment no, lidar pads 247, perception scene no)
- **scorecard**: missing
- **tee_overrides**: ok: osm_back 1 review, 3 review (snapped 2 yds to OSM tee 279486929), 17 review (snapped 4 yds to OSM tee 279487481);
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/hodge_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/hodge_park/imagery/dem.tif (17/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- hole 1: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.85: ask the golfer)
- hole 8: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.25: ask the golfer)
- hole 13: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.93: ask the golfer)
- hole 18: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.84: ask the golfer)
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
