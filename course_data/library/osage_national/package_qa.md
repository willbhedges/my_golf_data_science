# Osage National Golf Club (Osage Beach, MO) - Palmer tees

Built 2026-10-30T04:37:48Z. OSM relation/5897058. Scorecard: opengolfapi (opengolfapi). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Palmer, Tournament, Middle, Members, Forward, Green)).

**WARNING: requested tee set 'Black' is not on the card; using 'Palmer' instead (allow_substitute). Sets on the card: Palmer, Tournament, Middle, Members, Forward, Green**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 124 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.488 |
| mean_confidence | 0.825 |
| osm_score | 0.84 |

OSM features inside the course: buildings 48, built_up_landuse 1, golf=bunker 57, golf=cartpath 40, golf=fairway 34, golf=green 31, golf=hole 18, golf=lateral_water_hazard 25, golf=rough 44, golf=tee 124, holes_with_par 18, tees_with_colour 1, trees_polygons 9, water_polygons 25

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 377 / 378 | 279 | 0.70 | check the flags | 30% | 20% | 50% | tee stage: Palmer lidar_pad | tee: tee stage: Palmer lidar_pad; Palmer tee on a lidar pad (no OSM box at 377 yds) |
| 2 | 4 | 455 / 456 | 96 | 0.67 | check the flags | 33% | 14% | 53% | tee stage: Palmer walkback | tee: tee stage: Palmer walkback; Palmer tee walked back along the hole line (no box at 455 yds) |
| 3 | 4 | 370 / 377 | 88 | 0.72 | check the flags | 43% | 9% | 48% | tee stage: Palmer lidar_pad | tee: tee stage: Palmer lidar_pad; Palmer tee on a lidar pad (no OSM box at 370 yds) |
| 4 | 3 | 158 / 158 | 102 | 0.96 | auto | 100% | 0% | 0% | tee stage: Palmer tee_centroid |  |
| 5 | 4 | 441 / 438 | 220 | 0.81 | auto | 40% | 27% | 33% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 428 / 427 | 175 | 0.79 | check the flags | 76% | 0% | 24% | tee stage: Palmer lidar_pad | tee: tee stage: Palmer lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Palmer tee on a lidar pad (no OSM box at 428 yds) |
| 7 | 5 | 612 / 609 | 346 | 0.75 | check the flags | 54% | 7% | 38% | tee stage: Palmer lidar_pad | tee: tee stage: Palmer lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Palmer tee on a lidar pad (no OSM box at 612 yds) |
| 8 | 3 | 206 / 206 | 287 | 0.96 | auto | 100% | 0% | 0% | tee stage: Palmer tee_centroid |  |
| 9 | 5 | 512 / 511 | 321 | 0.80 | auto | 50% | 6% | 44% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis |
| 10 | 4 | 398 / 399 | 89 | 0.81 | auto | 50% | 12% | 38% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis |
| 11 | 4 | 445 / 445 | 141 | 0.83 | auto | 51% | 4% | 45% | tee stage: Palmer tee_centroid |  |
| 12 | 4 | 433 / 432 | 195 | 0.81 | auto | 56% | 3% | 41% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 3 | 215 / 215 | 179 | 0.96 | auto | 100% | 0% | 0% | tee stage: Palmer tee_centroid |  |
| 14 | 5 | 525 / 524 | 16 | 0.81 | auto | 48% | 13% | 39% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis |
| 15 | 4 | 314 / 314 | 4 | 0.78 | check the flags | 36% | 13% | 52% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis |
| 16 | 3 | 163 / 163 | 337 | 0.96 | auto | 100% | 0% | 0% | tee stage: Palmer tee_centroid |  |
| 17 | 4 | 442 / 441 | 339 | 0.87 | auto | 60% | 9% | 30% | tee stage: Palmer tee_centroid |  |
| 18 | 5 | 626 / 627 | 277 | 0.82 | auto | 55% | 5% | 39% | tee stage: Palmer tee_axis | tee: tee stage: Palmer tee_axis |

## Stages

- **resolve**: ok: relation/5897058 Osage National Golf Club (Osage Beach, MO)
- **osm**: ok: 522 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 108 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/osage_national/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2016)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2016
- **elevation**: ok: course_data/packages/osage_national/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Palmer' instead (allow_substitute). Sets on the card: Palmer, Tournament, Middle, Members, Forward, Green
