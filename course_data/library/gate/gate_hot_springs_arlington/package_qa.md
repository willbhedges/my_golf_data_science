# Hot Springs Country Club (Hot Springs, AR) - osm_back tees

Built 2026-10-29T20:32:23Z. OSM way/250816543. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 12 |
| tee_boxes | 35 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.005 |
| mean_confidence | 0.531 |
| osm_score | 0.634 |

OSM features inside the course: golf=bunker 53, golf=cartpath 10, golf=green 21, golf=hole 17, golf=tee 35, golf=water_hazard 1, holes_with_par 17, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 425 / 425 | 317 | 0.54 | needs review | 0% | 40% | 60% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); no fairway in the landing zone |
| 2 | 3 | 150 / 150 | 258 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 4 | 400 / 400 | 52 | 0.53 | needs review | 0% | 52% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon); no fairway in the landing zone |
| 4 | 4 | 341 / 341 | 222 | 0.54 | needs review | 2% | 40% | 57% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| 5 | 4 | 354 / 354 | 36 | 0.47 | needs review | 0% | 37% | 63% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); green from the hole-line end (no golf=green polygon); no fairway in the landing zone |
| 6 | 5 | 499 / 499 | 237 | 0.50 | needs review | 0% | 22% | 78% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); no fairway in the landing zone |
| 7 | 4 | 372 / 372 | 236 | 0.54 | needs review | 0% | 24% | 76% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no fairway in the landing zone |
| 8 | 3 | 171 / 171 | 26 | 0.43 | needs review | 0% | 0% | 100% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon) |
| 9 | 5 | 562 / 562 | 85 | 0.45 | needs review | 0% | 28% | 72% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); green from the hole-line end (no golf=green polygon); no fairway in the landing zone |
| 10 | 5 | 555 / 555 | 274 | 0.52 | needs review | 0% | 34% | 66% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); no fairway in the landing zone |
| 11 | 3 | 176 / 176 | 349 | 0.43 | needs review | 0% | 0% | 100% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon) |
| 12 | 4 | 403 / 403 | 332 | 0.54 | needs review | 0% | 24% | 76% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no fairway in the landing zone |
| 13 | 4 | 445 / 445 | 144 | 0.51 | needs review | 2% | 8% | 90% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no fairway in the landing zone |
| 14 | 4 | 401 / 401 | 335 | 0.52 | needs review | 0% | 13% | 87% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no fairway in the landing zone |
| 15 | 4 | 330 / 330 | 106 | 0.50 | needs review | 0% | 22% | 78% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); no fairway in the landing zone |
| 16 | 4 | 400 / 400 | 228 | 0.53 | needs review | 1% | 18% | 81% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no fairway in the landing zone |
| 17 | 3 | 143 / 143 | 78 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 5 | 507 / 507 | 99 | 0.47 | needs review | 1% | 17% | 82% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon); no fairway in the landing zone |

## Stages

- **resolve**: ok: way/250816543 Hot Springs Country Club (Hot Springs, AR)
- **osm**: ok: 331 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/gate_hot_springs_arlington/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 12/12 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gate_hot_springs_arlington/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 18 polygons (outside 18); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
