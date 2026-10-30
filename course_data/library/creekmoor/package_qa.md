# Creekmoor Golf Club (Raymore, MO) - Black tees

Built 2026-10-30T00:25:45Z. OSM relation/4249741. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 15 |
| holes_mapped | 15 |
| greens_found | 15 |
| tee_boxes | 80 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 4 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.013 |
| mean_confidence | 0.747 |
| osm_score | 0.523 |

OSM features inside the course: buildings 3, golf=bunker 68, golf=cartpath 12, golf=driving_range 1, golf=green 19, golf=hole 15, golf=tee 80, golf=water_hazard 4, holes_with_par 15, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 4 | 371 / 374 | 307 | 0.65 | check the flags | 0% | 0% | 100% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 3 | 4 | 440 / 440 | 313 | 0.74 | check the flags | 0% | 100% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Black tee walked back along the hole line (no box at 440 yds) |
| 4 | 3 | 195 / 195 | 11 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 5 | 537 / 526 | 51 | 0.75 | check the flags | 2% | 47% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 6 | 4 | 451 / 448 | 220 | 0.68 | check the flags | 4% | 9% | 86% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 7 | 3 | 170 / 170 | 166 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 441 / 441 | 146 | 0.69 | check the flags | 2% | 51% | 47% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no fairway in the landing zone; Black tee on a lidar pad (no OSM box at 441 yds) |
| 9 | 5 | 663 / 664 | 162 | 0.85 | auto | 0% | 100% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 10 | 4 | 482 / 473 | 128 | 0.71 | check the flags | 4% | 61% | 35% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); OB from the course boundary on 61% of the landing zone; Black tee on a lidar pad (no OSM box at 482 yds) |
| 11 | 4 | 374 / 375 | 83 | 0.76 | check the flags | 0% | 53% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no fairway in the landing zone |
| 13 | 5 | 548 / 549 | 239 | 0.70 | check the flags | 0% | 24% | 76% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no fairway in the landing zone |
| 14 | 4 | 420 / 421 | 276 | 0.79 | check the flags | 1% | 52% | 47% | tee stage: Black tee_centroid | no fairway in the landing zone |
| 15 | 4 | 460 / 451 | 343 | 0.66 | check the flags | 2% | 0% | 98% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 16 | 4 | 455 / 446 | 282 | 0.78 | check the flags | 0% | 100% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Black tee on a lidar pad (no OSM box at 455 yds) |
| 18 | 5 | 541 / 541 | 223 | 0.56 | needs review | 3% | 4% | 94% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Black tee walked back along the hole line (no box at 541 yds) |

## Stages

- **resolve**: ok: relation/4249741 Creekmoor Golf Club (Raymore, MO)
- **osm**: ok: 394 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 15/18 holes OSM has no way for (11 to check; segment no, lidar pads 500, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 80 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (15 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/creekmoor/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 15/15 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/creekmoor/imagery/dem.tif (15/15 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 43 polygons (outside 43); mode replace

## Warnings

- hole 2: placed by v2+structure inference, golfer check (ambiguous (89% of the posterior))
- hole 3: placed by v2+structure inference, golfer check (ambiguous (89% of the posterior))
- hole 4: placed by v2+structure inference, golfer check (ambiguous (92% of the posterior))
- hole 8: placed by v2+structure inference, golfer check (ambiguous (55% of the posterior))
- hole 9: placed by v2+structure inference, golfer check (ambiguous (67% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (56% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (95% of the posterior))
- hole 13: placed by v2+structure inference, golfer check (ambiguous (80% of the posterior))
- hole 14: placed by v2+structure inference, golfer check (ambiguous (81% of the posterior))
- hole 15: placed by v2+structure inference, golfer check (ambiguous (80% of the posterior))
- hole 16: placed by v2+structure inference, golfer check (ambiguous (74% of the posterior))
