# Old Kinderhook Resort, Golf, Club & Spa: automatic page QA

**Status: needs confirm** — confirm holes 9

* page: `course_data/library/old_kinderhook/page.html` (1.3 MB); request `course_data/requests/course_page_old_kinderhook.json`; built 2026-10-30T04:13Z
* course: Old Kinderhook Resort, Golf, Club & Spa (Camdenton, MO), OSM way/393079215; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Web (the two longest sets on the card (combination sets skipped)); page sets: Web
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2016-08-04,2016-08-21; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Web tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -6 |  |
| 2 | 4 | PASS | 4-wood -8 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 4 | PASS | 4-wood +4 |  |
| 6 | 4 | PASS | Driver -12 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood -7 |  |
| 9 | 5 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -13 |  |
| 13 | 4 | PASS | Driver +1 |  |
| 14 | 5 | PASS | Driver +22 |  |
| 15 | 4 | PASS | 4-wood -40 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +13 |  |
| 18 | 5 | PASS | Driver +15 |  |

