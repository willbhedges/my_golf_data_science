# Tiffany Greens Golf Club (Kansas City, MO) - Gold tees

Built 2026-10-30T00:36:26Z. OSM relation/1424708. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 82 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.465 |
| mean_confidence | 0.838 |
| osm_score | 0.865 |

OSM features inside the course: buildings 68, built_up_landuse 1, golf=bunker 54, golf=cartpath 38, golf=fairway 29, golf=green 23, golf=hole 17, golf=path 1, golf=pin 18, golf=tee 82, golf=water_hazard 3, holes_with_par 17, trees_polygons 1, water_lines 13, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 510 / 514 | 30 | 0.75 | check the flags | 60% | 3% | 38% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 510 yds) |
| 2 | 4 | 385 / 388 | 76 | 0.81 | auto | 44% | 16% | 40% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 4 | 425 / 426 | 248 | 0.85 | auto | 45% | 19% | 36% | tee stage: Gold tee_centroid |  |
| 4 | 3 | 195 / 195 | 40 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 5 | 4 | 370 / 371 | 91 | 0.77 | check the flags | 38% | 8% | 54% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 3 | 234 / 234 | 23 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 4 | 410 / 409 | 97 | 0.81 | auto | 50% | 10% | 39% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 8 | 4 | 430 / 431 | 276 | 0.79 | check the flags | 48% | 1% | 51% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 5 | 575 / 576 | 299 | 0.84 | auto | 49% | 8% | 43% | tee stage: Gold tee_centroid |  |
| 10 | 3 | 188 / 188 | 187 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 11 | 5 | 530 / 531 | 252 | 0.81 | auto | 47% | 14% | 39% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 12 | 4 | 410 / 413 | 58 | 0.80 | check the flags | 38% | 20% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 4 | 400 / 399 | 184 | 0.83 | auto | 62% | 4% | 34% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 14 | 4 | 370 / 370 | 230 | 0.85 | auto | 50% | 14% | 36% | tee stage: Gold tee_centroid |  |
| 15 | 3 | 195 / 195 | 239 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 16 | 5 | 535 / 526 | 241 | 0.78 | check the flags | 40% | 8% | 52% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 4 | 395 / 395 | 172 | 0.81 | auto | 33% | 18% | 49% | tee stage: Gold tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 420 / 420 | 55 | 0.83 | auto | 47% | 6% | 47% | tee stage: Gold tee_centroid |  |

## Stages

- **resolve**: ok: relation/1424708 Tiffany Greens Golf Club (Kansas City, MO)
- **osm**: ok: 870 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 97 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/tiffany_greens/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/tiffany_greens/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 25 polygons (outside 25); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red
