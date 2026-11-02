# Mapper inputs: Ellis Golf Course (Cedar Rapids, IA)

Base package: `course_data/mapper/ellis/base/package.json` (built 2026-11-02T06:14:52Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Blue**. Sets: Blue, White, Gold, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 60 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 395 | tee_centroid, 0.9 | Blue 395, White 383, Gold 336, Red 324 | fairway 3548, recovery 894, sand 5 | L1: 1344, 13.8, R1: 245, 11.1, R2: 245, 18.1, R3: 341, 23.8 |
| 2 | 4 | 365 | tee_centroid, 0.9 | Blue 365, White 348, Gold 319, Red 309 | fairway 4245, recovery 1152, sand 223 | L1: 907, 20.3, L2: 2025, 13.4, R1: 3179, 10.3, R2: 218, 12.6, R3: 2237, 13.3 |
| 3 | 5 | 481 | tee_axis, 0.8 | Blue 481, White 472, Gold 462, Red 394 | fairway 4740, ob 501, recovery 2024 | L1: 365, 5.3, L2: 3281, 8.2, R1: 589, 27.3 |
| 5 | 4 | 385 | tee_centroid, 0.9 | Blue 385, White 366, Gold 353, Red 254 | fairway 4826, recovery 593, sand 311 | L1: 3909, 5.6, R1: 1814, 13.8 |
| 6 | 4 | 420 | lidar_pad, 0.6 | Blue 420, White 390, Gold 360, Red 340 | fairway 4508, sand 385 | L1: 311, 5.2, L2: 1383, 13.1, L3: 233, 3.3 |
| 7 | 4 | 463 | tee_axis, 0.8 | Blue 463, White 434, Gold 306, Red 296 | fairway 5570, recovery 249 | L1: 242, 3.3, L2: 3129, 6.1, R1: 4066, 19.6, R2: 364, 8.0, R3: 162, 26.6 |
| 9 | 5 | 534 | tee_centroid, 0.9 | Blue 534, White 502, Gold 469, Red 390 | fairway 3749, ob 1093, recovery 333 | L1: 648, 17.2, L2: 224, 20.0, L3: 6216, 16.2, R1: 446, 16.9, R2: 231, 17.7, R3: 238, 11.5 |
| 10 | 4 | 321 | tee_centroid, 0.9 | Blue 321, White 303, Gold 281, Red 264 | fairway 3816, recovery 1386, sand 469 | L1: 242, 49.6, R1: 742, 18.9 |
| 12 | 5 | 519 | tee_centroid, 0.9 | Blue 519, White 497, Gold 484, Red 400 | fairway 4308, recovery 3873 | L1: 724, 15.7, R1: 166, 10.3 |
| 13 | 4 | 350 | tee_axis, 0.8 | Blue 350, White 338, Gold 316, Red 301 | fairway 2698, ob 4374, recovery 825 | L1: 341, 13.2, L2: 1332, 1.1, L3: 381, 15.2, L4: 294, 68.6, R1: 2148, 7.9, R2: 844, 5.8, R3: 1823, 14.5, R4: 962, 80.7 |
| 15 | 4 | 306 | tee_axis, 0.8 | Blue 306, White 283, Gold 263, Red 246 | fairway 2945, recovery 572 | L1: 798, 21.5, L2: 2148, 10.8, L3: 247, 36.6, R1: 368, 12.2, R2: 1014, 4.6 |
| 16 | 4 | 314 | tee_axis, 0.8 | Blue 314, White 303, Gold 266, Red 216 | fairway 3546, recovery 1817, sand 150 | L1: 3676, 13.2, R1: 239, 30.1, R2: 430, 16.7, R3: 234, 19.7, R4: 1412, 18.7 |
| 17 | 5 | 569 | tee_centroid, 0.9 | Blue 569, White 536, Gold 519, Red 325 | fairway 3583, recovery 811, sand 168 | L1: 2620, 7.7, L2: 184, 10.3, L3: 234, 13.1, R1: 781, 14.0, R2: 963, 6.4 |
| 18 | 4 | 418 | tee_axis, 0.8 | Blue 418, White 386, Gold 349, Red 315 | fairway 5567, recovery 2593, sand 304, water 470 | L1: 223, 14.0, L2: 391, 10.4, R1: 1802, 10.5, R2: 168, 8.9 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
