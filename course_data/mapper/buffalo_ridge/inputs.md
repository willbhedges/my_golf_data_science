# Mapper inputs: Buffalo Ridge Springs Golf Course (Branson, MO)

Base package: `course_data/mapper/buffalo_ridge/base/package.json` (built 2026-11-02T02:34:05Z; committed package: tees rebuilt: 7 tee(s) moved). Corridor set **Buffalo**. Sets: Buffalo, Gold, Blue, Silver, Silver (L), Red, Red (L).
Photo NAIP 2020; other years: NAIP 2022; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 69 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 5 | 578 | tee_axis, 0.8 | Buffalo 578, Gold 547, Blue 521, Silver 497, Silver (L) 497, Red 460, Red (L) 460 | fairway 8468, sand 404 |
| 2 | 4 | 471 | tee_centroid, 0.9 | Buffalo 471, Gold 458, Blue 439, Silver 390, Silver (L) 410, Red 276, Red (L) 304 | fairway 5855, native 151, recovery 1022, sand 92, water 2124 |
| 3 | 4 | 405 | tee_centroid, 0.9 | Buffalo 405, Gold 385, Blue 357, Silver 333, Silver (L) 315, Red 300, Red (L) 300 | fairway 8096, sand 927 |
| 5 | 4 | 449 | tee_centroid, 0.9 | Buffalo 449, Gold 418, Blue 386, Silver 369, Silver (L) 369, Red 296, Red (L) 296 | fairway 5058, recovery 496, sand 302 |
| 6 | 4 | 353 | tee_axis, 0.8 | Buffalo 353, Gold 328, Blue 315, Silver 294, Silver (L) 294, Red 280, Red (L) 280 | fairway 5095, recovery 3553, sand 387 |
| 8 | 5 | 524 | tee_axis, 0.8 | Buffalo 524, Gold 505, Blue 477, Silver 456, Silver (L) 456, Red 378, Red (L) 378 | fairway 6807, recovery 1337, sand 103, water 2600 |
| 10 | 4 | 377 | tee_centroid, 0.9 | Buffalo 377, Gold 356, Blue 328, Silver 318, Silver (L) 318, Red 281, Red (L) 281 | fairway 7198, native 50, ob 1399, recovery 2539, sand 1015 |
| 12 | 4 | 477 | tee_centroid, 0.9 | Buffalo 477, Gold 454, Blue 426, Silver 418, Silver (L) 418, Red 325, Red (L) 325 | fairway 9994, ob 333, recovery 1643, sand 449 |
| 13 | 4 | 462 | tee_axis, 0.8 | Buffalo 462, Gold 435, Blue 417, Silver 401, Silver (L) 401, Red 273, Red (L) 273 | fairway 8270, native 114, recovery 1125, sand 414 |
| 14 | 5 | 615 | tee_axis, 0.8 | Buffalo 615, Gold 576, Blue 551, Silver 537, Silver (L) 537, Red 500, Red (L) 500 | fairway 5064, recovery 3929, sand 180, water 792 |
| 15 | 4 | 366 | tee_centroid, 0.8 | Buffalo 366, Gold 348, Blue 332, Silver 309, Silver (L) 309, Red 268, Red (L) 268 | fairway 3052, native 402, recovery 1960, sand 379, water 3208 |
| 16 | 4 | 425 | tee_axis, 0.8 | Buffalo 425, Gold 379, Blue 360, Silver 326, Silver (L) 326, Red 270, Red (L) 270 | fairway 6601, native 17, ob 332, recovery 730, sand 480 |
| 18 | 5 | 573 | tee_axis, 0.8 | Buffalo 573, Gold 548, Blue 519, Silver 510, Silver (L) 510, Red 451, Red (L) 451 | fairway 5797, ob 1015, recovery 2285, sand 828 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
