# The Harvester Golf Club (Rhodes, IA) - Black tees

Built 2026-11-02T17:00:31Z. OSM way/325314320. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 61 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.479 |
| mean_confidence | 0.807 |
| osm_score | 0.796 |

OSM features inside the course: buildings 11, built_up_landuse 1, golf=bunker 102, golf=cartpath 44, golf=fairway 27, golf=green 23, golf=hole 18, golf=lateral_water_hazard 3, golf=path 9, golf=rough 25, golf=tee 61, golf=water_hazard 1, holes_with_par 18, tees_with_ref 1, water_lines 13, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 425 / 423 | 14 | 0.77 | check the flags | 39% | 5% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 360 / 361 | 357 | 0.73 | check the flags | 30% | 0% | 70% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 3 | 3 | 195 / 195 | 133 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 4 | 5 | 575 / 575 | 210 | 0.77 | check the flags | 43% | 1% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 4 | 370 / 366 | 76 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 5 | 560 / 556 | 268 | 0.80 | auto | 54% | 0% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 405 / 400 | 177 | 0.78 | check the flags | 45% | 0% | 55% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 225 / 226 | 194 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 9 | 4 | 437 / 439 | 8 | 0.69 | check the flags | 64% | 0% | 36% | tee stage: Black review (inside OSM tee 1080114243) | tee: tee stage: Black review (inside OSM tee 1080114243); no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 470 / 464 | 343 | 0.77 | check the flags | 44% | 0% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 385 / 385 | 199 | 0.76 | check the flags | 37% | 1% | 62% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 4 | 410 / 410 | 200 | 0.81 | auto | 38% | 7% | 55% | tee stage: Black tee_centroid |  |
| 13 | 4 | 414 / 415 | 96 | 0.81 | auto | 44% | 0% | 56% | tee stage: Black tee_centroid |  |
| 14 | 3 | 180 / 176 | 104 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Black review (inside OSM tee 1080146929) | tee: tee stage: Black review (inside OSM tee 1080146929) |
| 15 | 5 | 650 / 651 | 268 | 0.83 | auto | 50% | 3% | 47% | tee stage: Black tee_centroid |  |
| 16 | 4 | 500 / 501 | 100 | 0.84 | auto | 55% | 0% | 45% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 180 / 176 | 35 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 5 | 565 / 565 | 344 | 0.77 | check the flags | 82% | 0% | 18% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 565 yds) |

## Stages

- **resolve**: ok: way/325314320 The Harvester Golf Club (Marshall County, IA)
- **osm**: ok: 437 features
- **card_overrides**: ok: 4 review fix(es): hole 9 Black: card 465 -> 437 yds (review); hole 13 Black: card 390 -> 414 yds (review); hole 14 Black: card 230 -> 180 yds (review); hole 16 Black: card 480 -> 500 yds (review)
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 9 review (inside OSM tee 1080114243), 14 review (inside OSM tee 1080146929);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 67 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/harvester/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/harvester/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -29 m2 {'cells': 29}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 11 polygons (property_line 11); mode replace

## Warnings

- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 14 Blue 155 < White 195
