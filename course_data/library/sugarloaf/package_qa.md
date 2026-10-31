# Sugarloaf Golf Club (Carrabassett Valley, ME) - Black tees

Built 2026-10-31T01:50:22Z. OSM relation/17549879. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 80 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.59 |
| mean_confidence | 0.898 |
| osm_score | 0.918 |

OSM features inside the course: buildings 89, golf=bunker 64, golf=cartpath 57, golf=clubhouse 1, golf=driving_range 1, golf=fairway 21, golf=green 22, golf=hole 18, golf=rough 2, golf=tee 80, golf=water_hazard 2, holes_with_handicap 18, holes_with_par 18, single_trees 6, trees_polygons 28, water_lines 30, water_polygons 9

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 421 / 421 | 31 | 0.88 | auto | 51% | 28% | 21% | tee stage: Black tee_centroid |  |
| 2 | 5 | 563 / 563 | 17 | 0.91 | auto | 58% | 30% | 12% | tee stage: Black tee_centroid |  |
| 3 | 3 | 217 / 217 | 112 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 4 | 5 | 530 / 530 | 144 | 0.85 | auto | 49% | 32% | 19% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 403 / 404 | 270 | 0.83 | auto | 46% | 24% | 29% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 402 / 402 | 147 | 0.88 | auto | 54% | 19% | 27% | tee stage: Black tee_centroid |  |
| 7 | 4 | 384 / 384 | 330 | 0.88 | auto | 43% | 35% | 22% | tee stage: Black tee_centroid |  |
| 8 | 3 | 187 / 187 | 303 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 4 | 417 / 416 | 270 | 0.86 | auto | 62% | 18% | 19% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 334 / 334 | 216 | 0.87 | auto | 46% | 27% | 27% | tee stage: Black tee_centroid |  |
| 11 | 3 | 216 / 216 | 27 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 12 | 5 | 542 / 542 | 31 | 0.94 | auto | 78% | 17% | 6% | tee stage: Black tee_centroid |  |
| 13 | 4 | 401 / 401 | 45 | 0.91 | auto | 67% | 19% | 14% | tee stage: Black tee_centroid |  |
| 14 | 4 | 401 / 397 | 67 | 0.85 | auto | 58% | 19% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 3 | 178 / 178 | 41 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 16 | 5 | 525 / 525 | 197 | 0.90 | auto | 82% | 10% | 8% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 382 / 382 | 237 | 0.86 | auto | 62% | 20% | 18% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 407 / 407 | 212 | 0.90 | auto | 68% | 11% | 21% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: relation/17549879 Sugarloaf Golf Club (Carrabassett Valley, ME)
- **osm**: ok: 606 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 111 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/sugarloaf/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/sugarloaf/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace
