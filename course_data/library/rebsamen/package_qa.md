# Rebsamen Golf Course (Little Rock, AR) - Black tees

Built 2026-10-30T22:20:13Z. OSM way/77018704. Scorecard: opengolfapi (opengolfapi). Tee set: name.

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
| mean_landing_osm_share | 0.386 |
| mean_confidence | 0.8 |
| osm_score | 0.877 |

OSM features inside the course: buildings 9, golf=bunker 50, golf=cartpath 15, golf=fairway 16, golf=green 31, golf=hole 18, golf=lateral_water_hazard 6, golf=tee 73, holes_with_par 18, single_trees 165, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 381 / 379 | 33 | 0.76 | check the flags | 34% | 8% | 58% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 5 | 549 / 549 | 133 | 0.74 | check the flags | 46% | 13% | 41% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 549 yds) |
| 3 | 3 | 201 / 201 | 238 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 472 / 469 | 114 | 0.78 | check the flags | 40% | 8% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 441 / 439 | 322 | 0.76 | check the flags | 48% | 24% | 28% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 441 yds) |
| 6 | 4 | 313 / 313 | 60 | 0.82 | auto | 38% | 13% | 49% | tee stage: Black tee_centroid |  |
| 7 | 3 | 138 / 138 | 347 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 5 | 568 / 568 | 300 | 0.77 | check the flags | 30% | 18% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 411 / 410 | 201 | 0.71 | check the flags | 48% | 14% | 38% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 411 yds) |
| 10 | 4 | 430 / 430 | 114 | 0.82 | auto | 35% | 19% | 46% | tee stage: Black tee_centroid |  |
| 11 | 4 | 464 / 463 | 124 | 0.79 | check the flags | 42% | 11% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 5 | 501 / 500 | 336 | 0.83 | auto | 37% | 21% | 42% | tee stage: Black tee_centroid |  |
| 13 | 4 | 376 / 375 | 153 | 0.72 | check the flags | 34% | 25% | 41% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 376 yds) |
| 14 | 3 | 201 / 201 | 234 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; green not visible on the NAIP 2019 imagery (NDVI -0.006 vs 0.13 on the course's other greens: bare soil / construction); the outline is OSM's |
| 15 | 5 | 598 / 597 | 316 | 0.76 | check the flags | 28% | 13% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 177 / 177 | 306 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 316 / 317 | 78 | 0.77 | check the flags | 43% | 0% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 458 / 459 | 266 | 0.66 | check the flags | 36% | 8% | 55% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 458 yds) |

## Stages

- **resolve**: ok: way/77018704 Rebsamen Golf Course (Little Rock, AR)
- **osm**: ok: 776 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 70 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/rebsamen/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 17/18 greens visible as turf on NAIP 2019; NOT visible: holes 14
- **elevation**: ok: course_data/packages/rebsamen/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 3 polygons (outside 3); mode replace

## Warnings

- ignored 14 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 896615441, 896615442, 896615443, 896615444, 896615445, 896639471, 896639479, 896639481
- greens of holes 14 are not visible as turf on the NAIP 2019 imagery (bare soil / construction / dead turf): pick another NAIP year (imagery/naip_years.py)
- scorecard (opengolfapi): Black: holes sum to 6995 but the source says 7033 (-38): mixed card versions
- scorecard (opengolfapi): White: holes sum to 5911 but the source says 5889 (+22): mixed card versions
