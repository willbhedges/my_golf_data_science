# Annbriar Golf Course (Waterloo, IL) - Black tees

Built 2026-11-09T16:25:20Z. OSM way/1466372251. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 99 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.469 |
| mean_confidence | 0.864 |
| osm_score | 0.894 |

OSM features inside the course: buildings 7, golf=bunker 67, golf=cartpath 48, golf=clubhouse 1, golf=driving_range 1, golf=fairway 21, golf=green 20, golf=hole 18, golf=lateral_water_hazard 3, golf=path 26, golf=pin 18, golf=rough 72, golf=tee 99, golf=water_hazard 3, holes_with_handicap 18, holes_with_par 18, tees_with_colour 1, tees_with_ref 1, trees_polygons 1, water_lines 2, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 337 / 338 | 72 | 0.84 | auto | 41% | 37% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 395 / 394 | 104 | 0.85 | auto | 50% | 28% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 373 / 374 | 282 | 0.85 | auto | 60% | 15% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 190 / 191 | 263 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 5 | 496 / 497 | 79 | 0.82 | auto | 46% | 2% | 53% | tee stage: Black tee_centroid |  |
| 6 | 4 | 378 / 379 | 280 | 0.88 | auto | 65% | 7% | 28% | tee stage: Black tee_centroid |  |
| 7 | 3 | 155 / 155 | 282 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 8 | 4 | 415 / 415 | 196 | 0.83 | auto | 45% | 10% | 45% | tee stage: Black tee_centroid |  |
| 9 | 5 | 475 / 475 | 0 | 0.70 | check the flags | 40% | 40% | 20% | tee stage: Black review (inside OSM tee -1) | tee: tee stage: Black review (inside OSM tee -1) |
| 10 | 4 | 382 / 382 | 348 | 0.88 | auto | 42% | 37% | 21% | tee stage: Black tee_centroid |  |
| 11 | 4 | 404 / 405 | 248 | 0.87 | auto | 46% | 46% | 8% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 353 / 353 | 212 | 0.81 | auto | 50% | 12% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 356 / 354 | 73 | 0.79 | check the flags | 49% | 2% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 492 / 492 | 236 | 0.88 | auto | 38% | 43% | 19% | tee stage: Black tee_centroid |  |
| 15 | 3 | 151 / 151 | 136 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 16 | 4 | 446 / 444 | 157 | 0.83 | auto | 44% | 28% | 28% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 147 / 147 | 332 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 5 | 572 / 572 | 349 | 0.87 | auto | 42% | 32% | 26% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: way/1466372251 Annbriar Golf Course (Waterloo, IL)
- **osm**: ok: 445 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 9 review (inside OSM tee -1);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 104 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/annbriar/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/annbriar/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'annbriar' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 199 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py annbriar (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace
- **native_auto**: ok: 8 holes, sides 1 both, 2 both, 3 R, 9 both, 10 both, 12 R, 16 L, 18 R
