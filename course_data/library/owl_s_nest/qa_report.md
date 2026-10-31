# Owl's Nest Resort Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 5, 6, 9, 11, 12

* page: `course_data/library/owl_s_nest/page.html` (5.5 MB); request `course_data/requests/course_page_owl_s_nest.json`; built 2026-10-31T02:11Z
* course: Owl's Nest Resort Golf Course (Thornton, NH), OSM relation/17154512; holes: osm (tier mapped_card); card: club_site (club_site)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-23; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 4 | PASS | 2-wood +10 (tie) |  |
| 3 | 4 | PASS | Driver +14 |  |
| 4 | 5 | PASS | Driver -0 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | CHECK | Driver -34 | aim: Driver -34 lands 297 yds out in rough (8 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood -6 |  |
| 9 | 5 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (walkback; 17 yds from the nearest OSM tee box) |
| 10 | 3 | PASS |  |  |
| 11 | 4 | CHECK | Driver -31 | aim: Driver -31 lands 296 yds out in rough (16 yds from fairway) |
| 12 | 4 | CHECK | 4-wood +11 | aim: 4-wood +11 lands 276 yds out in rough (13 yds from fairway) |
| 13 | 5 | PASS | Driver -22 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +20 |  |
| 16 | 4 | PASS | 4-wood +2 |  |
| 17 | 5 | PASS | Driver +6 |  |
| 18 | 4 | PASS | Driver +12 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +8 |  |
| 2 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 334 yds out in rough (9 yds from fairway) |
| 3 | 4 | PASS | Driver +22 |  |
| 4 | 5 | PASS | Driver -6 |  |
| 5 | 3 | CHECK |  | yardage: measured 179 vs card 167 (+12) |
| 6 | 4 | PASS | Driver -40 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood -6 |  |
| 9 | 5 | PASS | 4-wood +6 (tie) |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | CHECK | 2-wood -36 (tie) | aim: 2-wood -36 lands 272 yds out in rough (8 yds from fairway) |
| 12 | 4 | PASS | Driver +5 (tie) |  |
| 13 | 5 | PASS | Driver -26 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +27 |  |
| 16 | 4 | PASS | Driver +13 |  |
| 17 | 5 | PASS | Driver +8 |  |
| 18 | 4 | PASS | Driver +12 |  |

