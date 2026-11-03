# The Plantation Course (Kapalua, HI) - Web tees

Built 2026-11-02T23:53:20Z. OSM relation/12152889. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Tour, Web, Championship, Combo_Championship/Regular, Regular, Combo_Regular/Resort, Resort, Combo_Resort/Forward, Forward)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Tour, Web, Championship, Combo_Championship/Regular, Regular, Combo_Regular/Resort, Resort, Combo_Resort/Forward, Forward**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 70 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 15 |
| of_par4_5 | 15 |
| mean_landing_osm_share | 0.689 |
| mean_confidence | 0.869 |
| osm_score | 0.924 |

OSM features inside the course: buildings 1, golf=bunker 94, golf=cartpath 10, golf=driving_range 1, golf=fairway 18, golf=green 20, golf=hole 17, golf=pin 18, golf=rough 2, golf=tee 70, holes_with_handicap 17, holes_with_par 17, single_trees 1, trees_polygons 47, water_lines 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 520 / 521 | 284 | 0.89 | auto | 75% | 0% | 25% | tee stage: Web tee_centroid |  |
| 2 | 3 | 219 / 219 | 217 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 3 | 4 | 424 / 425 | 92 | 0.81 | auto | 59% | 0% | 41% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 4 | 4 | 422 / 421 | 149 | 0.81 | auto | 58% | 0% | 42% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 5 | 5 | 526 / 524 | 161 | 0.89 | auto | 73% | 0% | 27% | tee stage: Web tee_centroid |  |
| 6 | 4 | 424 / 422 | 355 | 0.87 | auto | 66% | 0% | 34% | tee stage: Web tee_centroid |  |
| 7 | 4 | 522 / 523 | 294 | 0.85 | auto | 71% | 0% | 29% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 8 | 3 | 199 / 193 | 0 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 9 | 5 | 550 / 551 | 60 | 0.82 | auto | 61% | 0% | 39% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 10 | 4 | 384 / 385 | 104 | 0.86 | auto | 61% | 2% | 38% | tee stage: Web tee_centroid |  |
| 11 | 3 | 161 / 160 | 338 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 12 | 4 | 424 / 425 | 262 | 0.87 | auto | 67% | 0% | 33% | tee stage: Web tee_centroid |  |
| 13 | 4 | 383 / 384 | 92 | 0.84 | auto | 69% | 0% | 31% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 14 | 4 | 301 / 300 | 137 | 0.84 | auto | 69% | 0% | 31% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 15 | 5 | 541 / 534 | 154 | 0.88 | auto | 83% | 0% | 17% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 16 | 4 | 369 / 368 | 158 | 0.83 | auto | 65% | 0% | 35% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 4 | 550 / 549 | 331 | 0.88 | auto | 82% | 0% | 18% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 18 | 5 | 677 / 676 | 329 | 0.86 | auto | 74% | 0% | 26% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |

## Stages

- **resolve**: ok: relation/12152889 The Plantation Course (Maui County, HI)
- **osm**: ok: 412 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 9 sets; lidar pads: 70 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 9 tee set(s))
- **imagery**: ok: course_data/packages/kapalua_plantation/imagery (Sentinel-2 L2A via Planetary Computer, None)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP None
- **elevation**: ok: course_data/packages/kapalua_plantation/imagery/dem.tif (18/18 holes)
- **vision**: missing: no vision_any layers for 'kapalua_plantation' (FileNotFoundError: no NAIP for kapalua_plantation (course_data/vision_any/kapalua_plantation/raw/naip_*.tif or course_data/imagery/kapalua_); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them; CHECK: build it with course_data/vision_any/build_layers.py kapalua_plantation (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 17 polygons (outside 17); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Tour, Web, Championship, Combo_Championship/Regular, Regular, Combo_Regular/Resort, Resort, Combo_Resort/Forward, Forward
- scorecard (opengolfapi): Forward: holes sum to 5228 but the source says 5181 (+47): mixed card versions
- CHECK vision: missing: no vision_any layers for 'kapalua_plantation' (FileNotFoundError: no NAIP for kapalua_plantation (course_data/vision_any/kapalua_plantation/raw/naip_*.tif or course_data/imagery/kapalua_); ad; trees / water come from OSM (or the fallback) only
