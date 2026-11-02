# Mapper inputs: Colbert Hills Golf Course (Manhattan, KS)

Base package: `course_data/mapper/colbert_hills/base/package.json` (built 2026-11-02T13:20:42Z; committed package: tees rebuilt: 1 tee(s) moved). Corridor set **Black/Blue**. Sets: Black/Blue, Web, Silver, Purple, White, Gold.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 101 candidate pa; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 590 | walkback, 0.4 | Black/Blue 590, Web 590, Silver 578, Purple 530, White 507, Gold 444 | fairway 4775, ob 245 | L1: 2334, 3.8, L2: 190, 27.3, L3: 2174, 5.0, R1: 1811, 3.2, R2: 347, 8.7, R3: 198, 10.0 |
| 2 | 4 | 412 | tee_centroid, 0.9 | Black/Blue 412, Web 412, Silver 374, Purple 353, White 329, Gold 298 | fairway 5156, ob 1032, recovery 1921, sand 603 | L1: 1326, 6.1 |
| 3 | 4 | 416 | tee_axis, 0.8 | Black/Blue 416, Web 416, Silver 370, Purple 354, White 275, Gold 247 | fairway 4183, ob 1320, recovery 119, water 653 | L1: 245, 43.3, L2: 634, 7.3, L3: 304, 4.3, R1: 2492, 4.1, R2: 227, 6.5 |
| 4 | 4 | 494 | tee_axis, 0.8 | Black/Blue 494, Web 494, Silver 478, Purple 426, White 400, Gold 368 | fairway 5847, recovery 241 | L1: 2412, 8.9, R1: 574, 11.8, R2: 1069, 13.6, R3: 871, 4.0 |
| 6 | 4 | 428 | tee_axis, 0.8 | Black/Blue 428, Web 428, Silver 403, Purple 383, White 366, Gold 236 | fairway 5688, recovery 950 | none |
| 7 | 5 | 600 | tee_axis, 0.8 | Black/Blue 600, Web 600, Silver 559, Purple 540, White 511, Gold 403 | fairway 5550, recovery 1322, sand 556 | L1: 210, 13.4, L2: 466, 50.1, R1: 1548, 6.0, R2: 210, 19.4 |
| 9 | 4 | 462 | tee_centroid, 0.9 | Black/Blue 462, Web 462, Silver 424, Purple 389, White 361, Gold 308 | fairway 4175, recovery 239, sand 150 | L1: 264, 70.6, L2: 155, 10.6, L3: 217, 35.4, R1: 2955, 6.7, R2: 292, 18.7, R3: 710, 33.3 |
| 10 | 5 | 614 | tee_centroid, 0.9 | Black/Blue 614, Web 614, Silver 600, Purple 543, White 500, Gold 462 | fairway 5922, ob 378, recovery 527 | L1: 1875, 1.3, L2: 450, 4.6, L3: 235, 21.7, R1: 364, 45.6, R2: 354, 22.3 |
| 12 | 4 | 434 | tee_centroid, 0.9 | Black/Blue 434, Web 414, Silver 407, Purple 390, White 369, Gold 285 | fairway 6804, recovery 2107 | L1: 244, 25.3 |
| 13 | 4 | 357 | tee_axis, 0.8 | Black/Blue 357, Web 357, Silver 344, Purple 316, White 290, Gold 261 | fairway 3103, ob 508, recovery 675, sand 875 | L1: 253, 47.5, R1: 176, 74.5, R2: 1541, 0.0 |
| 14 | 4 | 487 | tee_axis, 0.8 | Black/Blue 487, Web 487, Silver 452, Purple 432, White 350, Gold 257 | fairway 6584, ob 1656, recovery 1700 | L1: 694, 8.4, R1: 356, 4.1, R2: 234, 8.2 |
| 15 | 4 | 375 | tee_axis, 0.8 | Black/Blue 375, Web 375, Silver 365, Purple 338, White 310, Gold 278 | fairway 5497, recovery 1502, sand 241 | L1: 714, 11.0, L2: 808, 8.4, L3: 790, 36.6, R1: 868, 5.4, R2: 781, 32.9 |
| 16 | 5 | 513 | tee_centroid, 0.9 | Black/Blue 513, Web 513, Silver 495, Purple 430, White 410, Gold 364 | fairway 5798, ob 257, sand 495 | L1: 1582, 10.4, L2: 3696, 7.6, R1: 8443, 7.2, R2: 232, 2.7 |
| 18 | 4 | 453 | tee_axis, 0.8 | Black/Blue 453, Web 453, Silver 423, Purple 394, White 365, Gold 333 | fairway 5417, sand 127, water 2557 | L1: 1092, 20.8, L2: 1656, 6.6, R1: 322, 2.8 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
