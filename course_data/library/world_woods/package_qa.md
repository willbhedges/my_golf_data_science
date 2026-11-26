# Cabot Citrus Farms ( Brooksville , FL) - Black tees

Built 2026-11-26T08:25:59Z. OSM way/410646892. Scorecard: golfify (golfify). Tee set: name.

## Coverage

| | |
|---|---|
| holes_built | 16 |
| holes_mapped | 16 |
| greens_found | 16 |
| tee_boxes | 163 |
| tees_with_colour | 0 |
| holes_with_trees_or_long_grass_in_landing_zone | 12 |
| of_par4_5 | 12 |
| mean_landing_osm_share | 0.296 |
| mean_confidence | 0.84 |
| osm_score | 0.831 |

OSM features inside the course: golf=bunker 144, golf=cartpath 27, golf=fairway 40, golf=green 39, golf=hole 16, golf=rough 1, golf=tee 163, golf=water_hazard 4, holes_with_par 16, water_polygons 4

## Holes

| hole | par | yds (card / measured) | bearing | score | band | OSM | imagery | inferred | tee | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 475 / 479 | 82 | 0.83 | auto | 33% | 42% | 25% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 3 | 3 | 292 / 238 | 119 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets; green not visible on the NAIP 2025 imagery (NDVI 0.023 vs 0.193 on the course's other greens: bare soil / construction); the outline is OSM's |
| 4 | 5 | 511 / 446 | 6 | 0.86 | auto | 55% | 28% | 17% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets; green not visible on the NAIP 2025 imagery (NDVI 0.02 vs 0.193 on the course's other greens: bare soil / construction); the outline is OSM's |
| 5 | 4 | 382 / 382 | 70 | 0.80 | check the flags | 8% | 45% | 47% | tee stage: Black tee_centroid |  |
| 6 | 5 | 563 / 557 | 331 | 0.80 | check the flags | 11% | 58% | 31% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 7 | 3 | 199 / 194 | 70 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 8 | 4 | 426 / 375 | 187 | 0.83 | auto | 47% | 26% | 27% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets |
| 9 | 4 | 421 / 420 | 14 | 0.70 | check the flags | 44% | 15% | 40% | tee stage: Black walkback | tee: tee stage: Black walkback; Black tee walked back along the hole line (no box at 421 yds) |
| 10 | 3 | 242 / 195 | 104 | 0.93 | auto | 100% | 0% | 0% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; green not visible on the NAIP 2025 imagery (NDVI 0.021 vs 0.193 on the course's other greens: bare soil / construction); the outline is OSM's |
| 11 | 4 | 427 / 423 | 280 | 0.80 | check the flags | 25% | 39% | 36% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; green not visible on the NAIP 2025 imagery (NDVI 0.069 vs 0.193 on the course's other greens: bare soil / construction); the outline is OSM's |
| 12 | 4 | 496 / 420 | 97 | 0.82 | auto | 36% | 34% | 30% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap |
| 14 | 5 | 581 / 581 | 48 | 0.82 | auto | 42% | 27% | 31% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |
| 15 | 4 | 388 / 393 | 61 | 0.81 | auto | 0% | 81% | 19% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis; no fairway in the landing zone |
| 16 | 3 | 201 / 201 | 104 | 0.96 | auto | 100% | 0% | 0% | tee stage: Black tee_centroid |  |
| 17 | 5 | 500 / 390 | 271 | 0.85 | auto | 34% | 54% | 13% | tee stage: Black tee_axis_far_cap | tee: tee stage: Black tee_axis_far_cap; Black tee out of order with the other sets |
| 18 | 4 | 489 / 488 | 224 | 0.77 | check the flags | 20% | 34% | 46% | tee stage: Black tee_axis | tee: tee stage: Black tee_axis |

## Stages

- **resolve**: ok: way/410646892 Cabot Citrus Farms (Hernando County, FL)
- **osm**: ok: 460 features
- **routing**: ok: v2+structure (mapped_card, lam 0.5, structure on osm) placed 16/18 holes OSM has no way for (11 to check; segment no, lidar pads 288, perception scene no)
- **scorecard**: ok: golfify (golfify)
- **tee_localizer**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment)
- **tees**: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 8 sets; lidar pads: 60 candidate pads near hole starts (7 on buildings / off the course dropped)
- **geometry**: ok: geometry/build_holes.py (16 holes, 8 tee set(s))
- **imagery**: ok: course_data/packages/world_woods/imagery (USDA NAIP via Microsoft Planetary Computer (collection 'naip'), 2025)
- **green_visibility**: ok: 12/16 greens visible as turf on NAIP 2025; NOT visible: holes 3, 4, 10, 11
- **elevation**: ok: course_data/packages/world_woods/imagery/dem.tif (16/16 holes)
- **vision**: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); water filter: false vision water -264 m2 {'strip': 264}
- **segment**: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json)
- **fairway_fill**: gated: mown / rough separation d' 0.63 < 1.0 (seeds 14999, rough 39365); no fairway filled
- **green_auto**: not needed: every hole has a mapped green
- **ob**: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms_buildings; 1 polygons (outside 1); mode replace
- **native_auto**: none: course gate shut: 0% of sides >= 0.675 (< 25%)

## Warnings

- hole 1: placed by v2+structure inference, golfer check (ambiguous (66% of the posterior))
- hole 3: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 4: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 5: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 6: placed by v2+structure inference, golfer check (ambiguous (80% of the posterior))
- hole 10: placed by v2+structure inference, golfer check (ambiguous (15% of the posterior))
- hole 11: placed by v2+structure inference, golfer check (ambiguous (47% of the posterior))
- hole 14: placed by v2+structure inference, golfer check (ambiguous (77% of the posterior))
- hole 15: placed by v2+structure inference, golfer check (ambiguous (92% of the posterior))
- hole 17: placed by v2+structure inference, golfer check (ambiguous (78% of the posterior))
- hole 18: placed by v2+structure inference, golfer check (ambiguous (83% of the posterior))
- hole 6 Blue(M): CHECK, tee was put 283 yds from this hole's start, at hole 9's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 6 Blue(W): CHECK, tee was put 283 yds from this hole's start, at hole 9's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 10 Green(M): CHECK, tee was put 64 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 10 Green(W): CHECK, tee was put 64 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 10 Blue(M): CHECK, tee was put 91 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 10 Blue(W): CHECK, tee was put 91 yds from this hole's start, at hole 11's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Yellow(M): CHECK, tee was put 72 yds from this hole's start, at hole 10's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Yellow(W): CHECK, tee was put 72 yds from this hole's start, at hole 10's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Green(M): CHECK, tee was put 104 yds from this hole's start, at hole 10's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 11 Green(W): CHECK, tee was put 104 yds from this hole's start, at hole 10's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 15 Green(M): CHECK, tee was put 138 yds from this hole's start, at hole 6's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 15 Green(W): CHECK, tee was put 138 yds from this hole's start, at hole 6's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 15 Blue(M): CHECK, tee was put 154 yds from this hole's start, at hole 6's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 15 Blue(W): CHECK, tee was put 154 yds from this hole's start, at hole 6's tee, to fit the card yardage: kept at the hole line's start (the card yardage does not fit this hole)
- hole 3: measured 238 vs card 292 yds for Black (no OSM tee box at that yardage?)
- hole 4: measured 446 vs card 511 yds for Black (no OSM tee box at that yardage?)
- hole 8: measured 375 vs card 426 yds for Black (no OSM tee box at that yardage?)
- hole 10: measured 195 vs card 242 yds for Black (no OSM tee box at that yardage?)
- hole 12: measured 420 vs card 496 yds for Black (no OSM tee box at that yardage?)
- hole 17: measured 390 vs card 500 yds for Black (no OSM tee box at that yardage?)
- greens of holes 3, 4, 10, 11 are not visible as turf on the NAIP 2025 imagery (bare soil / construction / dead turf): pick another NAIP year (imagery/naip_years.py)
- scorecard (golfify): 1 hole(s) where a longer set is shorter than the next set: 1 Yellow(W) 300 < Green(M) 334
- no fairway mapped on 2 hole(s) and the NAIP fairway fill did not run: gated: mown / rough separation d' 0.63 < 1.0 (seeds 14999, rough 39365); no fairway filled
