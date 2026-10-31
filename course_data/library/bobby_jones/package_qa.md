# Bobby Jones Golf Club (Atlanta, GA) - 8 tees

Built 2026-10-30T22:17:00Z. OSM way/29354026. Scorecard: allsquare (allsquare). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 9 |
| holes_mapped | 18 |
| greens_found | 9 |
| tee_boxes | 0 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 6 |
| of_par4_5 | 7 |
| mean_landing_osm_share | 0.715 |
| mean_confidence | 0.784 |
| osm_score | 0.814 |

OSM features inside the course: buildings 5, built_up_landuse 1, golf=bunker 22, golf=cartpath 20, golf=fairway 13, golf=green 16, golf=hole 18, golf=path 1, golf=rough 4, golf=water_hazard 1, holes_with_handicap 1, holes_with_par 18, water_lines 1, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 616 / 617 | 124 | 0.76 | check the flags | 74% | 6% | 21% | tee stage: 8 walkback | tee: tee stage: 8 walkback; 8 tee walked back along the hole line (no box at 616 yds) |
| 2 | 3 | 223 / 223 | 124 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: 8 texture_pad | tee: tee stage: 8 texture_pad; 8 tee on an imagery-detected pad (texture; no OSM box at 223 yds) |
| 3 | 4 | 441 / 441 | 327 | 0.80 | auto | 74% | 7% | 19% | tee stage: 8 lidar_pad | tee: tee stage: 8 lidar_pad; 8 tee on a lidar pad (no OSM box at 441 yds) |
| 4 | 4 | 329 / 329 | 313 | 0.64 | check the flags | 33% | 3% | 64% | tee stage: 8 walkback | tee: tee stage: 8 walkback; 8 tee walked back along the hole line (no box at 329 yds) |
| 5 | 5 | 505 / 505 | 319 | 0.83 | auto | 79% | 14% | 7% | tee stage: 8 lidar_pad | tee: tee stage: 8 lidar_pad; 8 tee on a lidar pad (no OSM box at 505 yds) |
| 6 | 4 | 402 / 403 | 106 | 0.79 | check the flags | 66% | 11% | 22% | tee stage: 8 lidar_pad | tee: tee stage: 8 lidar_pad; 8 tee on a lidar pad (no OSM box at 402 yds) |
| 7 | 3 | 195 / 195 | 164 | 0.82 | auto | 100% | 0% | 0% | tee stage: 8 walkback | tee: tee stage: 8 walkback; 8 tee walked back along the hole line (no box at 195 yds) |
| 8 | 4 | 486 / 486 | 147 | 0.82 | auto | 86% | 0% | 14% | tee stage: 8 lidar_pad | tee: tee stage: 8 lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); 8 tee on a lidar pad (no OSM box at 486 yds) |
| 9 | 4 | 452 / 453 | 290 | 0.79 | check the flags | 87% | 2% | 10% | tee stage: 8 walkback | tee: tee stage: 8 walkback; 8 tee walked back along the hole line (no box at 452 yds) |

## Stages

- **resolve**: ok: way/29354026 Bobby Jones Golf Club (Atlanta, GA)
- **osm**: ok: 846 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 25 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (9 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/bobby_jones/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 9/9 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/bobby_jones/imagery/dem.tif (9/9 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 11 polygons (outside 11); mode replace
