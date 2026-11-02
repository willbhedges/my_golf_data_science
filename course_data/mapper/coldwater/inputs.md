# Mapper inputs: Coldwater Golf Links (Ames, IA)

Base package: `course_data/mapper/coldwater/base/package.json` (built 2026-11-02T02:35:19Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Blue**. Sets: Black, Blue, White, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 74 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 307 | tee_axis, 0.8 | Black 323, Blue 307, White 290, Red 238 | fairway 6715, ob 1205, sand 516, water 1772 |
| 2 | 4 | 425 | lidar_pad, 0.6 | Black 460, Blue 425, White 397, Red 317 | fairway 5254, recovery 1219, sand 7, water 189 |
| 3 | 5 | 510 | tee_centroid, 0.9 | Black 534, Blue 510, White 472, Red 402 | fairway 8980, sand 156 |
| 4 | 4 | 371 | tee_centroid, 0.9 | Black 395, Blue 371, White 341, Red 287 | fairway 8028 |
| 6 | 4 | 418 | walkback, 0.5 | Black 449, Blue 418, White 399, Red 338 | fairway 6726, sand 53 |
| 7 | 5 | 505 | tee_axis, 0.8 | Black 528, Blue 505, White 482, Red 432 | fairway 6728, recovery 664, sand 182, water 17 |
| 9 | 4 | 371 | tee_axis, 0.8 | Black 390, Blue 371, White 341, Red 316 | fairway 6847, sand 202, water 4550 |
| 10 | 4 | 396 | tee_axis, 0.8 | Black 424, Blue 396, White 363, Red 306 | fairway 6698, sand 105 |
| 12 | 4 | 328 | tee_axis, 0.8 | Black 350, Blue 328, White 294, Red 258 | fairway 6866, sand 135, water 508 |
| 13 | 4 | 413 | tee_axis, 0.8 | Black 429, Blue 413, White 396, Red 309 | fairway 6856, sand 348 |
| 14 | 5 | 476 | tee_axis, 0.8 | Black 505, Blue 476, White 445, Red 372 | fairway 5385, recovery 1667, sand 123 |
| 15 | 4 | 417 | tee_axis, 0.8 | Black 453, Blue 417, White 381, Red 321 | fairway 6395, recovery 1104 |
| 17 | 4 | 395 | tee_axis, 0.8 | Black 415, Blue 395, White 376, Red 320 | fairway 4965, sand 253, water 108 |
| 18 | 4 | 433 | tee_axis, 0.8 | Black 453, Blue 433, White 409, Red 366 | fairway 7473, sand 308, water 18 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
