# Neshanic Valley Golf Course (Branchburg Township, NJ) - Black tees

Built 2026-11-01T21:53:54Z. OSM way/698906445. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 166 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 6 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.424 |
| mean_confidence | 0.808 |
| osm_score | 0.771 |

OSM features inside the course: buildings 3, golf=bunker 118, golf=cartpath 31, golf=clubhouse 3, golf=driving_range 1, golf=fairway 48, golf=green 44, golf=hole 18, golf=pin 38, golf=rough 1, golf=tee 166, holes_with_handicap 1, holes_with_par 18, trees_polygons 2, water_lines 1, water_polygons 6

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 419 / 419 | 40 | 0.79 | check the flags | 34% | 6% | 60% | tee stage: Black tee_centroid |  |
| 2 | 4 | 391 / 392 | 77 | 0.79 | check the flags | 46% | 3% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 197 / 197 | 64 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 4 | 5 | 523 / 523 | 255 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 458 / 459 | 74 | 0.78 | check the flags | 34% | 0% | 66% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 3 | 175 / 175 | 1 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 7 | 4 | 336 / 335 | 182 | 0.72 | check the flags | 50% | 0% | 50% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 336 yds) |
| 8 | 4 | 444 / 443 | 254 | 0.76 | check the flags | 35% | 5% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 5 | 577 / 572 | 211 | 0.78 | check the flags | 45% | 2% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 434 / 434 | 103 | 0.78 | check the flags | 43% | 5% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 362 / 363 | 250 | 0.82 | auto | 62% | 0% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 174 / 174 | 85 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 13 | 4 | 458 / 459 | 61 | 0.83 | auto | 63% | 2% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 588 / 589 | 251 | 0.80 | check the flags | 39% | 0% | 61% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 422 / 423 | 94 | 0.60 | needs review | 18% | 0% | 82% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee walked back along the hole line (no box at 422 yds) |
| 16 | 4 | 382 / 383 | 246 | 0.65 | check the flags | 34% | 4% | 62% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee walked back along the hole line (no box at 382 yds) |
| 17 | 3 | 204 / 204 | 346 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 5 | 525 / 525 | 311 | 0.80 | auto | 42% | 0% | 58% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/698906445 Neshanic Valley Golf Course (Branchburg Township, NJ)
- **osm**: ok: 667 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 17/17 holes OSM has no way for (7 to check; segment no, lidar pads 233, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 78 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/neshanic_valley/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/neshanic_valley/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 11 polygons (outside 11); mode replace

## Warnings

- hole refs: kept the plain-numbered holes (1 ways, refs as plain numbers)
- ignored 37 golf=hole way(s) of another course / practice area by ref: A1, A2, A3, A4, A5, A6, A7, A8, A9, L1, L2, L3 ...
- hole 1: placed by v2+structure inference, golfer check (ambiguous (76% of the posterior))
- hole 6: placed by v2+structure inference, golfer check (ambiguous (95% of the posterior))
- hole 7: placed by v2+structure inference, golfer check (ambiguous (90% of the posterior))
- hole 9: placed by v2+structure inference, golfer check (ambiguous (90% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (61% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (63% of the posterior))
- hole 12: placed by v2+structure inference, golfer check (ambiguous (61% of the posterior))
