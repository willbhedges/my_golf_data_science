# Theodore Wirth Golf Course (Minneapolis, MN) - Blue tees

Built 2026-11-26T08:46:56Z. OSM relation/20146766. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 66 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.361 |
| mean_confidence | 0.844 |
| osm_score | 0.872 |

OSM features inside the course: buildings 12, golf=bunker 19, golf=cartpath 58, golf=clubhouse 1, golf=fairway 28, golf=green 28, golf=hole 18, golf=lateral_water_hazard 1, golf=pin 27, golf=rough 6, golf=tee 66, golf=water_hazard 2, holes_with_handicap 18, holes_with_par 18, long_grass_polygons 2, trees_polygons 27, water_lines 17, water_polygons 22

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 368 / 368 | 150 | 0.83 | auto | 48% | 23% | 29% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 5 | 471 / 472 | 287 | 0.83 | auto | 40% | 32% | 28% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 311 / 312 | 106 | 0.80 | auto | 27% | 22% | 51% | tee stage: Blue tee_centroid |  |
| 4 | 3 | 195 / 195 | 167 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 5 | 4 | 410 / 411 | 254 | 0.86 | auto | 44% | 24% | 32% | tee stage: Blue tee_centroid |  |
| 6 | 5 | 471 / 472 | 59 | 0.77 | check the flags | 28% | 20% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 363 / 364 | 268 | 0.79 | check the flags | 20% | 22% | 57% | tee stage: Blue tee_centroid |  |
| 8 | 3 | 140 / 140 | 51 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 374 / 374 | 61 | 0.82 | auto | 46% | 5% | 49% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 370 / 370 | 350 | 0.85 | auto | 66% | 9% | 25% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 4 | 332 / 332 | 358 | 0.80 | check the flags | 34% | 8% | 57% | tee stage: Blue tee_centroid |  |
| 12 | 3 | 98 / 98 | 231 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 5 | 503 / 507 | 305 | 0.79 | check the flags | 20% | 41% | 39% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 410 / 410 | 173 | 0.79 | check the flags | 23% | 20% | 57% | tee stage: Blue tee_centroid |  |
| 15 | 4 | 358 / 358 | 352 | 0.81 | auto | 26% | 26% | 48% | tee stage: Blue tee_centroid |  |
| 16 | 5 | 485 / 485 | 154 | 0.84 | auto | 47% | 10% | 43% | tee stage: Blue tee_centroid |  |
| 17 | 3 | 175 / 175 | 311 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 18 | 4 | 330 / 331 | 103 | 0.82 | auto | 35% | 21% | 44% | tee stage: Blue tee_centroid |  |

## Stages

- **resolve**: ok: relation/20146766 Theodore Wirth Golf Course (Minneapolis, MN)
- **osm**: ok: 1678 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 2 sets; lidar pads: 53 candidate pads near hole starts (13 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 2 tee set(s))
- **imagery**: ok: course_data/packages/theodore_wirth/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/theodore_wirth/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -512 m2 {'road': 512}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 15 polygons (outside 15); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): #1 18, #2 9); kept the largest group (no name or near point decides: CHECK the course), 18 ways; ignored 9
- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White
- hole 4 White: CHECK, tee was put 71 yds from this hole's start, at hole 7's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 White: CHECK, tee was put 80 yds from this hole's start, at hole 15's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- scorecard (opengolfapi): Blue: holes sum to 6164 but the source says 6475 (-311): mixed card versions
- scorecard (opengolfapi): White: holes sum to 5053 but the source says 6179 (-1126): mixed card versions
