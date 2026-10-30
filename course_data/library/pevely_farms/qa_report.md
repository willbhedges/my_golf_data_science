# Pevely Farms Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 9, 10, 11, 16, 18

* page: `course_data/library/pevely_farms/page.html` (2.2 MB); request `course_data/requests/course_page_pevely_farms.json`; built 2026-10-30T04:16Z
* course: Pevely Farms Golf Course (Saint Louis, MO), OSM relation/5429230; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-18; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (walkback; 42 yds from the nearest OSM tee box); aim: Driver -32 lands 300 yds out in recovery (43 yds from fairway) |
| 2 | 5 | PASS | Driver -9 |  |
| 3 | 4 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver -5 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood +6 |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; 379 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 300 yds out in rough (198 yds from fairway) |
| 11 | 4 | CHECK | Driver -7 (tie) | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 12 | 5 | PASS | Driver -1 |  |
| 13 | 4 | PASS | 4-wood -11 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +2 |  |
| 16 | 4 | CHECK | 2-wood +40 (tie) | aim: 2-wood +40 lands 297 yds out in rough (22 yds from fairway) |
| 17 | 4 | PASS | Driver -28 |  |
| 18 | 4 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; 478 yds from the nearest OSM tee box); aim: Driver +40 lands 300 yds out in rough (122 yds from fairway) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box); aim: Driver -16 lands 300 yds out in rough (58 yds from fairway) |
| 2 | 5 | PASS | Driver -6 |  |
| 3 | 4 | CHECK | 4-wood +8 | aim: 4-wood +8 lands 270 yds out in rough (8 yds from fairway) |
| 4 | 4 | PASS | Driver -6 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Long iron +2 |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; 360 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver +38 | aim: Driver +38 lands 300 yds out in rough (216 yds from fairway) |
| 11 | 4 | PASS | Driver -18 (tie) |  |
| 12 | 5 | PASS | Driver -8 |  |
| 13 | 4 | PASS | Long iron +2 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +0 |  |
| 16 | 4 | CHECK | 4-wood +40 (tie) | aim: 4-wood +40 lands 286 yds out in rough (15 yds from fairway) |
| 17 | 4 | PASS | Driver -30 |  |
| 18 | 4 | CHECK | Driver -11 (tie) | tee: tee marker not on an OSM tee box (walkback; 466 yds from the nearest OSM tee box); aim: Driver -11 lands 300 yds out in rough (115 yds from fairway) |

