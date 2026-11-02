# Mapper inputs: St Andrews Golf Club (Overland Park, KS)

Base package: `course_data/mapper/st_andrews_op/base/package.json` (built 2026-11-02T21:45:09Z; committed package: tees rebuilt: 1 tee(s) moved). Corridor set **Black**. Sets: Black, Blue, White, Gold, Red.
Photo NAIP 2021; other years: NAIP 2023; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 74 candidate pad; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **none** (no S2 stack for this course): long grass from the photos only.

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 5 | 560 | tee_axis, 0.8 | Black 560, Blue 518, White 484, Gold 456, Red 421 | fairway 5400, recovery 2107, sand 804, water 296 | no S2 |
| 2 | 4 | 354 | tee_centroid, 0.9 | Black 354, Blue 332, White 310, Gold 221, Red 200 | fairway 4848, recovery 1693, sand 682 | no S2 |
| 3 | 4 | 343 | tee_axis, 0.8 | Black 343, Blue 313, White 313, Gold 232, Red 212 | fairway 4558, ob 450, recovery 8110 | no S2 |
| 5 | 4 | 330 | tee_axis, 0.8 | Black 330, Blue 323, White 312, Gold 255, Red 219 | fairway 3257, recovery 3325, sand 214 | no S2 |
| 7 | 5 | 524 | tee_centroid, 0.9 | Black 524, Blue 503, White 483, Gold 421, Red 377 | fairway 4678, recovery 5728, sand 46 | no S2 |
| 8 | 4 | 384 | tee_axis, 0.8 | Black 384, Blue 373, White 343, Gold 301, Red 279 | fairway 4676, recovery 3393, sand 137 | no S2 |
| 9 | 4 | 386 | tee_axis, 0.8 | Black 386, Blue 368, White 343, Gold 287, Red 244 | fairway 4139, recovery 4156 | no S2 |
| 10 | 5 | 577 | lidar_pad, 0.6 | Black 577, Blue 541, White 517, Gold 481, Red 440 | fairway 4665, recovery 4407 | no S2 |
| 11 | 4 | 384 | tee_axis, 0.8 | Black 384, Blue 358, White 311, Gold 257, Red 208 | fairway 4993, recovery 3085, water 1982 | no S2 |
| 13 | 4 | 328 | tee_axis, 0.8 | Black 328, Blue 304, White 284, Gold 268, Red 196 | fairway 4177, recovery 8129, sand 96 | no S2 |
| 15 | 5 | 498 | tee_axis, 0.8 | Black 498, Blue 474, White 444, Gold 402, Red 364 | fairway 5294, recovery 5448, sand 389, water 2004 | no S2 |
| 16 | 4 | 393 | tee_axis, 0.4 | Black 393, Blue 391, White 365, Gold 260, Red 241 | fairway 4465, recovery 668 | no S2 |
| 18 | 4 | 397 | tee_axis, 0.8 | Black 397, Blue 388, White 372, Gold 259, Red 242 | fairway 4458, recovery 3833 | no S2 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
