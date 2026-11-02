# Mapper inputs: Ellis Golf Course (Cedar Rapids, IA)

Base package: `course_data/mapper/ellis/base/package.json` (built 2026-11-02T02:35:39Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Blue**. Sets: Blue, White, Gold, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 60 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 395 | tee_centroid, 0.9 | Blue 395, White 383, Gold 336, Red 324 | fairway 3548, recovery 894, sand 5 |
| 2 | 4 | 365 | tee_centroid, 0.9 | Blue 365, White 348, Gold 319, Red 309 | fairway 4245, recovery 1152, sand 223 |
| 3 | 5 | 481 | tee_axis, 0.8 | Blue 481, White 472, Gold 462, Red 394 | fairway 4740, ob 501, recovery 2024 |
| 5 | 4 | 385 | tee_centroid, 0.9 | Blue 385, White 366, Gold 353, Red 254 | fairway 4826, recovery 593, sand 311 |
| 6 | 4 | 420 | lidar_pad, 0.6 | Blue 420, White 390, Gold 360, Red 340 | fairway 4508, sand 385 |
| 7 | 4 | 463 | tee_axis, 0.8 | Blue 463, White 434, Gold 306, Red 296 | fairway 5570, recovery 249 |
| 9 | 5 | 534 | tee_centroid, 0.9 | Blue 534, White 502, Gold 469, Red 390 | fairway 3749, ob 1093, recovery 333 |
| 10 | 4 | 321 | tee_centroid, 0.9 | Blue 321, White 303, Gold 281, Red 264 | fairway 3816, recovery 1386, sand 469 |
| 12 | 5 | 519 | tee_centroid, 0.9 | Blue 519, White 497, Gold 484, Red 400 | fairway 4308, recovery 3873 |
| 13 | 4 | 350 | tee_axis, 0.8 | Blue 350, White 338, Gold 316, Red 301 | fairway 2698, ob 4374, recovery 825 |
| 15 | 4 | 306 | tee_axis, 0.8 | Blue 306, White 283, Gold 263, Red 246 | fairway 2945, recovery 572 |
| 16 | 4 | 314 | tee_axis, 0.8 | Blue 314, White 303, Gold 266, Red 216 | fairway 3546, recovery 1817, sand 150 |
| 17 | 5 | 569 | tee_centroid, 0.9 | Blue 569, White 536, Gold 519, Red 325 | fairway 3583, recovery 811, sand 168 |
| 18 | 4 | 418 | tee_axis, 0.8 | Blue 418, White 386, Gold 349, Red 315 | fairway 5567, recovery 2593, sand 304, water 470 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
