# Cabot Citrus Farms ( Brooksville , FL) - Black tees

Built 2026-11-03T00:13:12Z. OSM way/410646892. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 16 |
| holes_mapped | 16 |
| greens_found | 16 |
| tee_boxes | 163 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.247 |
| mean_confidence | 0.755 |
| osm_score | 0.805 |

OSM features inside the course: golf=bunker 144, golf=cartpath 27, golf=fairway 40, golf=green 39, golf=hole 16, golf=rough 1, golf=tee 163, golf=water_hazard 4, holes_with_par 16, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 475 / 479 | 82 | 0.74 | check the flags | 33% | 2% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 292 / 292 | 119 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 292 yds) |
| 4 | 5 | 511 / 509 | 6 | 0.65 | check the flags | 32% | 7% | 61% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 511 yds) |
| 5 | 4 | 382 / 382 | 70 | 0.74 | check the flags | 8% | 14% | 78% | tee stage: Black tee_centroid |  |
| 6 | 5 | 563 / 557 | 331 | 0.75 | check the flags | 11% | 37% | 52% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 199 / 194 | 70 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 426 / 425 | 187 | 0.69 | check the flags | 44% | 9% | 47% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 426 yds) |
| 9 | 4 | 421 / 420 | 14 | 0.69 | check the flags | 44% | 10% | 46% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 421 yds) |
| 10 | 3 | 242 / 242 | 104 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 242 yds) |
| 11 | 4 | 427 / 423 | 280 | 0.73 | check the flags | 25% | 6% | 69% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 496 / 497 | 97 | 0.63 | check the flags | 32% | 0% | 68% | tee stage: Black walkback | tee: tee stage: Black walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Black tee walked back along the hole line (no box at 496 yds) |
| 14 | 5 | 581 / 581 | 48 | 0.78 | check the flags | 42% | 7% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 388 / 393 | 61 | 0.77 | check the flags | 0% | 58% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no fairway in the landing zone |
| 16 | 3 | 201 / 201 | 104 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 17 | 5 | 500 / 501 | 271 | 0.65 | check the flags | 4% | 47% | 48% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 500 yds) |
| 18 | 4 | 489 / 488 | 224 | 0.72 | check the flags | 20% | 6% | 74% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/410646892 Cabot Citrus Farms (Hernando County, FL)
- **osm**: ok: 460 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 16/18 holes OSM has no way for (11 to check; segment no, lidar pads 288, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 67 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (16 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/world_woods/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 16/16 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/world_woods/imagery/dem.tif (16/16 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 1 polygons (outside 1); mode replace

## Warnings

- hole 1: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 3: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 4: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 5: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 6: placed by v2+structure inference, golfer check (ambiguous (80% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (15% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (47% of the posterior))
- hole 14: placed by v2+structure inference, golfer check (ambiguous (77% of the posterior))
- hole 15: placed by v2+structure inference, golfer check (ambiguous (92% of the posterior))
- hole 17: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (83% of the posterior))
- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 1 Yellow(W) 300 < Green(M) 334
