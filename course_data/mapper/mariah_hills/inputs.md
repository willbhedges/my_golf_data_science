# Mapper inputs: Mariah Hills Golf Course (Dodge City, KS)

Base package: `course_data/mapper/mariah_hills/base/package.json` (built 2026-11-02T06:29:04Z; committed package: tees kept (no hole lines); trees rebuilt: buffer -1 m, 543 tree zones). Corridor set **Blue**. Sets: Black, Blue, White, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 33 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_dat

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 316 | tee_axis, 0.8 | Black 329, Blue 316, White 305, Red 298 | fairway 4956, recovery 542, sand 395 | L1: 1247, 4.9, L2: 477, 7.3, L3: 2374, 9.7, R1: 708, 5.6, R2: 617, 4.8, R3: 229, 10.4, R4: 1196, 18.6 |
| 2 | 4 | 410 | tee_centroid, 0.9 | Black 423, Blue 410, White 398, Red 303 | fairway 3976, recovery 1070 | L1: 12292, 5.6, R1: 2351, 12.6, R2: 340, 14.5, R3: 206, 25.7, R4: 222, 6.6, R5: 878, 6.3 |
| 3 | 5 | 550 | tee_axis, 0.8 | Black 561, Blue 550, White 540, Red 434 | fairway 6204 | L1: 3805, 2.4, L2: 750, 3.9, R1: 5305, 5.5 |
| 4 | 4 | 423 | tee_centroid, 0.9 | Black 457, Blue 423, White 413, Red 403 | fairway 5138 | L1: 778, 3.6, L2: 3776, 2.9, R1: 716, 5.7 |
| 6 | 5 | 498 | tee_axis, 0.8 | Black 545, Blue 498, White 490, Red 414 | fairway 4637, recovery 476, water 1347 | L1: 2401, 6.3, L2: 488, 7.4, L3: 172, 7.8, R1: 4241, 6.6, R2: 2902, 1.6, R3: 237, 25.1 |
| 7 | 4 | 372 | walkback, 0.5 | Black 400, Blue 372, White 354, Red 265 | fairway 981, recovery 494 | L1: 321, 9.0, L2: 6764, 3.6, L3: 1142, 2.0, R1: 345, 1.6, R2: 5051, 4.9, R3: 1921, 4.0 |
| 9 | 4 | 375 | tee_centroid, 0.9 | Black 395, Blue 375, White 365, Red 285 | fairway 4848, recovery 891 | L1: 620, 16.6, L2: 1063, 9.5, L3: 878, 8.8, L4: 253, 6.4, R1: 720, 8.5, R2: 579, 6.3, R3: 1170, 5.5, R4: 210, 7.3 |
| 10 | 4 | 361 | tee_axis, 0.8 | Black 407, Blue 361, White 350, Red 272 | fairway 3807, ob 1581, recovery 910, sand 135 | L1: 4154, 5.4, L2: 485, 31.4, L3: 594, 14.2, L4: 351, 16.8, R1: 774, 5.0, R2: 2938, 7.3, R3: 170, 20.4 |
| 12 | 5 | 498 | tee_centroid, 0.9 | Black 536, Blue 498, White 488, Red 444 | fairway 4497, recovery 1169 | L1: 10944, 1.8, R1: 1790, 5.1, R2: 238, 7.3, R3: 237, 24.4, R4: 1866, 7.0, R5: 610, 11.2 |
| 13 | 4 | 446 | tee_centroid, 0.9 | Black 459, Blue 446, White 431, Red 355 | fairway 4845 | L1: 637, 5.5, L2: 242, 16.5, L3: 350, 7.3, L4: 1572, 6.4, R1: 170, 9.3, R2: 306, 2.2, R3: 3700, 0.0 |
| 14 | 4 | 392 | tee_centroid, 0.9 | Black 401, Blue 392, White 380, Red 286 | fairway 4614, recovery 153 | L1: 5930, 1.1, L2: 1046, 7.5, R1: 2433, 0.0, R2: 2058, 3.0 |
| 15 | 4 | 386 | tee_axis, 0.8 | Black 416, Blue 386, White 365, Red 317 | fairway 4505, recovery 432 | L1: 5423, 2.8, L2: 4117, 5.6, R1: 165, 7.5, R2: 3381, 8.7, R3: 1040, 4.3 |
| 17 | 4 | 364 | tee_axis, 0.8 | Black 380, Blue 364, White 350, Red 280 | fairway 3220, recovery 1294 | L1: 1606, 5.3, L2: 844, 3.6, L3: 478, 3.4, L4: 927, 10.1, R1: 3334, 21.2, R2: 270, 33.1, R3: 930, 16.4, R4: 236, 11.0, R5: 818, 9.6 |
| 18 | 4 | 440 | tee_axis, 0.8 | Black 450, Blue 440, White 430, Red 418 | fairway 4912, recovery 496 | L1: 970, 13.6, L2: 2392, 6.7, L3: 1963, 5.2, R1: 3576, 2.9, R2: 242, 2.5 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
