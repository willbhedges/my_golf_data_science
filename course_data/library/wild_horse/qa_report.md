# Wild Horse Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 6, 8, 10

* page: `course_data/library/wild_horse/page.html` (2.1 MB); request `course_data/requests/course_page_wild_horse.json`; built 2026-10-31T01:50Z
* course: Wild Horse Golf Club (Gothenburg, NE), OSM way/383386145; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Black (the two longest sets on the card (combination sets skipped)); page sets: Gold, Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-07-17; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +12 |  |
| 3 | 5 | PASS | Driver +18 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -14 |  |
| 6 | 5 | CHECK | Driver -15 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver -20 (tie) |  |
| 8 | 4 | PASS | 4-wood -8 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | CHECK | 2-wood +6 (tie) | yardage: measured 395 vs card 408 (-13) |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +7 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -8 |  |
| 15 | 4 | PASS | Driver -6 |  |
| 16 | 4 | PASS | Driver +11 |  |
| 17 | 5 | PASS | Driver -1 |  |
| 18 | 4 | PASS | Driver +28 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -40 |  |
| 2 | 4 | PASS | Driver +12 |  |
| 3 | 5 | PASS | Driver +19 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -28 |  |
| 6 | 5 | PASS | Driver -10 |  |
| 7 | 4 | PASS | Driver -20 |  |
| 8 | 4 | CHECK | Driver -7 | aim: Driver -7 lands 297 yds out in sand (8 yds from fairway) |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood +6 (tie) |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 2-wood +32 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -16 |  |
| 15 | 4 | PASS | Driver +4 |  |
| 16 | 4 | PASS | Driver +18 |  |
| 17 | 5 | PASS | Driver -9 |  |
| 18 | 4 | PASS | Driver +36 |  |

