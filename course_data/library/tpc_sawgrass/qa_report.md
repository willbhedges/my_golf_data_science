# TPC Sawgrass: automatic page QA

**Status: needs confirm** — confirm holes 9, 10, 11, 12, 13

* page: `course_data/library/tpc_sawgrass/page.html` (2.8 MB); request `course_data/requests/course_page_tpc_sawgrass.json`; built 2026-10-30T22:28Z
* course: TPC Sawgrass (Ponte Vedra Beach, FL), OSM relation/1783123; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Tpc, Blue (the two longest sets on the card (combination sets skipped)); page sets: Tpc, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [65, 75, 85] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-11-18; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Tpc tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -2 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -4 (tie) |  |
| 4 | 4 | PASS | Driver -28 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -24 |  |
| 7 | 4 | PASS | Driver -19 |  |
| 8 | 5 | PASS | Driver -2 |  |
| 9 | 4 | PASS | Driver -13 |  |
| 10 | 4 | PASS | Driver -30 |  |
| 11 | 3 | CHECK |  | yardage: measured 581 vs card 229 (+352) |
| 12 | 4 | CHECK | Driver +24 | aim: Driver +24 lands 300 yds out in rough (12 yds from fairway) |
| 13 | 4 | CHECK | 4-wood +15 | yardage: measured 392 vs card 409 (-17) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -6 |  |
| 16 | 5 | PASS | Driver +6 |  |
| 17 | 5 | PASS | Driver +13 |  |
| 18 | 4 | PASS | 4-wood -0 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -5 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -9 |  |
| 4 | 4 | PASS | 4-wood -40 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -20 |  |
| 7 | 4 | PASS | Driver -20 |  |
| 8 | 5 | PASS | Driver -2 |  |
| 9 | 4 | CHECK | Driver -10 | yardage: measured 417 vs card 404 (+13) |
| 10 | 4 | CHECK | 4-wood -26 | yardage: measured 371 vs card 402 (-31) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 140 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | Driver +24 | aim: Driver +24 lands 300 yds out in rough (10 yds from fairway) |
| 13 | 4 | PASS | 4-wood +15 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -14 (tie) |  |
| 16 | 5 | PASS | Driver +6 |  |
| 17 | 5 | PASS | Driver +14 |  |
| 18 | 4 | PASS | 4-wood -2 |  |

