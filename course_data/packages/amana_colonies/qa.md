# Amana Colonies Golf Course (Amana, IA) - Black tees

Built 2026-11-03T09:21:06Z. OSM way/731221353. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 73 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.317 |
| mean_confidence | 0.821 |
| osm_score | 0.863 |

OSM features inside the course: buildings 1, golf=bunker 59, golf=cartpath 8, golf=fairway 19, golf=green 19, golf=hole 18, golf=tee 73, golf=water_hazard 4, holes_with_par 18, water_lines 2, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 420 / 419 | 0 | 0.81 | auto | 23% | 31% | 46% | tee stage: Black tee_centroid |  |
| 2 | 5 | 522 / 522 | 5 | 0.69 | check the flags | 32% | 30% | 38% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 522 yds) |
| 3 | 4 | 412 / 413 | 301 | 0.77 | check the flags | 30% | 19% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 179 / 179 | 338 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 4 | 372 / 372 | 155 | 0.78 | check the flags | 26% | 27% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 5 | 548 / 549 | 113 | 0.79 | check the flags | 38% | 16% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 348 / 348 | 201 | 0.79 | check the flags | 26% | 33% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 191 / 191 | 137 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 4 | 368 / 368 | 198 | 0.79 | check the flags | 26% | 17% | 57% | tee stage: Black tee_centroid |  |
| 10 | 4 | 418 / 418 | 339 | 0.82 | auto | 41% | 28% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 5 | 530 / 530 | 316 | 0.80 | auto | 32% | 32% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 432 / 433 | 297 | 0.83 | auto | 43% | 32% | 25% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 182 / 182 | 338 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 182 yds) |
| 14 | 4 | 350 / 345 | 178 | 0.77 | check the flags | 28% | 18% | 53% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 527 / 528 | 100 | 0.78 | check the flags | 30% | 23% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 405 / 403 | 167 | 0.80 | auto | 36% | 27% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 204 / 204 | 144 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 416 / 412 | 108 | 0.78 | check the flags | 31% | 22% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/731221353 Amana Colonies Golf Course (Iowa County, IA)
- **osm**: ok: 262 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 88 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/amana_colonies/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/amana_colonies/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'amana_colonies' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 82 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py amana_colonies (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 3 polygons (property_line 3); mode replace

## Warnings

- CHECK vision: missing: product layer vision_any/2 not built for 'amana_colonies' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 82 long-grass zo; trees / water come from OSM (or the fallback) only
