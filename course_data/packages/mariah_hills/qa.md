# Mariah Hills Golf Course (Dodge City, KS) - Blue tees

Built 2026-11-02T10:28:13Z. OSM way/329961222. Scorecard: golfify (golfify). Tee set: name.

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
| mean_confidence | 0.801 |
| osm_score | 0.864 |

OSM features inside the course: buildings 4, golf=bunker 16, golf=cartpath 23, golf=fairway 18, golf=green 20, golf=hole 18, golf=tee 41, golf=water_hazard 2, holes_with_par 18, single_trees 118, water_lines 3, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 316 / 317 | 106 | 0.75 | check the flags | 29% | 9% | 62% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 2 | 4 | 410 / 411 | 79 | 0.79 | check the flags | 30% | 8% | 62% | tee stage: Blue tee_centroid |  |
| 3 | 5 | 550 / 549 | 1 | 0.77 | check the flags | 40% | 3% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 4 | 423 / 422 | 181 | 0.78 | check the flags | 31% | 1% | 67% | tee stage: Blue tee_centroid |  |
| 5 | 3 | 165 / 165 | 158 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 6 | 5 | 498 / 499 | 275 | 0.78 | check the flags | 43% | 5% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 4 | 372 / 372 | 59 | 0.57 | needs review | 5% | 6% | 88% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 372 yds) |
| 8 | 3 | 195 / 195 | 28 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 9 | 4 | 375 / 375 | 232 | 0.80 | auto | 37% | 6% | 57% | tee stage: Blue tee_centroid |  |
| 10 | 4 | 361 / 360 | 12 | 0.77 | check the flags | 31% | 18% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 174 / 175 | 80 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 5 | 498 / 499 | 94 | 0.80 | check the flags | 31% | 11% | 57% | tee stage: Blue tee_centroid |  |
| 13 | 4 | 446 / 445 | 195 | 0.79 | check the flags | 35% | 2% | 63% | tee stage: Blue tee_centroid |  |
| 14 | 4 | 392 / 391 | 14 | 0.78 | check the flags | 34% | 1% | 65% | tee stage: Blue tee_centroid |  |
| 15 | 4 | 386 / 387 | 267 | 0.75 | check the flags | 33% | 3% | 64% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 3 | 184 / 184 | 186 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 364 / 364 | 62 | 0.76 | check the flags | 29% | 12% | 59% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 440 / 440 | 230 | 0.77 | check the flags | 39% | 3% | 58% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

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
- **vision**: missing: product layer vision_any/2 not built for 'mariah_hills' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 223 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py mariah_hills (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 5 polygons (outside 5); mode replace

## Warnings

- hole 9: placed by v2+structure inference, golfer check (ambiguous (62% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (77% of the posterior))
- CHECK vision: missing: product layer vision_any/2 not built for 'mariah_hills' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 223 long-grass zon; trees / water come from OSM (or the fallback) only
