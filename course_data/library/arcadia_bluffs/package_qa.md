# Arcadia Bluffs Golf Club (Arcadia, MI) - Champion tees

Built 2026-11-01T22:05:37Z. OSM way/293247442. Scorecard: allsquare (allsquare). Tee set: colour.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 69 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 1 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.496 |
| mean_confidence | 0.848 |
| osm_score | 0.715 |

OSM features inside the course: buildings 2, golf=bunker 202, golf=cartpath 35, golf=fairway 21, golf=green 24, golf=hole 18, golf=rough 92, golf=tee 69, golf=water_hazard 1, holes_with_handicap 17, holes_with_par 18, tees_with_ref 1, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 519 / 517 | 73 | 0.76 | check the flags | 40% | 0% | 60% | tee stage: Champion tee_axis | tee: tee stage: Champion tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 2 | 3 | 189 / 189 | 319 | 0.96 | auto | 100% | 0% | 0% | tee stage: Champion tee_centroid |  |
| 3 | 5 | 530 / 531 | 258 | 0.82 | auto | 49% | 0% | 51% | tee stage: Champion tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 4 | 4 | 415 / 416 | 259 | 0.80 | auto | 40% | 3% | 58% | tee stage: Champion tee_centroid |  |
| 5 | 5 | 583 / 589 | 262 | 0.74 | check the flags | 56% | 0% | 44% | tee stage: Champion lidar_pad | tee: tee stage: Champion lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Champion tee on a lidar pad (no OSM box at 583 yds) |
| 6 | 3 | 195 / 195 | 78 | 0.96 | auto | 100% | 0% | 0% | tee stage: Champion tee_centroid |  |
| 7 | 4 | 472 / 473 | 110 | 0.81 | auto | 57% | 0% | 43% | tee stage: Champion tee_axis | tee: tee stage: Champion tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 4 | 449 / 442 | 188 | 0.80 | auto | 55% | 0% | 45% | tee stage: Champion tee_axis | tee: tee stage: Champion tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 9 | 3 | 203 / 203 | 63 | 0.96 | auto | 100% | 0% | 0% | tee stage: Champion tee_centroid |  |
| 10 | 4 | 481 / 482 | 257 | 0.79 | check the flags | 37% | 0% | 63% | tee stage: Champion tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 5 | 633 / 634 | 257 | 0.85 | auto | 59% | 0% | 41% | tee stage: Champion tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 4 | 431 / 431 | 4 | 0.85 | auto | 59% | 0% | 41% | tee stage: Champion tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 3 | 240 / 240 | 320 | 0.96 | auto | 100% | 0% | 0% | tee stage: Champion tee_centroid |  |
| 14 | 4 | 340 / 341 | 98 | 0.76 | check the flags | 27% | 0% | 73% | tee stage: Champion tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 5 | 519 / 520 | 116 | 0.80 | check the flags | 52% | 0% | 48% | tee stage: Champion tee_axis | tee: tee stage: Champion tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 486 / 487 | 282 | 0.87 | auto | 66% | 0% | 34% | tee stage: Champion tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 17 | 3 | 176 / 176 | 209 | 0.96 | auto | 100% | 0% | 0% | tee stage: Champion tee_centroid |  |
| 18 | 4 | 439 / 440 | 58 | 0.79 | check the flags | 50% | 0% | 50% | tee stage: Champion tee_axis | tee: tee stage: Champion tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |

## Stages

- **resolve**: ok: way/293247442 Arcadia Bluffs Golf Club (Arcadia, MI)
- **osm**: ok: 482 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 77 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/arcadia_bluffs/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/arcadia_bluffs/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 3 polygons (outside 3); mode replace
