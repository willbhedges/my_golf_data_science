# L.A. Nickell Golf Course (Columbia, MO) - Blue tees

Built 2026-11-02T06:28:31Z. OSM way/387047950. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 40 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.278 |
| mean_confidence | 0.783 |
| osm_score | 0.842 |

OSM features inside the course: buildings 7, golf=cartpath 12, golf=clubhouse 1, golf=fairway 22, golf=green 20, golf=hole 17, golf=tee 40, golf=water_hazard 3, holes_with_par 17, water_lines 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 372 / 366 | 164 | 0.75 | check the flags | 24% | 16% | 61% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 369 / 364 | 131 | 0.76 | check the flags | 24% | 23% | 53% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 385 / 385 | 316 | 0.79 | check the flags | 41% | 11% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 3 | 224 / 227 | 276 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Blue texture_pad | tee: tee stage: Blue texture_pad; Blue tee on an imagery-detected pad (texture; no OSM box at 224 yds) |
| 5 | 4 | 325 / 320 | 166 | 0.78 | check the flags | 21% | 34% | 44% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 3 | 196 / 196 | 43 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 7 | 5 | 500 / 495 | 146 | 0.79 | check the flags | 30% | 30% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 392 / 391 | 329 | 0.77 | check the flags | 30% | 21% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 379 / 378 | 336 | 0.69 | check the flags | 30% | 30% | 40% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 379 yds) |
| 10 | 4 | 384 / 383 | 190 | 0.68 | check the flags | 30% | 26% | 44% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 384 yds) |
| 11 | 3 | 174 / 174 | 280 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 526 / 525 | 2 | 0.69 | check the flags | 30% | 27% | 42% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 526 yds) |
| 13 | 4 | 376 / 375 | 174 | 0.74 | check the flags | 28% | 39% | 33% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 376 yds) |
| 14 | 3 | 194 / 194 | 26 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 4 | 377 / 377 | 315 | 0.80 | check the flags | 32% | 28% | 40% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 4 | 328 / 329 | 73 | 0.82 | auto | 19% | 58% | 22% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 407 / 402 | 100 | 0.73 | check the flags | 18% | 14% | 67% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 427 / 426 | 207 | 0.69 | check the flags | 30% | 31% | 38% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 427 yds) |

## Stages

- **resolve**: ok: way/387047950 L.A. Nickell Golf Course (Columbia, MO)
- **osm**: ok: 422 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 28 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/la_nickell/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/la_nickell/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'la_nickell' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 149 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py la_nickell (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 11 polygons (outside 11); mode replace

## Warnings

- card consensus: opengolfapi: set order: 'Web' is longer than 'White' on 11 of 11 holes with several OSM tees: names may be swapped
- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
- CHECK vision: missing: product layer vision_any/2 not built for 'la_nickell' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 149 long-grass zones; trees / water come from OSM (or the fallback) only
