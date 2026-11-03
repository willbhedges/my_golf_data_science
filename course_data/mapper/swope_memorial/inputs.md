# Mapper inputs: Swope Memorial Golf Course (Kansas City, MO)

Base package: `course_data/mapper/swope_memorial/base/package.json` (built 2026-11-02T23:40:58Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Green**. Sets: Green, Bronze, Silver, Black.
Photo NAIP 2020; other years: NAIP 2022; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 46 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 390 | tee_axis, 0.8 | Green 390, Bronze 376, Silver 335, Black 272 | fairway 6370, recovery 1382 | none |
| 2 | 4 | 321 | tee_axis, 0.8 | Green 321, Bronze 307, Silver 257, Black 206 | fairway 4895, recovery 2015, sand 74 | none |
| 3 | 4 | 339 | tee_axis, 0.8 | Green 339, Bronze 325, Silver 294, Black 240 | fairway 3926, recovery 3075, sand 294 | none |
| 5 | 5 | 475 | tee_axis, 0.8 | Green 475, Bronze 461, Silver 434, Black 348 | fairway 2790, recovery 5750, sand 163 | none |
| 6 | 4 | 406 | tee_centroid, 0.9 | Green 406, Bronze 393, Silver 349, Black 227 | fairway 4169, recovery 3121, sand 110 | none |
| 8 | 4 | 273 | tee_centroid, 0.9 | Green 273, Bronze 259, Silver 225, Black 190 | fairway 2979, recovery 866, sand 616 | none |
| 9 | 4 | 371 | tee_axis, 0.8 | Green 371, Bronze 357, Silver 322, Black 277 | fairway 4804, recovery 3551 | none |
| 10 | 4 | 384 | tee_axis, 0.8 | Green 384, Bronze 371, Silver 333, Black 252 | fairway 4893, recovery 4949 | none |
| 11 | 4 | 375 | tee_axis, 0.8 | Green 375, Bronze 362, Silver 328, Black 275 | fairway 5218, recovery 2764, sand 90 | none |
| 12 | 5 | 533 | lidar_pad, 0.6 | Green 533, Bronze 519, Silver 475, Black 401 | fairway 7598, recovery 1036 | L1: 604, 9.8, L2: 588, 10.7 |
| 14 | 4 | 426 | tee_axis, 0.8 | Green 426, Bronze 413, Silver 372, Black 283 | fairway 7820, recovery 4050 | none |
| 15 | 4 | 347 | tee_centroid, 0.9 | Green 347, Bronze 333, Silver 284, Black 240 | fairway 5429, recovery 4608, sand 107 | none |
| 17 | 5 | 562 | tee_axis, 0.8 | Green 562, Bronze 549, Silver 505, Black 442 | fairway 5535, recovery 1421 | none |
| 18 | 4 | 413 | tee_axis, 0.8 | Green 413, Bronze 399, Silver 369, Black 299 | fairway 4578, recovery 2867 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
