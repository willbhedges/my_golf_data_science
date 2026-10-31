# RTJ Ross Bridge Golf: automatic page QA

**Status: needs confirm** — confirm holes 1, 5, 9, 18

* page: `course_data/library/ross_bridge/page.html` (1.2 MB); request `course_data/requests/course_page_ross_bridge.json`; built 2026-10-30T21:31Z
* course: RTJ Ross Bridge Golf (Hoover, AL), OSM way/55545496; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Web (the two longest sets on the card (combination sets skipped)); page sets: Web
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-09-09; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Web tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -15 | yardage: measured 609 vs card 620 (-11) |
| 2 | 4 | PASS | Driver -15 |  |
| 3 | 4 | PASS | Driver -0 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver +2 |  |
| 8 | 4 | PASS | Driver +9 |  |
| 9 | 4 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver +12 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +8 |  |
| 13 | 5 | PASS | Driver +10 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -3 |  |
| 16 | 5 | PASS | Driver -4 |  |
| 17 | 4 | PASS | Driver -14 |  |
| 18 | 4 | CHECK | Driver -4 | aim: Driver -4 lands 305 yds out in sand (4 yds from fairway) |

