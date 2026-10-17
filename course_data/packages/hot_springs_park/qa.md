# Hot Springs Country Club Park Course (Hot Springs, AR) - Gold tees

Built 2026-10-17T17:42:29Z. OSM none/0. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 11 |
| holes_mapped | 11 |
| greens_found | 11 |
| tee_boxes | 17 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 0 |
| of_par4_5 | 8 |
| mean_landing_osm_share | 0.059 |
| mean_confidence | 0.672 |
| osm_score | 0.392 |

OSM features inside the course: golf=bunker 25, golf=green 9, golf=hole 11, golf=tee 17, golf=water_hazard 1, holes_with_par 11, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 517 / 518 | 292 | 0.55 | needs review | 2% | 0% | 98% | tee stage: Gold walkback | tee: tee stage: Gold walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Gold tee walked back along the hole line (no box at 517 yds) |
| 2 | 4 | 440 / 440 | 114 | 0.51 | needs review | 0% | 0% | 100% | tee stage: Gold texture_pad | tee: tee stage: Gold texture_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Gold tee on an imagery-detected pad (texture; no OSM box at 440 yds) |
| 3 | 3 | 196 / 196 | 120 | 0.82 | auto | 100% | 0% | 0% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 196 yds) |
| 4 | 4 | 363 / 363 | 296 | 0.58 | needs review | 12% | 0% | 88% | tee stage: Gold walkback | tee: tee stage: Gold walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Gold tee walked back along the hole line (no box at 363 yds) |
| 5 | 5 | 509 / 500 | 174 | 0.69 | check the flags | 15% | 0% | 85% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 6 | 4 | 396 / 395 | 149 | 0.55 | needs review | 0% | 0% | 100% | tee stage: Gold walkback | tee: tee stage: Gold walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Gold tee walked back along the hole line (no box at 396 yds) |
| 7 | 3 | 199 / 199 | 51 | 0.82 | auto | 100% | 0% | 0% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 199 yds) |
| 8 | 4 | 405 / 405 | 250 | 0.69 | check the flags | 0% | 0% | 100% | tee stage: Gold tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 9 | 4 | 409 / 412 | 236 | 0.68 | check the flags | 12% | 0% | 88% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |
| 10 | 3 | 204 / 204 | 41 | 0.82 | auto | 100% | 0% | 0% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 204 yds) |
| 11 | 4 | 412 / 413 | 65 | 0.67 | check the flags | 6% | 0% | 94% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: none/0 Hot Springs Country Club Park Course (Hot Springs, AR)
- **osm**: ok: 186 features
- **routing**: ok: structure (unmapped_card, structure on osm) placed 11/18 holes OSM has no way for (11 to check; segment no, lidar pads 245, perception scene no)
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 34 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (11 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/hot_springs_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 11/11 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/hot_springs_park/imagery/dem.tif (11/11 holes)
- **vision**: missing: no vision_any layers for 'hot_springs_park' (FileNotFoundError: course_data/vision_any/hot_springs_park/raw (not fetched)); add the course to course_data/vision_any/courses.txt so .github/workflows/vision_any.yml fetches and builds them
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_data/requests/ob_*.json

## Warnings

- hole inference fallback: v2+structure: RuntimeError: unmapped and no perception scene: no structure prior
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- hole 1: placed by structure inference, golfer check (uncertain (25%): P(number) 46%, P(tee) 57%)
- hole 2: placed by structure inference, golfer check (uncertain (39%): P(number) 53%, P(tee) 100%)
- hole 3: placed by structure inference, golfer check (uncertain (38%): P(number) 53%, P(tee) 100%)
- hole 4: placed by structure inference, golfer check (uncertain (31%): P(number) 38%, P(tee) 100%)
- hole 5: placed by structure inference, golfer check (uncertain (35%): P(number) 50%, P(tee) 93%)
- hole 6: placed by structure inference, golfer check (uncertain (24%): P(number) 44%, P(tee) 57%)
- hole 7: placed by structure inference, golfer check (uncertain (34%): P(number) 44%, P(tee) 100%)
- hole 8: placed by structure inference, golfer check (uncertain (39%): P(number) 60%, P(tee) 91%)
- hole 9: placed by structure inference, golfer check (uncertain (43%): P(number) 79%, P(tee) 77%)
- hole 10: placed by structure inference, golfer check (uncertain (57%): P(number) 81%, P(tee) 100%)
- hole 11: placed by structure inference, golfer check (uncertain (44%): P(number) 74%, P(tee) 84%)
- vision: missing: no vision_any layers for 'hot_springs_park' (FileNotFoundError: course_data/vision_any/hot_springs_park/raw (not fetched)); add the course to course_da; trees / long grass come from OSM only
