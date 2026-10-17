# The National Golf Club (Parkville, MO) - Black tees

Built 2026-10-17T17:29:00Z. OSM relation/2630633. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 87 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.386 |
| mean_confidence | 0.83 |
| osm_score | 0.849 |

OSM features inside the course: buildings 22, built_up_landuse 1, golf=bunker 83, golf=cartpath 30, golf=fairway 22, golf=green 21, golf=hole 18, golf=path 1, golf=pin 2, golf=rough 3, golf=tee 87, holes_with_handicap 2, holes_with_par 18, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 358 / 358 | 198 | 0.82 | auto | 34% | 40% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 5 | 498 / 498 | 219 | 0.82 | auto | 44% | 7% | 49% | tee stage: Black tee_centroid |  |
| 3 | 4 | 342 / 335 | 84 | 0.82 | auto | 26% | 46% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 197 / 197 | 8 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 5 | 534 / 532 | 5 | 0.82 | auto | 39% | 34% | 28% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 3 | 206 / 206 | 194 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 7 | 4 | 437 / 426 | 50 | 0.80 | auto | 37% | 25% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 430 / 431 | 268 | 0.79 | check the flags | 30% | 27% | 43% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 418 / 418 | 311 | 0.85 | auto | 73% | 0% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 457 / 456 | 345 | 0.76 | check the flags | 39% | 1% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 466 / 465 | 171 | 0.74 | check the flags | 32% | 2% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 427 / 425 | 359 | 0.75 | check the flags | 34% | 3% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 330 / 331 | 253 | 0.77 | check the flags | 39% | 4% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 3 | 131 / 131 | 344 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 5 | 556 / 556 | 315 | 0.70 | check the flags | 30% | 34% | 36% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 556 yds) |
| 16 | 3 | 216 / 213 | 140 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 457 / 457 | 132 | 0.85 | auto | 37% | 31% | 32% | tee stage: Black tee_centroid |  |
| 18 | 5 | 577 / 576 | 163 | 0.85 | auto | 46% | 35% | 18% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: relation/2630633 The National Golf Club (Parkville, MO)
- **osm**: ok: 885 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 16/16 holes OSM has no way for (2 to check; segment no, lidar pads 624, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 123 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/national_kc/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/national_kc/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 35 polygons (outside 35); mode replace

## Warnings

- hole 14: placed by v2+structure inference, golfer check (ambiguous (60% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (60% of the posterior))
