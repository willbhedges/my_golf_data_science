# Keller Golf Course (Maplewood, MN) - Black tees

Built 2026-11-26T12:21:54Z. OSM none/0. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 56 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.513 |
| mean_confidence | 0.85 |
| osm_score | 0.903 |

OSM features inside the course: buildings 137, built_up_landuse 1, golf=bunker 55, golf=cartpath 26, golf=driving_range 1, golf=fairway 17, golf=green 19, golf=hole 18, golf=pin 18, golf=rough 3, golf=tee 56, golf=water_hazard 4, holes_with_handicap 18, holes_with_par 18, long_grass_polygons 2, single_trees 576, trees_polygons 11, water_lines 4, water_polygons 36

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 332 / 332 | 150 | 0.81 | auto | 41% | 6% | 54% | tee stage: Black tee_centroid |  |
| 2 | 4 | 393 / 393 | 153 | 0.87 | auto | 64% | 5% | 31% | tee stage: Black tee_centroid |  |
| 3 | 5 | 502 / 503 | 266 | 0.82 | auto | 51% | 15% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 150 / 150 | 264 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 371 / 372 | 68 | 0.79 | check the flags | 43% | 10% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 3 | 223 / 224 | 281 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 420 / 421 | 107 | 0.82 | auto | 46% | 4% | 50% | tee stage: Black tee_centroid |  |
| 8 | 4 | 385 / 386 | 298 | 0.82 | auto | 47% | 19% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 400 / 400 | 321 | 0.84 | auto | 52% | 6% | 42% | tee stage: Black tee_centroid |  |
| 10 | 5 | 503 / 503 | 146 | 0.87 | auto | 56% | 13% | 31% | tee stage: Black tee_centroid |  |
| 11 | 4 | 382 / 382 | 320 | 0.79 | check the flags | 43% | 10% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 5 | 519 / 519 | 211 | 0.82 | auto | 56% | 10% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 3 | 148 / 148 | 66 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 378 / 378 | 214 | 0.83 | auto | 58% | 9% | 33% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 3 | 195 / 195 | 86 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 5 | 557 / 557 | 43 | 0.82 | auto | 52% | 12% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 376 / 376 | 195 | 0.82 | auto | 58% | 2% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 441 / 441 | 13 | 0.84 | auto | 52% | 5% | 43% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: none/0 Keller Golf Course (Maplewood, MN)
- **osm**: ok: 1557 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 45 candidate pads near hole starts (5 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/keller/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/keller/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace
- **native_auto**: none: no S2 native P for this course (vision_any/s2/<slug>/s2_stack.npz)

## Warnings

- hole 3 White: CHECK, tee was put 88 yds from this hole's start, at hole 8's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 16 Blue: CHECK, tee was put 61 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 16 White: CHECK, tee was put 155 yds from this hole's start, at hole 5's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
