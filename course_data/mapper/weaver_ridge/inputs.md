# Mapper inputs: WeaverRidge Golf Club (Peoria, IL)

Base package: `course_data/mapper/weaver_ridge/base/package.json` (built 2026-11-02T23:42:23Z; committed package: tees rebuilt: 0 tee(s) moved; guard kept 1 package tee(s): 5 Black: measured 325 vs card 387 (16% > 15%; package 6%)). Corridor set **Black**. Sets: Black, Gold, Green, White, Red.
Photo NAIP 2019; other years: NAIP 2023, NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 80 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 540 | tee_axis, 0.8 | Black 540, Gold 518, Green 500, White 454, Red 426 | fairway 6999, recovery 234, sand 245 | L1: 593, 26.7, L2: 366, 20.9, R1: 518, 22.6 |
| 2 | 4 | 391 | tee_centroid, 0.9 | Black 391, Gold 365, Green 351, White 254, Red 241 | fairway 6388, recovery 350, sand 171 | L1: 917, 16.9, L2: 672, 21.5, R1: 238, 26.8 |
| 3 | 5 | 519 | tee_axis, 0.8 | Black 519, Gold 494, Green 475, White 449, Red 419 | fairway 5685, recovery 389, sand 505 | L1: 160, 31.5, L2: 859, 9.9, L3: 736, 8.9, R1: 338, 6.0 |
| 5 | 4 | 387 | review (inside OSM tee 749315882), 0.4 | Black 387, Gold 362, Green 297, White 260, Red 232 | fairway 2749, recovery 452, sand 298, water 7347 | L1: 167, 37.5, L2: 217, 47.4, L3: 284, 10.9, L4: 366, 32.8 |
| 6 | 4 | 388 | tee_centroid, 0.9 | Black 388, Gold 357, Green 331, White 306, Red 268 | fairway 4479, recovery 1271, sand 257, water 1194 | L1: 440, 13.4, R1: 319, 16.6 |
| 7 | 4 | 435 | tee_centroid, 0.9 | Black 435, Gold 401, Green 385, White 372, Red 357 | fairway 5552, ob 1296, recovery 688, sand 406, water 501 | L1: 178, 30.1, L2: 581, 22.4, L3: 488, 8.5 |
| 9 | 4 | 381 | tee_centroid, 0.9 | Black 381, Gold 357, Green 340, White 329, Red 307 | fairway 4586, ob 218, recovery 1157, sand 247, water 12 | R1: 1123, 2.9, R2: 235, 31.6 |
| 10 | 4 | 418 | tee_centroid, 0.9 | Black 418, Gold 387, Green 367, White 341, Red 313 | fairway 3843, ob 57, recovery 3071, water 2094 | none |
| 11 | 5 | 489 | tee_axis, 0.8 | Black 489, Gold 482, Green 447, White 406, Red 384 | fairway 4964, ob 99, recovery 2347, water 3518 | R1: 962, 6.6, R2: 286, 22.6 |
| 13 | 4 | 432 | tee_axis, 0.8 | Black 432, Gold 401, Green 349, White 323, Red 308 | fairway 6523, recovery 1577, water 359 | R1: 357, 19.3 |
| 14 | 4 | 406 | tee_axis, 0.8 | Black 406, Gold 362, Green 313, White 288, Red 276 | fairway 5208, recovery 4536, sand 141 | none |
| 15 | 4 | 458 | tee_axis, 0.8 | Black 458, Gold 424, Green 390, White 361, Red 332 | fairway 7919, recovery 275, sand 269 | L1: 824, 15.5, L2: 653, 5.4 |
| 16 | 4 | 401 | tee_axis, 0.8 | Black 401, Gold 401, Green 375, White 353, Red 321 | fairway 6803, recovery 244, sand 560 | L1: 200, 16.9, L2: 224, 22.1, R1: 218, 13.0 |
| 18 | 5 | 556 | tee_axis, 0.8 | Black 556, Gold 535, Green 465, White 435, Red 424 | fairway 6162, recovery 3512, sand 172, water 2459 | R1: 315, 33.3, R2: 594, 22.7 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
