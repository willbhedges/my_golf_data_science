# Ellis Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 6, 10, 13, 17

* page: `course_data/library/gate/gate_ellis/page.html` (4.4 MB); request `course_data/requests/course_page_gate_ellis.json`; built 2026-10-29T20:29Z
* course: Ellis Golf Course (Cedar Rapids, IA), OSM way/74271941; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Blue, White (tee sets of interest + the longest other set (White)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 4 | PASS | Driver +39 |  |
| 3 | 5 | PASS | Driver -8 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +6 |  |
| 6 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver -2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +6 |  |
| 10 | 4 | CHECK | Driver -2 | aim: Driver -2 lands 290 yds out in rough (7 yds from fairway) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver -6 |  |
| 13 | 4 | CHECK | 4-wood -29 (tie) | aim: 4-wood -29 lands 263 yds out in rough (23 yds from fairway) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +3 |  |
| 16 | 4 | PASS | 4-wood -8 |  |
| 17 | 5 | CHECK | Driver -40 (tie) | aim: Driver -40 lands 315 yds out in recovery (14 yds from fairway) |
| 18 | 4 | PASS | Driver -2 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +7 |  |
| 2 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 310 yds out in rough (9 yds from fairway) |
| 3 | 5 | PASS | Driver -10 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +5 |  |
| 6 | 4 | PASS | Driver +6 |  |
| 7 | 4 | PASS | Driver +3 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +6 |  |
| 10 | 4 | PASS | Driver +12 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver -8 |  |
| 13 | 4 | CHECK | 4-wood -36 (tie) | aim: 4-wood -36 lands 262 yds out in rough (20 yds from fairway) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | 2-wood +3 |  |
| 16 | 4 | PASS | Driver -18 |  |
| 17 | 5 | PASS | Driver +6 |  |
| 18 | 4 | PASS | 2-wood +25 |  |

