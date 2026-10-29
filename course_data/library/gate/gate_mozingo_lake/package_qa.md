# Mozingo Lake Golf Course (Maryville, MO) - osm_back tees

Built 2026-10-29T20:54:06Z. OSM way/385067034. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 66 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 8 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.485 |
| mean_confidence | 0.663 |
| osm_score | 0.811 |

OSM features inside the course: buildings 4, golf=bunker 25, golf=cartpath 23, golf=driving_range 1, golf=fairway 20, golf=green 25, golf=hole 18, golf=rough 22, golf=tee 66, golf=water_hazard 3, holes_with_handicap 16, holes_with_par 18, single_trees 12, tees_with_ref 12, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 398 / 398 | 174 | 0.62 | check the flags | 43% | 7% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 2 | 4 | 350 / 350 | 59 | 0.64 | check the flags | 46% | 11% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 5 | 581 / 581 | 233 | 0.65 | check the flags | 53% | 6% | 41% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 435 / 435 | 81 | 0.61 | check the flags | 43% | 0% | 57% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 3 | 180 / 180 | 210 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 6 | 5 | 514 / 514 | 266 | 0.64 | check the flags | 52% | 2% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 4 | 474 / 474 | 35 | 0.65 | check the flags | 58% | 1% | 42% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 3 | 187 / 187 | 26 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 4 | 420 / 420 | 11 | 0.63 | check the flags | 49% | 0% | 51% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 414 / 414 | 10 | 0.62 | check the flags | 46% | 3% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 11 | 3 | 220 / 220 | 343 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 12 | 5 | 508 / 508 | 265 | 0.62 | check the flags | 46% | 1% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 4 | 430 / 430 | 177 | 0.64 | check the flags | 49% | 6% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 5 | 464 / 464 | 187 | 0.63 | check the flags | 50% | 0% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 3 | 176 / 176 | 80 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 16 | 4 | 450 / 450 | 8 | 0.64 | check the flags | 54% | 0% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 4 | 386 / 386 | 50 | 0.60 | check the flags | 34% | 7% | 58% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 4 | 447 / 447 | 206 | 0.65 | check the flags | 57% | 0% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/385067034 Mozingo Lake Golf Course (Maryville, MO)
- **osm**: ok: 475 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/gate_mozingo_lake/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/gate_mozingo_lake/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 4 polygons (outside 4); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
