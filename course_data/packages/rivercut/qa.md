# Rivercut Golf Course (Springfield, MO) - Black tees

Built 2026-11-02T06:30:18Z. OSM relation/5981089. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 73 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.416 |
| mean_confidence | 0.825 |
| osm_score | 0.855 |

OSM features inside the course: buildings 8, golf=bunker 59, golf=cartpath 16, golf=clubhouse 1, golf=fairway 20, golf=green 18, golf=hole 17, golf=tee 73, golf=water_hazard 9, holes_with_par 17, water_lines 16, water_polygons 10

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 375 / 374 | 198 | 0.74 | check the flags | 33% | 1% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 3 | 204 / 204 | 69 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 415 / 415 | 36 | 0.81 | auto | 42% | 20% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 346 / 346 | 222 | 0.79 | check the flags | 34% | 21% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 5 | 511 / 511 | 240 | 0.80 | check the flags | 42% | 15% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 3 | 176 / 176 | 287 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 5 | 569 / 570 | 51 | 0.78 | check the flags | 40% | 8% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 443 / 443 | 231 | 0.78 | check the flags | 39% | 8% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 473 / 473 | 42 | 0.79 | check the flags | 50% | 2% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 5 | 611 / 611 | 245 | 0.81 | auto | 42% | 23% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 385 / 384 | 200 | 0.81 | auto | 52% | 9% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 409 / 409 | 317 | 0.77 | check the flags | 39% | 7% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 465 / 465 | 55 | 0.82 | auto | 42% | 25% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 435 / 435 | 21 | 0.84 | auto | 53% | 21% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 3 | 146 / 146 | 234 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 316 / 315 | 2 | 0.78 | check the flags | 34% | 18% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 243 / 243 | 96 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 544 / 543 | 153 | 0.81 | auto | 42% | 23% | 35% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/5981089 Rivercut Golf Course (Springfield, MO)
- **osm**: ok: 421 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 130 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/rivercut/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/rivercut/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'rivercut' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 159 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py rivercut (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 20 polygons (outside 20); mode replace

## Warnings

- CHECK vision: missing: product layer vision_any/2 not built for 'rivercut' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 159 long-grass zones d; trees / water come from OSM (or the fallback) only
