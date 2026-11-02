# Colbert Hills Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 4, 7, 13, 14, 17

* page: `course_data/library/colbert_hills/page.html` (5.5 MB); request `course_data/requests/course_page_colbert_hills.json`; built 2026-11-02T10:49Z
* course: Colbert Hills Golf Course (Manhattan, KS), OSM relation/13772939; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black/Blue, Silver (tee sets of interest); page sets: Black/Blue, Silver
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 55, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-20,2023-06-06; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* OSM greens 17 of 18 holes
* scorecard not matched (source opengolfapi, flags ['Purple: holes sum to 6432 but the source says 6452 (-20): mixed card versions'])
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black/Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -23 | yardage: measured 561 vs card 590 (-29) |
| 2 | 4 | PASS | Driver -16 |  |
| 3 | 4 | PASS | Driver -25 |  |
| 4 | 4 | PASS | 4-wood -14 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +4 |  |
| 7 | 5 | CHECK | Driver +16 | aim: Driver +16 lands 338 yds out in rough (12 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -16 |  |
| 10 | 5 | PASS | Driver -0 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -2 |  |
| 13 | 4 | PASS | Driver +52 |  |
| 14 | 4 | PASS | Driver +8 |  |
| 15 | 4 | PASS | Driver +8 |  |
| 16 | 5 | PASS | Driver -14 |  |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +0 (tie) |  |

## Silver tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (tee_axis; 8 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver -32 (tie) |  |
| 3 | 4 | CHECK | Driver -46 | aim: Driver -46 lands 284 yds out in rough (15 yds from fairway) |
| 4 | 4 | CHECK | Driver +16 | aim: Driver +16 lands 315 yds out in rough (19 yds from fairway) |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +8 |  |
| 7 | 5 | PASS | Driver +20 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -16 |  |
| 10 | 5 | PASS | Driver +2 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +2 |  |
| 13 | 4 | CHECK | Driver +50 | aim: Driver +50 lands 302 yds out in sand (6 yds from fairway) |
| 14 | 4 | CHECK | Driver +16 (tie) | aim: Driver +16 lands 335 yds out in rough (14 yds from fairway) |
| 15 | 4 | PASS | Driver +12 |  |
| 16 | 5 | PASS | Driver -17 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +28 |  |

