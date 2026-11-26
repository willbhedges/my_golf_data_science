# Brown Deer Golf Club (Coralville, IA) - Gold tees

Built 2026-11-26T22:14:47Z. OSM way/191258543. Scorecard: file (course_data/library/brown_deer/routed_card.json). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Gold, Blue, White, Red)).

**WARNING: requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 127 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 13 |
| mean_landing_osm_share | 0.445 |
| mean_confidence | 0.833 |
| osm_score | 0.874 |

OSM features inside the course: buildings 5, built_up_landuse 2, golf=bunker 38, golf=cartpath 21, golf=clubhouse 1, golf=driving_range 1, golf=fairway 17, golf=green 20, golf=hole 18, golf=lateral_water_hazard 10, golf=path 1, golf=tee 127, golf=water_hazard 2, holes_with_par 18, trees_polygons 7, water_lines 2, water_polygons 12

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 329 / 329 | 348 | 0.77 | check the flags | 41% | 5% | 54% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 2 | 5 | 559 / 559 | 333 | 0.84 | auto | 54% | 4% | 43% | tee stage: Gold tee_centroid |  |
| 3 | 4 | 326 / 326 | 330 | 0.81 | auto | 38% | 10% | 53% | tee stage: Gold tee_centroid |  |
| 4 | 5 | 513 / 514 | 109 | 0.77 | check the flags | 39% | 3% | 58% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 3 | 182 / 182 | 194 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 6 | 4 | 405 / 405 | 134 | 0.80 | auto | 50% | 7% | 43% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 4 | 383 / 383 | 122 | 0.76 | check the flags | 39% | 0% | 61% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 8 | 4 | 414 / 415 | 293 | 0.83 | auto | 63% | 3% | 34% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 3 | 246 / 246 | 126 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 10 | 5 | 480 / 480 | 196 | 0.73 | check the flags | 55% | 0% | 45% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 480 yds) |
| 11 | 4 | 357 / 357 | 130 | 0.80 | check the flags | 24% | 40% | 36% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 12 | 3 | 200 / 200 | 310 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 4 | 275 / 276 | 280 | 0.82 | auto | 29% | 29% | 42% | tee stage: Gold tee_centroid |  |
| 14 | 3 | 120 / 120 | 19 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 15 | 5 | 496 / 496 | 354 | 0.75 | check the flags | 26% | 14% | 60% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 16 | 4 | 459 / 337 | 155 | 0.74 | check the flags | 28% | 57% | 15% | tee stage: Gold walkback_capped | tee: tee stage: Gold walkback_capped; Gold tee walked back along the hole line (no box at 459 yds) |
| 17 | 3 | 178 / 176 | 95 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 18 | 4 | 393 / 394 | 61 | 0.91 | auto | 94% | 0% | 6% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no fairway in the landing zone |

## Stages

- **resolve**: ok: way/191258543 Brown Deer Golf Club (Coralville, IA)
- **osm**: ok: 612 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/brown_deer/routed_card.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 57 candidate pads near hole starts (20 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/brown_deer/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2025
- **elevation**: ok: course_data/packages/brown_deer/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -2 m2 {'cells': 2}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: ok: 0/1 hole(s) without a mapped fairway filled from NAIP (d' 3.23; gated: 18)
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings+parcels; 32 polygons (property_line 32); mode replace
- **native_auto**: none: course gate shut: 4% of sides >= 0.675 (< 25%)

## Warnings

- ignored 2 practice / driving-range tee box(es): OSM -61, -83
- requested tee set 'Black' is not on the card; using 'Gold' instead (allow_substitute). Sets on the card: Gold, Blue, White, Red
- hole 16 Gold: CHECK, walk-back ran onto a residential (OSM 795398931) 74 yds behind the line start: capped there (122 yds short of the card)
- hole 16: measured 337 vs card 459 yds for Gold (no OSM tee box at that yardage?)
