# Sharon Woods Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 7, 8, 9, 10, 11, 12, 14, 15, 16

* page: `course_data/library/sharon_woods/page.html` (3.1 MB); request `course_data/requests/course_page_sharon_woods.json`; built 2026-10-31T04:17Z
* course: Sharon Woods Golf Course (Sharonville, OH), OSM way/31875338; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Green, Blue (the two longest sets on the card (combination sets skipped)); page sets: Green, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-22; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['3 hole(s) where a longer set is shorter than the next set: 1 Blue 320 < White 341, 7 Blue 375 < White 405, 14 Blue 360 < White 378'])
* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +24 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 20 yds from the nearest OSM tee box) |
| 2 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | Driver -4 |  |
| 4 | 4 | PASS | Driver +10 |  |
| 5 | 4 | PASS | 4-wood +4 |  |
| 6 | 4 | PASS | Driver +17 (tie) |  |
| 7 | 4 | CHECK | Driver +20 | aim: Driver +20 lands 303 yds out in rough (11 yds from fairway) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 36 yds from the nearest OSM tee box) |
| 9 | 5 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 76 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | 2-wood -40 | tee: tee marker not on an OSM tee box (lidar_pad; 29 yds from the nearest OSM tee box) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (walkback; 40 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -7 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 15 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 40 yds from the nearest OSM tee box) |
| 16 | 5 | CHECK | Driver -15 | tee: tee marker not on an OSM tee box (lidar_pad; 32 yds from the nearest OSM tee box) |
| 17 | 4 | PASS | 4-wood -2 (tie) |  |
| 18 | 4 | PASS | Driver +3 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 284 yds out in rough (15 yds from fairway) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -4 |  |
| 4 | 4 | PASS | Driver +13 |  |
| 5 | 4 | PASS | 4-wood +4 |  |
| 6 | 4 | PASS | 4-wood +11 (tie) |  |
| 7 | 4 | CHECK | Driver +14 | aim: Driver +14 lands 304 yds out in rough (8 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 61 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 335 yds out in rough (12 yds from fairway) |
| 11 | 3 | PASS |  |  |
| 12 | 4 | CHECK | Long iron -6 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 5 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 26 yds from the nearest OSM tee box) |
| 16 | 5 | PASS | Driver -3 |  |
| 17 | 4 | PASS | Driver -3 |  |
| 18 | 4 | PASS | Driver +4 |  |

