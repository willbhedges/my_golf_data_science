# Mapper inputs: Dub's Dread Golf Club (Kansas City, KS)

Base package: `course_data/mapper/dubs_dread/base/package.json` (built 2026-11-02T21:39:01Z; committed package: tees rebuilt: 3 tee(s) moved). Corridor set **Championship**. Sets: Championship, Back, Middle, Middle/Forward, Forward.
Photo NAIP 2021; other years: NAIP 2023; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 47 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 515 | tee_centroid, 0.9 | Championship 515, Back 491, Middle 456, Middle/Forward 450, Forward 412 | fairway 4511, recovery 4155 | none |
| 2 | 4 | 410 | tee_axis, 0.8 | Championship 410, Back 367, Middle 331, Middle/Forward 305, Forward 277 | fairway 4582, native 249, recovery 3257 | none |
| 3 | 4 | 446 | tee_axis, 0.8 | Championship 446, Back 420, Middle 397, Middle/Forward 387, Forward 320 | fairway 3142, recovery 3220, water 697 | none |
| 5 | 4 | 382 | tee_axis, 0.4 | Championship 382, Back 351, Middle 325, Middle/Forward 305, Forward 299 | fairway 4223, recovery 2665 | none |
| 6 | 4 | 467 | tee_centroid, 0.9 | Championship 467, Back 427, Middle 417, Middle/Forward 344, Forward 339 | fairway 3498, recovery 4098 | L1: 353, 31.1 |
| 7 | 5 | 550 | tee_centroid, 0.9 | Championship 550, Back 535, Middle 513, Middle/Forward 496, Forward 437 | fairway 4054, recovery 1139 | none |
| 9 | 4 | 418 | tee_axis, 0.4 | Championship 418, Back 381, Middle 365, Middle/Forward 352, Forward 345 | fairway 4125, recovery 3123 | none |
| 10 | 4 | 362 | tee_axis, 0.8 | Championship 362, Back 344, Middle 333, Middle/Forward 330, Forward 325 | fairway 3979, ob 2443, recovery 1963 | none |
| 12 | 5 | 547 | tee_axis, 0.8 | Championship 547, Back 530, Middle 519, Middle/Forward 510, Forward 400 | fairway 4924, recovery 248, water 744 | none |
| 13 | 4 | 420 | lidar_pad, 0.6 | Championship 420, Back 358, Middle 338, Middle/Forward 336, Forward 326 | fairway 4507, ob 2507, recovery 601, water 2180 | none |
| 14 | 4 | 444 | tee_centroid, 0.9 | Championship 444, Back 425, Middle 412, Middle/Forward 310, Forward 306 | fairway 4046, ob 36, recovery 1277 | none |
| 15 | 4 | 409 | tee_axis, 0.8 | Championship 409, Back 361, Middle 345, Middle/Forward 340, Forward 323 | fairway 4404, recovery 1801, water 353 | none |
| 17 | 5 | 555 | tee_axis, 0.8 | Championship 555, Back 530, Middle 505, Middle/Forward 495, Forward 375 | fairway 4437, recovery 1665, water 543 | none |
| 18 | 4 | 433 | tee_centroid, 0.9 | Championship 433, Back 415, Middle 390, Middle/Forward 360, Forward 356 | fairway 3665, recovery 3794 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
