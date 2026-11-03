# Mapper inputs: Tournament Club of Iowa (Polk City, IA)

Base package: `course_data/mapper/tournament_club_iowa/base/package.json` (built 2026-11-03T09:58:59Z; committed package: tees rebuilt: 35 tee(s) moved). Corridor set **King**. Sets: King, Palmer, Deacon, Legend.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 100 candidate pa; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 553 | tee_axis, 0.4 | King 553, Palmer 527, Deacon 511, Legend 441 | fairway 7647, recovery 1851, water 309 | L1: 2259, 13.3, L2: 209, 3.1, L3: 2294, 4.9, L4: 1405, 8.0, R1: 1466, 10.6, R2: 1292, 3.9, R3: 1635, 4.0 |
| 2 | 4 | 420 | tee_axis, 0.4 | King 420, Palmer 386, Deacon 365, Legend 270 | fairway 3600, recovery 2951, water 437 | L1: 3436, 4.9, R1: 676, 20.1, R2: 270, 39.7, R3: 151, 5.1 |
| 4 | 5 | 593 | tee_axis, 0.4 | King 593, Palmer 578, Deacon 548, Legend 478 | fairway 7107, recovery 2223, sand 926 | L1: 740, 32.9, L2: 517, 26.7, L3: 301, 8.0 |
| 6 | 4 | 480 | tee_axis, 0.4 | King 480, Palmer 448, Deacon 423, Legend 393 | fairway 5806, recovery 793, sand 1668, water 502 | L1: 1022, 2.8, L2: 592, 9.7, L3: 155, 21.5, R1: 514, 37.0, R2: 523, 3.3 |
| 7 | 4 | 386 | tee_axis, 0.4 | King 386, Palmer 359, Deacon 350, Legend 253 | fairway 5242, recovery 3080, sand 144, water 543 | L1: 2573, 17.3, L2: 180, 4.1, L3: 190, 20.3, L4: 324, 1.5, R1: 349, 7.6 |
| 9 | 4 | 456 | tee_centroid, 0.4 | King 456, Palmer 395, Deacon 378, Legend 305 | fairway 4528, recovery 1898, water 2905 | L1: 161, 18.6, L2: 626, 7.5, R1: 306, 8.8 |
| 10 | 4 | 356 | tagged, 0.4 | King 356, Palmer 347, Deacon 326, Legend 273 | fairway 5689, recovery 1415, sand 537, water 3186 | L1: 1299, 8.4, L2: 259, 59.8, R1: 1534, 5.1, R2: 154, 11.7 |
| 11 | 4 | 376 | tee_axis, 0.4 | King 376, Palmer 369, Deacon 354, Legend 308 | fairway 3202, ob 511, recovery 4667 | L1: 739, 12.4, L2: 470, 11.0, R1: 370, 6.8 |
| 12 | 4 | 442 | tee_axis, 0.4 | King 442, Palmer 427, Deacon 386, Legend 348 | fairway 5991, ob 1005, recovery 3253 | R1: 724, 10.8, R2: 1792, 9.7 |
| 13 | 5 | 526 | review (snapped 7 yds along OSM tee 676110869), 0.4 | King 526, Palmer 504, Deacon 485, Legend 445 | fairway 6122, ob 1812, recovery 2328 | R1: 244, 28.1 |
| 14 | 4 | 325 | tee_axis, 0.4 | King 325, Palmer 301, Deacon 258, Legend 140 | fairway 5349, ob 211, recovery 4233 | L1: 207, 9.1, L2: 2022, 13.5, R1: 839, 11.8 |
| 17 | 5 | 638 | tee_centroid, 0.4 | King 638, Palmer 560, Deacon 520, Legend 516 | fairway 6260, water 963 | L1: 5771, 4.4, L2: 225, 4.4, L3: 172, 5.7, R1: 7308, 12.2 |
| 18 | 4 | 459 | tee_centroid, 0.4 | King 459, Palmer 441, Deacon 399, Legend 338 | fairway 7470, water 974 | L1: 150, 3.9, L2: 268, 4.5, L3: 790, 11.8, R1: 7498, 7.5, R2: 170, 14.3 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
