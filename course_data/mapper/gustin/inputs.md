# Mapper inputs: A. L. Gustin Golf Course (Columbia, MO)

Base package: `course_data/mapper/gustin/base/package.json` (built 2026-11-02T10:26:50Z; committed package: tees rebuilt: 0 tee(s) moved; trees rebuilt: buffer -1 m, 464 tree zones). Corridor set **Black**. Sets: Black, Gold, White.
Photo NAIP 2020; other years: NAIP 2022; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 3 sets; lidar pads: 47 candidate pad; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 492 | tee_axis, 0.8 | Black 492, Gold 470, White 350 | fairway 4945, recovery 1776, sand 119 | none |
| 3 | 4 | 440 | tee_axis, 0.8 | Black 440, Gold 351, White 284 | fairway 4709, recovery 2083, sand 169 | none |
| 4 | 4 | 384 | tee_axis, 0.8 | Black 384, Gold 360, White 290 | fairway 5681, recovery 4114 | none |
| 6 | 4 | 418 | tee_axis, 0.8 | Black 418, Gold 393, White 277 | fairway 4821, recovery 2047, sand 209 | none |
| 7 | 4 | 369 | lidar_pad, 0.6 | Black 369, Gold 305, White 254 | fairway 5091, recovery 1917, sand 256, water 2 | none |
| 8 | 4 | 376 | tee_axis, 0.8 | Black 376, Gold 346, White 270 | fairway 5487, recovery 4266 | none |
| 9 | 4 | 338 | tee_axis, 0.8 | Black 338, Gold 323, White 310 | fairway 2634, recovery 2689, sand 137 | none |
| 11 | 4 | 424 | lidar_pad_capped, 0.6 | Black 424, Gold 397, White 300 | fairway 4898, ob 40, recovery 1518, sand 151 | none |
| 12 | 5 | 518 | tee_axis, 0.8 | Black 518, Gold 493, White 438 | fairway 4844, ob 1286, recovery 2267, sand 252 | none |
| 14 | 4 | 378 | lidar_pad, 0.6 | Black 378, Gold 348, White 260 | fairway 3193, recovery 4163, water 910 | none |
| 15 | 4 | 467 | walkback, 0.5 | Black 467, Gold 401, White 250 | fairway 3828, recovery 2805, water 504 | none |
| 16 | 4 | 332 | tee_axis, 0.8 | Black 332, Gold 311, White 258 | fairway 4077, recovery 2656, water 232 | none |
| 17 | 4 | 405 | tee_centroid, 0.9 | Black 405, Gold 375, White 305 | fairway 6291, recovery 1891 | none |
| 18 | 4 | 378 | tee_axis, 0.8 | Black 378, Gold 365, White 270 | fairway 3402, recovery 2149, sand 82 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
