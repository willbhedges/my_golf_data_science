# Buffalo Ridge Springs Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 8, 16

* page: `course_data/library/buffalo_ridge/page.html` (2.7 MB); request `course_data/requests/course_page_buffalo_ridge.json`; built 2026-10-30T12:11Z
* course: Buffalo Ridge Springs Golf Course (Branson, MO), OSM way/399501608; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Buffalo, Gold (the two longest sets on the card (combination sets skipped)); page sets: Buffalo, Gold
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-07-08,2020-07-26; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 3 Silver (L) 315 < Silver 333'])
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Buffalo tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -10 |  |
| 2 | 4 | PASS | Driver +0 |  |
| 3 | 4 | PASS | Driver -16 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -1 |  |
| 6 | 4 | PASS | 4-wood -7 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 2-wood -28 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -13 |  |
| 13 | 4 | PASS | Driver -20 |  |
| 14 | 5 | PASS | Driver -12 |  |
| 15 | 4 | PASS | 4-wood +12 |  |
| 16 | 4 | PASS | Driver +0 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -10 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -0 |  |
| 2 | 4 | PASS | Driver -0 |  |
| 3 | 4 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (lidar_pad; 16 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -8 |  |
| 6 | 4 | PASS | Driver -8 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver -1 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood -35 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -16 |  |
| 13 | 4 | PASS | Driver -28 |  |
| 14 | 5 | PASS | Driver -7 |  |
| 15 | 4 | PASS | 4-wood +22 |  |
| 16 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (walkback; 31 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -22 |  |

