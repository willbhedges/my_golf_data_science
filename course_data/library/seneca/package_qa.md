# Seneca Golf Course (Louisville, KY) - Blue tees

Built 2026-11-01T22:01:27Z. OSM way/59714994. Scorecard: golfify (golfify). Tee set: substitute: longest set (tee set 'Black' not on the card (sets: Blue, White, Yellow, Green, Red, Pink, Orange)).

**WARNING: requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Yellow, Green, Red, Pink, Orange**

## Coverage

| | |
|---|---|
| holes_built | 18 |
| holes_mapped | 27 |
| greens_found | 18 |
| tee_boxes | 86 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 14 |
| mean_landing_osm_share | 0.235 |
| mean_confidence | 0.729 |
| osm_score | 0.818 |

OSM features inside the course: buildings 10, golf=bunker 23, golf=cartpath 25, golf=clubhouse 1, golf=driving_range 2, golf=fairway 28, golf=green 30, golf=hole 27, golf=pin 10, golf=tee 86, holes_with_handicap 18, holes_with_par 27, tees_with_ref 83, trees_polygons 3, water_lines 1, water_polygons 3

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 426 / 425 | 339 | 0.64 | check the flags | 24% | 14% | 62% | tee stage: Blue walkback | tee: tee stage: Blue walkback; no fairway in the landing zone; Blue tee walked back along the hole line (no box at 426 yds) |
| 2 | 4 | 412 / 93 | 65 | 0.63 | check the flags | 19% | 16% | 65% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 412 yds) |
| 3 | 5 | 586 / 296 | 112 | 0.60 | needs review | 6% | 18% | 75% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 586 yds) |
| 4 | 3 | 217 / 217 | 51 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 5 | 4 | 463 / 189 | 194 | 0.58 | needs review | 1% | 18% | 81% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 463 yds) |
| 6 | 4 | 397 / 370 | 356 | 0.58 | needs review | 3% | 13% | 84% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 397 yds) |
| 7 | 5 | 564 / 384 | 267 | 0.58 | needs review | 4% | 12% | 83% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 564 yds) |
| 8 | 3 | 149 / 148 | 294 | 0.79 | check the flags | 100% | 0% | 0% | tee stage: Blue texture_pad | tee: tee stage: Blue texture_pad; Blue tee on an imagery-detected pad (texture; no OSM box at 149 yds) |
| 9 | 4 | 320 / 99 | 219 | 0.61 | check the flags | 20% | 3% | 77% | tee stage: Blue walkback_capped | tee: tee stage: Blue walkback_capped; Blue tee walked back along the hole line (no box at 320 yds) |
| 10 | 5 | 577 / 576 | 317 | 0.70 | check the flags | 19% | 0% | 81% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 11 | 4 | 390 / 390 | 56 | 0.82 | auto | 60% | 4% | 37% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 12 | 4 | 346 / 346 | 203 | 0.76 | check the flags | 32% | 8% | 60% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 13 | 3 | 213 / 213 | 19 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 14 | 4 | 438 / 437 | 188 | 0.74 | check the flags | 31% | 3% | 66% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 15 | 5 | 565 / 565 | 42 | 0.74 | check the flags | 32% | 0% | 68% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis; no trees or long grass mapped in the landing zone (unmapped hazards play as rough) |
| 16 | 3 | 206 / 206 | 140 | 0.93 | auto | 100% | 0% | 0% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 17 | 4 | 399 / 400 | 287 | 0.78 | check the flags | 44% | 5% | 51% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |
| 18 | 4 | 442 / 442 | 235 | 0.76 | check the flags | 34% | 9% | 57% | tee stage: Blue tee_axis | tee: tee stage: Blue tee_axis |

## Stages

- **resolve**: ok: way/59714994 Seneca Golf Course (Louisville, KY)
- **osm**: ok: 1558 features
- **routing**: not needed: OSM has a golf=hole way for every hole
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 23 candidate pads near hole starts
- **geometry**: ok: geometry/build_holes.py (18 holes, 7 tee set(s))
- **imagery**: ok: course_data/packages/seneca/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2022)
- **green_visibility**: ok: 18/18 greens visible as turf on NAIP 2022
- **elevation**: ok: course_data/packages/seneca/imagery/dem.tif (18/18 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer)
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 11 polygons (outside 11); mode replace

## Warnings

