# Ironhorse Golf Club (Leawood, KS) - Black tees

Built 2026-11-26T20:25:22Z. OSM way/237531758. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 20 |
| greens_found | 18 |
| tee_boxes | 94 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.437 |
| mean_confidence | 0.848 |
| osm_score | 0.887 |

OSM features inside the course: buildings 4, golf=bunker 48, golf=cartpath 61, golf=clubhouse 1, golf=driving_range 7, golf=fairway 26, golf=green 23, golf=hole 20, golf=lateral_water_hazard 1, golf=pin 18, golf=rough 2, golf=tee 94, golf=water_hazard 1, holes_with_par 18, tees_with_ref 89, trees_polygons 12, water_lines 11, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 374 / 413 | 58 | 0.68 | check the flags | 57% | 3% | 40% | tee stage: Black review | tee: tee stage: Black review |
| 2 | 3 | 211 / 211 | 237 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 4 | 425 / 425 | 49 | 0.84 | auto | 51% | 21% | 27% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 5 | 518 / 519 | 87 | 0.84 | auto | 42% | 18% | 39% | tee stage: Black tee_centroid |  |
| 5 | 3 | 212 / 210 | 70 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 405 / 406 | 276 | 0.82 | auto | 45% | 22% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 340 / 341 | 109 | 0.78 | check the flags | 32% | 22% | 47% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 408 / 409 | 277 | 0.82 | auto | 41% | 28% | 32% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 5 | 555 / 555 | 246 | 0.88 | auto | 56% | 17% | 27% | tee stage: Black tee_centroid |  |
| 10 | 5 | 555 / 555 | 293 | 0.83 | auto | 43% | 31% | 26% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 4 | 371 / 312 | 182 | 0.81 | auto | 42% | 22% | 36% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap |
| 12 | 3 | 190 / 190 | 300 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 387 / 381 | 4 | 0.82 | auto | 41% | 29% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 481 / 482 | 284 | 0.86 | auto | 44% | 26% | 31% | tee stage: Black tee_centroid |  |
| 15 | 4 | 372 / 372 | 130 | 0.85 | auto | 27% | 46% | 27% | tee stage: Black tee_centroid |  |
| 16 | 4 | 380 / 379 | 339 | 0.84 | auto | 44% | 35% | 22% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 199 / 199 | 165 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 475 / 471 | 105 | 0.84 | auto | 49% | 26% | 25% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/237531758 Ironhorse Golf Club (Leawood, KS)
- **osm**: ok: 1522 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 1/1 holes OSM has no way for (0 to check; segment no, lidar pads 561, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 1 review;
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 94 candidate pads near hole starts (19 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/ironhorse/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/ironhorse/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 32 polygons (outside 32); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- ignored 3 practice / driving-range tee box(es): OSM 837929723, 837929724, -1
- hole 7 Red: CHECK, tee was put 121 yds from this hole's start, at hole 8's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Gold: CHECK, tee was put 81 yds from this hole's start, at hole 13's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 12 Red: CHECK, tee was put 104 yds from this hole's start, at hole 13's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 16 White: CHECK, tee was put 92 yds from this hole's start, at hole 14's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 16 Gold: CHECK, tee was put 124 yds from this hole's start, at hole 14's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 16 Red: CHECK, tee was put 124 yds from this hole's start, at hole 14's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 White: CHECK, tee was put 76 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 18 Gold: CHECK, tee was put 78 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 1: measured 413 vs card 374 yds for Black (no OSM tee box at that yardage?)
- hole 11: measured 312 vs card 371 yds for Black (no OSM tee box at that yardage?)
