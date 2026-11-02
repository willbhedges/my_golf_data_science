# Mapper inputs: Blue Hills Country Club (Kansas City, MO)

Base package: `course_data/mapper/blue_hills/base/package.json` (built 2026-10-24T18:19:59Z; committed package: tees rebuilt: 11 tee(s) moved). Corridor set **Black**. Sets: Black, Blue, Blue/White, White, White/Gold, Gold, Gold/Red, Red (M), Red (L).
Photo NAIP 2021; other years: NAIP 2023, NAIP 2022; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 9 sets; lidar pads: 52 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 5 | 523 | tee_axis, 0.8 | Black 523, Blue 513, Blue/White 513, White 483, White/Gold 483, Gold 483, Gold/Red 483, Red (M) 458, Red (L) 458 | fairway 4618, ob 2473, recovery 3413, sand 433 |
| 2 | 4 | 419 | tee_axis, 0.6 | Black 419, Blue 402, Blue/White 402, White 380, White/Gold 380, Gold 349, Gold/Red 349, Red (M) 299, Red (L) 299 | fairway 3547, ob 2883, recovery 2357, sand 98 |
| 3 | 4 | 405 | tee_centroid, 0.9 | Black 405, Blue 387, Blue/White 387, White 365, White/Gold 365, Gold 360, Gold/Red 360, Red (M) 305, Red (L) 305 | fairway 3979, ob 17, recovery 3960 |
| 4 | 4 | 446 | tee_axis, 0.8 | Black 446, Blue 440, Blue/White 417, White 417, White/Gold 390, Gold 390, Gold/Red 302, Red (M) 302, Red (L) 302 | fairway 3553, ob 3494, recovery 3744 |
| 6 | 5 | 567 | tee_axis, 0.8 | Black 567, Blue 556, Blue/White 529, White 529, White/Gold 483, Gold 483, Gold/Red 483, Red (M) 422, Red (L) 422 | fairway 3257, recovery 2208 |
| 7 | 4 | 417 | tee_axis, 0.8 | Black 417, Blue 398, Blue/White 398, White 378, White/Gold 378, Gold 351, Gold/Red 351, Red (M) 347, Red (L) 347 | fairway 4490, ob 789, recovery 3418, sand 255 |
| 9 | 4 | 441 | tee_axis, 0.8 | Black 441, Blue 433, Blue/White 403, White 403, White/Gold 387, Gold 387, Gold/Red 387, Red (M) 277, Red (L) 277 | fairway 4093, ob 2560, recovery 2383, sand 312 |
| 10 | 4 | 397 | tee_axis, 0.8 | Black 397, Blue 382, Blue/White 382, White 352, White/Gold 352, Gold 315, Gold/Red 315, Red (M) 306, Red (L) 306 | fairway 3834, ob 1380, recovery 3696, sand 108 |
| 11 | 4 | 384 | tee_axis, 0.8 | Black 384, Blue 361, Blue/White 361, White 321, White/Gold 321, Gold 320, Gold/Red 320, Red (M) 311, Red (L) 311 | fairway 2986, ob 1963, recovery 3209 |
| 13 | 5 | 560 | tee_axis, 0.8 | Black 560, Blue 532, Blue/White 502, White 502, White/Gold 502, Gold 454, Gold/Red 454, Red (M) 444, Red (L) 444 | fairway 3632, recovery 3312, sand 104 |
| 15 | 4 | 460 | tee_axis, 0.8 | Black 460, Blue 450, Blue/White 424, White 424, White/Gold 403, Gold 403, Gold/Red 332, Red (M) 332, Red (L) 332 | fairway 4285, recovery 4213 |
| 16 | 4 | 456 | tee_axis, 0.8 | Black 456, Blue 446, Blue/White 420, White 420, White/Gold 384, Gold 384, Gold/Red 346, Red (M) 346, Red (L) 346 | fairway 4117, recovery 3749 |
| 17 | 4 | 449 | tee_axis, 0.8 | Black 449, Blue 412, Blue/White 412, White 387, White/Gold 360, Gold 360, Gold/Red 274, Red (M) 274, Red (L) 274 | fairway 4854, recovery 3843 |
| 18 | 5 | 627 | tee_axis, 0.8 | Black 627, Blue 562, Blue/White 528, White 528, White/Gold 462, Gold 462, Gold/Red 412, Red (M) 412, Red (L) 412 | fairway 2796, ob 4265, recovery 1490, sand 104 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
