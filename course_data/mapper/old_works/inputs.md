# Mapper inputs: Old Works Golf Club (Anaconda, MT)

Base package: `course_data/mapper/old_works/base/package.json` (built 2026-11-03T17:42:21Z; committed package: tees rebuilt: 0 tee(s) moved). Corridor set **Slag**. Sets: Slag, Gold, Copper, Limestone, Limestone (L), Brick, Brick (L).
Photo NAIP 2021; other years: NAIP 2023; lidar canopy: NO (trees can only be checked on the photo); CIR: yes.

Auto layer sources: tees: ok: tees/localize v2 (osm+lidar+texture pads, joint chain assignment) for 7 sets; lidar pads: 0 candidate pads; vision: ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar canopy edge buffer); ; segment: not run (no course_data/segment/<slug>/segment.geojson; commit requests/segment_<slug>.json); ob: ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow hand OB); layers osm+ms

S2 native suggestion: **full** (full model (trained on 23 courses; this course is not one of them)); P >= 0.5 clusters outside the package fairway / first cut / green / water / sand / trees, per side (`render/hNN_corridor_s2.png`, edits.template.json `s2_suggested`). A hint where to look: decide every candidate from the photos (BRIEF 'S2 suggestions').

| hole | par | card yds | auto tee (corridor set): method, conf | sets on the hole | AUTO landing zone 180-330 x +/-50 (sq yds) | S2 suggested native (id: sq yds, gap to fairway yds) |
|---|---|---|---|---|---|---|
| 1 | 4 | 451 | walkback, 0.5 | Slag 451, Gold 424, Copper 416, Limestone 392, Limestone (L) 392, Brick 321, Brick (L) 321 | fairway 9141, water 906 | none |
| 2 | 4 | 361 | walkback, 0.5 | Slag 361, Gold 334, Copper 310, Limestone 260, Limestone (L) 260, Brick 219, Brick (L) 219 | fairway 8920, sand 64 | none |
| 3 | 5 | 587 | walkback, 0.5 | Slag 587, Gold 555, Copper 532, Limestone 504, Limestone (L) 504, Brick 448, Brick (L) 448 | fairway 9118, sand 757 | none |
| 5 | 4 | 463 | walkback, 0.5 | Slag 463, Gold 454, Copper 424, Limestone 387, Limestone (L) 387, Brick 310, Brick (L) 310 | fairway 8555, sand 789 | none |
| 6 | 5 | 600 | walkback, 0.5 | Slag 600, Gold 570, Copper 552, Limestone 497, Limestone (L) 497, Brick 459, Brick (L) 459 | fairway 10033, sand 237 | none |
| 8 | 4 | 435 | walkback, 0.5 | Slag 435, Gold 389, Copper 360, Limestone 331, Limestone (L) 331, Brick 302, Brick (L) 302 | fairway 7822, sand 1080 | none |
| 9 | 4 | 485 | walkback, 0.5 | Slag 485, Gold 427, Copper 404, Limestone 363, Limestone (L) 363, Brick 315, Brick (L) 315 | fairway 7539 | none |
| 10 | 4 | 442 | walkback, 0.5 | Slag 442, Gold 422, Copper 396, Limestone 353, Limestone (L) 353, Brick 298, Brick (L) 298 | fairway 9165, water 95 | none |
| 11 | 5 | 597 | walkback, 0.5 | Slag 597, Gold 581, Copper 546, Limestone 502, Limestone (L) 502, Brick 455, Brick (L) 455 | fairway 9319 | none |
| 12 | 4 | 445 | walkback, 0.5 | Slag 445, Gold 421, Copper 397, Limestone 343, Limestone (L) 343, Brick 312, Brick (L) 312 | fairway 10006 | none |
| 14 | 4 | 443 | walkback, 0.5 | Slag 443, Gold 409, Copper 380, Limestone 338, Limestone (L) 338, Brick 299, Brick (L) 299 | fairway 7487 | none |
| 15 | 5 | 644 | walkback, 0.5 | Slag 644, Gold 605, Copper 573, Limestone 522, Limestone (L) 522, Brick 470, Brick (L) 470 | fairway 6697, recovery 566, water 723 | none |
| 16 | 4 | 471 | walkback, 0.5 | Slag 471, Gold 459, Copper 436, Limestone 395, Limestone (L) 395, Brick 348, Brick (L) 348 | fairway 9429, water 586 | none |
| 18 | 4 | 440 | walkback, 0.5 | Slag 440, Gold 411, Copper 374, Limestone 341, Limestone (L) 341, Brick 298, Brick (L) 298 | fairway 7441 | none |

Par 3s are not corridors (their tees are still checked in edits.json `tees`).
