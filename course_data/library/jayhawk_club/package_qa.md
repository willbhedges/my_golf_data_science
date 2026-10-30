# The Jayhawk Club (Lawrence, KS) - Black tees

Built 2026-10-30T03:51:58Z. OSM relation/2053560. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 10 |
| holes_mapped | 10 |
| greens_found | 10 |
| tee_boxes | 32 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 8 |
| mean_landing_osm_share | 0.232 |
| mean_confidence | 0.722 |
| osm_score | 0.71 |

OSM features inside the course: buildings 15, built_up_landuse 1, golf=bunker 18, golf=cartpath 15, golf=driving_range 1, golf=fairway 8, golf=green 10, golf=hole 10, golf=pin 2, golf=rough 1, golf=tee 32, golf=water_hazard 2, holes_with_par 10, single_trees 67, water_lines 39, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 412 / 412 | 152 | 0.82 | auto | 29% | 28% | 43% | tee stage: Black tee_centroid |  |
| 2 | 5 | 534 / 535 | 307 | 0.62 | check the flags | 26% | 3% | 71% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 534 yds) |
| 3 | 4 | 408 / 409 | 264 | 0.55 | needs review | 0% | 2% | 98% | tee stage: Black walkback | tee: tee stage: Black walkback; no fairway in the landing zone; Black tee walked back along the hole line (no box at 408 yds) |
| 4 | 3 | 208 / 208 | 337 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 208 yds) |
| 5 | 4 | 396 / 385 | 65 | 0.67 | check the flags | 0% | 45% | 55% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Black tee on a lidar pad (no OSM box at 396 yds) |
| 6 | 4 | 444 / 445 | 271 | 0.71 | check the flags | 34% | 36% | 31% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 444 yds) |
| 7 | 3 | 236 / 236 | 239 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 236 yds) |
| 8 | 5 | 512 / 513 | 107 | 0.68 | check the flags | 25% | 33% | 42% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 512 yds) |
| 9 | 4 | 412 / 412 | 312 | 0.78 | check the flags | 32% | 1% | 67% | tee stage: Black tee_centroid |  |
| 10 | 4 | 408 / 408 | 344 | 0.70 | check the flags | 41% | 5% | 54% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 408 yds) |

## Stages

- **resolve**: ok: relation/2053560 The Jayhawk Club (Lawrence, KS)
- **osm**: ok: 1093 features
- **routing**: ok: structure (unmapped_card, structure on osm) placed 8/16 holes OSM has no way for (8 to check; segment no, lidar pads 655, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 36 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (10 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/jayhawk_club/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 10/10 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/jayhawk_club/imagery/dem.tif (10/10 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 14 polygons (outside 14); mode replace

## Warnings

- hole inference fallback: v2+structure: RuntimeError: unmapped and no perception scene: no structure prior
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- hole 2: placed by structure inference, golfer check (uncertain (30%): P(number) 52%, P(tee) 71%; long walk from the previous green (394 yds))
- hole 3: placed by structure inference, golfer check (uncertain (37%): P(number) 72%, P(tee) 70%)
- hole 4: placed by structure inference, golfer check (uncertain (33%): P(number) 45%, P(tee) 93%)
- hole 5: placed by structure inference, golfer check (uncertain (26%): P(number) 72%, P(tee) 41%)
- hole 6: placed by structure inference, golfer check (uncertain (31%): P(number) 74%, P(tee) 52%)
- hole 7: placed by structure inference, golfer check (uncertain (41%): P(number) 74%, P(tee) 78%)
- hole 8: placed by structure inference, golfer check (uncertain (39%): P(number) 58%, P(tee) 94%)
- hole 10: placed by structure inference, golfer check (uncertain (25%): P(number) 41%, P(tee) 63%)
