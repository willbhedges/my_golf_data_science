# Jimmie Austin Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 10, 12

* page: `course_data/library/jimmie_austin/page.html` (5.7 MB); request `course_data/requests/course_page_jimmie_austin.json`; built 2026-10-31T03:50Z
* course: Jimmie Austin Golf Club (Norman, OK), OSM way/315995643; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: I, II (the two longest sets on the card (combination sets skipped)); page sets: I, II
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [50, 65, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-06-19; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## I tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -18 | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -8 |  |
| 4 | 4 | PASS | Driver +30 |  |
| 5 | 5 | PASS | Driver -4 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +2 |  |
| 8 | 5 | PASS | Driver +9 |  |
| 9 | 4 | PASS | 4-wood -2 |  |
| 10 | 4 | PASS | 4-wood +18 |  |
| 11 | 4 | PASS | Driver +7 |  |
| 12 | 3 | CHECK |  | par3_box: target box 0% on the green, centre OFF it |
| 13 | 5 | PASS | Driver -4 |  |
| 14 | 4 | PASS | Driver +1 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -2 |  |
| 17 | 4 | PASS | Driver -4 |  |
| 18 | 5 | PASS | Driver +13 |  |

## II tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -6 (tie) |  |
| 4 | 4 | PASS | Driver +29 (tie) |  |
| 5 | 5 | PASS | Driver -1 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +2 |  |
| 8 | 5 | PASS | Driver +6 |  |
| 9 | 4 | PASS | Driver -10 |  |
| 10 | 4 | CHECK | Driver +26 | aim: Driver +26 lands 295 yds out in rough (7 yds from fairway) |
| 11 | 4 | PASS | Driver +2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | 4-wood -4 |  |
| 14 | 4 | PASS | Driver +11 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +4 (tie) |  |
| 17 | 4 | PASS | 4-wood +2 |  |
| 18 | 5 | PASS | Driver +10 |  |

