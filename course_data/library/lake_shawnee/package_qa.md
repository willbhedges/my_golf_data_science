# Lake Shawnee Golf Course (Topeka, KS) - Blue tees

Built 2026-10-30T03:59:28Z. OSM relation/2053245. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red, Gold)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red, Gold**

## Coverage

| | |
|---|---|
| holes_built | 4 |
| holes_mapped | 4 |
| greens_found | 4 |
| tee_boxes | 13 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 3 |
| of_par4_5 | 3 |
| mean_landing_osm_share | 0.29 |
| mean_confidence | 0.738 |
| osm_score | 0.719 |

OSM features inside the course: buildings 4, golf=bunker 4, golf=cartpath 14, golf=clubhouse 1, golf=fairway 5, golf=green 4, golf=hole 4, golf=tee 13, holes_with_par 4, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 348 / 362 | 39 | 0.75 | check the flags | 29% | 9% | 62% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 369 / 369 | 190 | 0.67 | check the flags | 28% | 7% | 64% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 369 yds) |
| 3 | 4 | 353 / 352 | 220 | 0.70 | check the flags | 30% | 20% | 50% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 353 yds) |
| 4 | 3 | 148 / 148 | 216 | 0.82 | auto | 100% | 0% | 0% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 148 yds) |

## Stages

- **resolve**: ok: relation/2053245 Lake Shawnee Golf Course (Shawnee County, KS)
- **osm**: ok: 452 features
- **routing**: ok: structure (unmapped_card, structure on osm) placed 4/18 holes OSM has no way for (4 to check; segment no, lidar pads 181, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 17 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (4 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/lake_shawnee/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 4/4 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/lake_shawnee/imagery/dem.tif (4/4 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red, Gold
- hole inference fallback: v2+structure: RuntimeError: unmapped and no perception scene: no structure prior
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- hole 1: placed by structure inference, golfer check (uncertain (52%): P(number) 88%, P(tee) 85%)
- hole 2: placed by structure inference, golfer check (uncertain (36%): P(number) 88%, P(tee) 56%)
- hole 3: placed by structure inference, golfer check (uncertain (64%): P(number) 88%, P(tee) 100%)
- hole 4: placed by structure inference, golfer check (uncertain (34%): P(number) 88%, P(tee) 51%)
