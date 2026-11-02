# Mapper inputs: Pevely Farms Golf Course (Saint Louis, MO)

Base package: `course_data/mapper/pevely_farms/base/package.json` (built 2026-11-02T21:44:10Z; committed package). Corridor set **Black**. Sets: Black, Blue, White, Red.
Photo NAIP 2022; other years: NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 79 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 446 | tee_centroid, 0.9 | Black 446, Blue 425, White 388, Red 355 | fairway 3986, recovery 2070 | none |
| 2 | 5 | 531 | tee_axis, 0.8 | Black 531, Blue 524, White 492, Red 441 | fairway 4813 | L1: 564, 25.0, R1: 216, 26.5 |
| 3 | 4 | 277 | lidar_pad, 0.6 | Black 277, Blue 250, White 235, Red 191 | fairway 2403, ob 1219, recovery 729, sand 94, water 396 | R1: 1657, 13.3, R2: 1644, 16.2 |
| 4 | 4 | 439 | tee_axis, 0.8 | Black 439, Blue 426, White 383, Red 336 | fairway 4219, ob 229, recovery 730 | none |
| 6 | 4 | 398 | tee_axis, 0.8 | Black 398, Blue 363, White 321, Red 309 | fairway 2853, ob 1122, water 3227 | none |
| 7 | 4 | 397 | tee_axis, 0.8 | Black 397, Blue 384, White 353, Red 228 | fairway 3683, ob 89, recovery 751, water 2927 | none |
| 9 | 5 | 527 | tee_axis, 0.8 | Black 527, Blue 506, White 481, Red 424 | fairway 4472, ob 283 | R1: 208, 36.0 |
| 10 | 4 | 403 | tee_centroid, 0.9 | Black 403, Blue 384, White 352, Red 306 | fairway 3564, ob 814, recovery 2969 | none |
| 11 | 4 | 401 | walkback, 0.5 | Black 401, Blue 381, White 352, Red 323 | fairway 3833, ob 1041, recovery 4242, water 21 | none |
| 12 | 5 | 572 | tee_axis, 0.8 | Black 572, Blue 544, White 527, Red 465 | fairway 3614, ob 298, recovery 973, water 1758 | none |
| 13 | 4 | 389 | tee_axis, 0.8 | Black 389, Blue 371, White 335, Red 283 | fairway 3541, ob 740, recovery 3438, water 1844 | none |
| 15 | 4 | 358 | tee_axis, 0.8 | Black 358, Blue 344, White 328, Red 248 | fairway 3841, recovery 1545, sand 112 | none |
| 16 | 4 | 443 | tee_axis, 0.8 | Black 443, Blue 439, White 403, Red 324 | fairway 2407, recovery 2628 | R1: 756, 15.8, R2: 232, 32.6 |
| 17 | 4 | 422 | tee_centroid, 0.9 | Black 422, Blue 408, White 376, Red 303 | fairway 4787, recovery 647, sand 15 | L1: 235, 20.5, R1: 266, 9.6 |
| 18 | 4 | 468 | walkback, 0.5 | Black 468, Blue 453, White 408, Red 325 | fairway 4341, ob 32, recovery 1574, sand 515 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
