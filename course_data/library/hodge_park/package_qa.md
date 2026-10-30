# Hodge Park Golf Course (Kansas City, MO) - Blue tees

Built 2026-10-30T00:17:12Z. OSM way/195221873. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 56 |
| tees_with_colour | 54 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.392 |
| mean_confidence | 0.887 |
| osm_score | 0.864 |

OSM features inside the course: buildings 2, golf=bunker 3, golf=cartpath 20, golf=clubhouse 1, golf=fairway 22, golf=green 18, golf=hole 18, golf=tee 56, holes_with_par 18, tees_with_colour 54, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 425 / 414 | 165 | 0.89 | auto | 56% | 5% | 40% | tee stage: Blue tagged |  |
| 2 | 4 | 347 / 332 | 355 | 0.82 | auto | 33% | 4% | 63% | tee stage: Blue tagged |  |
| 3 | 3 | 168 / 156 | 129 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 4 | 5 | 452 / 438 | 353 | 0.85 | auto | 45% | 0% | 55% | tee stage: Blue tagged | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 446 / 436 | 98 | 0.85 | auto | 36% | 16% | 48% | tee stage: Blue tagged |  |
| 6 | 4 | 304 / 278 | 10 | 0.84 | auto | 22% | 30% | 49% | tee stage: Blue tagged |  |
| 7 | 3 | 174 / 163 | 190 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 8 | 4 | 409 / 393 | 290 | 0.85 | auto | 36% | 16% | 48% | tee stage: Blue tagged |  |
| 9 | 4 | 401 / 394 | 191 | 0.85 | auto | 34% | 16% | 49% | tee stage: Blue tagged |  |
| 10 | 4 | 405 / 375 | 36 | 0.83 | auto | 11% | 40% | 48% | tee stage: Blue tagged |  |
| 11 | 5 | 459 / 455 | 330 | 0.89 | auto | 56% | 6% | 37% | tee stage: Blue tagged |  |
| 12 | 3 | 193 / 164 | 337 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 13 | 4 | 388 / 369 | 138 | 0.83 | auto | 36% | 5% | 59% | tee stage: Blue tagged |  |
| 14 | 4 | 260 / 255 | 354 | 0.85 | auto | 41% | 8% | 51% | tee stage: Blue tagged |  |
| 15 | 4 | 338 / 325 | 136 | 0.94 | auto | 73% | 10% | 18% | tee stage: Blue tagged |  |
| 16 | 3 | 192 / 177 | 108 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 17 | 5 | 518 / 516 | 256 | 0.88 | auto | 42% | 22% | 36% | tee stage: Blue tagged |  |
| 18 | 4 | 302 / 311 | 188 | 0.80 | check the flags | 27% | 2% | 71% | tee stage: Blue tagged |  |

## Stages

- **resolve**: ok: way/195221873 Hodge Park Golf Course (Kansas City, MO)
- **osm**: ok: 602 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 34 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/hodge_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/hodge_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
- hole 6: measured 278 vs card 304 yds for Blue (no OSM tee box at that yardage?)
- hole 8: measured 393 vs card 409 yds for Blue (no OSM tee box at that yardage?)
- hole 10: measured 375 vs card 405 yds for Blue (no OSM tee box at that yardage?)
- hole 12: measured 164 vs card 193 yds for Blue (no OSM tee box at that yardage?)
- hole 13: measured 369 vs card 388 yds for Blue (no OSM tee box at that yardage?)
