# Dub's Dread Golf Club (Kansas City, KS) - osm_back tees

Built 2026-10-30T00:14:57Z. OSM way/505160823. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 19 |
| greens_found | 18 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 15 |
| of_par4_5 | 15 |
| mean_landing_osm_share | 0.332 |
| mean_confidence | 0.64 |
| osm_score | 0.866 |

OSM features inside the course: buildings 3, golf=bunker 12, golf=fairway 20, golf=green 19, golf=hole 19, golf=path 13, golf=pin 18, golf=tee 67, golf=water_hazard 8, holes_with_par 19, trees_polygons 2, water_lines 9, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 513 / 513 | 247 | 0.64 | check the flags | 30% | 32% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 4 | 401 / 401 | 174 | 0.64 | check the flags | 50% | 4% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 434 / 434 | 174 | 0.61 | check the flags | 41% | 4% | 55% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 401 / 401 | 119 | 0.67 | check the flags | 61% | 2% | 37% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 4 | 352 / 352 | 354 | 0.60 | needs review | 23% | 21% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 4 | 488 / 488 | 109 | 0.61 | check the flags | 23% | 27% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 5 | 570 / 570 | 201 | 0.59 | needs review | 28% | 9% | 63% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 210 / 210 | 68 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 367 / 367 | 1 | 0.59 | needs review | 26% | 13% | 61% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 371 / 371 | 91 | 0.63 | check the flags | 27% | 33% | 40% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 232 / 232 | 99 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 4 | 555 / 555 | 259 | 0.59 | needs review | 35% | 2% | 62% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 4 | 407 / 407 | 113 | 0.65 | check the flags | 38% | 26% | 36% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 4 | 445 / 445 | 278 | 0.59 | needs review | 29% | 10% | 61% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 4 | 405 / 405 | 314 | 0.60 | check the flags | 34% | 8% | 57% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 3 | 206 / 206 | 242 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 5 | 561 / 561 | 37 | 0.59 | needs review | 27% | 13% | 60% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 433 / 433 | 15 | 0.61 | check the flags | 26% | 26% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/505160823 Dub's Dread Golf Club (Kansas City, KS)
- **osm**: ok: 277 features
- **routing**: ok: structure (mapped_nocard, structure on osm) placed 1/1 holes OSM has no way for (1 to check; segment no, lidar pads 159, perception scene no)
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/dubs_dread/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/dubs_dread/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- hole 4: placed by structure inference, golfer check (uncertain (25%): P(number) 44%, P(tee) 59%)
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
