# A. L. Gustin Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 7, 9, 11, 14, 16

* page: `course_data/library/gustin/page.html` (2.6 MB); request `course_data/requests/course_page_gustin.json`; built 2026-11-02T12:19Z
* course: A. L. Gustin Golf Course (Columbia, MO), OSM way/449108205; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-07-08; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +3 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +16 |  |
| 4 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -40 |  |
| 7 | 4 | CHECK | 4-wood -4 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 36 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -2 |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | CHECK | 4-wood +4 (tie) | tee: tee marker not on an OSM tee box (lidar_pad_capped; 11 yds from the nearest OSM tee box) |
| 12 | 5 | PASS | Driver +8 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -9 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 183 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 2-wood -26 (tie) |  |
| 16 | 4 | CHECK | 2-wood +54 | aim: 2-wood +54 lands 304 yds out in rough (11 yds from fairway) |
| 17 | 4 | PASS | Driver +18 |  |
| 18 | 4 | PASS | 4-wood +0 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +8 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | 4-wood +40 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 6 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver +2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -59 |  |
| 7 | 4 | PASS | 2-wood -38 |  |
| 8 | 4 | PASS | 4-wood +7 (tie) |  |
| 9 | 4 | CHECK | Driver -14 | aim: Driver -14 lands 304 yds out in sand (4 yds from fairway) |
| 10 | 3 | PASS |  |  |
| 11 | 4 | PASS | Driver +6 (tie) |  |
| 12 | 5 | PASS | Driver +12 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (lidar_pad; 150 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood +20 |  |
| 16 | 4 | CHECK | 4-wood +58 | aim: 4-wood +58 lands 290 yds out in rough (14 yds from fairway); oval: landing pattern 40% trees / water / OB (recovery 29%, unverified 23%) |
| 17 | 4 | PASS | Driver +23 |  |
| 18 | 4 | PASS | 4-wood -0 (tie) |  |

