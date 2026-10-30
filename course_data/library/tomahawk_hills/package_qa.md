# Tomahawk Hills Golf Course (Shawnee, KS) - Blue tees

Built 2026-10-30T03:40:52Z. OSM way/117417596. Scorecard: club_site (club_site). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 45 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.422 |
| mean_confidence | 0.839 |
| osm_score | 0.884 |

OSM features inside the course: buildings 4, golf=bunker 16, golf=cartpath 26, golf=fairway 19, golf=green 20, golf=hole 18, golf=tee 45, golf=water_hazard 1, holes_with_par 18, single_trees 103, trees_polygons 15, water_lines 10, water_polygons 1

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 544 / 545 | 79 | 0.82 | auto | 37% | 18% | 46% | tee stage: Blue tee_centroid |  |
| 2 | 3 | 183 / 183 | 185 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 3 | 4 | 393 / 394 | 280 | 0.82 | auto | 56% | 7% | 37% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 4 | 4 | 427 / 427 | 150 | 0.64 | check the flags | 29% | 6% | 66% | tee stage: Blue walkback | tee: tee stage: Blue walkback; Blue tee walked back along the hole line (no box at 427 yds) |
| 5 | 4 | 269 / 269 | 3 | 0.74 | check the flags | 28% | 6% | 66% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 6 | 3 | 173 / 173 | 192 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 7 | 5 | 472 / 473 | 276 | 0.79 | check the flags | 47% | 5% | 48% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 8 | 4 | 305 / 305 | 327 | 0.78 | check the flags | 40% | 8% | 52% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 9 | 3 | 196 / 196 | 355 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 10 | 4 | 361 / 362 | 247 | 0.80 | check the flags | 49% | 6% | 45% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 11 | 3 | 155 / 155 | 116 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 12 | 4 | 375 / 371 | 187 | 0.80 | check the flags | 51% | 4% | 46% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 4 | 285 / 285 | 202 | 0.80 | check the flags | 18% | 50% | 32% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 5 | 512 / 513 | 89 | 0.84 | auto | 64% | 6% | 30% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 5 | 508 / 509 | 269 | 0.78 | check the flags | 35% | 16% | 49% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 16 | 3 | 195 / 195 | 93 | 0.96 | auto | 100% | 0% | 0% | tee stage: Blue tee_centroid |  |
| 17 | 4 | 391 / 391 | 26 | 0.81 | auto | 53% | 8% | 39% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 3 | 193 / 193 | 37 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/117417596 Tomahawk Hills Golf Course (Shawnee, KS)
- **osm**: ok: 595 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 18/18 holes OSM has no way for (1 to check; segment no, lidar pads 104, perception scene no)
- **scorecard**: ok: club_site (club_site)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 35 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 3 tee set(s))
- **imagery**: ok: course_data/packages/tomahawk_hills/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/tomahawk_hills/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 9 polygons (outside 9); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Red
- hole 1: placed by v2+structure inference, golfer check (ambiguous (57% of the posterior))
