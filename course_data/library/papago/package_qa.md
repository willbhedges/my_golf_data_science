# Papago Golf Club (Phoenix, AZ) - Black tees

Built 2026-10-30T21:43:44Z. OSM way/51990955. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 60 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.355 |
| mean_confidence | 0.811 |
| osm_score | 0.842 |

OSM features inside the course: buildings 6, golf=bunker 60, golf=driving_range 1, golf=fairway 21, golf=green 21, golf=hole 18, golf=path 18, golf=pin 18, golf=tee 60, golf=water_hazard 2, holes_with_handicap 18, holes_with_par 18, single_trees 41, trees_polygons 4, water_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 561 / 556 | 146 | 0.74 | check the flags | 30% | 2% | 68% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 386 / 386 | 40 | 0.80 | check the flags | 37% | 4% | 59% | tee stage: Black tee_centroid |  |
| 3 | 4 | 467 / 466 | 184 | 0.75 | check the flags | 36% | 0% | 64% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 4 | 3 | 233 / 232 | 186 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 5 | 4 | 383 / 382 | 0 | 0.78 | check the flags | 46% | 0% | 54% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 442 / 438 | 277 | 0.77 | check the flags | 41% | 0% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 4 | 454 / 453 | 39 | 0.80 | auto | 38% | 5% | 57% | tee stage: Black tee_centroid |  |
| 8 | 3 | 253 / 253 | 208 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 5 | 542 / 531 | 23 | 0.75 | check the flags | 34% | 0% | 66% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; green not visible on the NAIP 2023 imagery (NDVI 0.172 vs 0.295 on the course's other greens: bare soil / construction); the outline is OSM's |
| 10 | 5 | 525 / 524 | 170 | 0.77 | check the flags | 42% | 3% | 56% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 11 | 3 | 187 / 187 | 93 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 12 | 4 | 322 / 321 | 195 | 0.76 | check the flags | 27% | 2% | 72% | tee stage: Black tee_centroid |  |
| 13 | 4 | 402 / 402 | 297 | 0.77 | check the flags | 31% | 0% | 69% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 442 / 443 | 73 | 0.79 | check the flags | 35% | 5% | 60% | tee stage: Black tee_centroid |  |
| 15 | 5 | 585 / 586 | 259 | 0.78 | check the flags | 32% | 3% | 65% | tee stage: Black tee_centroid |  |
| 16 | 4 | 442 / 441 | 14 | 0.76 | check the flags | 36% | 5% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 3 | 243 / 242 | 7 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 464 / 464 | 27 | 0.76 | check the flags | 32% | 9% | 59% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; green not visible on the NAIP 2023 imagery (NDVI 0.161 vs 0.295 on the course's other greens: bare soil / construction); the outline is OSM's |

## Stages

- **resolve**: ok: way/51990955 Papago Golf Club (Phoenix, AZ)
- **osm**: ok: 656 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 52 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/papago/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 16/18 greens visible as turf on NAIP 2023; NOT visible: holes 9, 18
- **elevation**: ok: course_data/packages/papago/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 7 polygons (outside 7); mode replace

## Warnings

- greens of holes 9, 18 are not visible as turf on the NAIP 2023 imagery (bare soil / construction / dead turf): pick another NAIP year (imagery/naip_years.py)
