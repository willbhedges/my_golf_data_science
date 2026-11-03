# TPC Harding Park (San Francisco, CA) - Championship tees

Built 2026-11-03T05:53:13Z. OSM way/16753068. Scorecard: allsquare (allsquare). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 101 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.431 |
| mean_confidence | 0.823 |
| osm_score | 0.886 |

OSM features inside the course: buildings 3, golf=bunker 60, golf=cartpath 65, golf=driving_range 2, golf=fairway 28, golf=green 44, golf=hole 18, golf=pin 27, golf=tee 101, holes_with_handicap 18, holes_with_par 18, single_trees 1059, tees_with_ref 20, trees_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 395 / 395 | 144 | 0.84 | auto | 50% | 22% | 27% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 2 | 4 | 449 / 449 | 142 | 0.78 | check the flags | 41% | 8% | 51% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 3 | 3 | 183 / 183 | 160 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 4 | 5 | 606 / 605 | 26 | 0.82 | auto | 40% | 12% | 48% | tee stage: Championship tee_centroid |  |
| 5 | 4 | 429 / 428 | 184 | 0.69 | check the flags | 42% | 16% | 42% | tee stage: Championship walkback | tee: tee stage: Championship walkback; Championship tee walked back along the hole line (no box at 429 yds) |
| 6 | 4 | 473 / 473 | 341 | 0.81 | auto | 46% | 14% | 39% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 7 | 4 | 344 / 344 | 147 | 0.79 | check the flags | 45% | 8% | 47% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 8 | 3 | 230 / 230 | 317 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 9 | 5 | 525 / 526 | 322 | 0.78 | check the flags | 41% | 7% | 53% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 10 | 5 | 562 / 561 | 93 | 0.81 | auto | 49% | 11% | 40% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 11 | 3 | 200 / 200 | 126 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 12 | 5 | 494 / 493 | 195 | 0.69 | check the flags | 36% | 23% | 42% | tee stage: Championship walkback | tee: tee stage: Championship walkback; Championship tee walked back along the hole line (no box at 494 yds) |
| 13 | 4 | 428 / 427 | 202 | 0.81 | auto | 45% | 16% | 39% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 14 | 4 | 467 / 467 | 317 | 0.83 | auto | 45% | 11% | 44% | tee stage: Championship tee_centroid |  |
| 15 | 4 | 405 / 405 | 320 | 0.80 | check the flags | 41% | 15% | 44% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 16 | 4 | 336 / 336 | 294 | 0.81 | auto | 40% | 23% | 38% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 17 | 3 | 175 / 174 | 321 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 18 | 4 | 468 / 468 | 100 | 0.81 | auto | 44% | 2% | 54% | tee stage: Championship tee_centroid |  |

## Stages

- **resolve**: ok: way/16753068 TPC Harding Park (San Francisco, CA)
- **osm**: ok: 2372 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 53 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/tpc_harding_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/tpc_harding_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- multi-course facility: 2 courses' hole ways in one outline (by hole chains (green -> next tee): #1 18, fleming 9); kept the largest group (no name or near point decides: CHECK the course), 18 ways; ignored 9
