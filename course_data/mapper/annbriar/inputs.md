# Mapper inputs: Annbriar Golf Course (Waterloo, IL)

Base package: `course_data/mapper/annbriar/base/package.json` (built 2026-11-02T02:32:39Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Black**. Sets: Black, Hickory, Maple, Oak, Pine.
Photo NAIP 2021; other years: NAIP 2023; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 5 sets; lidar pads: 104 candidate pa; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) |
|---|---|---|---|---|---|
| 1 | 4 | 337 | tee_axis, 0.8 | Black 337, Hickory 361, Maple 304, Oak 225, Pine 281 | fairway 5628, native 1784, recovery 9, sand 142 |
| 2 | 4 | 395 | tee_axis, 0.8 | Black 395, Hickory 435, Maple 364, Oak 289, Pine 340 | fairway 7158, native 791, sand 276 |
| 3 | 4 | 373 | tee_axis, 0.8 | Black 373, Hickory 385, Maple 343, Oak 275, Pine 310 | fairway 7859, native 444, recovery 447, sand 46 |
| 5 | 5 | 496 | tee_centroid, 0.9 | Black 496, Hickory 514, Maple 489, Oak 434, Pine 463 | fairway 6586, native 723, recovery 460, sand 384, water 1635 |
| 6 | 4 | 378 | tee_centroid, 0.9 | Black 378, Hickory 388, Maple 349, Oak 287, Pine 313 | fairway 6921, recovery 1294, sand 212, water 1804 |
| 8 | 4 | 415 | tee_centroid, 0.9 | Black 415, Hickory 426, Maple 400, Oak 283, Pine 354 | fairway 6727, native 752, recovery 1096, sand 95 |
| 9 | 5 | 475 | review (snapped 0 yds to OSM tee -1), 0.4 | Black 475, Hickory 495, Maple 427, Oak 384, Pine 401 | fairway 6146, native 891, recovery 2176, sand 431 |
| 10 | 4 | 382 | tee_centroid, 0.9 | Black 382, Hickory 408, Maple 361, Oak 310, Pine 342 | fairway 6358, native 296, recovery 1140, sand 70 |
| 11 | 4 | 404 | tee_axis, 0.8 | Black 404, Hickory 404, Maple 352, Oak 266, Pine 328 | fairway 7205, native 91, recovery 5128, sand 15, water 734 |
| 12 | 4 | 353 | tee_axis, 0.8 | Black 353, Hickory 368, Maple 321, Oak 258, Pine 299 | fairway 7406, native 342, recovery 578, sand 90 |
| 13 | 4 | 356 | tee_axis, 0.8 | Black 356, Hickory 383, Maple 309, Oak 251, Pine 283 | fairway 6895, native 259, recovery 1090, sand 73 |
| 14 | 5 | 492 | tee_centroid, 0.9 | Black 492, Hickory 509, Maple 467, Oak 368, Pine 424 | fairway 5946, recovery 5682, sand 226 |
| 16 | 4 | 446 | tee_axis, 0.8 | Black 446, Hickory 466, Maple 388, Oak 292, Pine 314 | fairway 6891, recovery 2360, sand 143 |
| 18 | 5 | 572 | tee_centroid, 0.9 | Black 572, Hickory 603, Maple 495, Oak 452, Pine 473 | fairway 6937, native 30, recovery 1423, sand 125 |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
