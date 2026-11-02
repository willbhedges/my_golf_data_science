# Eagle Bend Golf Course (Lawrence, KS) - Gold tees

Built 2026-11-02T23:41:23Z. OSM way/151983193. Scorecard: file (course_data/library/eagle_bend/card_fix.json). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 74 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 10 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.362 |
| mean_confidence | 0.791 |
| osm_score | 0.815 |

OSM features inside the course: buildings 9, golf=bunker 23, golf=cartpath 24, golf=clubhouse 1, golf=driving_range 1, golf=fairway 24, golf=green 20, golf=hole 18, golf=pin 18, golf=tee 74, golf=water_hazard 4, holes_with_par 18, water_lines 7, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 411 / 412 | 101 | 0.82 | auto | 40% | 11% | 49% | tee stage: Gold tee_centroid |  |
| 2 | 4 | 362 / 360 | 82 | 0.73 | check the flags | 28% | 1% | 70% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 3 | 5 | 574 / 573 | 358 | 0.79 | check the flags | 34% | 22% | 45% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 4 | 3 | 163 / 163 | 274 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 5 | 4 | 383 / 382 | 186 | 0.81 | auto | 36% | 15% | 50% | tee stage: Gold tee_centroid |  |
| 6 | 4 | 460 / 456 | 275 | 0.81 | auto | 50% | 10% | 39% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 7 | 5 | 560 / 561 | 295 | 0.65 | check the flags | 34% | 7% | 60% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 560 yds) |
| 8 | 3 | 172 / 172 | 312 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 9 | 4 | 430 / 429 | 175 | 0.76 | check the flags | 30% | 15% | 55% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 10 | 4 | 417 / 418 | 86 | 0.71 | check the flags | 39% | 12% | 49% | tee stage: Gold lidar_pad | tee: tee stage: Gold lidar_pad; Gold tee on a lidar pad (no OSM box at 417 yds) |
| 11 | 4 | 385 / 386 | 92 | 0.74 | check the flags | 34% | 0% | 66% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 12 | 3 | 165 / 165 | 161 | 0.93 | auto | 100% | 0% | 0% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 13 | 5 | 610 / 611 | 285 | 0.73 | check the flags | 29% | 0% | 71% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 14 | 4 | 429 / 430 | 250 | 0.70 | check the flags | 44% | 17% | 40% | tee stage: Gold walkback | tee: tee stage: Gold walkback; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Gold tee walked back along the hole line (no box at 429 yds) |
| 15 | 4 | 340 / 341 | 81 | 0.73 | check the flags | 27% | 5% | 68% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 4 | 448 / 449 | 255 | 0.80 | check the flags | 38% | 20% | 42% | tee stage: Gold tee_axis | tee: tee stage: Gold tee_axis |
| 17 | 3 | 196 / 196 | 185 | 0.96 | auto | 100% | 0% | 0% | tee stage: Gold tee_centroid |  |
| 18 | 5 | 547 / 547 | 321 | 0.69 | check the flags | 46% | 6% | 48% | tee stage: Gold walkback | tee: tee stage: Gold walkback; Gold tee walked back along the hole line (no box at 547 yds) |

## Stages

- **resolve**: ok: way/151983193 Eagle Bend Golf Course (Lawrence, KS)
- **osm**: ok: 266 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: file (course_data/library/eagle_bend/card_fix.json)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 58 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/eagle_bend/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2021)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2021
- **elevation**: ok: course_data/packages/eagle_bend/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'eagle_bend' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 132 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py eagle_bend (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 0 polygons (); mode replace

## Warnings

- CHECK vision: missing: product layer vision_any/2 not built for 'eagle_bend' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 132 long-grass zones; trees / water come from OSM (or the fallback) only
