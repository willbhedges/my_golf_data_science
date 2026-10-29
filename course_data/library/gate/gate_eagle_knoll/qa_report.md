# Eagle Knoll Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 7, 9, 18

* page: `course_data/library/gate/gate_eagle_knoll/page.html` (2.7 MB); request `course_data/requests/course_page_gate_eagle_knoll.json`; built 2026-10-29T20:36Z
* course: Eagle Knoll Golf Club (Hartsburg, MO), OSM way/389825776; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Back, Eagle (tee sets of interest + the longest other set (Eagle)); page sets: Back, Eagle
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-11; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -34 | aim: Driver -34 lands 329 yds out in rough (6 yds from fairway) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +10 |  |
| 4 | 4 | PASS | Driver -6 |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -6 |  |
| 8 | 4 | PASS | Driver +12 |  |
| 9 | 5 | PASS | Driver -1 |  |
| 10 | 4 | PASS | 4-wood +2 |  |
| 11 | 4 | PASS | Driver +2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +14 |  |
| 14 | 4 | PASS | Mid iron +12 |  |
| 15 | 4 | PASS | 4-wood -15 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | 4-wood +12 |  |
| 18 | 4 | PASS | Driver +2 |  |

## Eagle tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -2 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +6 |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 4 | PASS | Driver +3 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver -6 | yardage: measured 482 vs card 493 (-11) |
| 8 | 4 | PASS | Driver +11 |  |
| 9 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback; 18 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 4-wood +2 |  |
| 11 | 4 | PASS | Driver +0 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +14 |  |
| 14 | 4 | PASS | Mid iron +12 |  |
| 15 | 4 | PASS | 4-wood -10 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | 4-wood +12 |  |
| 18 | 4 | CHECK | Driver +2 | yardage: measured 430 vs card 442 (-12) |

