# WeaverRidge Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 5, 6, 10, 13

* page: `course_data/library/weaver_ridge/page.html` (6.2 MB); request `course_data/requests/course_page_weaver_ridge.json`; built 2026-11-01T21:18Z
* course: WeaverRidge Golf Club (Peoria, IL), OSM way/749257217; holes: osm (tier mapped_card); card: course_data/library/weaver_ridge/card_review.json (file)
* solved tee sets: Black, Gold (tee sets of interest); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-25; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -3 | yardage: measured 529 vs card 540 (-11) |
| 2 | 4 | PASS | Driver +18 |  |
| 3 | 5 | PASS | Driver +6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver -18 | tee: tee marker not on an OSM tee box (walkback_capped; 31 yds from the nearest OSM tee box); yardage: measured 326 vs card 387 (-61) |
| 6 | 4 | PASS | 4-wood -6 |  |
| 7 | 4 | PASS | Driver +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -3 |  |
| 10 | 4 | PASS | 4-wood +40 |  |
| 11 | 5 | PASS | Driver +1 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +2 |  |
| 15 | 4 | PASS | Driver +4 |  |
| 16 | 4 | PASS | Driver -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Long iron +10 (tie) |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -5 |  |
| 2 | 4 | PASS | Driver +32 (tie) |  |
| 3 | 5 | PASS | Driver +2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +40 |  |
| 6 | 4 | CHECK | 4-wood -4 | aim: 4-wood -4 lands 279 yds out in rough (12 yds from fairway) |
| 7 | 4 | PASS | Driver +9 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | CHECK | 4-wood +40 | oval: landing pattern 48% trees / water / OB (recovery 24%, water 24%) |
| 11 | 5 | PASS | Driver +1 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +6 |  |
| 15 | 4 | PASS | 2-wood +17 |  |
| 16 | 4 | PASS | Driver -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Long iron +10 (tie) |  |

