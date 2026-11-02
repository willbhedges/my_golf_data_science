# Mapper inputs: Spirit Hollow Golf Course (Burlington, IA)

Base package: `course_data/mapper/spirit_hollow/base/package.json` (built 2026-11-02T06:34:27Z; committed package: tees rebuilt: 3 tee(s) moved). Corridor set **Black**. Sets: Gold, Black, White, Rust.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture+segment pads, joint chain assignment) for 4 sets; lidar pads: 69 candi; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: ok: segment gap-fill ariadgolf-v4@43ee2944 (+1 zones on 1 holes, +0 greens, 36 tee candidates); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 391 | tee_axis, 0.8 | Gold 426, Black 391, White 376, Rust 299 | fairway 3992, recovery 3460, water 42 | R1: 723, 28.3 |
| 2 | 5 | 507 | tee_axis, 0.8 | Gold 607, Black 507, White 452, Rust 390 | fairway 3518, ob 1464, recovery 816, sand 299, water 214 | L1: 220, 27.7, L2: 473, 23.8, L3: 278, 64.2, R1: 307, 51.2 |
| 4 | 5 | 532 | tee_axis, 0.8 | Gold 607, Black 532, White 501, Rust 439 | fairway 4909, ob 772, recovery 963 | L1: 370, 17.1, L2: 812, 18.2, L3: 466, 34.6, R1: 6153, 3.8 |
| 5 | 4 | 384 | tee_axis, 0.8 | Gold 468, Black 384, White 361, Rust 273 | fairway 6283, ob 39, recovery 67, sand 851 | L1: 4918, 16.3, L2: 224, 12.5, R1: 2368, 17.6, R2: 2984, 13.7 |
| 6 | 4 | 408 | tee_axis, 0.8 | Gold 445, Black 408, White 365, Rust 303 | fairway 5010, recovery 213 | L1: 3394, 4.9, L2: 3225, 8.2, R1: 9126, 16.3 |
| 8 | 4 | 383 | tee_axis, 0.8 | Gold 431, Black 383, White 365, Rust 332 | fairway 4444, ob 1893, sand 473 | L1: 242, 17.9, L2: 799, 10.3, L3: 396, 7.4, R1: 372, 31.9, R2: 1215, 22.0, R3: 1190, 40.6, R4: 1077, 20.3 |
| 9 | 4 | 365 | tee_axis, 0.8 | Gold 410, Black 365, White 323, Rust 266 | fairway 3974, recovery 3167, water 904 | L1: 923, 10.9, L2: 379, 28.3, R1: 458, 21.6, R2: 615, 11.1 |
| 10 | 5 | 502 | tee_axis, 0.8 | Gold 575, Black 502, White 457, Rust 394 | fairway 4927, recovery 13, sand 138, water 3521 | R1: 340, 9.0 |
| 11 | 4 | 338 | tee_axis, 0.8 | Gold 352, Black 338, White 305, Rust 252 | fairway 3095, recovery 1356, sand 115, water 3611 | L1: 556, 41.2, L2: 1094, 26.6, R1: 226, 37.5, R2: 634, 22.7 |
| 13 | 4 | 409 | tee_axis, 0.8 | Gold 480, Black 409, White 389, Rust 298 | fairway 3772, recovery 745, sand 341, water 1960 | L1: 1843, 7.7, L2: 2190, 22.4, L3: 803, 64.6, R1: 370, 31.5 |
| 14 | 4 | 393 | tee_axis, 0.8 | Gold 467, Black 393, White 370, Rust 328 | fairway 4066, recovery 1558, water 1924 | L1: 468, 25.1, R1: 1498, 21.7, R2: 314, 21.3 |
| 16 | 4 | 378 | tee_axis, 0.8 | Gold 434, Black 378, White 331, Rust 282 | fairway 4275, recovery 1642, sand 496 | L1: 5442, 6.8, L2: 155, 21.0, R1: 368, 26.7, R2: 300, 15.8, R3: 1632, 23.5 |
| 17 | 4 | 445 | tee_axis, 0.8 | Gold 496, Black 445, White 397, Rust 341 | fairway 5290, recovery 1172, sand 177 | L1: 8452, 12.9, R1: 208, 2.6, R2: 911, 5.8 |
| 18 | 5 | 521 | tee_centroid, 0.9 | Gold 579, Black 521, White 483, Rust 423 | fairway 3766, recovery 320, water 4822 | L1: 1476, 34.1, R1: 763, 24.9 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