- requested tee set 'Black' is not on the card; using 'Blue' instead (allow_substitute). Sets on the card: Blue, White, Yellow, Green, Red, Pink, Orange
- hole 9 Blue: CHECK, walk-back ran onto a green (OSM 824425846) 26 yds behind the line start: capped there (222 yds short of the card)
- hole 9 White: CHECK, walk-back ran onto a green (OSM 824425846) 26 yds behind the line start: capped there (201 yds short of the card)
- hole 9 Yellow: CHECK, walk-back ran onto a green (OSM 824425846) 26 yds behind the line start: capped there (176 yds short of the card)
- hole 9 Green: CHECK, walk-back ran onto a green (OSM 824425846) 26 yds behind the line start: capped there (159 yds short of the card)
- hole 9 Red: CHECK, walk-back ran onto a green (OSM 824425846) 26 yds behind the line start: capped there (141 yds short of the card)
- hole 9 Pink: CHECK, walk-back ran onto a green (OSM 824425846) 26 yds behind the line start: capped there (137 yds short of the card)
- hole 7 Blue: CHECK, walk-back ran onto a road (OSM 16233533) 300 yds behind the line start: capped there (181 yds short of the card)
- hole 7 White: CHECK, walk-back ran onto a road (OSM 16233533) 300 yds behind the line start: capped there (162 yds short of the card)
- hole 7 Yellow: CHECK, walk-back ran onto a road (OSM 16233533) 300 yds behind the line start: capped there (133 yds short of the card)
- hole 7 Green: CHECK, walk-back ran onto a road (OSM 16233533) 300 yds behind the line start: capped there (75 yds short of the card)
- hole 7 Red: CHECK, walk-back ran onto a road (OSM 16233533) 300 yds behind the line start: capped there (24 yds short of the card)
- hole 6 Blue: CHECK, walk-back ran onto a green (OSM 824425856) 304 yds behind the line start: capped there (26 yds short of the card)
- hole 6 White: CHECK, walk-back ran onto a green (OSM 824425856) 304 yds behind the line start: capped there (9 yds short of the card)
- hole 5 Blue: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (274 yds short of the card)
- hole 5 White: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (239 yds short of the card)
- hole 5 Yellow: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (211 yds short of the card)
- hole 5 Green: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (171 yds short of the card)
- hole 5 Red: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (114 yds short of the card)
- hole 5 Pink: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (68 yds short of the card)
- hole 5 Orange: CHECK, walk-back ran onto a road (OSM 16242375) 104 yds behind the line start: capped there (68 yds short of the card)
- hole 3 Blue: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (291 yds short of the card)
- hole 3 White: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (240 yds short of the card)
- hole 3 Yellow: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (225 yds short of the card)
- hole 3 Green: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (167 yds short of the card)
- hole 3 Red: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (114 yds short of the card)
- hole 3 Pink: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (45 yds short of the card)
- hole 3 Orange: CHECK, walk-back ran onto a road (OSM 16242375) 226 yds behind the line start: capped there (45 yds short of the card)
- hole 2 Blue: CHECK, walk-back ran onto a green (OSM 1001887250) 30 yds behind the line start: capped there (320 yds short of the card)
- hole 2 White: CHECK, walk-back ran onto a green (OSM 1001887250) 30 yds behind the line start: capped there (310 yds short of the card)
- hole 2 Yellow: CHECK, walk-back ran onto a green (OSM 1001887250) 30 yds behind the line start: capped there (227 yds short of the card)
- hole 2 Green: CHECK, walk-back ran onto a green (OSM 1001887250) 30 yds behind the line start: capped there (208 yds short of the card)
- hole 2 Red: CHECK, walk-back ran onto a green (OSM 1001887250) 30 yds behind the line start: capped there (189 yds short of the card)
- hole 2 Pink: CHECK, walk-back ran onto a green (OSM 1001887250) 30 yds behind the line start: capped there (182 yds short of the card)
- hole 2: measured 93 vs card 412 yds for Blue (no OSM tee box at that yardage?)
- hole 3: measured 296 vs card 586 yds for Blue (no OSM tee box at that yardage?)
- hole 5: measured 189 vs card 463 yds for Blue (no OSM tee box at that yardage?)
- hole 6: measured 370 vs card 397 yds for Blue (no OSM tee box at that yardage?)
- hole 7: measured 384 vs card 564 yds for Blue (no OSM tee box at that yardage?)
- hole 9: measured 99 vs card 320 yds for Blue (no OSM tee box at that yardage?)
