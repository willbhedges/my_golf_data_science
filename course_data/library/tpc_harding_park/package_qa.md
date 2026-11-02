# TPC Harding Park (San Francisco, CA) - Championship tees

Built 2026-11-01T22:24:32Z. OSM way/16753068. Scorecard: allsquare (allsquare). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 27 |
| greens_found | 18 |
| tee_boxes | 101 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.436 |
| mean_confidence | 0.803 |
| osm_score | 0.887 |

OSM features inside the course: buildings 3, golf=bunker 60, golf=cartpath 65, golf=driving_range 2, golf=fairway 28, golf=green 44, golf=hole 27, golf=pin 27, golf=tee 101, holes_with_handicap 25, holes_with_par 27, single_trees 1059, tees_with_ref 20, trees_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 396 | 96 | 0.85 | auto | 63% | 12% | 25% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 2 | 4 | 449 / 181 | 133 | 0.60 | needs review | 16% | 4% | 80% | tee stage: Championship walkback_capped | tee: tee stage: Championship walkback_capped; no fairway in the landing zone; Championship tee walked back along the hole line (no box at 449 yds) |
| 3 | 3 | 183 / 186 | 208 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 4 | 5 | 606 / 605 | 30 | 0.72 | check the flags | 53% | 14% | 33% | tee stage: Championship walkback | tee: tee stage: Championship walkback; Championship tee walked back along the hole line (no box at 606 yds) |
| 5 | 4 | 429 / 303 | 239 | 0.68 | check the flags | 42% | 6% | 52% | tee stage: Championship walkback_capped | tee: tee stage: Championship walkback_capped; Championship tee walked back along the hole line (no box at 429 yds) |
| 6 | 4 | 473 / 370 | 277 | 0.65 | check the flags | 23% | 19% | 58% | tee stage: Championship walkback_capped | tee: tee stage: Championship walkback_capped; Championship tee walked back along the hole line (no box at 473 yds) |
| 7 | 4 | 344 / 344 | 65 | 0.85 | auto | 44% | 22% | 34% | tee stage: Championship tee_centroid |  |
| 8 | 3 | 230 / 230 | 249 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 9 | 5 | 525 / 525 | 302 | 0.72 | check the flags | 52% | 15% | 32% | tee stage: Championship walkback | tee: tee stage: Championship walkback; Championship tee walked back along the hole line (no box at 525 yds) |
| 10 | 5 | 562 / 563 | 85 | 0.81 | auto | 50% | 11% | 39% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 11 | 3 | 200 / 200 | 126 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 12 | 5 | 494 / 493 | 195 | 0.69 | check the flags | 36% | 23% | 42% | tee stage: Championship walkback | tee: tee stage: Championship walkback; Championship tee walked back along the hole line (no box at 494 yds) |
| 13 | 4 | 428 / 427 | 202 | 0.81 | auto | 45% | 16% | 39% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 14 | 4 | 467 / 467 | 317 | 0.83 | auto | 45% | 11% | 44% | tee stage: Championship tee_centroid |  |
| 15 | 4 | 405 / 405 | 320 | 0.80 | check the flags | 41% | 15% | 44% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 16 | 4 | 336 / 336 | 294 | 0.81 | auto | 40% | 23% | 38% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 17 | 3 | 175 / 174 | 321 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 18 | 4 | 468 / 469 | 92 | 0.88 | auto | 61% | 11% | 28% | tee stage: Championship tee_centroid |  |

## Stages

- **resolve**: ok: way/16753068 TPC Harding Park (San Francisco, CA)
- **osm**: ok: 2372 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 1/1 holes OSM has no way for (1 to check; segment no, lidar pads 156, perception scene no)
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 52 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/tpc_harding_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/tpc_harding_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- ignored 1 golf=hole way(s) of a neighbouring course (outside this course's boundary): OSM 685545912
- hole 18: placed by v2+structure inference, golfer check (ambiguous (41% of the posterior))
- hole 2 Championship: CHECK, walk-back ran onto a green (OSM 854304741) 42 yds behind the line start: capped there (269 yds short of the card)
- hole 2 Blue: CHECK, walk-back ran onto a green (OSM 854304741) 42 yds behind the line start: capped there (250 yds short of the card)
- hole 2 White: CHECK, walk-back ran onto a green (OSM 854304741) 42 yds behind the line start: capped there (220 yds short of the card)
- hole 2 Red: CHECK, walk-back ran onto a green (OSM 854304741) 42 yds behind the line start: capped there (180 yds short of the card)
- hole 5 Championship: CHECK, walk-back ran onto a green (OSM 858007613) 80 yds behind the line start: capped there (126 yds short of the card)
- hole 5 Blue: CHECK, walk-back ran onto a green (OSM 858007613) 80 yds behind the line start: capped there (92 yds short of the card)
- hole 6 Championship: CHECK, walk-back ran onto a green (OSM 858007607) 170 yds behind the line start: capped there (104 yds short of the card)
- hole 6 Blue: CHECK, walk-back ran onto a green (OSM 858007607) 170 yds behind the line start: capped there (71 yds short of the card)
- hole 6 White: CHECK, walk-back ran onto a green (OSM 858007607) 170 yds behind the line start: capped there (21 yds short of the card)
- hole 2: measured 181 vs card 449 yds for Championship (no OSM tee box at that yardage?)
- hole 5: measured 303 vs card 429 yds for Championship (no OSM tee box at that yardage?)
- hole 6: measured 370 vs card 473 yds for Championship (no OSM tee box at that yardage?)
