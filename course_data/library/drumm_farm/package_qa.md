# Drumm Farm Golf Club (Independence, MO) - osm_back tees

Built 2026-10-30T00:19:06Z. OSM way/316101757. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 81 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 7 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.42 |
| mean_confidence | 0.655 |
| osm_score | 0.784 |

OSM features inside the course: buildings 7, golf=bunker 45, golf=cartpath 29, golf=clubhouse 1, golf=driving_range 1, golf=fairway 28, golf=green 23, golf=hole 18, golf=pin 18, golf=tee 81, holes_with_handicap 18, holes_with_par 18, single_trees 18, trees_polygons 1, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 372 / 372 | 290 | 0.63 | check the flags | 50% | 0% | 50% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 4 | 435 / 435 | 300 | 0.62 | check the flags | 44% | 2% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 3 | 3 | 197 / 197 | 91 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 4 | 4 | 395 / 395 | 95 | 0.64 | check the flags | 54% | 0% | 46% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 5 | 4 | 441 / 441 | 351 | 0.62 | check the flags | 46% | 0% | 54% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 6 | 3 | 242 / 242 | 169 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 7 | 5 | 538 / 538 | 277 | 0.60 | needs review | 27% | 17% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 8 | 4 | 356 / 356 | 169 | 0.62 | check the flags | 22% | 35% | 43% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 9 | 5 | 507 / 507 | 98 | 0.62 | check the flags | 44% | 4% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 10 | 4 | 435 / 435 | 7 | 0.64 | check the flags | 51% | 1% | 48% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 369 / 369 | 333 | 0.58 | needs review | 33% | 0% | 67% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 4 | 451 / 451 | 131 | 0.61 | check the flags | 44% | 0% | 56% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 4 | 380 / 380 | 317 | 0.66 | check the flags | 54% | 8% | 38% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 14 | 3 | 182 / 182 | 276 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 15 | 5 | 520 / 520 | 168 | 0.61 | check the flags | 42% | 0% | 58% | tee nearest the hole-line start | tee: tee nearest the hole-line start; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 332 / 332 | 260 | 0.62 | check the flags | 32% | 19% | 49% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 17 | 3 | 192 / 192 | 303 | 0.77 | check the flags | 100% | 0% | 0% | tee nearest the hole-line start | tee: tee nearest the hole-line start |
| 18 | 5 | 522 / 522 | 102 | 0.64 | check the flags | 44% | 11% | 45% | tee nearest the hole-line start | tee: tee nearest the hole-line start |

## Stages

- **resolve**: ok: way/316101757 Drumm Farm Golf Club (Independence, MO)
- **osm**: ok: 945 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (18 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/drumm_farm/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/drumm_farm/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 14 polygons (outside 14); mode replace

## Warnings

- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
