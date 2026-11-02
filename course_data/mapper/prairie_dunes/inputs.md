# Mapper inputs: Prairie Dunes (Hutchinson, KS)

Base package: `course_data/mapper/prairie_dunes/base/package.json` (built 2026-11-02T06:30:13Z; committed package: tees rebuilt: 0 tee(s) moved; trees rebuilt: buffer -1 m, 181 tree zones). Corridor set **Blue**. Sets: Gold, Blue, White, Silver, Bronze.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 95 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_dat

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 435 | tee_axis, 0.8 | Gold 452, Blue 435, White 401, Silver 390, Bronze 385 | fairway 3997, ob 159, sand 142 | L1: 12427, 0.0, L2: 342, 55.7, R1: 3020, 6.8, R2: 725, 1.3 |
| 3 | 4 | 315 | tee_axis, 0.8 | Gold 355, Blue 315, White 308, Silver 272, Bronze 202 | fairway 4807, sand 255 | L1: 16089, 2.6, R1: 1769, 3.9, R2: 8066, 2.4 |
| 5 | 4 | 418 | tee_axis, 0.8 | Gold 477, Blue 418, White 402, Silver 402, Bronze 400 | fairway 5913, sand 150 | L1: 8166, 4.5, R1: 14022, 3.2 |
| 6 | 4 | 370 | tee_centroid, 0.9 | Gold 387, Blue 370, White 360, Silver 324, Bronze 275 | fairway 5218, recovery 526, sand 232 | L1: 11772, 0.3, R1: 8646, 0.0 |
| 7 | 5 | 512 | tee_axis, 0.8 | Gold 512, Blue 512, White 487, Silver 429, Bronze 429 | fairway 5195, sand 213 | L1: 11688, 0.0, R1: 12646, 5.3 |
| 8 | 4 | 440 | lidar_pad, 0.6 | Gold 468, Blue 440, White 417, Silver 359, Bronze 390 | fairway 4750 | L1: 3920, 2.6, L2: 3973, 1.2, R1: 13784, 1.8, R2: 174, 0.0 |
| 9 | 4 | 426 | tee_axis, 0.8 | Gold 452, Blue 426, White 400, Silver 400, Bronze 390 | fairway 5425, sand 46 | L1: 9078, 0.0, L2: 534, 0.0, R1: 13672, 3.7 |
| 11 | 4 | 453 | tee_axis, 0.8 | Gold 472, Blue 453, White 426, Silver 415, Bronze 415 | fairway 5605, recovery 907, sand 244 | L1: 10177, 0.0, L2: 269, 51.3, R1: 7071, 0.0, R2: 202, 5.0 |
| 12 | 4 | 390 | tee_centroid, 0.9 | Gold 390, Blue 390, White 371, Silver 323, Bronze 249 | fairway 4468, recovery 919, sand 409 | L1: 8731, 4.8, R1: 11664, 1.4 |
| 13 | 4 | 395 | tee_axis, 0.8 | Gold 445, Blue 395, White 357, Silver 276, Bronze 276 | fairway 5510, recovery 152, sand 478 | L1: 11747, 0.0, L2: 408, 4.7, R1: 11116, 0.0 |
| 14 | 4 | 377 | tee_axis, 0.8 | Gold 405, Blue 377, White 324, Silver 281, Bronze 257 | fairway 4221, sand 827 | L1: 10184, 2.7, L2: 194, 7.8, L3: 311, 6.1, R1: 4758, 0.0, R2: 220, 12.2, R3: 3991, 14.1 |
| 16 | 4 | 408 | tee_axis, 0.8 | Gold 415, Blue 408, White 396, Silver 349, Bronze 349 | fairway 5465, recovery 244, sand 234 | L1: 840, 0.0, L2: 2341, 2.0, L3: 2425, 4.1, R1: 16193, 0.2 |
| 17 | 5 | 500 | tee_axis, 0.8 | Gold 519, Blue 500, White 477, Silver 447, Bronze 447 | fairway 5484, recovery 143 | L1: 15585, 1.1, R1: 9047, 1.0, R2: 152, 2.0 |
| 18 | 4 | 382 | tee_axis, 0.8 | Gold 390, Blue 382, White 372, Silver 352, Bronze 284 | fairway 5340 | L1: 8319, 2.6, R1: 13578, 2.0 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
