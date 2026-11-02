# Mapper inputs: Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO)

Base package: `course_data/mapper/old_kinderhook/base/package.json` (built 2026-11-02T21:42:10Z; committed package: tees rebuilt: 2 tee(s) moved). Corridor set **Championship**. Sets: Championship.
Photo NAIP 2016; other years: NAIP 2022, NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 1 sets; lidar pads: 81 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 430 | tee_axis, 0.8 | Championship 430 | fairway 6156, ob 1334, recovery 1195, sand 275 | none |
| 2 | 4 | 386 | tee_axis, 0.8 | Championship 386 | fairway 5213, ob 2940, recovery 212, sand 151, water 1238 | none |
| 4 | 4 | 432 | tee_axis, 0.8 | Championship 432 | fairway 5203, sand 71, water 1134 | none |
| 5 | 4 | 446 | tee_centroid, 0.9 | Championship 446 | fairway 5779, ob 3267, recovery 460, water 200 | none |
| 6 | 4 | 344 | tee_axis, 0.8 | Championship 344 | fairway 4840, ob 272, recovery 6070, sand 545 | none |
| 8 | 4 | 416 | tee_axis, 0.8 | Championship 416 | fairway 5793, recovery 3786, water 595 | none |
| 9 | 5 | 514 | tagged, 0.4 | Championship 514 | fairway 5160, ob 3315, recovery 978, water 980 | none |
| 10 | 4 | 423 | tee_axis, 0.8 | Championship 423 | fairway 4700, ob 2611, recovery 680, water 1020 | none |
| 12 | 4 | 408 | tee_axis, 0.8 | Championship 408 | fairway 6477, recovery 704 | none |
| 13 | 4 | 437 | tee_axis, 0.8 | Championship 437 | fairway 7640, recovery 1768 | none |
| 14 | 5 | 559 | tee_axis, 0.8 | Championship 559 | fairway 6611, recovery 408, water 4853 | none |
| 15 | 4 | 402 | tagged, 0.4 | Championship 402 | fairway 4967, recovery 12, water 1997 | none |
| 17 | 4 | 376 | tee_axis, 0.8 | Championship 376 | fairway 5735, ob 851, recovery 881, sand 1091 | L1: 228, 20.0 |
| 18 | 5 | 516 | tee_axis, 0.8 | Championship 516 | fairway 5867, ob 1843, recovery 287, sand 339, water 66 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
