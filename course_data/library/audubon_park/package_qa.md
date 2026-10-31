# Audubon Park Golf Course (New Orleans, LA) - Gold tees

Built 2026-10-31T01:49:52Z. OSM way/27887431. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White**

## Coverage

| | |
|---|---|
| holes_built | 16 |
| holes_mapped | 16 |
| greens_found | 16 |
| tee_boxes | 32 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 6 |
| of_par4_5 | 6 |
| mean_landing_osm_share | 0.216 |
| mean_confidence | 0.847 |
| osm_score | 0.715 |

OSM features inside the course: buildings 2, golf=bunker 69, golf=green 16, golf=hole 16, golf=tee 32, holes_with_par 16, single_trees 28, water_polygons 5

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 323 / 324 | 34 | 0.67 | check the flags | 26% | 8% | 66% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 323 yds) |
| 2 | 3 | 148 / 148 | 56 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 3 | 227 / 224 | 223 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 3 | 129 / 124 | 147 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 4 | 292 / 281 | 237 | 0.67 | check the flags | 4% | 3% | 92% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 3 | 167 / 167 | 53 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 3 | 127 / 126 | 223 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 8 | 3 | 187 / 184 | 303 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 5 | 462 / 463 | 60 | 0.85 | auto | 71% | 0% | 29% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no fairway in the landing zone |
| 10 | 4 | 360 / 360 | 59 | 0.77 | check the flags | 2% | 41% | 57% | tee stage: Gold tee_centroid | no fairway in the landing zone |
| 11 | 3 | 137 / 137 | 32 | 0.86 | auto | 100% | 0% | 0% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 137 yds) |
| 12 | 3 | 195 / 194 | 284 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 3 | 148 / 146 | 235 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 14 | 4 | 282 / 282 | 119 | 0.75 | check the flags | 12% | 14% | 74% | tee stage: Gold tee_centroid |  |
| 16 | 3 | 163 / 162 | 47 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 18 | 5 | 471 / 476 | 203 | 0.62 | check the flags | 14% | 0% | 86% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; no fairway in the landing zone; Gold tee on a lidar pad (no OSM box at 471 yds) |

## Stages

- **resolve**: ok: way/27887431 Audubon Park Golf Course (New Orleans, LA)
- **osm**: ok: 1238 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 16/18 holes OSM has no way for (16 to check; segment no, lidar pads 67, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 35 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (16 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/audubon_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 16/16 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/audubon_park/imagery/dem.tif (16/16 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 12 polygons (outside 12); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White
- hole 1: placed by v2+structure inference, golfer check (ambiguous (49% of the posterior))
- hole 2: placed by v2+structure inference, golfer check (ambiguous (81% of the posterior))
- hole 3: placed by v2+structure inference, golfer check (ambiguous (46% of the posterior))
- hole 4: placed by v2+structure inference, golfer check (ambiguous (53% of the posterior))
- hole 5: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 6: placed by v2+structure inference, golfer check (ambiguous (56% of the posterior))
- hole 7: placed by v2+structure inference, golfer check (ambiguous (40% of the posterior))
- hole 8: placed by v2+structure inference, golfer check (ambiguous (64% of the posterior))
- hole 9: placed by v2+structure inference, golfer check (ambiguous (53% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (63% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (73% of the posterior))
- hole 12: placed by v2+structure inference, golfer check (ambiguous (81% of the posterior))
- hole 13: placed by v2+structure inference, golfer check (ambiguous (51% of the posterior))
- hole 14: placed by v2+structure inference, golfer check (ambiguous (27% of the posterior))
- hole 16: placed by v2+structure inference, golfer check (ambiguous (55% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (55% of the posterior))
