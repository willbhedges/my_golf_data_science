# Mapper inputs: Gateway National Golf Links (Madison, IL)

Base package: `course_data/mapper/gateway_national/base/package.json` (built 2026-11-02T02:35:57Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Back**. Sets: Back, Champions, Forward, Middle, The Tips.
Photo NAIP 2023; other years: NAIP 2022; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 70 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 376 | tee_axis, 0.8 | Back 376, Champions 401, Forward 302, Middle 354, The Tips 410 | fairway 7796, sand 202 |
| 2 | 4 | 422 | tee_centroid, 0.9 | Back 422, Champions 462, Forward 329, Middle 397, The Tips 469 | fairway 6755, recovery 13, sand 106, water 2168 |
| 3 | 5 | 630 | tee_centroid, 0.9 | Back 630, Champions 655, Forward 475, Middle 566, The Tips 661 | fairway 5236, ob 2146, recovery 315, sand 107 |
| 5 | 4 | 452 | tee_axis, 0.8 | Back 452, Champions 475, Forward 351, Middle 421, The Tips 482 | fairway 6162, sand 155 |
| 6 | 5 | 530 | tee_axis, 0.8 | Back 530, Champions 556, Forward 455, Middle 500, The Tips 560 | fairway 6576, recovery 1237, sand 180 |
| 8 | 4 | 408 | tee_axis, 0.8 | Back 408, Champions 417, Forward 300, Middle 378, The Tips 419 | fairway 5754, recovery 794, sand 121 |
| 9 | 4 | 390 | tee_centroid, 0.9 | Back 390, Champions 427, Forward 310, Middle 360, The Tips 430 | fairway 5139, recovery 340, sand 138, water 413 |
| 10 | 4 | 271 | tee_centroid, 0.9 | Back 271, Champions 315, Forward 202, Middle 251, The Tips 317 | fairway 6056, sand 148, water 1086 |
| 11 | 4 | 416 | tee_centroid, 0.9 | Back 416, Champions 442, Forward 330, Middle 394, The Tips 444 | fairway 6651 |
| 13 | 5 | 533 | tee_axis, 0.8 | Back 533, Champions 557, Forward 462, Middle 520, The Tips 562 | fairway 7102, sand 169, water 586 |
| 15 | 4 | 428 | tee_axis, 0.8 | Back 428, Champions 454, Forward 330, Middle 408, The Tips 458 | fairway 6992, sand 230 |
| 16 | 4 | 354 | tee_centroid, 0.9 | Back 354, Champions 384, Forward 274, Middle 325, The Tips 390 | fairway 6004, sand 117, water 988 |
| 18 | 5 | 527 | tee_axis, 0.8 | Back 527, Champions 545, Forward 391, Middle 494, The Tips 550 | fairway 7053, recovery 67, sand 266 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
