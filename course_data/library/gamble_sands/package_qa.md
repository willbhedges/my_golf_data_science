# Quicksands at Gamble Sands (Brewster, WA) - osm_back tees

Built 2026-11-01T21:04:52Z. OSM way/1551387386. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 14 |
| holes_mapped | 14 |
| greens_found | 14 |
| tee_boxes | 15 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 0 |
| of_par4_5 | 0 |
| mean_landing_osm_share | 0.0 |
| mean_confidence | 0.77 |
| osm_score | 0.498 |

OSM features inside the course: buildings 1, golf=bunker 1, golf=fairway 1, golf=green 13, golf=hole 14, golf=rough 1, golf=tee 15, holes_with_handicap 14, holes_with_par 14, single_trees 36, trees_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 146 / 146 | 120 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 3 | 114 / 114 | 340 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 110 / 110 | 154 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 3 | 116 / 116 | 73 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 5 | 3 | 98 / 98 | 19 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 3 | 115 / 115 | 258 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 3 | 111 / 111 | 97 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 3 | 175 / 175 | 2 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 3 | 114 / 114 | 213 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 3 | 112 / 112 | 255 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 113 / 113 | 154 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 3 | 95 / 95 | 327 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 13 | 3 | 232 / 232 | 243 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 108 / 108 | 243 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/1551387386 Quicksands at Gamble Sands (Brewster, WA)
- **osm**: ok: 132 features
- **routing**: ok: structure (unmapped_nocard, structure on osm) placed 0/4 holes OSM has no way for (0 to check; segment no, lidar pads 1, perception scene no)
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (14 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/gamble_sands/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 14/14 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gamble_sands/imagery/dem.tif (14/14 holes)
- **vision**: missing: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer) ran but added no zones
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- ignored 2 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 947409626, 947440597
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
- vision: missing: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer) ran but added no zones; trees / long grass come from OSM only
