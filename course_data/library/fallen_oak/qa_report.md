# Fallen Oak Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 6, 7

* page: `course_data/library/fallen_oak/page.html` (3.0 MB); request `course_data/requests/course_page_fallen_oak.json`; built 2026-10-31T01:59Z
* course: Fallen Oak Golf Course (Saucier, MS), OSM way/677755041; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Tee 1, Tee 2 (the two longest sets on the card (combination sets skipped)); page sets: Tee 1, Tee 2
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2016-09-01; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Tee 1 tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -6 | yardage: measured 582 vs card 596 (-14) |
| 2 | 4 | PASS | Driver -5 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +2 (tie) |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 5 | CHECK | Driver -4 | yardage: measured 536 vs card 548 (-12) |
| 7 | 4 | CHECK | Driver +8 (tie) | aim: Driver +8 lands 306 yds out in rough (8 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +4 |  |
| 10 | 4 | PASS | Driver -1 |  |
| 11 | 4 | PASS | 4-wood +2 |  |
| 12 | 4 | PASS | Driver +2 |  |
| 13 | 5 | PASS | Driver -1 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +6 |  |
| 16 | 4 | PASS | Driver -8 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +4 |  |

## Tee 2 tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver -9 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood +2 |  |
| 5 | 4 | PASS | Driver -4 |  |
| 6 | 5 | PASS | 2-wood -4 (tie) |  |
| 7 | 4 | CHECK | Driver +12 | aim: Driver +12 lands 308 yds out in rough (13 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +10 |  |
| 10 | 4 | PASS | Driver +2 |  |
| 11 | 4 | PASS | 4-wood -4 |  |
| 12 | 4 | PASS | Driver +8 |  |
| 13 | 5 | PASS | Driver -14 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +20 |  |
| 16 | 4 | PASS | Driver +14 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -0 |  |

