# South River Golf Course (Edgewater, MD) - Green tees

Built 2026-11-03T15:03:41Z. OSM way/61239088. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Green, Blue, Gold, Gold (L), White, White (L), Red (L))).

**WARNING: requested tee set 'Black' is not on the card; using 'Green' instead (allow_substitute). Sets on the card: Green, Blue, Gold, Gold (L), White, White (L), Red (L)**

## Coverage

| | |
|---|---|
| holes_built | 9 |
| holes_mapped | 9 |
| greens_found | 9 |
| tee_boxes | 22 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 6 |
| of_par4_5 | 6 |
| mean_landing_osm_share | 0.13 |
| mean_confidence | 0.801 |
| osm_score | 0.826 |

OSM features inside the course: buildings 2, golf=bunker 18, golf=fairway 7, golf=green 7, golf=hole 9, golf=lateral_water_hazard 3, golf=path 6, golf=pin 3, golf=tee 22, holes_with_par 9, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 416 / 415 | 15 | 0.63 | check the flags | 1% | 39% | 60% | tee stage: Green walkback | tee: tee stage: Green walkback; Green tee walked back along the hole line (no box at 416 yds) |
| 2 | 4 | 455 / 455 | 325 | 0.83 | auto | 34% | 23% | 43% | tee stage: Green tee_centroid |  |
| 3 | 3 | 184 / 184 | 78 | 0.93 | auto | 100% | 0% | 0% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 4 | 5 | 550 / 545 | 136 | 0.82 | auto | 15% | 63% | 22% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 5 | 4 | 376 / 375 | 199 | 0.72 | check the flags | 0% | 89% | 11% | tee stage: Green walkback | tee: tee stage: Green walkback; no fairway in the landing zone; Green tee walked back along the hole line (no box at 376 yds) |
| 6 | 3 | 178 / 178 | 311 | 0.96 | auto | 100% | 0% | 0% | tee stage: Green tee_centroid |  |
| 7 | 5 | 534 / 530 | 270 | 0.81 | auto | 22% | 51% | 27% | tee stage: Green tee_axis | tee: tee stage: Green tee_axis |
| 8 | 3 | 206 / 323 | 82 | 0.82 | auto | 100% | 0% | 0% | tee stage: Green walkback_capped | tee: tee stage: Green walkback_capped; Green tee walked back along the hole line (no box at 206 yds) |
| 9 | 5 | 567 / 345 | 15 | 0.68 | check the flags | 5% | 62% | 32% | tee stage: Green walkback_capped | tee: tee stage: Green walkback_capped; Green tee walked back along the hole line (no box at 567 yds) |

## Stages

- **resolve**: ok: way/61239088 South River Golf Course (Edgewater, MD)
- **osm**: ok: 215 features
- **routing**: ok: structure (unmapped_card, structure on osm) placed 9/18 holes OSM has no way for (9 to check; segment no, lidar pads 139, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 39 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (9 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/queenstown_harbor/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 9/9 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/queenstown_harbor/imagery/dem.tif (9/9 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: gated: mown / rough separation d' 0.47 < 1.0 (seeds 9730, rough 31424); no fairway filled
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 21 polygons (outside 21); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Green' instead (allow_substitute). Sets on the card: Green, Blue, Gold, Gold (L), White, White (L), Red (L)
- hole inference fallback: v2+structure: RuntimeError: unmapped and no perception scene: no structure prior
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- hole 1: placed by structure inference, golfer check (uncertain (39%): P(number) 100%, P(tee) 53%)
- hole 2: placed by structure inference, golfer check (uncertain (49%): P(number) 79%, P(tee) 89%)
- hole 3: placed by structure inference, golfer check (uncertain (45%): P(number) 79%, P(tee) 82%)
- hole 4: placed by structure inference, golfer check (uncertain (40%): P(number) 79%, P(tee) 71%; long walk from the previous green (287 yds))
- hole 5: placed by structure inference, golfer check (uncertain (53%): P(number) 79%, P(tee) 97%)
- hole 6: placed by structure inference, golfer check (uncertain (55%): P(number) 79%, P(tee) 100%)
- hole 7: placed by structure inference, golfer check (uncertain (34%): P(number) 58%, P(tee) 77%)
- hole 8: placed by structure inference, golfer check (uncertain (35%): P(number) 79%, P(tee) 59%)
- hole 9: placed by structure inference, golfer check (uncertain (41%): P(number) 58%, P(tee) 100%)
- hole 8 Green: CHECK, walk-back moved the back tee 117 yds up the hole line to fit the card: kept at the line start (card hole may not be this OSM hole)
- hole 8 Blue: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 8 Gold: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 8 Gold (L): CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 8 White: CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 8 White (L): CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 8 Red (L): CHECK, the hole's back tee was walked up the hole line: card hole may not be this OSM hole
- hole 9 Green: CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (222 yds short of the card)
- hole 9 Blue: CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (194 yds short of the card)
- hole 9 Gold: CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (175 yds short of the card)
- hole 9 Gold (L): CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (175 yds short of the card)
- hole 9 White: CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (40 yds short of the card)
- hole 9 White (L): CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (40 yds short of the card)
- hole 9 Red (L): CHECK, walk-back ran onto a building (OSM 436476837) 178 yds behind the line start: capped there (40 yds short of the card)
- hole 8: measured 323 vs card 206 yds for Green (no OSM tee box at that yardage?)
- hole 9: measured 345 vs card 567 yds for Green (no OSM tee box at that yardage?)
