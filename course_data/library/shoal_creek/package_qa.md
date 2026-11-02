# Shoal Creek Golf Course (Kansas City, MO) - Black tees

Built 2026-11-02T17:11:03Z. OSM way/195221881. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 76 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.286 |
| mean_confidence | 0.79 |
| osm_score | 0.8 |

OSM features inside the course: buildings 1, golf=bunker 39, golf=cartpath 19, golf=clubhouse 1, golf=fairway 19, golf=green 18, golf=hole 18, golf=path 1, golf=pin 18, golf=tee 76, holes_with_par 18, single_trees 4, trees_polygons 2, water_lines 4, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 313 / 313 | 146 | 0.78 | check the flags | 32% | 1% | 67% | tee stage: Black tee_centroid |  |
| 2 | 4 | 292 / 288 | 85 | 0.75 | check the flags | 32% | 5% | 64% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 112 / 112 | 164 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 4 | 4 | 299 / 299 | 136 | 0.77 | check the flags | 16% | 35% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 5 | 3 | 130 / 139 | 321 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Black review (snapped 11 yds along OSM tee 897738874) | tee: tee stage: Black review (snapped 11 yds along OSM tee 897738874) |
| 6 | 4 | 281 / 283 | 309 | 0.56 | needs review | 17% | 0% | 83% | tee stage: Black review | tee: tee stage: Black review; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 7 | 5 | 448 / 447 | 163 | 0.79 | check the flags | 33% | 9% | 58% | tee stage: Black tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 4 | 355 / 355 | 342 | 0.80 | check the flags | 27% | 19% | 54% | tee stage: Black tee_centroid |  |
| 9 | 5 | 378 / 378 | 329 | 0.81 | auto | 48% | 11% | 40% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 4 | 235 / 231 | 15 | 0.69 | check the flags | 13% | 1% | 86% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 3 | 126 / 126 | 119 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 12 | 4 | 166 / 163 | 129 | 0.58 | needs review | 0% | 0% | 100% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); no fairway in the landing zone; Black tee on a lidar pad (no OSM box at 166 yds) |
| 13 | 5 | 367 / 367 | 152 | 0.83 | auto | 40% | 17% | 43% | tee stage: Black tee_centroid |  |
| 14 | 4 | 292 / 292 | 333 | 0.79 | check the flags | 28% | 15% | 57% | tee stage: Black tee_centroid |  |
| 15 | 4 | 312 / 312 | 62 | 0.88 | auto | 68% | 0% | 32% | tee stage: Black tee_centroid |  |
| 16 | 4 | 246 / 246 | 246 | 0.76 | check the flags | 19% | 12% | 69% | tee stage: Black tee_centroid |  |
| 17 | 3 | 104 / 104 | 339 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 18 | 4 | 303 / 298 | 184 | 0.75 | check the flags | 26% | 14% | 60% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/195221881 Shoal Creek Golf Course (Kansas City, MO)
- **osm**: ok: 1631 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tee_overrides**: ok: Gold 5 review (inside OSM tee 897738876), 6 review (inside OSM tee 897746433); Blue 5 review (snapped 1 yds along OSM tee 897738875), 6 review (inside OSM tee 897746432); White 5 review (snapped 1 yds along OSM tee 897738874), 6 review (snapped 12 yds along OSM tee 897746432); Black 5 review (snapped 11 yds along OSM tee 897738874), 6 review;
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 106 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/shoal_creek/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2018)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2018
- **elevation**: ok: course_data/packages/shoal_creek/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -459 m2 {'road': 459}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 18 polygons (outside 18); mode replace
