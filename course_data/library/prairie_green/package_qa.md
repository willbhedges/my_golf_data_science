# Prairie Green Golf Course (Sioux Falls, SD) - Professional tees

Built 2026-10-31T03:56:55Z. OSM relation/17830055. Scorecard: golfify (golfify). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 72 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 6 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.41 |
| mean_confidence | 0.847 |
| osm_score | 0.768 |

OSM features inside the course: buildings 4, golf=bunker 48, golf=cartpath 21, golf=fairway 19, golf=green 21, golf=hole 18, golf=tee 72, golf=water_hazard 13, holes_with_par 18, single_trees 13, water_polygons 13

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 449 / 449 | 181 | 0.84 | auto | 38% | 25% | 38% | tee stage: Professional tee_centroid |  |
| 2 | 3 | 175 / 175 | 196 | 0.93 | auto | 100% | 0% | 0% | tee stage: Professional tee_axis | tee: tee stage: Professional tee_axis |
| 3 | 5 | 575 / 577 | 263 | 0.81 | auto | 38% | 10% | 52% | tee stage: Professional tee_centroid |  |
| 4 | 4 | 419 / 420 | 88 | 0.81 | auto | 45% | 0% | 55% | tee stage: Professional tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 380 / 381 | 256 | 0.82 | auto | 50% | 0% | 50% | tee stage: Professional tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 5 | 547 / 547 | 307 | 0.81 | auto | 43% | 4% | 52% | tee stage: Professional tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 402 / 402 | 159 | 0.86 | auto | 57% | 6% | 37% | tee stage: Professional tee_centroid |  |
| 8 | 3 | 204 / 205 | 104 | 0.96 | auto | 100% | 0% | 0% | tee stage: Professional tee_centroid |  |
| 9 | 4 | 443 / 443 | 0 | 0.81 | auto | 46% | 16% | 38% | tee stage: Professional tee_axis | tee: tee stage: Professional tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 457 / 458 | 304 | 0.80 | check the flags | 36% | 5% | 59% | tee stage: Professional tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 163 / 163 | 257 | 0.93 | auto | 100% | 0% | 0% | tee stage: Professional tee_axis | tee: tee stage: Professional tee_axis |
| 12 | 4 | 417 / 418 | 271 | 0.82 | auto | 32% | 23% | 45% | tee stage: Professional tee_centroid |  |
| 13 | 5 | 580 / 582 | 88 | 0.86 | auto | 41% | 32% | 28% | tee stage: Professional tee_centroid |  |
| 14 | 4 | 364 / 365 | 66 | 0.79 | check the flags | 34% | 7% | 60% | tee stage: Professional tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 5 | 566 / 567 | 147 | 0.82 | auto | 30% | 27% | 43% | tee stage: Professional tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 3 | 193 / 194 | 99 | 0.96 | auto | 100% | 0% | 0% | tee stage: Professional tee_centroid |  |
| 17 | 4 | 394 / 394 | 170 | 0.82 | auto | 46% | 1% | 53% | tee stage: Professional tee_centroid |  |
| 18 | 4 | 451 / 452 | 273 | 0.78 | check the flags | 38% | 9% | 53% | tee stage: Professional tee_axis | tee: tee stage: Professional tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: relation/17830055 Prairie Green Golf Course (Sioux Falls, SD)
- **osm**: ok: 2156 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 78 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/prairie_green/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/prairie_green/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 30 polygons (outside 30); mode replace
