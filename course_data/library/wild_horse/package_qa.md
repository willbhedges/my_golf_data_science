# Wild Horse Golf Club (Gothenburg, NE) - Black tees

Built 2026-10-31T01:50:42Z. OSM way/383386145. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 69 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 3 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.568 |
| mean_confidence | 0.861 |
| osm_score | 0.757 |

OSM features inside the course: buildings 5, golf=bunker 69, golf=clubhouse 1, golf=driving_range 1, golf=fairway 19, golf=green 20, golf=hole 18, golf=path 60, golf=tee 69, holes_with_handicap 18, holes_with_par 18

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 328 / 328 | 350 | 0.76 | check the flags | 26% | 0% | 74% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 414 / 415 | 258 | 0.89 | auto | 84% | 0% | 16% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 5 | 494 / 495 | 101 | 0.88 | auto | 78% | 5% | 17% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 3 | 160 / 160 | 301 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 4 | 339 / 340 | 288 | 0.81 | auto | 36% | 10% | 54% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 5 | 527 / 527 | 139 | 0.86 | auto | 50% | 18% | 32% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 345 / 345 | 348 | 0.85 | auto | 58% | 0% | 42% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 4 | 433 / 433 | 146 | 0.81 | auto | 49% | 10% | 41% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 3 | 143 / 143 | 338 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 10 | 4 | 382 / 386 | 131 | 0.79 | check the flags | 49% | 0% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 113 / 113 | 82 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 393 / 393 | 329 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 3 | 191 / 191 | 159 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 14 | 5 | 490 / 490 | 331 | 0.93 | auto | 87% | 0% | 13% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 307 / 308 | 278 | 0.83 | auto | 49% | 4% | 47% | tee stage: Black tee_centroid |  |
| 16 | 4 | 418 / 418 | 142 | 0.90 | auto | 75% | 0% | 25% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 5 | 474 / 474 | 328 | 0.85 | auto | 59% | 0% | 40% | tee stage: Black tee_centroid |  |
| 18 | 4 | 384 / 385 | 160 | 0.78 | check the flags | 45% | 1% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/383386145 Wild Horse Golf Club (Dawson County, NE)
- **osm**: ok: 309 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 29 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/wild_horse/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/wild_horse/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 18 polygons (outside 18); mode replace
