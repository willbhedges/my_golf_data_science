# Paa-Ko Ridge Golf Club (Sandia Park, NM) - Black tees

Built 2026-11-03T09:09:58Z. OSM relation/3585731. Scorecard: file (course_data/library/paa_ko_ridge/card_golfify.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 132 |
| tees_with_colour | 1 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.4 |
| mean_confidence | 0.836 |
| osm_score | 0.88 |

OSM features inside the course: buildings 3, golf=bunker 119, golf=cartpath 27, golf=clubhouse 1, golf=fairway 34, golf=green 28, golf=hole 18, golf=pin 27, golf=rough 85, golf=tee 132, golf=water_hazard 4, holes_with_handicap 1, holes_with_par 18, tees_with_colour 1, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 429 / 430 | 266 | 0.81 | auto | 38% | 9% | 53% | tee stage: Black tee_centroid |  |
| 2 | 4 | 394 / 395 | 264 | 0.80 | auto | 30% | 15% | 54% | tee stage: Black tee_centroid |  |
| 3 | 5 | 604 / 604 | 250 | 0.84 | auto | 52% | 5% | 43% | tee stage: Black tee_centroid |  |
| 4 | 3 | 183 / 183 | 306 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 5 | 562 / 557 | 32 | 0.79 | check the flags | 35% | 22% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 327 / 327 | 36 | 0.82 | auto | 37% | 14% | 48% | tee stage: Black tee_centroid |  |
| 7 | 4 | 496 / 496 | 157 | 0.82 | auto | 48% | 18% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 3 | 265 / 267 | 108 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 477 / 478 | 74 | 0.78 | check the flags | 44% | 4% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 416 / 417 | 263 | 0.82 | auto | 38% | 15% | 47% | tee stage: Black tee_centroid |  |
| 11 | 4 | 449 / 449 | 234 | 0.82 | auto | 40% | 10% | 50% | tee stage: Black tee_centroid |  |
| 12 | 5 | 541 / 541 | 239 | 0.81 | auto | 40% | 24% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 386 / 385 | 246 | 0.78 | check the flags | 34% | 18% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 272 / 272 | 74 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 640 / 639 | 18 | 0.79 | check the flags | 38% | 16% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 228 / 228 | 53 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 419 / 420 | 66 | 0.80 | auto | 46% | 10% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 474 / 470 | 83 | 0.81 | auto | 38% | 24% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/3585731 Paa-Ko Ridge Golf Club (Sandia Park, NM)
- **osm**: ok: 620 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/paa_ko_ridge/card_golfify.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 104 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/paa_ko_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/paa_ko_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- multi-course facility of nines: 3 nine-hole groups (by sub-course outline: Paa-ko Ridge 10-18 9, Paa-ko Ridge 1-9 9, Paa-ko Ridge 19-27 9); kept the 'Paa-ko Ridge 1-9' nine as holes 1-9 + the 'Paa-ko Ridge 10-18' nine as holes 10-18 (the 1-9 nine, the 10-18 nine): CHECK the nines against the card, 18 ways; ignored 9
