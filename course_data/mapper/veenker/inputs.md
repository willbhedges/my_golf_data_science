# Mapper inputs: Veenker Memorial Golf Course (Ames, IA)

Base package: `course_data/mapper/veenker/base/package.json` (built 2026-11-02T02:40:58Z; committed package: tees rebuilt: 5 tee(s) moved). Corridor set **Blue**. Sets: Blue, Gold, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture+segment pads, joint chain assignment) for 3 sets; lidar pads: 36 candi; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: ok: segment gap-fill ariadgolf-v4@43ee2944 (+3 zones on 2 holes, +0 greens, 22 tee candidates); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 435 | tee_axis, 0.8 | Blue 435, Gold 419, Red 400 | fairway 5087, recovery 1323 |
| 2 | 4 | 334 | tee_centroid, 0.9 | Blue 334, Gold 283, Red 257 | fairway 2799, recovery 6410 |
| 3 | 4 | 333 | tee_centroid, 0.8 | Blue 333, Gold 289, Red 203 | fairway 3936, recovery 3478, sand 55 |
| 4 | 4 | 349 | tee_axis, 0.8 | Blue 349, Gold 340, Red 330 | fairway 4950, recovery 3690, sand 212 |
| 5 | 4 | 402 | tee_centroid, 0.9 | Blue 402, Gold 350, Red 319 | fairway 2694, ob 69, recovery 2666, water 1872 |
| 7 | 5 | 590 | lidar_pad_capped, 0.6 | Blue 590, Gold 570, Red 530 | fairway 2333, recovery 3464, water 452 |
| 9 | 5 | 537 | tee_centroid, 0.9 | Blue 537, Gold 495, Red 432 | fairway 4974, recovery 804 |
| 10 | 5 | 520 | tee_centroid, 0.9 | Blue 520, Gold 473, Red 459 | fairway 3863, recovery 2541 |
| 12 | 4 | 330 | tee_axis, 0.8 | Blue 330, Gold 306, Red 290 | fairway 3200, ob 154, recovery 2124, sand 92, water 562 |
| 14 | 4 | 416 | tee_axis, 0.8 | Blue 416, Gold 397, Red 346 | fairway 4094, recovery 2758 |
| 15 | 4 | 420 | tee_axis, 0.8 | Blue 420, Gold 386, Red 344 | fairway 3224, recovery 2790, water 2085 |
| 16 | 5 | 544 | lidar_pad, 0.6 | Blue 544, Gold 485, Red 368 | fairway 3150, recovery 3761, water 1939 |
| 18 | 5 | 534 | tee_axis, 0.8 | Blue 534, Gold 521, Red 407 | fairway 4271, recovery 1404 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
