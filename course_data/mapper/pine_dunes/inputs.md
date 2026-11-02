# Mapper inputs: Pine Dunes Resort & Golf Club (Frankston, TX)

Base package: `course_data/mapper/pine_dunes/base/package.json` (built 2026-10-17T19:14:29Z; committed package: tees rebuilt: 21 tee(s) moved). Corridor set **Gold**. Sets: Gold, Blue, White, Red.
Photo NAIP 2020; other years: NAIP 2022; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 0 candidate pads; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 391 | tagged, 1.0 | Gold 391, Blue 376, White 319, Red 287 | fairway 3692, recovery 6972, sand 204 |
| 2 | 4 | 348 | tagged, 1.0 | Gold 348, Blue 314, White 270, Red 232 | fairway 3428, recovery 4005, sand 184 |
| 4 | 4 | 463 | tagged, 1.0 | Gold 463, Blue 432, White 399, Red 370 | fairway 5220, recovery 5524, sand 54 |
| 5 | 5 | 501 | tagged, 1.0 | Gold 501, Blue 469, White 436, Red 400 | fairway 6268, recovery 4750, sand 1419 |
| 7 | 4 | 443 | tagged, 1.0 | Gold 443, Blue 409, White 367, Red 325 | fairway 5001, recovery 3717, sand 2613 |
| 8 | 4 | 389 | tagged, 1.0 | Gold 389, Blue 360, White 314, Red 263 | fairway 2474, recovery 6399, sand 946 |
| 9 | 5 | 551 | tagged, 1.0 | Gold 551, Blue 512, White 465, Red 428 | fairway 5120, recovery 5590, sand 305 |
| 10 | 4 | 439 | tagged, 1.0 | Gold 439, Blue 403, White 355, Red 317 | fairway 5966, recovery 4591, sand 373 |
| 11 | 5 | 605 | tagged, 1.0 | Gold 605, Blue 575, White 521, Red 450 | fairway 3092, recovery 2717, sand 1778 |
| 13 | 4 | 426 | tagged, 1.0 | Gold 426, Blue 395, White 355, Red 324 | fairway 5649, recovery 1961, sand 550, water 1144 |
| 14 | 4 | 434 | tagged, 1.0 | Gold 434, Blue 394, White 348, Red 318 | fairway 5732, recovery 3425, sand 352, water 994 |
| 15 | 4 | 344 | tagged, 1.0 | Gold 344, Blue 311, White 287, Red 263 | fairway 4430, recovery 3702, sand 890, water 653 |
| 17 | 4 | 475 | tagged, 1.0 | Gold 475, Blue 434, White 399, Red 295 | fairway 5358, recovery 5598 |
| 18 | 5 | 512 | tagged, 1.0 | Gold 512, Blue 480, White 434, Red 410 | fairway 5358, recovery 5006, sand 270, water 241 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
