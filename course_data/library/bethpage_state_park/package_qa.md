# Bethpage Black (Old Bethpage, NY) - osm_back tees

Built 2026-10-31T03:31:41Z. OSM node/2854158382. Scorecard: None (None). Tee set: no scorecard.

## Coverage

| | |
|---|---|
| holes_built | 3 |
| holes_mapped | 3 |
| greens_found | 1 |
| tee_boxes | 4 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 3 |
| of_par4_5 | 3 |
| mean_landing_osm_share | 0.256 |
| mean_confidence | 0.528 |
| osm_score | 0.551 |

OSM features inside the course: buildings 3, golf=bunker 7, golf=cartpath 4, golf=fairway 3, golf=green 1, golf=hole 3, golf=pin 1, golf=tee 4, holes_with_handicap 3, holes_with_par 3, single_trees 74, trees_polygons 2

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| Black - 13 | 5 | 604 / 604 | 204 | 0.60 | check the flags | 49% | 4% | 46% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it) |
| Black - 4 | 5 | 518 / 518 | 46 | 0.43 | needs review | 0% | 20% | 80% | hole-line start (no golf=tee near it) | tee: hole-line start (no golf=tee near it); green from the hole-line end (no golf=green polygon); no fairway in the landing zone |
| Black - 5 | 4 | 478 / 478 | 14 | 0.55 | needs review | 28% | 20% | 52% | tee nearest the hole-line start | tee: tee nearest the hole-line start; green from the hole-line end (no golf=green polygon) |

## Stages

- **resolve**: ok: node/2854158382 Bethpage Black (Old Bethpage, NY)
- **osm**: ok: 103 features
- **routing**: fallback: geometry/build_holes.infer_holes (structure: RuntimeError: no OSM greens and no perception scene; v2: RuntimeError: routing v2: no greens)
- **scorecard**: missing
- **tees**: fallback: OSM tee nearest the hole-line start (no yardages)
- **geometry**: ok: geometry/build_holes.py (3 holes, 1 tee set(s))
- **imagery**: ok: course_data/packages/bethpage_state_park/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 1/1 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/bethpage_state_park/imagery/dem.tif (0/3 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: failed: TypeError: 'float' object is not subscriptable

## Warnings

- hole inference fallback: structure: RuntimeError: no OSM greens and no perception scene
- hole inference fallback: v2: RuntimeError: routing v2: no greens
- no scorecard (request yardages, card file, golfify, club site all missing): tee = the OSM tee box nearest each hole-line start (usually the back tee); lengths are measured
