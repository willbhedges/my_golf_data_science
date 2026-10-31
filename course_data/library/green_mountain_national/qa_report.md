# Green Mountain National Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 5, 15

* page: `course_data/library/green_mountain_national/page.html` (7.2 MB); request `course_data/requests/course_page_green_mountain_national.json`; built 2026-10-31T04:38Z
* course: Green Mountain National Golf Course (Killington, VT), OSM way/570014047; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-06-22; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +5 |  |
| 2 | 4 | PASS | 4-wood +10 |  |
| 3 | 4 | PASS | Driver -0 |  |
| 4 | 4 | PASS | Driver +4 |  |
| 5 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 26 yds from the nearest OSM tee box) |
| 6 | 5 | PASS | Driver +4 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -40 |  |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 4 | PASS | Driver -1 |  |
| 11 | 4 | PASS | Long iron -0 |  |
| 12 | 4 | PASS | 4-wood -6 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood -40 |  |
| 15 | 5 | CHECK | 2-wood +22 (tie) | aim: 2-wood +22 lands 308 yds out in rough (6 yds from fairway) |
| 16 | 4 | PASS | Driver -18 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -10 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +10 |  |
| 2 | 4 | PASS | Long iron +12 |  |
| 3 | 4 | PASS | Driver -3 |  |
| 4 | 4 | PASS | Driver +0 (tie) |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | 4-wood +4 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -40 |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | PASS | Driver -4 |  |
| 11 | 4 | PASS | Driver +6 |  |
| 12 | 4 | PASS | 4-wood -14 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Long iron -10 |  |
| 15 | 5 | CHECK | Driver +40 | aim: Driver +40 lands 317 yds out in rough (11 yds from fairway); oval: landing pattern 44% trees / water / OB (recovery 43%, unverified 2%) |
| 16 | 4 | PASS | Driver -22 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -12 |  |

