# WeaverRidge Golf Club (Peoria, IL) - Black tees

Built 2026-10-30T12:24:00Z. OSM way/749257217. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 82 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 9 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.399 |
| mean_confidence | 0.831 |
| osm_score | 0.808 |

OSM features inside the course: buildings 183, golf=bunker 78, golf=cartpath 46, golf=clubhouse 1, golf=driving_range 1, golf=fairway 24, golf=green 19, golf=hole 18, golf=rough 1, golf=tee 82, golf=water_hazard 8, holes_with_par 18, water_lines 3, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 508 / 509 | 274 | 0.80 | auto | 52% | 4% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 365 / 365 | 156 | 0.76 | check the flags | 26% | 0% | 74% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 5 | 494 / 495 | 274 | 0.81 | auto | 44% | 0% | 56% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 163 / 163 | 16 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 290 / 291 | 93 | 0.75 | check the flags | 23% | 0% | 77% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 357 / 357 | 9 | 0.77 | check the flags | 39% | 5% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 4 | 401 / 402 | 85 | 0.79 | check the flags | 42% | 10% | 48% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 171 / 171 | 176 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 4 | 357 / 357 | 189 | 0.77 | check the flags | 38% | 6% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 387 / 390 | 182 | 0.81 | auto | 30% | 40% | 30% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 5 | 447 / 447 | 220 | 0.81 | auto | 41% | 22% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 195 / 196 | 275 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 13 | 4 | 359 / 354 | 35 | 0.78 | check the flags | 44% | 4% | 53% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 4 | 313 / 313 | 211 | 0.83 | auto | 38% | 38% | 24% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 424 / 425 | 293 | 0.86 | auto | 53% | 12% | 36% | tee stage: Black tee_centroid |  |
| 16 | 4 | 375 / 375 | 85 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 168 / 168 | 84 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 506 / 506 | 57 | 0.84 | auto | 39% | 21% | 40% | tee stage: Black tee_centroid |  |

## Stages

- **resolve**: ok: way/749257217 WeaverRidge Golf Club (Peoria, IL)
- **osm**: ok: 822 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 80 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/weaver_ridge/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/weaver_ridge/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 10 polygons (outside 10); mode replace

## Warnings

- scorecard (opengolfapi): Gold: holes sum to 6876 but the source says 6500 (+376): mixed card versions
- scorecard (opengolfapi): Black: holes sum to 6280 but the source says 7000 (-720): mixed card versions
- scorecard (opengolfapi): Green: holes sum to 5938 but the source says 6011 (-73): mixed card versions
- scorecard (opengolfapi): White: holes sum to 5442 but the source says 5487 (-45): mixed card versions
- scorecard (opengolfapi): Red: holes sum to 4891 but the source says 5046 (-155): mixed card versions
