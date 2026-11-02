# Sand Creek Station (Newton, KS) - Championship tees

Built 2026-11-02T18:07:28Z. OSM relation/6702217. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Championship, Tournament, Medal, Ladies (L))).

**WARNING: requested tee set 'Black' is not on the card; using 'Championship' instead (allow_substitute). Sets on the card: Championship, Tournament, Medal, Ladies (L)**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 18 |
| greens_found | 18 |
| tee_boxes | 69 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 11 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.549 |
| mean_confidence | 0.852 |
| osm_score | 0.867 |

OSM features inside the course: buildings 34, built_up_landuse 1, golf=bunker 62, golf=cartpath 11, golf=driving_range 1, golf=fairway 22, golf=green 18, golf=hole 18, golf=rough 41, golf=tee 69, golf=water_hazard 15, holes_with_par 18, long_grass_polygons 31, trees_polygons 6, water_lines 1, water_polygons 16

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 474 / 473 | 23 | 0.72 | check the flags | 46% | 4% | 49% | tee stage: Championship lidar_pad | tee: tee stage: Championship lidar_pad; Championship tee on a lidar pad (no OSM box at 474 yds) |
| 2 | 5 | 613 / 613 | 212 | 0.78 | check the flags | 24% | 31% | 46% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 3 | 3 | 178 / 178 | 264 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 4 | 5 | 601 / 599 | 280 | 0.85 | auto | 72% | 0% | 28% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 5 | 4 | 345 / 345 | 152 | 0.83 | auto | 64% | 0% | 36% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 6 | 4 | 467 / 467 | 129 | 0.85 | auto | 72% | 0% | 28% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 7 | 3 | 229 / 229 | 134 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 8 | 4 | 470 / 469 | 8 | 0.91 | auto | 79% | 2% | 19% | tee stage: Championship tee_centroid |  |
| 9 | 4 | 373 / 373 | 28 | 0.86 | auto | 44% | 26% | 30% | tee stage: Championship tee_centroid |  |
| 10 | 5 | 648 / 647 | 194 | 0.74 | check the flags | 58% | 0% | 42% | tee stage: Championship lidar_pad | tee: tee stage: Championship lidar_pad; no trees or long grass mapped in the landing zone (unmapped hazards play as rough); Championship tee on a lidar pad (no OSM box at 648 yds) |
| 11 | 4 | 364 / 365 | 85 | 0.81 | auto | 36% | 14% | 50% | tee stage: Championship tee_centroid |  |
| 12 | 4 | 420 / 419 | 81 | 0.80 | auto | 54% | 0% | 46% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 13 | 3 | 230 / 231 | 262 | 0.96 | auto | 100% | 0% | 0% | tee stage: Championship tee_centroid |  |
| 14 | 4 | 484 / 483 | 3 | 0.83 | auto | 52% | 0% | 48% | tee stage: Championship tee_centroid | no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 15 | 4 | 382 / 382 | 59 | 0.82 | auto | 54% | 12% | 34% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 16 | 5 | 525 / 526 | 263 | 0.86 | auto | 60% | 4% | 36% | tee stage: Championship tee_centroid |  |
| 17 | 3 | 138 / 138 | 80 | 0.93 | auto | 100% | 0% | 0% | tee stage: Championship tee_axis | tee: tee stage: Championship tee_axis |
| 18 | 4 | 426 / 425 | 201 | 0.84 | auto | 54% | 0% | 46% | tee stage: Championship tee_centroid |  |

## Stages

- **resolve**: ok: relation/6702217 Sand Creek Station (Newton, KS)
- **osm**: ok: 520 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 94 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 4 tee set(s))
- **imagery**: ok: course_data/packages/sand_creek_station/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2023)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2023
- **elevation**: ok: course_data/packages/sand_creek_station/imagery/dem.tif (18/18 holes)
- **vision**: missing: product layer vision_any/2 not built for 'sand_creek_station' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 197 long-grass zones dropped); CHECK: build it with course_data/vision_any/build_layers.py sand_creek_station (course_package.yml does on a fetch)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 25 polygons (outside 25); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Championship' instead (allow_substitute). Sets on the card: Championship, Tournament, Medal, Ladies (L)
- CHECK vision: missing: product layer vision_any/2 not built for 'sand_creek_station' (fell back to vision_any/1 (lidar canopy + NAIP native, OSM-self-supervise from raw/ on the fly: trees / water kept, 197 long-gra; trees / water come from OSM (or the fallback) only
