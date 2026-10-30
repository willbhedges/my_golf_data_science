# Falcon Ridge Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 6, 7, 8, 9, 11, 12, 13, 14, 15, 18

* page: `course_data/library/falcon_ridge/page.html` (5.0 MB); request `course_data/requests/course_page_falcon_ridge.json`; built 2026-10-30T03:27Z
* course: Falcon Ridge Golf Course (Lenexa, KS), OSM relation/3961566; holes: osm (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16,2023-08-17; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* OSM greens 11 of 18 holes
* 10 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 4 | PASS | Driver -6 |  |
| 3 | 4 | PASS | Driver +3 (tie) |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (walkback; 132 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 328 yds from the nearest OSM tee box); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 8 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (lidar_pad; 287 yds from the nearest OSM tee box); yardage: measured 500 vs card 513 (-13); aim: no fairway mapped on this hole; Driver lands in rough |
| 9 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 387 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 10 | 4 | PASS | Driver +29 |  |
| 11 | 5 | PASS | 4-wood +6 (tie) |  |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 502 yds from the nearest OSM tee box); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 13 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (lidar_pad; 681 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; 786 yds from the nearest OSM tee box); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 15 | 5 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (lidar_pad; 546 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -26 |  |
| 18 | 4 | PASS | Driver +13 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 |  |
| 2 | 4 | PASS | 2-wood -4 (tie) |  |
| 3 | 4 | PASS | 4-wood +5 (tie) |  |
| 4 | 4 | PASS | Driver -6 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (lidar_pad; 137 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 305 yds from the nearest OSM tee box); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 8 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (lidar_pad; 287 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 9 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 358 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 10 | 4 | PASS | Driver -9 |  |
| 11 | 5 | CHECK | Driver +21 | tee: tee marker not on an OSM tee box (lidar_pad; 37 yds from the nearest OSM tee box); aim: Driver +21 lands 311 yds out in rough (10 yds from fairway) |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 536 yds from the nearest OSM tee box); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 13 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (texture_pad; 690 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 748 yds from the nearest OSM tee box); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 15 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 524 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -23 |  |
| 18 | 4 | CHECK | 4-wood +30 | tee: tee marker not on an OSM tee box (lidar_pad; 40 yds from the nearest OSM tee box) |

