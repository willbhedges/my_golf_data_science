# Mapper inputs: Buffalo Dunes (Garden City, KS)

Base package: `course_data/mapper/buffalo_dunes/base/package.json` (built 2026-11-02T06:13:13Z; committed package: tees rebuilt: 0 tee(s) moved; trees rebuilt: buffer -1 m, 541 tree zones). Corridor set **Blue**. Sets: Blue, White, Gold, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 25 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_dat

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 548 | tee_axis, 0.8 | Blue 548, White 538, Gold 470, Red 464 | fairway 4051, recovery 1605, sand 406 | L1: 2806, 3.6, L2: 3148, 2.7, R1: 232, 4.2, R2: 5478, 1.3 |
| 2 | 4 | 371 | tee_centroid, 0.9 | Blue 371, White 329, Gold 284, Red 275 | fairway 3711, recovery 1241 | L1: 7043, 0.6, L2: 363, 10.5, L3: 414, 9.3, R1: 451, 7.8, R2: 3085, 2.0, R3: 1193, 8.8, R4: 382, 0.0 |
| 3 | 4 | 389 | tee_axis, 0.8 | Blue 389, White 379, Gold 311, Red 311 | fairway 3945, recovery 1608, sand 315, water 789 | L1: 5559, 3.6, L2: 572, 5.8, R1: 905, 9.9, R2: 202, 13.6, R3: 2318, 1.3, R4: 259, 49.8, R5: 946, 10.0 |
| 5 | 5 | 539 | lidar_pad, 0.6 | Blue 539, White 530, Gold 445, Red 437 | fairway 5626, recovery 1858, sand 152 | L1: 7745, 0.0, R1: 2850, 4.0, R2: 1072, 10.6, R3: 2172, 0.4 |
| 6 | 4 | 400 | walkback, 0.5 | Blue 400, White 345, Gold 329, Red 299 | fairway 3906, recovery 858, sand 252 | L1: 4674, 3.3, L2: 5087, 4.7, R1: 9497, 2.2, R2: 496, 2.2 |
| 7 | 4 | 357 | tee_axis, 0.8 | Blue 357, White 347, Gold 285, Red 277 | fairway 4450, recovery 1643 | L1: 808, 4.8, L2: 4290, 2.8, L3: 1982, 6.4, R1: 2126, 0.5, R2: 234, 8.0, R3: 349, 10.1, R4: 999, 5.6, R5: 611, 16.4 |
| 9 | 4 | 392 | tee_axis, 0.8 | Blue 392, White 380, Gold 328, Red 319 | fairway 3652, recovery 1271, sand 253 | L1: 4971, 1.5, L2: 1659, 5.1, R1: 6606, 2.1 |
| 10 | 4 | 391 | tee_axis, 0.8 | Blue 391, White 383, Gold 332, Red 265 | fairway 3922, ob 105, recovery 1182 | L1: 9686, 0.9, R1: 9452, 5.4 |
| 11 | 4 | 423 | lidar_pad, 0.6 | Blue 423, White 373, Gold 316, Red 308 | fairway 3867, recovery 2131 | L1: 6447, 0.0, L2: 784, 1.9, R1: 3716, 4.8, R2: 586, 5.5, R3: 4199, 2.2 |
| 13 | 5 | 515 | tee_axis, 0.8 | Blue 515, White 498, Gold 402, Red 395 | fairway 3549, recovery 988 | L1: 7652, 0.4, L2: 238, 13.2, R1: 4166, 8.1, R2: 596, 5.4, R3: 2371, 6.4 |
| 14 | 4 | 413 | lidar_pad, 0.6 | Blue 413, White 370, Gold 354, Red 348 | fairway 4119, recovery 1900, water 1718 | L1: 13672, 0.4, R1: 3926, 0.0, R2: 3123, 4.4, R3: 157, 16.3 |
| 15 | 4 | 398 | tee_axis, 0.8 | Blue 398, White 380, Gold 314, Red 307 | fairway 4090, recovery 1058 | L1: 12024, 3.5, R1: 10596, 5.6 |
| 16 | 5 | 564 | tee_axis, 0.8 | Blue 564, White 550, Gold 431, Red 425 | fairway 4538, recovery 705 | L1: 12990, 2.8, R1: 10702, 1.2 |
| 18 | 4 | 357 | tee_axis, 0.8 | Blue 357, White 342, Gold 330, Red 222 | fairway 3744, recovery 2053, sand 99 | L1: 10816, 0.0, R1: 2234, 7.8, R2: 3657, 5.4, R3: 1518, 2.0 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
