# Mapper inputs: Osage National Golf Club (Osage Beach, MO)

Base package: `course_data/mapper/osage_national/base/package.json` (built 2026-11-02T10:28:55Z; committed package: tees rebuilt: 0 tee(s) moved; trees rebuilt: buffer -1 m, 215 tree zones). Corridor set **Palmer**. Sets: Palmer, Tournament, Middle, Members, Forward, Green.
Photo NAIP 2016; other years: NAIP 2022, NAIP 2020; lidar canopy: yes; CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 6 sets; lidar pads: 108 candidate pa; vision: ok: vision_any/1 (lidar canopy + NAIP native, OSM-self-supervised); segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **loco** (leave-one-course-out fold model (trained on the 22 other S2 training courses, not on this one)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 377 | tee_axis, 0.8 | Palmer 377, Tournament 352, Middle 306, Members 283, Forward 231, Green 190 | fairway 2550, recovery 3091, sand 303 | none |
| 2 | 4 | 455 | walkback, 0.5 | Palmer 455, Tournament 425, Middle 393, Members 353, Forward 285, Green 240 | fairway 3725, recovery 1934, sand 218 | none |
| 3 | 4 | 370 | lidar_pad, 0.6 | Palmer 370, Tournament 335, Middle 307, Members 264, Forward 253, Green 190 | fairway 4435, ob 1421, recovery 1281, sand 661 | L1: 332, 29.8 |
| 5 | 4 | 441 | tee_axis, 0.8 | Palmer 441, Tournament 434, Middle 405, Members 376, Forward 344, Green 266 | fairway 4943, ob 3329, recovery 2, sand 135 | R1: 1543, 9.4, R2: 242, 5.0, R3: 222, 29.0 |
| 6 | 4 | 428 | lidar_pad, 0.6 | Palmer 428, Tournament 397, Middle 383, Members 359, Forward 341, Green 250 | fairway 6422, sand 342, water 1990 | L1: 512, 26.3, L2: 380, 79.8 |
| 7 | 5 | 612 | lidar_pad, 0.6 | Palmer 612, Tournament 597, Middle 527, Members 500, Forward 258, Green 258 | fairway 4135, recovery 62, sand 357, water 2773 | none |
| 9 | 5 | 512 | tee_axis, 0.8 | Palmer 512, Tournament 483, Middle 469, Members 430, Forward 373, Green 333 | fairway 4763, recovery 451, sand 10, water 904 | none |
| 10 | 4 | 398 | tee_axis, 0.8 | Palmer 398, Tournament 383, Middle 367, Members 329, Forward 315, Green 240 | fairway 6392, recovery 663, water 1675 | none |
| 11 | 4 | 445 | tee_centroid, 0.9 | Palmer 445, Tournament 421, Middle 391, Members 364, Forward 318, Green 250 | fairway 6602, recovery 393, sand 383, water 308 | none |
| 12 | 4 | 433 | tee_axis, 0.8 | Palmer 433, Tournament 400, Middle 370, Members 322, Forward 292, Green 252 | fairway 6699, sand 8, water 434 | none |
| 14 | 5 | 525 | tee_axis, 0.8 | Palmer 525, Tournament 511, Middle 475, Members 459, Forward 420, Green 350 | fairway 5753, recovery 2795, water 1316 | R1: 505, 41.1 |
| 15 | 4 | 314 | tee_axis, 0.8 | Palmer 314, Tournament 291, Middle 271, Members 271, Forward 220, Green 220 | fairway 2970, recovery 1264, sand 251, water 3148 | none |
| 17 | 4 | 442 | tee_centroid, 0.9 | Palmer 442, Tournament 404, Middle 381, Members 337, Forward 308, Green 250 | fairway 6858, recovery 1382, sand 1594, water 45 | R1: 490, 27.0, R2: 219, 30.8, R3: 312, 17.0 |
| 18 | 5 | 626 | tee_axis, 0.8 | Palmer 626, Tournament 583, Middle 520, Members 477, Forward 425, Green 360 | fairway 7193, recovery 497, water 418 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
