# Arrowhead Golf Club (Littleton, CO) - Black Bear tees

Built 2026-10-30T21:55:22Z. OSM way/296786618. Scorecard: golfify (golfify). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 45 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 13 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.361 |
| mean_confidence | 0.815 |
| osm_score | 0.872 |

OSM features inside the course: buildings 2, golf=bunker 66, golf=cartpath 33, golf=fairway 56, golf=green 21, golf=hole 18, golf=pin 18, golf=rough 52, golf=tee 45, golf=water_hazard 8, holes_with_handicap 18, holes_with_par 18, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 465 / 464 | 342 | 0.68 | check the flags | 41% | 11% | 48% | tee stage: Black Bear walkback | tee: tee stage: Black Bear walkback; Black Bear tee walked back along the hole line (no box at 465 yds) |
| 2 | 5 | 566 / 566 | 316 | 0.78 | check the flags | 41% | 8% | 52% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |
| 3 | 3 | 198 / 198 | 30 | 0.86 | auto | 100% | 0% | 0% | tee stage: Black Bear lidar_pad | tee: tee stage: Black Bear lidar_pad; Black Bear tee on a lidar pad (no OSM box at 198 yds) |
| 4 | 4 | 432 / 433 | 105 | 0.65 | check the flags | 34% | 3% | 63% | tee stage: Black Bear walkback | tee: tee stage: Black Bear walkback; Black Bear tee walked back along the hole line (no box at 432 yds) |
| 5 | 4 | 352 / 352 | 282 | 0.77 | check the flags | 19% | 13% | 68% | tee stage: Black Bear tee_centroid |  |
| 6 | 4 | 447 / 447 | 155 | 0.82 | auto | 36% | 16% | 48% | tee stage: Black Bear tee_centroid |  |
| 7 | 4 | 361 / 361 | 328 | 0.74 | check the flags | 28% | 5% | 67% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |
| 8 | 4 | 409 / 409 | 149 | 0.84 | auto | 35% | 29% | 36% | tee stage: Black Bear tee_centroid |  |
| 9 | 3 | 175 / 175 | 170 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black Bear tee_centroid |  |
| 10 | 4 | 420 / 419 | 153 | 0.81 | auto | 39% | 27% | 34% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |
| 11 | 3 | 156 / 156 | 199 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |
| 12 | 4 | 419 / 419 | 224 | 0.78 | check the flags | 30% | 22% | 49% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |
| 13 | 3 | 173 / 173 | 60 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black Bear tee_centroid |  |
| 14 | 4 | 365 / 364 | 346 | 0.82 | auto | 44% | 5% | 51% | tee stage: Black Bear tee_centroid |  |
| 15 | 4 | 409 / 409 | 272 | 0.80 | check the flags | 34% | 27% | 39% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |
| 16 | 5 | 585 / 589 | 349 | 0.69 | check the flags | 36% | 5% | 58% | tee stage: Black Bear lidar_pad | tee: tee stage: Black Bear lidar_pad; Black Bear tee on a lidar pad (no OSM box at 585 yds) |
| 17 | 3 | 202 / 202 | 41 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black Bear tee_centroid |  |
| 18 | 5 | 502 / 501 | 152 | 0.81 | auto | 54% | 5% | 41% | tee stage: Black Bear tee_axis | tee: tee stage: Black Bear tee_axis |

## Stages

- **resolve**: ok: way/296786618 Arrowhead Golf Club (Littleton, CO)
- **osm**: ok: 475 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 40 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/arrowhead/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/arrowhead/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 19 polygons (outside 19); mode replace
