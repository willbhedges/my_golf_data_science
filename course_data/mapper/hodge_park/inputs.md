# Mapper inputs: Hodge Park Golf Course (Kansas City, MO)

Base package: `course_data/mapper/hodge_park/base/package.json` (built 2026-11-02T15:34:05Z; committed package: tees rebuilt: 7 tee(s) moved). Corridor set **Blue**. Sets: Blue, White, Red.
Photo NAIP 2018; other years: NAIP 2022, NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 36 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 425 | tagged, 1.0 | Blue 425, White 380, Red 330 | fairway 6399, recovery 3137 | L1: 238, 28.0 |
| 2 | 4 | 347 | tagged, 1.0 | Blue 347, White 310, Red 291 | fairway 4805, recovery 838 | L1: 244, 27.8, L2: 464, 23.8 |
| 4 | 5 | 452 | tagged, 1.0 | Blue 452, White 400, Red 364 | fairway 5390, ob 89, recovery 432, water 428 | L1: 356, 19.6 |
| 5 | 4 | 446 | tagged, 1.0 | Blue 446, White 432, Red 408 | fairway 5590, ob 1787 | L1: 544, 31.7, L2: 217, 31.3 |
| 6 | 4 | 304 | tagged, 1.0 | Blue 304, White 269, Red 254 | fairway 2582, ob 2182, recovery 1703, water 731 | L1: 2210, 20.5, L2: 1053, 21.3 |
| 8 | 4 | 409 | tagged, 1.0 | Blue 409, White 388, Red 369 | fairway 6144, recovery 1778 | none |
| 9 | 4 | 401 | tagged, 1.0 | Blue 401, White 371, Red 352 | fairway 5357, recovery 2254 | none |
| 10 | 4 | 405 | tagged, 0.6 | Blue 405, White 371, Red 329 | fairway 1390, ob 1100, recovery 7052, water 536 | none |
| 11 | 5 | 459 | tagged, 1.0 | Blue 459, White 445, Red 429 | fairway 5780, recovery 3313, water 116 | none |
| 13 | 4 | 388 | tagged, 1.0 | Blue 388, White 376, Red 356 | fairway 5458, recovery 2329 | none |
| 14 | 4 | 260 | tagged, 1.0 | Blue 260, White 248, Red 234 | fairway 2408, recovery 5415, sand 150 | L1: 198, 37.0, L2: 510, 60.0, R1: 1470, 59.3 |
| 15 | 4 | 338 | tagged, 1.0 | Blue 338, White 310, Red 290 | fairway 2520, native 778, recovery 4577, water 2978 | R1: 194, 45.7 |
| 17 | 5 | 518 | tagged, 1.0 | Blue 518, White 485, Red 470 | fairway 5499, recovery 4021 | L1: 712, 32.4 |
| 18 | 4 | 302 | tagged, 1.0 | Blue 302, White 277, Red 253 | fairway 4535, recovery 388 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
