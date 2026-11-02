# Old Works Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/old_works/page.html` (2.5 MB); request `course_data/requests/course_page_old_works.json`; built 2026-11-01T22:00Z
* course: Old Works Golf Club (Anaconda, MT), OSM way/296526499; holes: osm (tier unmapped_card); card: golfify (golfify)
* solved tee sets: Slag, Gold (the two longest sets on the card (combination sets skipped)); page sets: Slag, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [30, 45, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-06-28; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* OSM greens 0 of 18 holes
* 18 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Slag tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 2 | 4 | CHECK | Driver +25 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 3 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 5 | 4 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 6 | 5 | CHECK | Driver -34 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 8 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 9 | 4 | CHECK | Driver +24 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 10 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 11 | 5 | CHECK | Driver -38 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 12 | 4 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 14 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 15 | 5 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 16 | 4 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 18 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 2 | 4 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 3 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 5 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 6 | 5 | CHECK | Driver -34 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 8 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 9 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 10 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 11 | 5 | CHECK | Driver -38 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 12 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 14 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 15 | 5 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 16 | 4 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); par3_box: no OSM green outline (the target box is drawn on an estimated green) |
| 18 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course); aim: no fairway mapped on this hole; Driver lands in rough |

