# Hodge Park Golf Course (Kansas City, MO) - Blue tees

Built 2026-11-02T22:45:01Z. OSM way/195221873. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 56 |
| tees_with_colour | 54 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.386 |
| mean_confidence | 0.864 |
| osm_score | 0.877 |

OSM features inside the course: buildings 2, golf=bunker 3, golf=cartpath 20, golf=clubhouse 1, golf=fairway 22, golf=green 18, golf=hole 18, golf=tee 56, holes_with_par 18, tees_with_colour 54, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 425 / 424 | 165 | 0.90 | auto | 58% | 7% | 35% | tee stage: Blue tagged |  |
| 2 | 4 | 347 / 341 | 355 | 0.83 | auto | 34% | 6% | 60% | tee stage: Blue tagged |  |
| 3 | 3 | 168 / 167 | 129 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Blue review (inside OSM tee 279486929) | tee: tee stage: Blue review (inside OSM tee 279486929) |
| 4 | 5 | 452 / 451 | 353 | 0.85 | auto | 44% | 5% | 51% | tee stage: Blue tagged |  |
| 5 | 4 | 446 / 447 | 98 | 0.86 | auto | 37% | 18% | 45% | tee stage: Blue tagged |  |
| 6 | 4 | 304 / 304 | 8 | 0.83 | auto | 25% | 22% | 54% | tee stage: Blue tagged |  |
| 7 | 3 | 174 / 174 | 190 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 8 | 4 | 409 / 407 | 292 | 0.87 | auto | 38% | 20% | 42% | tee stage: Blue tagged |  |
| 9 | 4 | 401 / 401 | 190 | 0.86 | auto | 34% | 21% | 45% | tee stage: Blue tagged |  |
| 10 | 4 | 405 / 400 | 42 | 0.60 | check the flags | 19% | 20% | 61% | tee stage: Blue review | tee: tee stage: Blue review |
| 11 | 5 | 459 / 458 | 330 | 0.89 | auto | 57% | 6% | 37% | tee stage: Blue tagged |  |
| 12 | 3 | 193 / 188 | 337 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 13 | 4 | 388 / 383 | 136 | 0.85 | auto | 36% | 12% | 51% | tee stage: Blue tagged |  |
| 14 | 4 | 260 / 260 | 354 | 0.84 | auto | 39% | 8% | 53% | tee stage: Blue tagged |  |
| 15 | 4 | 338 / 338 | 134 | 0.90 | auto | 54% | 13% | 33% | tee stage: Blue tagged |  |
| 16 | 3 | 192 / 188 | 108 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 17 | 5 | 518 / 519 | 256 | 0.88 | auto | 42% | 24% | 35% | tee stage: Blue tagged |  |
| 18 | 4 | 302 / 304 | 190 | 0.80 | check the flags | 23% | 6% | 71% | tee stage: Blue tagged |  |

## Stages

- **resolve**: ok: way/195221873 Hodge Park Golf Course (Kansas City, MO)
- **osm**: ok: 601 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Blue 3 review (inside OSM tee 279486929), 10 review; White 1 review (inside OSM tee 279486921), 3 review (inside OSM tee 279486929), 10 review (inside OSM tee 279487450), 17 review (inside OSM tee 279487481); Red 1 review (inside OSM tee 279486921), 3 review (inside OSM tee 1566347479), 10 review (inside OSM tee 279487451), 11 review (inside OSM tee 279487456), 12 review (inside OSM tee 1566349137), 16 review (inside OSM tee 1566350080);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 34 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/hodge_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/hodge_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -249 m2 {'cells': 210}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace
- **agent_layers**: ok: course_data/mapper/hodge_park (62 zone edits on 13 holes, 1 tee(s) moved, 51 checked)

## Warnings

- ignored 1 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 898587302
- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
