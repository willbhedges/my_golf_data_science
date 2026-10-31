# Torrey Pines South Course: automatic page QA

**Status: needs confirm** — confirm holes 10

* page: `course_data/library/torrey_pines/page.html` (2.3 MB); request `course_data/requests/course_page_torrey_pines.json`; built 2026-10-30T21:54Z
* course: Torrey Pines South Course (La Jolla, CA), OSM way/35679036; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Brown (the two longest sets on the card (combination sets skipped)); page sets: Black, Brown
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-08-21,2018-08-23; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +5 |  |
| 2 | 4 | PASS | 4-wood +6 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +2 |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 5 | PASS | Driver +22 |  |
| 7 | 4 | PASS | Driver +14 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +8 |  |
| 10 | 4 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (lidar_pad; 31 yds from the nearest OSM tee box) |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -0 |  |
| 13 | 5 | PASS | Driver -1 |  |
| 14 | 4 | PASS | Driver -1 |  |
| 15 | 4 | PASS | Driver -2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +2 |  |
| 18 | 5 | PASS | Driver +0 |  |

## Brown tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +8 |  |
| 2 | 4 | PASS | Driver +18 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 4 | PASS | Driver +11 |  |
| 6 | 5 | PASS | Driver +28 |  |
| 7 | 4 | PASS | Driver +12 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +7 |  |
| 10 | 4 | PASS | Driver -13 (tie) |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +5 |  |
| 13 | 5 | PASS | Driver -17 |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 4 | PASS | Driver +5 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +3 |  |
| 18 | 5 | PASS | Driver +0 |  |

