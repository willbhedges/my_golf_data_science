# Cowboys Golf Club and Grapevine Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 4, 5, 7, 9, 18

* page: `course_data/library/cowboys/page.html` (1.2 MB); request `course_data/requests/course_page_cowboys.json`; built 2026-10-31T04:00Z
* course: Cowboys Golf Club and Grapevine Golf Course (Grapevine, TX), OSM relation/17453587; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Web (the two longest sets on the card (combination sets skipped)); page sets: Web
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 70, 85] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-07-04,2022-07-13; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Web tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +16 | yardage: measured 520 vs card 533 (-13) |
| 2 | 4 | PASS | Driver +2 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (lidar_pad; 37 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 8 | 5 | PASS | Driver -1 |  |
| 9 | 4 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -4 |  |
| 11 | 4 | PASS | Driver -10 |  |
| 12 | 4 | PASS | Driver -6 |  |
| 13 | 5 | PASS | Driver -12 |  |
| 14 | 4 | PASS | Driver -8 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver -10 | yardage: measured 506 vs card 519 (-13) |

