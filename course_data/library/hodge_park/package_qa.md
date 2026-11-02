# Hodge Park Golf Course (Kansas City, MO) - osm_back tees

Built 2026-11-02T10:49:11Z. OSM way/195221873. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 16 |
| greens_found | 17 |
| tee_boxes | 35 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.363 |
| mean_confidence | 0.653 |
| osm_score | 0.834 |

OSM features inside the course: buildings 2, golf=bunker 3, golf=cartpath 20, golf=clubhouse 1, golf=fairway 22, golf=green 18, golf=hole 16, golf=tee 35, holes_with_par 16, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 811 / 811 | 49 | 0.77 | check the flags | 100% | 0% | 0% | tee stage: review | tee: tee stage: review |
| 2 | 4 | 364 / 364 | 277 | 0.57 | needs review | 18% | 15% | 67% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 115 / 115 | 270 | 0.55 | needs review | 20% | 0% | 80% | tee stage: review (inside OSM tee 279486929) | tee: tee stage: review (inside OSM tee 279486929); no fairway in the landing zone |
| 4 | 4 | 412 / 412 | 167 | 0.69 | check the flags | 67% | 5% | 28% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 332 / 332 | 360 | 0.58 | needs review | 30% | 3% | 67% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 3 | 141 / 141 | 128 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 435 / 435 | 347 | 0.66 | check the flags | 60% | 1% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 435 / 435 | 95 | 0.60 | check the flags | 37% | 4% | 59% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 276 / 276 | 13 | 0.62 | check the flags | 14% | 43% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 390 / 390 | 7 | 0.68 | check the flags | 44% | 34% | 22% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 215 / 215 | 109 | 0.43 | needs review | 0% | 0% | 100% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon) |
| 12 | 3 | 178 / 178 | 307 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 446 / 446 | 339 | 0.67 | check the flags | 30% | 46% | 24% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 158 / 158 | 336 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 350 / 350 | 147 | 0.64 | check the flags | 30% | 31% | 39% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 4 | 247 / 247 | 354 | 0.63 | check the flags | 46% | 5% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 4 | 272 / 272 | 313 | 0.60 | needs review | 38% | 2% | 60% | tee stage: review (inside OSM tee 279487481) | tee: tee stage: review (inside OSM tee 279487481) |
| 18 | 3 | 169 / 169 | 108 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/195221873 Hodge Park Golf Course (Kansas City, MO)
- **osm**: ok: 563 features
- **routing**: ok: pathroute_v2 (mapped_nocard) placed 16/16 holes OSM has no way for (3 to check; segment no, lidar pads 247, perception scene no)
- **scorecard**: missing
- **tee_overrides**: ok: osm_back 1 review, 3 review (inside OSM tee 279486929), 17 review (inside OSM tee 279487481);
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/hodge_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/hodge_park/imagery/dem.tif (17/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace

## Warnings

- hole 1: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.88: ask the golfer)
- hole 3: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.87: ask the golfer)
- hole 12: placed by pathroute_v2 inference, golfer check (pathroute_v2 pair confidence 0.35: ask the golfer)
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
