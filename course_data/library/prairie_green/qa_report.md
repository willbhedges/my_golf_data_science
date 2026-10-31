# Prairie Green Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 5, 9

* page: `course_data/library/prairie_green/page.html` (2.6 MB); request `course_data/requests/course_page_prairie_green.json`; built 2026-10-31T03:57Z
* course: Prairie Green Golf Course (Sioux Falls, SD), OSM relation/17830055; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Professional, Championship (the two longest sets on the card (combination sets skipped)); page sets: Professional, Championship
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-09-05; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Professional tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +1 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +3 |  |
| 4 | 4 | PASS | Driver -0 |  |
| 5 | 4 | PASS | Driver +9 (tie) |  |
| 6 | 5 | PASS | Driver +10 |  |
| 7 | 4 | PASS | Driver -3 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood +3 (tie) |  |
| 10 | 4 | PASS | Driver -8 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +4 (tie) |  |
| 13 | 5 | PASS | Driver +15 |  |
| 14 | 4 | PASS | Driver +12 |  |
| 15 | 5 | PASS | Driver -30 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -4 |  |
| 18 | 4 | PASS | Driver +7 |  |

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -0 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +9 |  |
| 4 | 4 | PASS | Driver +0 |  |
| 5 | 4 | CHECK | Driver +28 | aim: Driver +28 lands 301 yds out in rough (6 yds from fairway) |
| 6 | 5 | PASS | Driver +10 |  |
| 7 | 4 | PASS | 4-wood -3 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; 35 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood +4 |  |
| 13 | 5 | PASS | Driver +12 |  |
| 14 | 4 | PASS | Driver +22 |  |
| 15 | 5 | PASS | Driver -32 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -10 |  |
| 18 | 4 | PASS | Driver +6 |  |

