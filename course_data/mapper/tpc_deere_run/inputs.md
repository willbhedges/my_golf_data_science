# Mapper inputs: TPC Deere Run (Silvis, IL)

Base package: `course_data/mapper/tpc_deere_run/base/package.json` (built 2026-11-02T23:48:33Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Gold**. Sets: Gold, Black, Blue, White, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 78 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 395 | tee_axis, 0.8 | Gold 395, Black 386, Blue 359, White 343, Red 313 | fairway 6367, recovery 3122, sand 777 | L1: 184, 19.1, L2: 510, 24.2 |
| 2 | 5 | 561 | tee_axis, 0.8 | Gold 561, Black 546, Blue 501, White 476, Red 407 | fairway 5019, recovery 1683, sand 812 | L1: 1084, 18.3, L2: 1989, 21.4, R1: 1359, 31.3, R2: 1136, 8.0, R3: 164, 21.3 |
| 4 | 4 | 454 | tee_axis, 0.8 | Gold 454, Black 443, Blue 417, White 355, Red 305 | fairway 9151, recovery 2570 | L1: 237, 52.8, L2: 156, 37.1, L3: 472, 20.9, L4: 1322, 22.2, R1: 1330, 13.2, R2: 225, 7.0 |
| 5 | 4 | 433 | tee_axis, 0.8 | Gold 433, Black 424, Blue 411, White 400, Red 284 | fairway 4736, recovery 2050, sand 346, water 11 | L1: 1980, 17.0, L2: 1154, 11.9, L3: 361, 13.5 |
| 6 | 4 | 367 | tee_axis, 0.8 | Gold 367, Black 357, Blue 332, White 309, Red 248 | fairway 2685, recovery 7859, sand 545 | none |
| 8 | 4 | 428 | tee_centroid, 0.9 | Gold 428, Black 377, Blue 366, White 348, Red 313 | fairway 3757, ob 1271, recovery 6010, sand 364 | L1: 1043, 20.2, R1: 314, 8.0 |
| 9 | 4 | 503 | tee_axis, 0.8 | Gold 503, Black 480, Blue 449, White 409, Red 348 | fairway 3648, recovery 1332, sand 311 | L1: 10786, 16.3 |
| 10 | 5 | 596 | tee_axis, 0.8 | Gold 596, Black 576, Blue 512, White 486, Red 466 | fairway 5775, recovery 587, sand 397 | L1: 9770, 15.1, R1: 525, 6.5, R2: 449, 6.2, R3: 231, 7.1 |
| 11 | 4 | 432 | tee_axis, 0.8 | Gold 432, Black 425, Blue 392, White 386, Red 318 | fairway 4814, recovery 5802 | L1: 3071, 27.6 |
| 13 | 4 | 424 | tee_axis, 0.8 | Gold 424, Black 411, Blue 381, White 351, Red 325 | fairway 6606, recovery 151, sand 1268 | R1: 152, 33.4, R2: 1574, 29.7 |
| 14 | 4 | 361 | tee_axis, 0.8 | Gold 361, Black 353, Blue 322, White 300, Red 273 | fairway 4837, recovery 2628, sand 622 | R1: 180, 39.1, R2: 236, 29.8, R3: 179, 37.8 |
| 15 | 4 | 484 | tee_axis, 0.8 | Gold 484, Black 449, Blue 419, White 397, Red 366 | fairway 4537, recovery 2560, sand 747 | L1: 195, 31.2, L2: 286, 28.2, L3: 168, 9.5, L4: 978, 7.3, R1: 282, 27.5 |
| 17 | 5 | 569 | tee_axis, 0.8 | Gold 569, Black 545, Blue 490, White 480, Red 430 | fairway 3698, recovery 6537, water 85 | L1: 279, 30.1 |
| 18 | 4 | 476 | tee_axis, 0.8 | Gold 476, Black 458, Blue 428, White 381, Red 324 | fairway 3821, recovery 8429, sand 25 | R1: 1079, 37.4 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
