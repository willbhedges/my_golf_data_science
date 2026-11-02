# Gaylord Springs Golf Links (Nashville, TN) - Black tees

Built 2026-11-01T20:48:41Z. OSM way/499135540. Scorecard: allsquare (allsquare). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 3 |
| holes_mapped | 3 |
| greens_found | 3 |
| tee_boxes | 12 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 2 |
| of_par4_5 | 2 |
| mean_landing_osm_share | 0.362 |
| mean_confidence | 0.767 |
| osm_score | 0.706 |

OSM features inside the course: buildings 5, golf=bunker 8, golf=fairway 8, golf=green 3, golf=hole 3, golf=tee 12, holes_with_par 3, water_polygons 8

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 529 / 528 | 179 | 0.78 | check the flags | 40% | 9% | 50% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 2 | 4 | 441 / 440 | 177 | 0.69 | check the flags | 32% | 13% | 55% | tee stage: Black lidar_pad | tee: tee stage: Black lidar_pad; Black tee on a lidar pad (no OSM box at 441 yds) |
| 3 | 3 | 160 / 160 | 57 | 0.82 | auto | 100% | 0% | 0% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 160 yds) |

## Stages

- **resolve**: ok: way/499135540 Gaylord Springs Golf Links (Nashville, TN)
- **osm**: ok: 222 features
- **routing**: ok: structure (unmapped_card, structure on osm) placed 1/16 holes OSM has no way for (1 to check; segment no, lidar pads 235, perception scene no)
- **scorecard**: ok: allsquare (allsquare)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 16 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (3 holes, 5 tee set(s))
- **imagery**: ok: course_data/packages/gaylord_springs/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 3/3 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/gaylord_springs/imagery/dem.tif (3/3 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 1 polygons (outside 1); mode replace

## Warnings

- hole inference fallback: v2+structure: RuntimeError: unmapped and no perception scene: no structure prior
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- hole 3: CHECK, shares hole 2's green
- hole 3: placed by structure inference, golfer check (uncertain (25%): P(number) 53%, P(tee) 50%; shares hole 2's green and no unused green fits)
