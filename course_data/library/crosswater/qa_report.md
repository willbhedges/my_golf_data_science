# Crosswater Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 4, 6

* page: `course_data/library/crosswater/page.html` (4.5 MB); request `course_data/requests/course_page_crosswater.json`; built 2026-10-31T03:50Z
* course: Crosswater Golf Course (Sunriver, OR), OSM relation/14236725; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Championship, Black (the two longest sets on the card (combination sets skipped)); page sets: Championship, Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-28; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +13 |  |
| 2 | 5 | PASS | Driver -13 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -4 | yardage: measured 430 vs card 413 (+17) |
| 5 | 4 | PASS | Driver +0 |  |
| 6 | 5 | PASS | Driver -0 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -0 |  |
| 9 | 4 | PASS | Driver +2 |  |
| 10 | 4 | PASS | Driver +33 |  |
| 11 | 4 | PASS | Driver -22 |  |
| 12 | 5 | PASS | Driver +0 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +10 |  |
| 15 | 4 | PASS | Driver +14 |  |
| 16 | 5 | PASS | Driver -13 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +2 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +16 (tie) |  |
| 2 | 5 | PASS | Driver -10 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -12 | yardage: measured 409 vs card 393 (+16) |
| 5 | 4 | PASS | Driver -10 |  |
| 6 | 5 | CHECK | Driver +8 | yardage: measured 592 vs card 603 (-11) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood +5 |  |
| 9 | 4 | PASS | Driver +5 |  |
| 10 | 4 | PASS | 2-wood +34 |  |
| 11 | 4 | PASS | Driver -16 |  |
| 12 | 5 | PASS | Driver -7 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +10 |  |
| 15 | 4 | PASS | Driver +20 |  |
| 16 | 5 | PASS | 4-wood -17 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +3 (tie) |  |

