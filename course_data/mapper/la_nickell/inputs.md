# Mapper inputs: L.A. Nickell Golf Course (Columbia, MO)

Base package: `course_data/mapper/la_nickell/base/package.json` (built 2026-11-02T10:27:38Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Blue**. Sets: Blue, White, Red.
Photo NAIP 2022; other years: NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 28 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 372 | tee_axis, 0.8 | Blue 372, White 350, Red 289 | fairway 3888, recovery 1723 | none |
| 2 | 4 | 369 | tee_axis, 0.8 | Blue 369, White 350, Red 313 | fairway 3540, recovery 2969 | none |
| 3 | 4 | 385 | tee_axis, 0.8 | Blue 385, White 365, Red 331 | fairway 5693, recovery 1732 | none |
| 5 | 4 | 325 | tee_axis, 0.8 | Blue 325, White 315, Red 270 | fairway 4024, ob 3, recovery 3466 | none |
| 7 | 5 | 500 | tee_axis, 0.8 | Blue 500, White 465, Red 397 | fairway 4508, recovery 2817 | none |
| 8 | 4 | 392 | tee_axis, 0.8 | Blue 392, White 351, Red 302 | fairway 4091, recovery 3236 | none |
| 9 | 4 | 379 | walkback, 0.5 | Blue 379, White 358, Red 304 | fairway 4342, recovery 3727 | none |
| 10 | 4 | 384 | walkback, 0.5 | Blue 384, White 364, Red 290 | fairway 4319, recovery 3142 | none |
| 12 | 5 | 526 | walkback, 0.5 | Blue 526, White 480, Red 365 | fairway 3317, ob 3464, recovery 532, water 509 | none |
| 13 | 4 | 376 | lidar_pad, 0.6 | Blue 376, White 359, Red 258 | fairway 4340, recovery 3901 | none |
| 15 | 4 | 377 | tee_axis, 0.8 | Blue 377, White 339, Red 275 | fairway 3261, recovery 2362, water 1049 | none |
| 16 | 4 | 328 | tee_axis, 0.8 | Blue 328, White 321, Red 292 | fairway 4015, ob 5015, recovery 1584 | none |
| 17 | 4 | 407 | tee_axis, 0.8 | Blue 407, White 374, Red 246 | fairway 2859, recovery 2998 | none |
| 18 | 4 | 427 | walkback, 0.5 | Blue 427, White 382, Red 276 | fairway 2944, recovery 3803 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
