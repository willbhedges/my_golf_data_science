# Buffalo Dunes (Garden City, KS) - Blue tees

Built 2026-11-03T16:13:11Z. OSM way/783368916. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 39 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.289 |
| mean_confidence | 0.782 |
| osm_score | 0.858 |

OSM features inside the course: buildings 9, golf=bunker 27, golf=fairway 22, golf=green 21, golf=hole 18, golf=lateral_water_hazard 3, golf=path 30, golf=rough 1, golf=tee 39, holes_with_par 18, single_trees 50, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 548 / 548 | 201 | 0.77 | check the flags | 31% | 15% | 55% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 371 / 371 | 61 | 0.78 | check the flags | 25% | 14% | 62% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 389 / 388 | 22 | 0.76 | check the flags | 29% | 16% | 56% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 195 / 195 | 188 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 5 | 539 / 544 | 221 | 0.71 | check the flags | 33% | 18% | 50% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 539 yds) |
| 6 | 4 | 400 / 400 | 21 | 0.65 | check the flags | 30% | 11% | 59% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 400 yds) |
| 7 | 4 | 357 / 352 | 220 | 0.77 | check the flags | 33% | 16% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 3 | 189 / 189 | 360 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 392 / 392 | 49 | 0.76 | check the flags | 24% | 19% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 4 | 391 / 391 | 234 | 0.75 | check the flags | 28% | 13% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 4 | 423 / 422 | 190 | 0.70 | check the flags | 37% | 11% | 52% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 423 yds) |
| 12 | 3 | 198 / 198 | 276 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 5 | 515 / 514 | 6 | 0.74 | check the flags | 24% | 12% | 65% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 413 / 412 | 333 | 0.71 | check the flags | 32% | 19% | 49% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 413 yds) |
| 15 | 4 | 398 / 392 | 359 | 0.74 | check the flags | 25% | 11% | 64% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 564 / 563 | 168 | 0.74 | check the flags | 29% | 6% | 65% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 3 | 167 / 167 | 152 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; green not visible on the NAIP 2023 imagery (NDVI -0.065 vs 0.372 on the course's other greens: bare soil / construction); the outline is OSM's |
| 18 | 4 | 357 / 356 | 64 | 0.77 | check the flags | 26% | 20% | 53% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/783368916 Buffalo Dunes (Finney County, KS)
- **osm**: ok: 227 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 25 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/buffalo_dunes/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 17/18 greens visible as turf on NAIP 2023; NOT visible: holes 17
- **elevation**: ok: course_data/packages/buffalo_dunes/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'buffalo_dunes' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 148 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py buffalo_dunes (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace

## Warnings

- greens of holes 17 are not visible as turf on the NAIP 2023 imagery (bare soil / construction / dead turf): pick another NAIP year (imagery/naip_years.py)
- CHECK vision: missing: product layer vision_any/2 not built for 'buffalo_dunes' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 148 long-grass zo; trees / water come from OSM (or the fallback) only
