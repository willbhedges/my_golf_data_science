# Mapper inputs: Creekmoor Golf Club (Raymore, MO)

Base package: `course_data/mapper/creekmoor/base/package.json` (built 2026-11-02T13:54:32Z; committed package: tees rebuilt: 4 tee(s) moved). Corridor set **Black**. Sets: Black, Green, White, Red.
Photo NAIP 2018; other years: NAIP 2022, NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 74 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 404 | tee_axis, 0.8 | Black 404, Green 377, White 342, Red 306 | recovery 526, sand 493 | none |
| 2 | 4 | 371 | tee_centroid, 0.9 | Black 371, Green 345, White 321, Red 290 | ob 880, recovery 1442, sand 621 | none |
| 3 | 4 | 440 | lidar_pad, 0.6 | Black 440, Green 412, White 385, Red 319 | ob 1431, recovery 912, sand 473 | none |
| 5 | 5 | 537 | tee_centroid, 0.9 | Black 537, Green 500, White 453, Red 410 | ob 499, sand 500, water 559 | none |
| 6 | 4 | 451 | tee_centroid, 0.9 | Black 451, Green 404, White 371, Red 311 | ob 1450, sand 527 | none |
| 8 | 4 | 441 | tee_centroid, 0.9 | Black 441, Green 409, White 365, Red 305 | ob 3407, recovery 190, sand 362 | none |
| 9 | 5 | 663 | tee_centroid, 0.9 | Black 663, Green 619, White 572, Red 503 | ob 1522, sand 77, water 4405 | none |
| 10 | 4 | 482 | tee_axis, 0.8 | Black 482, Green 448, White 387, Red 336 | ob 3796, recovery 1, sand 308, water 22 | none |
| 11 | 4 | 374 | tee_centroid, 0.9 | Black 374, Green 350, White 317, Red 284 | ob 379, recovery 1744, sand 576, water 37 | none |
| 13 | 5 | 548 | tee_centroid, 0.9 | Black 548, Green 509, White 466, Red 423 | sand 676 | none |
| 14 | 4 | 420 | tee_axis, 0.8 | Black 420, Green 387, White 351, Red 312 | recovery 839, sand 369 | none |
| 15 | 4 | 460 | tee_axis, 0.8 | Black 460, Green 435, White 400, Red 349 | ob 1466, recovery 941, sand 839, water 109 | none |
| 16 | 4 | 455 | tee_axis, 0.8 | Black 455, Green 398, White 365, Red 335 | ob 145, sand 898, water 1257 | none |
| 18 | 5 | 541 | tee_axis, 0.8 | Black 541, Green 508, White 465, Red 417 | sand 326, water 1079 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
