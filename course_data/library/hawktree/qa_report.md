# Hawktree Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 7, 8, 10, 12, 14, 16

* page: `course_data/library/hawktree/page.html` (2.2 MB); request `course_data/requests/course_page_hawktree.json`; built 2026-10-31T03:43Z
* course: Hawktree Golf Club (Bismarck, ND), OSM way/852532291; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Falcon, Falcon 2 (the two longest sets on the card (combination sets skipped)); page sets: Falcon, Falcon 2
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-08-14; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Falcon tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver -12 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -8 |  |
| 5 | 5 | PASS | Driver -0 |  |
| 6 | 4 | PASS | Driver -18 |  |
| 7 | 5 | CHECK | Driver +0 | tee: tee marker not on an OSM tee box (walkback; 548 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 8 | 3 | CHECK |  | yardage: measured 180 vs card 194 (-14) |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 5 | CHECK | Driver +37 | aim: Driver +37 lands 329 yds out in rough (6 yds from fairway) |
| 11 | 4 | PASS | Driver +8 |  |
| 12 | 4 | CHECK | Driver -18 | tee: tee marker not on an OSM tee box (lidar_pad; 48 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 5 | CHECK | Driver -10 | yardage: measured 527 vs card 540 (-13) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | CHECK | 2-wood -36 | aim: 2-wood -36 lands 297 yds out in rough (8 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -22 |  |

## Falcon 2 tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver -12 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -8 |  |
| 5 | 5 | PASS | Driver -0 |  |
| 6 | 4 | PASS | Driver -18 |  |
| 7 | 5 | CHECK | Driver +0 | tee: tee marker not on an OSM tee box (walkback; 548 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |
| 8 | 3 | CHECK |  | yardage: measured 180 vs card 194 (-14) |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 5 | CHECK | Driver +37 | aim: Driver +37 lands 329 yds out in rough (6 yds from fairway) |
| 11 | 4 | PASS | Driver +8 |  |
| 12 | 4 | PASS | Driver -30 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | CHECK | Driver -10 | yardage: measured 527 vs card 540 (-13) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | CHECK | 2-wood -36 | aim: 2-wood -36 lands 297 yds out in rough (8 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -22 |  |

