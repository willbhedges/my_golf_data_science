# Prairie Dunes (Hutchinson, KS) - Blue tees

Built 2026-11-04T02:11:16Z. OSM way/778336759. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.375 |
| mean_confidence | 0.865 |
| osm_score | 0.875 |

OSM features inside the course: buildings 11, golf=bunker 88, golf=cartpath 87, golf=driving_range 2, golf=fairway 17, golf=green 26, golf=hole 18, golf=lateral_water_hazard 1, golf=rough 4, golf=tee 67, golf=water_hazard 3, holes_with_par 18, single_trees 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 435 / 435 | 236 | 0.84 | auto | 33% | 50% | 17% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 3 | 161 / 161 | 242 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 315 / 315 | 24 | 0.83 | auto | 32% | 44% | 24% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 168 / 168 | 314 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 5 | 4 | 418 / 412 | 201 | 0.84 | auto | 43% | 37% | 20% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 4 | 370 / 371 | 97 | 0.87 | auto | 38% | 41% | 22% | tee stage: Blue tee_centroid |  |
| 7 | 5 | 512 / 511 | 3 | 0.84 | auto | 38% | 42% | 20% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 440 / 441 | 286 | 0.77 | check the flags | 34% | 47% | 19% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 440 yds) |
| 9 | 4 | 426 / 425 | 118 | 0.84 | auto | 39% | 39% | 22% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 3 | 185 / 185 | 38 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 4 | 453 / 447 | 22 | 0.85 | auto | 40% | 44% | 16% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 390 / 389 | 339 | 0.88 | auto | 33% | 51% | 16% | tee stage: Blue tee_centroid |  |
| 13 | 4 | 395 / 393 | 137 | 0.85 | auto | 43% | 37% | 19% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 377 / 372 | 146 | 0.84 | auto | 38% | 41% | 21% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 3 | 200 / 200 | 284 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 16 | 4 | 408 / 408 | 210 | 0.85 | auto | 39% | 44% | 16% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 5 | 500 / 499 | 191 | 0.84 | auto | 38% | 41% | 21% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 382 / 386 | 349 | 0.84 | auto | 37% | 42% | 22% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/778336759 Prairie Dunes (Reno County, KS)
- **osm**: ok: 400 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 95 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/prairie_dunes/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/prairie_dunes/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'prairie_dunes' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 199 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py prairie_dunes (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 6 polygons (outside 6); mode replace
- **native_auto**: ok: 14 holes, sides 1 both, 3 both, 5 both, 6 both, 7 both, 8 both, 9 both, 11 both, 12 both, 13 both, 14 both, 16 both, 17 both, 18 both

## Warnings

- ignored 1 practice / driving-range tee box(es): OSM 700139683
- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 8 Silver 359 < Bronze 390
