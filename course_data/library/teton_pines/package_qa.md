# Teton Pines Country Club (Wilson, WY) - Black tees

Built 2026-10-31T05:30:04Z. OSM way/185769563. Scorecard: opengolfapi (opengolfapi). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 17 |
| greens_found | 18 |
| tee_boxes | 95 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 14 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.525 |
| mean_confidence | 0.804 |
| osm_score | 0.891 |

OSM features inside the course: buildings 6, built_up_landuse 2, golf=bunker 58, golf=cartpath 40, golf=clubhouse 1, golf=driving_range 1, golf=fairway 22, golf=green 20, golf=hole 17, golf=tee 95, holes_with_par 17, single_trees 1502, water_lines 15, water_polygons 16

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 444 / 444 | 132 | 0.72 | check the flags | 64% | 0% | 36% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 444 yds) |
| 2 | 5 | 609 / 608 | 188 | 0.72 | check the flags | 61% | 3% | 36% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 609 yds) |
| 3 | 3 | 204 / 204 | 186 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 4 | 4 | 408 / 409 | 255 | 0.76 | check the flags | 60% | 3% | 36% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 408 yds) |
| 5 | 4 | 423 / 417 | 331 | 0.80 | auto | 54% | 2% | 45% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 6 | 4 | 426 / 427 | 109 | 0.81 | auto | 56% | 0% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 5 | 634 / 633 | 10 | 0.69 | check the flags | 50% | 0% | 50% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 634 yds) |
| 8 | 3 | 181 / 181 | 200 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 9 | 4 | 437 / 427 | 4 | 0.77 | check the flags | 41% | 1% | 58% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 10 | 5 | 572 / 572 | 197 | 0.73 | check the flags | 53% | 4% | 44% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 572 yds) |
| 11 | 4 | 412 / 413 | 77 | 0.79 | check the flags | 46% | 5% | 49% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 12 | 3 | 221 / 216 | 166 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 13 | 4 | 463 / 464 | 264 | 0.73 | check the flags | 43% | 13% | 44% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 463 yds) |
| 14 | 5 | 518 / 518 | 200 | 0.81 | auto | 50% | 8% | 42% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 443 / 441 | 24 | 0.80 | auto | 53% | 3% | 44% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 16 | 3 | 202 / 197 | 354 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 17 | 4 | 333 / 333 | 26 | 0.82 | auto | 43% | 22% | 34% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 18 | 4 | 472 / 462 | 21 | 0.74 | check the flags | 62% | 12% | 26% | tee stage: Black walkback_capped | tee: tee stage: Black walkback_capped; Black tee walked back along the hole line (no box at 472 yds) |

## Stages

- **resolve**: ok: way/185769563 Teton Pines Country Club (Wilson, WY)
- **osm**: ok: 2708 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: opengolfapi (opengolfapi)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 110 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 6 tee set(s))
- **imagery**: ok: course_data/packages/teton_pines/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2019)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2019
- **elevation**: ok: course_data/packages/teton_pines/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 38 polygons (outside 38); mode replace

## Warnings

- hole 18 Black: CHECK, walk-back ran onto a residential (OSM 1078233547) 50 yds behind the line start: capped there (10 yds short of the card)
- scorecard (opengolfapi): Blue: holes sum to 6906 but the source says 6888 (+18): mixed card versions
- scorecard (opengolfapi): Palmer: holes sum to 6604 but the source says 6585 (+19): mixed card versions
