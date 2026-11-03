# Mapper inputs: The Falls Golf Club (O'Fallon, MO)

Base package: `course_data/mapper/the_falls_ofallon/base/package.json` (built 2026-11-02T23:41:08Z; committed package: tees rebuilt: 8 tee(s) moved). Corridor set **Gold**. Sets: Gold, Blue, White, Red.
Photo NAIP 2022; other years: NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 4 sets; lidar pads: 103 candidate pa; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 416 | tee_axis, 0.8 | Gold 416, Blue 386, White 363, Red 310 | fairway 5044, recovery 3671, sand 208, water 401 | none |
| 2 | 4 | 390 | tee_centroid, 0.4 | Gold 390, Blue 379, White 350, Red 305 | fairway 4793, ob 1889, recovery 1854, water 110 | none |
| 3 | 4 | 368 | tee_axis, 0.4 | Gold 368, Blue 341, White 332, Red 280 | fairway 4011, ob 1532, recovery 3648, water 1388 | none |
| 5 | 4 | 419 | tee_axis, 0.8 | Gold 419, Blue 389, White 356, Red 310 | fairway 4632, ob 1530, recovery 1743, water 1259 | none |
| 6 | 5 | 524 | tee_axis, 0.8 | Gold 524, Blue 492, White 451, Red 410 | fairway 4197, ob 1536, recovery 1990, sand 267 | none |
| 7 | 4 | 428 | tee_axis, 0.8 | Gold 428, Blue 378, White 355, Red 315 | fairway 4377, ob 539, recovery 1822, sand 272 | none |
| 9 | 5 | 476 | tee_axis, 0.4 | Gold 476, Blue 449, White 434, Red 361 | fairway 3803, recovery 4330, sand 407, water 594 | none |
| 10 | 4 | 374 | tee_axis, 0.4 | Gold 374, Blue 360, White 341, Red 307 | fairway 3261, ob 152, recovery 2294, water 4264 | none |
| 11 | 4 | 365 | review (inside OSM tee 1243312620), 0.4 | Gold 365, Blue 365, White 338, Red 288 | fairway 4488, ob 757, recovery 2621 | none |
| 13 | 4 | 344 | tee_axis, 0.4 | Gold 344, Blue 345, White 311, Red 254 | fairway 3372, ob 109, recovery 955, water 2348 | none |
| 15 | 5 | 506 | tee_axis, 0.4 | Gold 506, Blue 510, White 483, Red 400 | fairway 4805, ob 1409, recovery 1205, sand 294 | none |
| 16 | 4 | 330 | review (inside OSM tee 705151255), 0.4 | Gold 330, Blue 330, White 319, Red 267 | fairway 2269, ob 3696, recovery 1443, sand 195, water 1423 | none |
| 18 | 5 | 482 | tee_axis, 0.4 | Gold 482, Blue 482, White 463, Red 437 | fairway 4373, ob 1647, recovery 3078, water 1649 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
