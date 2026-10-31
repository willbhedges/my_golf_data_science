# Sugarloaf Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 10, 16

* page: `course_data/library/sugarloaf/page.html` (3.7 MB); request `course_data/requests/course_page_sugarloaf.json`; built 2026-10-31T01:50Z
* course: Sugarloaf Golf Club (Carrabassett Valley, ME), OSM relation/17549879; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [30, 40, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-07-21; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +24 |  |
| 2 | 5 | PASS | Long iron -12 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver +0 |  |
| 5 | 4 | PASS | 4-wood -8 (tie) |  |
| 6 | 4 | PASS | 4-wood +1 |  |
| 7 | 4 | PASS | 4-wood -19 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 4 | CHECK | Driver +5 | aim: Driver +5 lands 308 yds out in rough (10 yds from fairway) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +2 |  |
| 13 | 4 | PASS | 4-wood +8 |  |
| 14 | 4 | PASS | 2-wood -12 (tie) |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | PASS | Driver +36 |  |
| 17 | 4 | PASS | 4-wood -4 (tie) |  |
| 18 | 4 | PASS | Driver -6 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +32 (tie) |  |
| 2 | 5 | CHECK | Driver +40 | aim: Driver +40 lands 334 yds out in recovery (27 yds from fairway); oval: landing pattern 92% trees / water / OB (recovery 90%, unverified 3%) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | 4-wood +0 (tie) |  |
| 5 | 4 | PASS | 4-wood -3 (tie) |  |
| 6 | 4 | PASS | Long iron -7 |  |
| 7 | 4 | PASS | 4-wood -34 (tie) |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -12 |  |
| 10 | 4 | CHECK | 4-wood +24 | tee: tee marker not on an OSM tee box (lidar_pad; 52 yds from the nearest OSM tee box); aim: 4-wood +24 lands 252 yds out in sand (12 yds from fairway) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | 4-wood +2 |  |
| 13 | 4 | PASS | 4-wood +6 |  |
| 14 | 4 | PASS | 4-wood -20 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | CHECK | Driver +40 | oval: landing pattern 49% trees / water / OB (recovery 46%, water 3%, unverified 0%) |
| 17 | 4 | PASS | Driver -34 (tie) |  |
| 18 | 4 | PASS | Driver -10 (tie) |  |

