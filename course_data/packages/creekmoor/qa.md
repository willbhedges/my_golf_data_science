# Creekmoor Golf Club (Raymore, MO) - Black tees

Built 2026-11-03T15:02:11Z. OSM relation/4249741. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 17 |
| tee_boxes | 75 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 5 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.05 |
| mean_confidence | 0.799 |
| osm_score | 0.559 |

OSM features inside the course: buildings 3, golf=bunker 68, golf=cartpath 12, golf=driving_range 1, golf=green 19, golf=hole 17, golf=pin 18, golf=tee 75, golf=water_hazard 4, holes_with_handicap 17, holes_with_par 17, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 404 / 404 | 292 | 0.79 | check the flags | 1% | 66% | 33% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 371 / 371 | 28 | 0.80 | auto | 4% | 53% | 43% | tee stage: Black tee_centroid |  |
| 3 | 4 | 440 / 441 | 236 | 0.69 | check the flags | 4% | 48% | 48% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 440 yds) |
| 4 | 3 | 195 / 195 | 11 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 5 | 537 / 537 | 41 | 0.80 | check the flags | 2% | 53% | 46% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 4 | 451 / 451 | 225 | 0.80 | check the flags | 4% | 50% | 46% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 3 | 170 / 170 | 166 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 441 / 442 | 75 | 0.81 | auto | 2% | 62% | 36% | tee stage: Black tee_centroid |  |
| 9 | 5 | 663 / 662 | 170 | 0.84 | auto | 24% | 46% | 30% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 482 / 481 | 68 | 0.78 | check the flags | 2% | 60% | 37% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 374 / 374 | 43 | 0.81 | auto | 4% | 58% | 37% | tee stage: Black tee_centroid |  |
| 12 | 3 | 240 / 240 | 57 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Black review (inside OSM tee 1490361208) | tee: tee stage: Black review (inside OSM tee 1490361208) |
| 13 | 5 | 548 / 547 | 334 | 0.79 | check the flags | 3% | 50% | 48% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 420 / 419 | 174 | 0.70 | check the flags | 3% | 51% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; green from the hole-line end (no golf=green polygon); no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 460 / 460 | 264 | 0.78 | check the flags | 7% | 55% | 38% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 455 / 454 | 354 | 0.75 | check the flags | 6% | 42% | 51% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 214 / 216 | 163 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Black review (inside OSM tee 1490357722) | tee: tee stage: Black review (inside OSM tee 1490357722) |
| 18 | 5 | 541 / 536 | 220 | 0.76 | check the flags | 3% | 53% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: relation/4249741 Creekmoor Golf Club (Raymore, MO)
- **osm**: ok: 420 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Black 12 review (inside OSM tee 1490361208), 17 review (inside OSM tee 1490357722); Green 12 review (inside OSM tee 1490361210), 17 review (inside OSM tee 1490357723);
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 74 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/creekmoor/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 17/17 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/creekmoor/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -82229 m2 {'raised': 67203, 'road': 3160, 'strip': 2309, 'cells': 9286}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: ok: 14/14 hole(s) without a mapped fairway filled from NAIP (d' 2.01; gated: none)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 41 polygons (outside 41); mode replace

## Warnings

- ignored 2 practice / driving-range tee box(es): OSM 1489923974, 1489923975
