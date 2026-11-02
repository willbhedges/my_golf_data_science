# Mapper inputs: Falcon Ridge Golf Course (Lenexa, KS)

Base package: `course_data/mapper/falcon_ridge/base/package.json` (built 2026-11-02T10:26:23Z; committed package: tees rebuilt: 1 tee(s) moved). Corridor set **Black**. Sets: Black, Blue, White, Red.
Photo NAIP 2023; other years: NAIP 2021; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 83 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **none** (no S2 stack for this course): long grass from the photos only.

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 375 | tee_axis, 0.8 | Black 375, Blue 338, White 328, Red 270 | fairway 5940, ob 1078, sand 204 | no S2 |
| 2 | 4 | 419 | tee_centroid, 0.9 | Black 419, Blue 383, White 346, Red 287 | fairway 5133, ob 2509, recovery 938 | no S2 |
| 3 | 4 | 370 | tee_centroid, 0.9 | Black 370, Blue 348, White 338, Red 279 | fairway 5217, ob 2882, recovery 348, sand 99 | no S2 |
| 4 | 4 | 486 | tee_centroid, 0.9 | Black 486, Blue 450, White 417, Red 384 | fairway 3682, ob 1234, recovery 867, sand 91 | no S2 |
| 6 | 5 | 499 | walkback, 0.5 | Black 499, Blue 477, White 464, Red 396 | ob 1491, recovery 2429 | no S2 |
| 8 | 5 | 513 | lidar_pad, 0.6 | Black 513, Blue 500, White 490, Red 441 | ob 2238, recovery 194 | no S2 |
| 9 | 4 | 415 | lidar_pad, 0.6 | Black 415, Blue 387, White 371, Red 331 | ob 436 | no S2 |
| 10 | 4 | 417 | tee_axis, 0.8 | Black 417, Blue 364, White 354, Red 303 | fairway 6004, ob 1767, recovery 784, sand 158 | no S2 |
| 11 | 5 | 568 | tee_axis, 0.8 | Black 568, Blue 548, White 532, Red 496 | fairway 4703, ob 3565, recovery 1007 | no S2 |
| 13 | 4 | 436 | lidar_pad, 0.6 | Black 436, Blue 409, White 391, Red 291 | ob 3285, recovery 782 | no S2 |
| 15 | 5 | 529 | lidar_pad, 0.6 | Black 529, Blue 499, White 487, Red 448 | ob 268, recovery 291 | no S2 |
| 17 | 5 | 517 | tee_axis, 0.8 | Black 517, Blue 498, White 477, Red 428 | fairway 5909, recovery 2457, sand 231 | no S2 |
| 18 | 4 | 401 | tee_axis, 0.8 | Black 401, Blue 373, White 354, Red 306 | fairway 4409, ob 3963, recovery 319, sand 311 | no S2 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
