# Mapper inputs: Eagle Bend Golf Course (Lawrence, KS)

Base package: `course_data/mapper/eagle_bend/base/package.json` (built 2026-11-02T06:14:42Z; committed package: tees rebuilt: 0 tee(s) moved; trees rebuilt: buffer -1 m, 99 tree zones). Corridor set **Gold**. Sets: Gold, Blue, White, Red.
Photo NAIP 2021; other years: NAIP 2023; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 58 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: geometry only (OSM outline / buildings / roads): no OB evidence fetched for this course; list it in course_dat

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 411 | tee_centroid, 0.9 | Gold 411, Blue 397, White 370, Red 341 | fairway 5513, recovery 1150 | none |
| 2 | 4 | 362 | tee_axis, 0.8 | Gold 362, Blue 344, White 325, Red 280 | fairway 4182 | R1: 350, 23.6 |
| 3 | 5 | 574 | tee_axis, 0.8 | Gold 574, Blue 545, White 499, Red 471 | fairway 3420, ob 424, recovery 3267 | none |
| 5 | 4 | 383 | tee_centroid, 0.9 | Gold 383, Blue 368, White 320, Red 290 | fairway 5085, ob 213, recovery 2067 | none |
| 6 | 4 | 460 | tee_axis, 0.8 | Gold 460, Blue 439, White 379, Red 306 | fairway 5307, ob 396, recovery 1565, water 1912 | none |
| 7 | 5 | 560 | walkback, 0.5 | Gold 560, Blue 540, White 483, Red 419 | fairway 4128, recovery 367 | R1: 212, 26.6, R2: 354, 18.8 |
| 9 | 4 | 430 | tee_axis, 0.8 | Gold 430, Blue 410, White 390, Red 360 | fairway 4924, recovery 1057 | L1: 340, 17.6, R1: 243, 40.2 |
| 10 | 4 | 417 | lidar_pad, 0.6 | Gold 417, Blue 396, White 360, Red 278 | fairway 5344, recovery 2428 | none |
| 11 | 4 | 385 | tee_axis, 0.8 | Gold 385, Blue 366, White 344, Red 319 | fairway 4738 | L1: 349, 23.3 |
| 13 | 5 | 610 | tee_axis, 0.8 | Gold 610, Blue 527, White 500, Red 461 | fairway 2983, ob 918, recovery 26 | L1: 454, 85.5, L2: 1544, 22.6, L3: 204, 44.1 |
| 14 | 4 | 429 | walkback, 0.5 | Gold 429, Blue 368, White 335, Red 311 | fairway 4806, water 913 | none |
| 15 | 4 | 340 | tee_axis, 0.8 | Gold 340, Blue 320, White 300, Red 273 | fairway 4076, sand 128, water 12 | R1: 213, 24.1, R2: 261, 49.9 |
| 16 | 4 | 448 | tee_axis, 0.8 | Gold 448, Blue 430, White 409, Red 341 | fairway 4903, recovery 2403, sand 324 | none |
| 18 | 5 | 547 | walkback, 0.5 | Gold 547, Blue 491, White 470, Red 404 | fairway 4010, recovery 547, water 3105 | L1: 230, 23.6, L2: 559, 18.3 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
