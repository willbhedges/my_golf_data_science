# Forest Dunes Course (South Branch Township, MI) - Web tees

Built 2026-11-26T17:17:27Z. OSM way/1536953640. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: I, Web, Ii, Combo_Ii_&Amp;_Iii, Iii, Iv)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: I, Web, Ii, Combo_Ii_&Amp;_Iii, Iii, Iv**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 77 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.473 |
| mean_confidence | 0.87 |
| osm_score | 0.88 |

OSM features inside the course: buildings 2, golf=bunker 126, golf=cartpath 23, golf=fairway 20, golf=green 19, golf=hole 18, golf=lateral_water_hazard 2, golf=rough 37, golf=tee 77, golf=water_hazard 1, holes_with_handicap 1, holes_with_par 18, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 403 / 403 | 135 | 0.82 | auto | 44% | 23% | 33% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 2 | 4 | 451 / 451 | 204 | 0.87 | auto | 38% | 40% | 21% | tee stage: Web tee_centroid |  |
| 3 | 3 | 203 / 203 | 42 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 4 | 4 | 399 / 401 | 72 | 0.83 | auto | 36% | 38% | 26% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 5 | 5 | 605 / 606 | 124 | 0.85 | auto | 48% | 16% | 35% | tee stage: Web tee_centroid |  |
| 6 | 4 | 378 / 375 | 306 | 0.85 | auto | 50% | 28% | 22% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 7 | 5 | 537 / 537 | 335 | 0.90 | auto | 39% | 54% | 6% | tee stage: Web tee_centroid |  |
| 8 | 4 | 443 / 443 | 279 | 0.85 | auto | 44% | 41% | 15% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 9 | 3 | 203 / 203 | 310 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 10 | 4 | 439 / 440 | 92 | 0.83 | auto | 63% | 5% | 33% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 11 | 3 | 193 / 193 | 159 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 12 | 4 | 397 / 398 | 127 | 0.90 | auto | 46% | 44% | 10% | tee stage: Web tee_centroid |  |
| 13 | 4 | 373 / 373 | 29 | 0.90 | auto | 54% | 32% | 14% | tee stage: Web tee_centroid |  |
| 14 | 4 | 464 / 464 | 2 | 0.85 | auto | 54% | 5% | 40% | tee stage: Web tee_centroid |  |
| 15 | 5 | 563 / 563 | 210 | 0.83 | auto | 47% | 24% | 29% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 16 | 3 | 233 / 233 | 234 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 4 | 302 / 303 | 303 | 0.77 | check the flags | 43% | 0% | 57% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 530 / 532 | 269 | 0.85 | auto | 56% | 3% | 42% | tee stage: Web tee_centroid |  |

## Stages

- **resolve**: ok: way/1536953640 Forest Dunes Course (South Branch Township, MI)
- **osm**: ok: 449 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 53 candidate pads near hole starts (6 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/forest_dunes/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/forest_dunes/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 3 polygons (outside 3); mode replace
- **native_auto**: none: course gate shut: 4% of sides >= 0.675 (< 25%)

## Warnings

- ignored 10 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 1528336302, 1528336303, 1528336304, 1528336305, 1528336306, 1528336307, 1528336308, 1528336309
- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: I, Web, Ii, Combo_Ii_&Amp;_Iii, Iii, Iv
- hole 11 Iv: CHECK, tee was put 62 yds from this hole's start, at hole 18's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
