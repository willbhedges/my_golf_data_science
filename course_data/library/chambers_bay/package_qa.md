# Chambers Bay Golf Course (University Place, WA) - Navy tees

Built 2026-10-31T05:23:21Z. OSM way/26787026. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Navy, Sand, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Navy' instead (allow_substitute). Sets on the card: Navy, Sand, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 63 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.607 |
| mean_confidence | 0.86 |
| osm_score | 0.879 |

OSM features inside the course: buildings 3, golf=bunker 70, golf=cartpath 55, golf=fairway 19, golf=green 19, golf=hole 18, golf=path 4, golf=pin 18, golf=rough 6, golf=tee 63, holes_with_par 18, single_trees 1, tees_with_ref 61, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 494 / 495 | 99 | 0.83 | auto | 66% | 0% | 34% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 395 / 395 | 20 | 0.87 | auto | 45% | 45% | 10% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 3 | 3 | 167 / 167 | 338 | 0.86 | auto | 100% | 0% | 0% | tee stage: Navy lidar_pad | tee: tee stage: Navy lidar_pad; Navy tee on a lidar pad (no OSM box at 167 yds) |
| 4 | 5 | 530 / 531 | 105 | 0.85 | auto | 73% | 0% | 27% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 465 / 466 | 282 | 0.88 | auto | 76% | 9% | 15% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 6 | 4 | 418 / 412 | 159 | 0.89 | auto | 67% | 24% | 9% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 7 | 4 | 482 / 483 | 42 | 0.89 | auto | 69% | 25% | 6% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 8 | 5 | 557 / 563 | 184 | 0.63 | check the flags | 42% | 0% | 57% | tee stage: Navy texture_pad | tee: tee stage: Navy texture_pad; Navy tee on an imagery-detected pad (texture; no OSM box at 557 yds) |
| 9 | 3 | 227 / 227 | 290 | 0.93 | auto | 100% | 0% | 0% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 10 | 4 | 398 / 399 | 307 | 0.84 | auto | 51% | 25% | 24% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 11 | 4 | 457 / 447 | 21 | 0.78 | check the flags | 55% | 23% | 23% | tee stage: Navy lidar_pad | tee: tee stage: Navy lidar_pad; Navy tee on a lidar pad (no OSM box at 457 yds) |
| 12 | 4 | 281 / 289 | 20 | 0.83 | auto | 52% | 16% | 32% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 13 | 4 | 485 / 486 | 287 | 0.89 | auto | 50% | 32% | 18% | tee stage: Navy tee_centroid |  |
| 14 | 4 | 496 / 495 | 306 | 0.87 | auto | 80% | 0% | 20% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 3 | 139 / 139 | 232 | 0.96 | auto | 100% | 0% | 0% | tee stage: Navy tee_centroid |  |
| 16 | 4 | 396 / 396 | 180 | 0.88 | auto | 65% | 21% | 14% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 17 | 3 | 172 / 159 | 194 | 0.93 | auto | 100% | 0% | 0% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |
| 18 | 5 | 541 / 542 | 94 | 0.87 | auto | 60% | 25% | 15% | tee stage: Navy tee_axis | tee: tee stage: Navy tee_axis |

## Stages

- **resolve**: ok: way/26787026 Chambers Bay Golf Course (University Place, WA)
- **osm**: ok: 791 features
- **renumber**: ok: OSM hole refs -> card holes 1->13, 13->1
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 93 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/chambers_bay/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/chambers_bay/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace

## Warnings

- card consensus: opengolfapi: set names swapped: the rows under 'Blue' sum to 6345 = the stated 'Blue' total 5226; they were listed as 'Sand' (rows moved back)
- card consensus: opengolfapi: set order: 'Blue' is longer than 'White' on 16 of 16 holes with several OSM tees: names may be swapped
- requested tee set 'Black' is not on the card; using 'Navy' instead (allow_substitute). Sets on the card: Navy, Sand, White, Red
- OSM hole numbering differs from the card: OSM hole refs -> card holes 1->13, 13->1 (CHECK)
- hole 11 Sand: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 15 White: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 15 Red: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 17 Red: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
