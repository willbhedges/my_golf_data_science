# Dub's Dread Golf Club (Kansas City, KS) - Championship tees

Built 2026-11-03T15:02:38Z. OSM way/505160823. Scorecard: file (course_data/library/dubs_dread/card_golfify.json). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 19 |
| greens_found | 18 |
| tee_boxes | 69 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.315 |
| mean_confidence | 0.791 |
| osm_score | 0.863 |

OSM features inside the course: buildings 3, golf=bunker 12, golf=fairway 20, golf=green 19, golf=hole 19, golf=path 13, golf=pin 18, golf=tee 69, golf=water_hazard 8, holes_with_par 19, trees_polygons 2, water_lines 9, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 515 / 516 | 247 | 0.84 | auto | 31% | 32% | 37% | tee stage: Championship tee_centroid |  |
| 2 | 4 | 410 / 408 | 174 | 0.80 | check the flags | 50% | 4% | 47% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 3 | 4 | 446 / 441 | 174 | 0.77 | check the flags | 42% | 4% | 55% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 4 | 3 | 216 / 218 | 352 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Championship review (inside OSM tee 505295054) | tee: tee stage: Championship review (inside OSM tee 505295054) |
| 5 | 4 | 382 / 377 | 355 | 0.63 | check the flags | 27% | 22% | 51% | tee stage: Championship review (inside OSM tee 505295061) | tee: tee stage: Championship review (inside OSM tee 505295061) |
| 6 | 4 | 467 / 468 | 108 | 0.79 | check the flags | 20% | 23% | 57% | tee stage: Championship tee_centroid |  |
| 7 | 5 | 550 / 550 | 198 | 0.78 | check the flags | 28% | 7% | 64% | tee stage: Championship tee_centroid |  |
| 8 | 3 | 210 / 210 | 68 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 9 | 4 | 418 / 397 | 360 | 0.62 | check the flags | 30% | 14% | 56% | tee stage: Championship review (inside OSM tee 505304285) | tee: tee stage: Championship review (inside OSM tee 505304285) |
| 10 | 4 | 362 / 363 | 97 | 0.78 | check the flags | 27% | 24% | 48% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 11 | 3 | 234 / 235 | 99 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 12 | 5 | 547 / 547 | 259 | 0.75 | check the flags | 33% | 4% | 62% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 13 | 4 | 420 / 421 | 107 | 0.74 | check the flags | 38% | 26% | 36% | tee stage: Championship lidar_pad | tee: tee stage: Championship lidar_pad; Championship tee on a lidar pad (no OSM box at 420 yds) |
| 14 | 4 | 444 / 445 | 278 | 0.79 | check the flags | 29% | 10% | 62% | tee stage: Championship tee_centroid |  |
| 15 | 4 | 409 / 409 | 315 | 0.76 | check the flags | 33% | 9% | 58% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 16 | 3 | 212 / 212 | 242 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 17 | 5 | 555 / 557 | 38 | 0.75 | check the flags | 27% | 14% | 59% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 18 | 4 | 433 / 432 | 15 | 0.81 | auto | 25% | 26% | 49% | tee stage: Championship tee_centroid |  |

## Stages

- **resolve**: ok: way/505160823 Dub's Dread Golf Club (Kansas City, KS)
- **osm**: ok: 280 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/dubs_dread/card_golfify.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Championship 4 review (inside OSM tee 505295054), 5 review (inside OSM tee 505295061), 9 review (inside OSM tee 505304285);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 47 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/dubs_dread/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/dubs_dread/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- hole 9: measured 397 vs card 418 yds for Championship (no OSM tee box at that yardage?)
