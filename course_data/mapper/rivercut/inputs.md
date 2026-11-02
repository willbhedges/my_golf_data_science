# Mapper inputs: Rivercut Golf Course (Springfield, MO)

Base package: `course_data/mapper/rivercut/base/package.json` (built 2026-11-02T10:31:07Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Black**. Sets: Black, Blue, White, Red.
Photo NAIP 2018; other years: NAIP 2022, NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 130 candidate pa; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 375 | tee_axis, 0.8 | Black 375, Blue 352, White 331, Red 302 | fairway 4483, sand 539, water 80 | none |
| 3 | 4 | 415 | tee_axis, 0.8 | Black 415, Blue 391, White 367, Red 339 | fairway 5988, recovery 2247 | none |
| 4 | 4 | 346 | tee_axis, 0.8 | Black 346, Blue 323, White 307, Red 251 | fairway 4853, recovery 2172, sand 90, water 948 | none |
| 5 | 5 | 511 | tee_axis, 0.8 | Black 511, Blue 490, White 464, Red 441 | fairway 6058, recovery 1600, sand 365, water 367 | none |
| 7 | 5 | 569 | tee_axis, 0.8 | Black 569, Blue 537, White 466, Red 442 | fairway 5144, recovery 608, sand 326 | none |
| 8 | 4 | 443 | tee_axis, 0.8 | Black 443, Blue 412, White 380, Red 354 | fairway 5538, recovery 273, water 1347 | none |
| 9 | 4 | 473 | tee_axis, 0.8 | Black 473, Blue 435, White 398, Red 368 | fairway 5217, sand 486, water 2539 | none |
| 10 | 5 | 611 | tee_axis, 0.8 | Black 611, Blue 576, White 533, Red 476 | fairway 5582, ob 1071, recovery 2069, sand 351, water 149 | none |
| 11 | 4 | 385 | tee_axis, 0.8 | Black 385, Blue 354, White 329, Red 307 | fairway 5573, ob 299, recovery 866, sand 392, water 1212 | none |
| 12 | 4 | 409 | tee_axis, 0.8 | Black 409, Blue 375, White 349, Red 320 | fairway 5223, native 951, ob 401, recovery 243, sand 99 | none |
| 13 | 4 | 465 | tee_axis, 0.8 | Black 465, Blue 424, White 391, Red 358 | fairway 5964, ob 1664, recovery 1419, water 276 | none |
| 14 | 4 | 435 | tee_axis, 0.8 | Black 435, Blue 401, White 382, Red 324 | fairway 5718, ob 484, recovery 771, water 3178 | none |
| 16 | 4 | 316 | tee_axis, 0.8 | Black 316, Blue 295, White 274, Red 257 | fairway 4581, ob 2038, recovery 151, sand 780 | none |
| 18 | 5 | 544 | tee_axis, 0.8 | Black 544, Blue 506, White 469, Red 438 | fairway 5467, ob 871, recovery 2697, sand 196, water 631 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
