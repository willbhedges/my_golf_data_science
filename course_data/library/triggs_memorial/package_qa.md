# Triggs Memorial Golf Course (Providence, RI) - Blue tees

Built 2026-10-31T03:54:48Z. OSM way/43150786. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Gold, Red, White (L), Gold (L), Red (L))).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red, White (L), Gold (L), Red (L)**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 43 |
| tees_with_colour | 43 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.361 |
| mean_confidence | 0.857 |
| osm_score | 0.872 |

OSM features inside the course: buildings 4, golf=bunker 70, golf=cartpath 20, golf=driving_range 1, golf=fairway 20, golf=green 19, golf=hole 18, golf=lateral_water_hazard 4, golf=rough 1, golf=tee 43, golf=water_hazard 5, holes_with_handicap 18, holes_with_par 18, single_trees 287, tees_with_colour 43, trees_polygons 11, water_polygons 9

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 402 / 403 | 347 | 0.89 | auto | 41% | 25% | 34% | tee stage: Blue tagged |  |
| 2 | 4 | 425 / 420 | 334 | 0.77 | check the flags | 35% | 10% | 56% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 457 / 456 | 87 | 0.84 | auto | 30% | 18% | 52% | tee stage: Blue tagged |  |
| 4 | 3 | 200 / 198 | 242 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 5 | 4 | 327 / 327 | 145 | 0.76 | check the flags | 24% | 2% | 74% | tee stage: Blue tee_centroid |  |
| 6 | 5 | 511 / 509 | 6 | 0.79 | check the flags | 25% | 2% | 74% | tee stage: Blue tagged |  |
| 7 | 3 | 191 / 182 | 221 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 8 | 4 | 341 / 341 | 197 | 0.74 | check the flags | 27% | 7% | 65% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 402 / 402 | 176 | 0.79 | check the flags | 37% | 19% | 44% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 5 | 513 / 513 | 8 | 0.80 | check the flags | 37% | 22% | 41% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 4 | 350 / 344 | 17 | 0.84 | auto | 30% | 15% | 54% | tee stage: Blue tagged |  |
| 12 | 3 | 200 / 200 | 182 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 5 | 462 / 461 | 212 | 0.86 | auto | 31% | 26% | 43% | tee stage: Blue tagged |  |
| 14 | 3 | 158 / 155 | 123 | 1.00 | auto | 100% | 0% | 0% | tee stage: Blue tagged |  |
| 15 | 5 | 508 / 506 | 355 | 0.88 | auto | 44% | 17% | 39% | tee stage: Blue tagged |  |
| 16 | 4 | 319 / 328 | 352 | 0.94 | auto | 70% | 10% | 20% | tee stage: Blue tagged |  |
| 17 | 4 | 412 / 412 | 208 | 0.77 | check the flags | 38% | 7% | 55% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 410 / 405 | 197 | 0.85 | auto | 38% | 12% | 50% | tee stage: Blue tagged |  |

## Stages

- **resolve**: ok: way/43150786 Triggs Memorial Golf Course (Providence, RI)
- **osm**: ok: 1702 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 44 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/triggs_memorial/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/triggs_memorial/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 11 polygons (outside 11); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red, White (L), Gold (L), Red (L)
- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 5 White (L) 316 < Gold 322
