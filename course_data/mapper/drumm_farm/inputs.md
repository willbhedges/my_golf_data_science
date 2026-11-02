# Mapper inputs: Drumm Farm Golf Club (Independence, MO)

Base package: `course_data/mapper/drumm_farm/base/package.json` (built 2026-11-02T14:27:34Z; committed package: tees rebuilt: 1 tee(s) moved). Corridor set **Tour**. Sets: Tour, Championship, Preferred, Forward.
Photo NAIP 2018; other years: NAIP 2022, NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 81 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 379 | tee_axis, 0.8 | Tour 379, Championship 357, Preferred 338, Forward 238 | fairway 6066, sand 176 | none |
| 2 | 4 | 444 | tee_axis, 0.8 | Tour 444, Championship 414, Preferred 390, Forward 292 | fairway 5400, recovery 385, sand 45 | L1: 472, 12.5, L2: 348, 17.9, L3: 714, 11.9, R1: 186, 75.3, R2: 212, 64.1 |
| 4 | 4 | 402 | tee_axis, 0.8 | Tour 402, Championship 356, Preferred 334, Forward 274 | fairway 6205, recovery 96, sand 140 | R1: 231, 30.4 |
| 5 | 4 | 460 | tee_axis, 0.8 | Tour 460, Championship 408, Preferred 385, Forward 358 | fairway 5117, sand 278 | none |
| 7 | 5 | 598 | lidar_pad, 0.4 | Tour 598, Championship 548, Preferred 533, Forward 469 | fairway 4477, ob 62, recovery 584, sand 288 | none |
| 8 | 4 | 390 | lidar_pad, 0.6 | Tour 390, Championship 364, Preferred 342, Forward 282 | fairway 5045, recovery 1499, sand 243 | L1: 706, 12.8, L2: 305, 19.1, L3: 438, 11.8 |
| 9 | 5 | 516 | tee_axis, 0.8 | Tour 516, Championship 492, Preferred 462, Forward 396 | fairway 5135, ob 815, recovery 785 | none |
| 10 | 4 | 444 | tee_axis, 0.8 | Tour 444, Championship 414, Preferred 380, Forward 318 | fairway 5851, ob 74, sand 92, water 1845 | none |
| 11 | 4 | 377 | tee_axis, 0.8 | Tour 377, Championship 348, Preferred 298, Forward 266 | fairway 4737 | none |
| 12 | 4 | 459 | tee_axis, 0.8 | Tour 459, Championship 428, Preferred 412, Forward 369 | fairway 5170, ob 41, sand 327 | none |
| 13 | 4 | 414 | walkback, 0.5 | Tour 414, Championship 388, Preferred 359, Forward 288 | fairway 4677, recovery 2309, sand 142 | none |
| 15 | 5 | 534 | tee_axis, 0.8 | Tour 534, Championship 497, Preferred 471, Forward 411 | fairway 5409 | none |
| 16 | 4 | 342 | tee_axis, 0.8 | Tour 342, Championship 320, Preferred 289, Forward 237 | fairway 4273, recovery 2134, sand 208, water 1995 | none |
| 18 | 5 | 528 | tee_axis, 0.8 | Tour 528, Championship 496, Preferred 470, Forward 394 | fairway 4962, recovery 2645, sand 97 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
