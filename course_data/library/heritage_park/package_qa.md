# Heritage Park Golf Course (Olathe, KS) - Blue tees

Built 2026-10-30T03:44:17Z. OSM way/254360563. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Silver, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Silver, Red**

## Coverage

| | |
|---|---|
| holes_built | 16 |
| holes_mapped | 16 |
| greens_found | 16 |
| tee_boxes | 67 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.36 |
| mean_confidence | 0.796 |
| osm_score | 0.811 |

OSM features inside the course: buildings 4, built_up_landuse 1, golf=bunker 16, golf=cartpath 24, golf=driving_range 1, golf=fairway 23, golf=green 21, golf=hole 16, golf=rough 1, golf=tee 67, golf=water_hazard 3, holes_with_par 16, trees_polygons 1, water_lines 3, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 3 | 193 / 193 | 164 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 359 / 360 | 113 | 0.80 | auto | 35% | 9% | 56% | tee stage: Blue tee_centroid |  |
| 4 | 3 | 184 / 184 | 237 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 5 | 629 / 628 | 335 | 0.68 | check the flags | 34% | 2% | 64% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 629 yds) |
| 6 | 3 | 187 / 187 | 44 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 7 | 4 | 433 / 433 | 73 | 0.69 | check the flags | 36% | 4% | 60% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 433 yds) |
| 8 | 4 | 373 / 373 | 238 | 0.86 | auto | 65% | 12% | 23% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 5 | 517 / 519 | 342 | 0.66 | check the flags | 26% | 4% | 70% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 517 yds) |
| 10 | 4 | 396 / 388 | 178 | 0.75 | check the flags | 26% | 14% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 395 / 394 | 165 | 0.65 | check the flags | 28% | 11% | 61% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 395 yds) |
| 13 | 4 | 409 / 409 | 33 | 0.77 | check the flags | 40% | 6% | 54% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 465 / 464 | 343 | 0.84 | auto | 31% | 35% | 34% | tee stage: Blue tee_centroid |  |
| 15 | 5 | 599 / 595 | 165 | 0.78 | check the flags | 41% | 9% | 50% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 3 | 215 / 215 | 346 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 17 | 4 | 388 / 387 | 355 | 0.79 | check the flags | 36% | 0% | 64% | tee stage: Blue tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 5 | 539 / 538 | 182 | 0.64 | check the flags | 35% | 0% | 65% | tee stage: Blue walkback | tee: tee stage: Blue walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Blue tee walked back along the hole line (no box at 539 yds) |

## Stages

- **resolve**: ok: way/254360563 Heritage Park Golf Course (Johnson County, KS)
- **osm**: ok: 483 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 16/18 holes OSM has no way for (6 to check; segment no, lidar pads 224, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 66 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (16 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/heritage_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 16/16 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/heritage_park/imagery/dem.tif (16/16 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Silver, Red
- hole 2: placed by v2+structure inference, golfer check (ambiguous (60% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (62% of the posterior))
- hole 13: placed by v2+structure inference, golfer check (ambiguous (92% of the posterior))
- hole 15: placed by v2+structure inference, golfer check (ambiguous (73% of the posterior))
- hole 16: placed by v2+structure inference, golfer check (ambiguous (73% of the posterior))
- hole 17: placed by v2+structure inference, golfer check (ambiguous (74% of the posterior))
