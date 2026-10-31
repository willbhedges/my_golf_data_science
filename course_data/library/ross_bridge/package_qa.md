# RTJ Ross Bridge Golf (Hoover, AL) - Web tees

Built 2026-10-30T21:31:11Z. OSM way/55545496. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Web)).

**WARNING: requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Web**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 91 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.58 |
| mean_confidence | 0.846 |
| osm_score | 0.873 |

OSM features inside the course: buildings 2, golf=bunker 66, golf=cartpath 30, golf=fairway 20, golf=green 27, golf=hole 18, golf=lateral_water_hazard 2, golf=rough 14, golf=tee 91, golf=water_hazard 1, holes_with_par 18, single_trees 101, tees_with_ref 83, tree_rows 1, trees_polygons 24, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 620 / 609 | 274 | 0.83 | auto | 60% | 4% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 2 | 4 | 467 / 466 | 171 | 0.82 | auto | 60% | 2% | 38% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 3 | 4 | 470 / 471 | 103 | 0.81 | auto | 55% | 0% | 45% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 226 / 225 | 356 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 5 | 4 | 469 / 467 | 340 | 0.80 | auto | 54% | 2% | 44% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 6 | 3 | 207 / 207 | 110 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 7 | 5 | 619 / 618 | 120 | 0.78 | check the flags | 46% | 0% | 54% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 8 | 4 | 502 / 501 | 148 | 0.73 | check the flags | 25% | 3% | 72% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 9 | 4 | 518 / 518 | 311 | 0.81 | auto | 59% | 0% | 41% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 477 / 474 | 168 | 0.85 | auto | 72% | 0% | 28% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 11 | 3 | 208 / 207 | 11 | 0.96 | auto | 100% | 0% | 0% | tee stage: Web tee_centroid |  |
| 12 | 4 | 454 / 454 | 220 | 0.82 | auto | 58% | 6% | 36% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 13 | 5 | 698 / 698 | 80 | 0.78 | check the flags | 40% | 9% | 51% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 14 | 3 | 239 / 239 | 219 | 0.93 | auto | 100% | 0% | 0% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 15 | 4 | 458 / 457 | 78 | 0.85 | auto | 70% | 0% | 30% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 16 | 5 | 571 / 569 | 129 | 0.81 | auto | 55% | 4% | 41% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 17 | 4 | 501 / 501 | 308 | 0.84 | auto | 66% | 0% | 34% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis |
| 18 | 4 | 487 / 486 | 313 | 0.90 | auto | 90% | 0% | 10% | tee stage: Web tee_axis | tee: tee stage: Web tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/55545496 RTJ Ross Bridge Golf (Hoover, AL)
- **osm**: ok: 1423 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 1 sets; lidar pads: 108 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/ross_bridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/ross_bridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 17 polygons (outside 17); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Web' instead (allow_substitute). Sets on the card: Web
