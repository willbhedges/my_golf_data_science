# The Jayhawk Club (Lawrence, KS) - Black tees

Built 2026-11-26T07:52:05Z. OSM relation/2053560. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 10 |
| holes_mapped | 10 |
| greens_found | 10 |
| tee_boxes | 32 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 8 |
| of_par4_5 | 8 |
| mean_landing_osm_share | 0.267 |
| mean_confidence | 0.821 |
| osm_score | 0.742 |

OSM features inside the course: buildings 15, built_up_landuse 1, golf=bunker 18, golf=cartpath 15, golf=driving_range 1, golf=fairway 8, golf=green 10, golf=hole 10, golf=pin 2, golf=rough 1, golf=tee 32, golf=water_hazard 2, holes_with_par 10, single_trees 67, water_lines 39, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 412 / 412 | 152 | 0.84 | auto | 29% | 38% | 33% | tee stage: Black tee_centroid |  |
| 2 | 5 | 534 / 412 | 307 | 0.79 | check the flags | 38% | 14% | 48% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets |
| 3 | 4 | 408 / 290 | 264 | 0.80 | check the flags | 15% | 52% | 33% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets |
| 4 | 3 | 208 / 538 | 337 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback_capped | tee: tee stage: Black walkback_capped; Black tee walked back along the hole line (no box at 208 yds) |
| 5 | 4 | 396 / 392 | 65 | 0.72 | check the flags | 0% | 72% | 28% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no fairway in the landing zone; Black tee on a lidar pad (no OSM box at 396 yds) |
| 6 | 4 | 444 / 337 | 271 | 0.84 | auto | 30% | 55% | 16% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets |
| 7 | 3 | 236 / 231 | 250 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 5 | 512 / 380 | 107 | 0.86 | auto | 36% | 53% | 11% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets |
| 9 | 4 | 412 / 412 | 312 | 0.81 | auto | 32% | 15% | 53% | tee stage: Black tee_centroid |  |
| 10 | 4 | 408 / 299 | 347 | 0.80 | auto | 34% | 30% | 37% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap |

## Stages

- **resolve**: ok: relation/2053560 The Jayhawk Club (Lawrence, KS)
- **osm**: ok: 1095 features
- **routing**: ok: structure (unmapped_card, structure on osm) placed 8/16 holes OSM has no way for (8 to check; segment no, lidar pads 655, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 18 candidate pads near hole starts (18 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (10 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/jayhawk_club/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 10/10 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/jayhawk_club/imagery/dem.tif (10/10 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -739 m2 {'strip': 699, 'cells': 40}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: ok: 0/1 hole(s) without a mapped fairway filled from NAIP (d' 1.56; gated: 5)
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole inference fallback: v2+structure: RuntimeError: unmapped and no perception scene: no structure prior
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- hole 2: CHECK, shares hole 9's green
- hole 2: placed by structure inference, golfer check (uncertain (30%): P(number) 52%, P(tee) 71%; long walk from the previous green (394 yds); shares hole 9's green and no unused green fits)
- hole 3: placed by structure inference, golfer check (uncertain (37%): P(number) 72%, P(tee) 70%)
- hole 4: placed by structure inference, golfer check (uncertain (33%): P(number) 45%, P(tee) 93%)
- hole 5: placed by structure inference, golfer check (uncertain (26%): P(number) 72%, P(tee) 41%)
- hole 6: placed by structure inference, golfer check (uncertain (31%): P(number) 74%, P(tee) 52%)
- hole 7: placed by structure inference, golfer check (uncertain (41%): P(number) 74%, P(tee) 78%)
- hole 8: placed by structure inference, golfer check (uncertain (39%): P(number) 58%, P(tee) 94%)
- hole 10: placed by structure inference, golfer check (uncertain (25%): P(number) 41%, P(tee) 63%)
- hole 9 Green: CHECK, tee was put 79 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 9 White: CHECK, tee was put 112 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 9 Combo: CHECK, tee was put 112 yds from this hole's start, at hole 2's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 White: CHECK, tee was put 61 yds from this hole's start, at hole 9's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 2 Combo: CHECK, tee was put 61 yds from this hole's start, at hole 9's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 4 Black: CHECK, walk-back moved the back tee 330 yds up the hole line to fit the card: kept at the line start (card hole may not be this OSM hole)
- hole 4 Green: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 4 White: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 4 Combo: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 4 Rust: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 6 White: CHECK, tee was on a road (OSM 625303705): moved 7 yds forward off it
- hole 2: measured 412 vs card 534 yds for Black (no OSM tee box at that yardage?)
- hole 3: measured 290 vs card 408 yds for Black (no OSM tee box at that yardage?)
- hole 4: measured 538 vs card 208 yds for Black (no OSM tee box at that yardage?)
- hole 6: measured 337 vs card 444 yds for Black (no OSM tee box at that yardage?)
- hole 8: measured 380 vs card 512 yds for Black (no OSM tee box at that yardage?)
- hole 10: measured 299 vs card 408 yds for Black (no OSM tee box at that yardage?)
