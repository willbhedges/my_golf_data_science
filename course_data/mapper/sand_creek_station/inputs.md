# Mapper inputs: Sand Creek Station (Newton, KS)

Base package: `course_data/mapper/sand_creek_station/base/package.json` (built 2026-11-02T06:30:53Z; committed package: tees rebuilt: 0 tee(s) moved; trees rebuilt: buffer -1 m, 128 tree zones). Corridor set **Championship**. Sets: Championship, Tournament, Medal, Ladies (L).
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 94 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_dat

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 474 | lidar_pad, 0.6 | Championship 474, Tournament 419, Medal 393, Ladies (L) 316 | fairway 3931, native 965, recovery 1021, water 1120 | L1: 695, 6.2, L2: 1232, 13.7, L3: 242, 18.4, L4: 866, 8.8, R1: 351, 8.6 |
| 2 | 5 | 613 | tee_axis, 0.8 | Championship 613, Tournament 579, Medal 530, Ladies (L) 432 | fairway 2112, native 488, recovery 4815 | L1: 219, 19.1, L2: 1262, 13.9, L3: 244, 15.2 |
| 4 | 5 | 601 | tee_axis, 0.8 | Championship 601, Tournament 552, Medal 521, Ladies (L) 453 | fairway 5380, native 3369, recovery 244, sand 105, water 1079 | L1: 9052, 3.5, R1: 272, 69.6, R2: 2233, 5.0, R3: 1826, 5.5 |
| 5 | 4 | 345 | tee_axis, 0.8 | Championship 345, Tournament 318, Medal 300, Ladies (L) 271 | fairway 6488, native 2211, recovery 1178, sand 303 | L1: 5572, 3.6, L2: 2159, 5.5, R1: 601, 3.0, R2: 344, 10.0, R3: 1190, 7.6, R4: 697, 26.8 |
| 6 | 4 | 467 | tee_axis, 0.8 | Championship 467, Tournament 442, Medal 379, Ladies (L) 343 | fairway 5137, native 4189, recovery 69, sand 240 | L1: 8420, 2.1, L2: 3180, 0.8, R1: 3061, 11.8, R2: 860, 5.6 |
| 8 | 4 | 470 | tee_centroid, 0.9 | Championship 470, Tournament 443, Medal 407, Ladies (L) 357 | fairway 4816, native 1109, recovery 482, sand 219, water 5568 | L1: 1443, 3.8, L2: 277, 5.0, R1: 154, 45.0, R2: 1127, 4.6 |
| 9 | 4 | 373 | tee_centroid, 0.9 | Championship 373, Tournament 337, Medal 294, Ladies (L) 225 | fairway 4720, native 66, recovery 4514, water 736 | L1: 402, 70.4, R1: 356, 29.0 |
| 10 | 5 | 648 | lidar_pad, 0.6 | Championship 648, Tournament 612, Medal 555, Ladies (L) 525 | fairway 2938, ob 57, water 4307 | L1: 332, 43.9, L2: 217, 17.0, L3: 1570, 32.9, L4: 1609, 6.6, R1: 185, 102.0, R2: 600, 60.6, R3: 1099, 20.2 |
| 11 | 4 | 364 | tee_centroid, 0.9 | Championship 364, Tournament 337, Medal 316, Ladies (L) 296 | fairway 5641, recovery 1370 | L1: 4135, 8.8, L2: 4460, 6.3, R1: 2124, 13.5, R2: 2491, 1.7 |
| 12 | 4 | 420 | tee_axis, 0.8 | Championship 420, Tournament 378, Medal 354, Ladies (L) 258 | fairway 5729, sand 744 | L1: 9210, 3.2, R1: 3782, 31.4, R2: 1514, 9.3, R3: 880, 8.9, R4: 322, 27.1 |
| 14 | 4 | 484 | tee_centroid, 0.9 | Championship 484, Tournament 438, Medal 395, Ladies (L) 324 | fairway 5906, sand 930 | L1: 11085, 5.4, R1: 1322, 23.6, R2: 862, 8.4, R3: 364, 10.1, R4: 1806, 18.3, R5: 242, 13.2 |
| 15 | 4 | 382 | tee_axis, 0.8 | Championship 382, Tournament 342, Medal 289, Ladies (L) 223 | fairway 5559, native 3071, ob 1407, sand 107 | L1: 3224, 0.0, L2: 980, 3.5, R1: 3805, 8.0, R2: 283, 38.1, R3: 474, 6.5, R4: 462, 4.9, R5: 411, 14.3 |
| 16 | 5 | 525 | tee_centroid, 0.9 | Championship 525, Tournament 498, Medal 480, Ladies (L) 429 | fairway 4846, native 4103, ob 333, recovery 170, sand 299 | L1: 8589, 7.2, R1: 4976, 21.8, R2: 333, 21.6 |
| 18 | 4 | 426 | tee_centroid, 0.9 | Championship 426, Tournament 373, Medal 336, Ladies (L) 261 | fairway 3468, native 3898, sand 309, water 140 | L1: 344, 20.0, L2: 230, 9.0, L3: 312, 24.4, L4: 231, 7.2, R1: 6541, 6.9 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
