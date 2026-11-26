# Kokopelli Golf Club (Marion, IL) - Black tees

Built 2026-11-26T07:48:06Z. OSM way/759870279. Scorecard: allsquare (allsquare). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 60 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.527 |
| mean_confidence | 0.841 |
| osm_score | 0.891 |

OSM features inside the course: buildings 2, golf=bunker 78, golf=cartpath 21, golf=clubhouse 1, golf=driving_range 1, golf=fairway 20, golf=green 19, golf=hole 18, golf=tee 60, golf=water_hazard 1, holes_with_par 18, single_trees 41, water_lines 3, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 407 / 408 | 83 | 0.78 | check the flags | 46% | 0% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 318 / 318 | 50 | 0.81 | auto | 50% | 9% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 211 / 211 | 230 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 4 | 426 / 422 | 282 | 0.81 | auto | 49% | 14% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 146 / 146 | 207 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 426 / 427 | 269 | 0.81 | auto | 44% | 16% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 452 / 453 | 83 | 0.89 | auto | 84% | 0% | 15% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 459 / 460 | 263 | 0.80 | check the flags | 47% | 8% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 5 | 540 / 536 | 77 | 0.82 | auto | 54% | 9% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 409 / 410 | 69 | 0.83 | auto | 60% | 9% | 31% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 437 / 438 | 290 | 0.82 | auto | 48% | 19% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 5 | 559 / 554 | 74 | 0.84 | auto | 64% | 7% | 29% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 420 / 419 | 192 | 0.86 | auto | 52% | 13% | 35% | tee stage: Black tee_centroid |  |
| 14 | 3 | 184 / 184 | 275 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 472 / 473 | 96 | 0.77 | check the flags | 43% | 0% | 57% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 4 | 444 / 442 | 234 | 0.77 | check the flags | 44% | 0% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 204 / 204 | 24 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 525 / 526 | 221 | 0.80 | check the flags | 54% | 0% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/759870279 Kokopelli Golf Club (Marion, IL)
- **osm**: ok: 494 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 54 candidate pads near hole starts (13 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/kokopelli/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/kokopelli/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -435 m2 {'cells': 388}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 13 polygons (outside 13); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- card consensus: golfify: fits the OSM ground on only 38% of hole/set values (best card 80%): stale or scrambled card
- hole 11 Red: CHECK, tee was put 160 yds from this hole's start, at hole 15's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
