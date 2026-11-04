# Mariah Hills Golf Course (Dodge City, KS) - Blue tees

Built 2026-11-04T02:05:52Z. OSM way/329961222. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 41 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.32 |
| mean_confidence | 0.863 |
| osm_score | 0.864 |

OSM features inside the course: buildings 4, golf=bunker 16, golf=cartpath 23, golf=fairway 18, golf=green 20, golf=hole 18, golf=tee 41, golf=water_hazard 2, holes_with_par 18, single_trees 118, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 316 / 317 | 106 | 0.82 | auto | 29% | 45% | 26% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 410 / 411 | 79 | 0.87 | auto | 30% | 53% | 17% | tee stage: Blue tee_centroid |  |
| 3 | 5 | 550 / 549 | 1 | 0.82 | auto | 40% | 29% | 31% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 4 | 423 / 422 | 181 | 0.85 | auto | 31% | 37% | 32% | tee stage: Blue tee_centroid |  |
| 5 | 3 | 165 / 165 | 158 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 6 | 5 | 498 / 499 | 275 | 0.85 | auto | 43% | 39% | 18% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 372 / 372 | 59 | 0.73 | check the flags | 5% | 85% | 10% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 372 yds); Blue tee out of order with the other sets |
| 8 | 3 | 195 / 195 | 28 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 9 | 4 | 375 / 375 | 232 | 0.86 | auto | 37% | 37% | 26% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 361 / 360 | 12 | 0.83 | auto | 31% | 50% | 20% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 174 / 175 | 80 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 498 / 499 | 94 | 0.85 | auto | 31% | 39% | 30% | tee stage: Blue tee_centroid |  |
| 13 | 4 | 446 / 445 | 195 | 0.87 | auto | 35% | 44% | 21% | tee stage: Blue tee_centroid |  |
| 14 | 4 | 392 / 391 | 14 | 0.86 | auto | 34% | 42% | 24% | tee stage: Blue tee_centroid |  |
| 15 | 4 | 386 / 387 | 267 | 0.83 | auto | 33% | 47% | 20% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 3 | 184 / 184 | 186 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 364 / 364 | 62 | 0.84 | auto | 29% | 53% | 18% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 440 / 440 | 230 | 0.84 | auto | 39% | 42% | 19% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/329961222 Mariah Hills Golf Course (Dodge City, KS)
- **osm**: ok: 272 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 18/18 holes OSM has no way for (2 to check; segment no, lidar pads 58, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 33 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/mariah_hills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/mariah_hills/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'mariah_hills' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 222 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py mariah_hills (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: not needed: every par-4/5 landing corridor has a fairway
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace
- **native_auto**: ok: 14 holes, sides 1 both, 2 both, 3 both, 4 both, 6 both, 7 both, 9 both, 10 both, 12 L, 13 both, 14 both, 15 both, 17 both, 18 both

## Warnings

- hole 9: placed by v2+structure inference, golfer check (ambiguous (62% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (77% of the posterior))
