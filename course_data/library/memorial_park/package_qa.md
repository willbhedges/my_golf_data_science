# Memorial Park Golf Course (Houston, TX) - Blue tees

Built 2026-11-01T22:32:53Z. OSM relation/13729803. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Gold, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 51 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.309 |
| mean_confidence | 0.793 |
| osm_score | 0.833 |

OSM features inside the course: buildings 10, golf=bunker 21, golf=cartpath 30, golf=clubhouse 1, golf=driving_range 1, golf=fairway 19, golf=green 23, golf=hole 18, golf=lateral_water_hazard 8, golf=path 3, golf=pin 18, golf=tee 51, holes_with_par 18, tees_with_ref 12, trees_polygons 8, water_lines 4, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 522 / 521 | 221 | 0.75 | check the flags | 28% | 12% | 59% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 3 | 182 / 174 | 174 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 3 | 4 | 587 / 586 | 339 | 0.74 | check the flags | 53% | 4% | 43% | tee stage: Blue lidar_pad | tee: tee stage: Blue lidar_pad; Blue tee on a lidar pad (no OSM box at 587 yds) |
| 4 | 4 | 466 / 465 | 164 | 0.77 | check the flags | 32% | 14% | 54% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 440 / 440 | 323 | 0.83 | auto | 46% | 7% | 47% | tee stage: Blue tee_centroid |  |
| 6 | 4 | 388 / 388 | 145 | 0.79 | check the flags | 40% | 12% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 3 | 223 / 219 | 70 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 5 | 510 / 505 | 21 | 0.78 | check the flags | 29% | 23% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 4 | 202 / 201 | 14 | 0.68 | check the flags | 4% | 11% | 85% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 10 | 4 | 453 / 453 | 303 | 0.76 | check the flags | 32% | 8% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 238 / 237 | 158 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 496 / 495 | 330 | 0.77 | check the flags | 29% | 19% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 5 | 406 / 405 | 171 | 0.74 | check the flags | 29% | 5% | 67% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 529 / 530 | 63 | 0.75 | check the flags | 12% | 15% | 73% | tee stage: Blue tee_centroid |  |
| 15 | 3 | 155 / 155 | 153 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 5 | 613 / 610 | 352 | 0.59 | needs review | 16% | 20% | 64% | tee stage: Blue texture_pad | tee: tee stage: Blue texture_pad; Blue tee on an imagery-detected pad (texture; no OSM box at 613 yds) |
| 17 | 4 | 414 / 413 | 171 | 0.80 | auto | 55% | 0% | 45% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 18 | 4 | 393 / 392 | 205 | 0.81 | auto | 28% | 26% | 47% | tee stage: Blue tee_centroid |  |

## Stages

- **resolve**: ok: relation/13729803 Memorial Park Golf Course (Houston, TX)
- **osm**: ok: 832 features
- **renumber**: ok: OSM hole refs -> card holes 3->16, 13->18, 14->13, 16->3, 18->14
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 42 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/memorial_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2020)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2020
- **elevation**: ok: course_data/packages/memorial_park/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 10 polygons (outside 10); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Gold, Red
- OSM hole numbering differs from the card: OSM hole refs -> card holes 3->16, 13->18, 14->13, 16->3, 18->14 (CHECK)
- hole 9 White: CHECK, walk-back ran onto a building (OSM 778558182) 34 yds behind the line start: capped there (150 yds short of the card)
- hole 9 Gold: CHECK, walk-back ran onto a building (OSM 778558182) 34 yds behind the line start: capped there (123 yds short of the card)
- hole 9 Red: CHECK, walk-back ran onto a building (OSM 778558182) 34 yds behind the line start: capped there (96 yds short of the card)
- scorecard (golfify): 5 hole(s) where a longer set is shorter than the next set: 8 Blue 510 < White 554, 9 Blue 202 < White 378, 13 Blue 406 < White 480, 18 Blue 393 < White 410
