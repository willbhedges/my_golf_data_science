# Brown Deer Golf Club (Coralville, IA) - Gold tees

Built 2026-11-26T07:58:56Z. OSM way/191258543. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 17 |
| holes_mapped | 17 |
| greens_found | 17 |
| tee_boxes | 66 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.483 |
| mean_confidence | 0.84 |
| osm_score | 0.849 |

OSM features inside the course: buildings 5, built_up_landuse 2, golf=bunker 38, golf=cartpath 21, golf=clubhouse 1, golf=driving_range 1, golf=fairway 17, golf=green 19, golf=hole 17, golf=lateral_water_hazard 10, golf=path 1, golf=tee 66, golf=water_hazard 2, holes_with_par 17, trees_polygons 7, water_lines 2, water_polygons 12

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 2 | 5 | 559 / 560 | 299 | 0.83 | auto | 63% | 3% | 34% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 4 | 326 / 324 | 324 | 0.84 | auto | 62% | 9% | 29% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 5 | 513 / 509 | 99 | 0.74 | check the flags | 21% | 15% | 64% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 3 | 182 / 182 | 194 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 4 | 405 / 405 | 138 | 0.81 | auto | 53% | 5% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 4 | 383 / 321 | 165 | 0.77 | check the flags | 20% | 32% | 48% | tee stage: Gold tee_axis_far_cap | tee: tee stage: Gold tee_axis_far_cap; Gold tee out of order with the other sets |
| 8 | 4 | 414 / 283 | 108 | 0.84 | auto | 66% | 2% | 33% | tee stage: Gold tee_axis_far_cap | tee: tee stage: Gold tee_axis_far_cap; Gold tee out of order with the other sets |
| 9 | 3 | 246 / 246 | 166 | 0.86 | auto | 100% | 0% | 0% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 246 yds) |
| 10 | 5 | 480 / 480 | 220 | 0.92 | auto | 97% | 0% | 3% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 357 / 357 | 130 | 0.80 | check the flags | 24% | 40% | 36% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 12 | 3 | 200 / 195 | 310 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 4 | 275 / 276 | 282 | 0.71 | check the flags | 30% | 26% | 44% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 275 yds) |
| 14 | 3 | 120 / 120 | 314 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 15 | 5 | 496 / 496 | 342 | 0.78 | check the flags | 1% | 98% | 2% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 496 yds) |
| 16 | 4 | 459 / 454 | 144 | 0.75 | check the flags | 51% | 14% | 34% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 459 yds) |
| 17 | 3 | 178 / 176 | 95 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 18 | 4 | 393 / 397 | 61 | 0.91 | auto | 93% | 0% | 7% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone |

## Stages

- **resolve**: ok: way/191258543 Brown Deer Golf Club (Coralville, IA)
- **osm**: ok: 526 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 17/18 holes OSM has no way for (6 to check; segment no, lidar pads 370, perception scene no)
- **green_overrides**: ok: hole 1: green override but no hole line and no review tee (not applied)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 57 candidate pads near hole starts (31 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (17 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/brown_deer/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/brown_deer/imagery/dem.tif (17/17 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -5 m2 {'cells': 5}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: gated: mown / rough separation d' 0.36 < 1.0 (seeds 11784, rough 40940); no fairway filled
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 32 polygons (property_line 32); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red
- hole 2: placed by v2+structure inference, golfer check (ambiguous (76% of the posterior))
- hole 7: placed by v2+structure inference, golfer check (ambiguous (75% of the posterior))
- hole 8: placed by v2+structure inference, golfer check (ambiguous (25% of the posterior))
- hole 9: placed by v2+structure inference, golfer check (ambiguous (59% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (67% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (85% of the posterior))
- hole 2 Red: CHECK, tee was put 176 yds from this hole's start, at hole 7's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 15 Blue: CHECK, tee was on a road (OSM 15946659): moved 11 yds forward off it
- hole 7: measured 321 vs card 383 yds for Gold (no OSM tee box at that yardage?)
- hole 8: measured 283 vs card 414 yds for Gold (no OSM tee box at that yardage?)
- no fairway mapped on 3 hole(s) and the NAIP fairway fill did not run: gated: mown / rough separation d' 0.36 < 1.0 (seeds 11784, rough 40940); no fairway filled
