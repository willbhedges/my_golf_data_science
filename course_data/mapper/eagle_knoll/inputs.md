# Mapper inputs: Eagle Knoll Golf Club (Hartsburg, MO)

Base package: `course_data/mapper/eagle_knoll/base/package.json` (built 2026-11-02T02:35:28Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Back**. Sets: Eagle, Back, Middle, Forward.
Photo NAIP 2022; other years: NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 45 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 366 | tee_axis, 0.8 | Eagle 399, Back 366, Middle 346, Forward 327 | fairway 3402, recovery 5223, sand 45 |
| 3 | 4 | 397 | tee_centroid, 0.9 | Eagle 409, Back 397, Middle 361, Forward 203 | fairway 6670, recovery 2078, sand 173 |
| 4 | 4 | 399 | tee_axis, 0.8 | Eagle 416, Back 399, Middle 363, Forward 313 | fairway 5048, recovery 882 |
| 5 | 4 | 465 | tee_centroid, 0.9 | Eagle 473, Back 465, Middle 380, Forward 353 | fairway 4994, recovery 5098, sand 243 |
| 7 | 5 | 475 | tee_axis, 0.8 | Eagle 493, Back 475, Middle 451, Forward 390 | fairway 5908, recovery 4140 |
| 8 | 4 | 407 | tee_axis, 0.8 | Eagle 424, Back 407, Middle 376, Forward 322 | fairway 4462, recovery 1049, sand 561 |
| 9 | 5 | 510 | tee_axis, 0.8 | Eagle 526, Back 510, Middle 486, Forward 454 | fairway 4409, recovery 1294, sand 130 |
| 10 | 4 | 405 | tee_centroid, 0.9 | Eagle 420, Back 405, Middle 380, Forward 264 | fairway 4741, recovery 7320 |
| 11 | 4 | 441 | tee_axis, 0.8 | Eagle 448, Back 441, Middle 420, Forward 364 | fairway 4849, recovery 1027 |
| 13 | 5 | 546 | tee_axis, 0.8 | Eagle 556, Back 546, Middle 524, Forward 438 | fairway 6632, recovery 26 |
| 14 | 4 | 265 | tee_axis, 0.8 | Eagle 265, Back 265, Middle 246, Forward 215 | fairway 1430, recovery 5867, water 2087 |
| 15 | 4 | 447 | tee_axis, 0.8 | Eagle 459, Back 447, Middle 427, Forward 345 | fairway 5673, recovery 7847 |
| 17 | 5 | 489 | tee_axis, 0.8 | Eagle 499, Back 489, Middle 471, Forward 424 | fairway 5305, recovery 4988, water 2293 |
| 18 | 4 | 428 | tee_axis, 0.8 | Eagle 442, Back 428, Middle 405, Forward 353 | fairway 4623, ob 2445, recovery 2999 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
