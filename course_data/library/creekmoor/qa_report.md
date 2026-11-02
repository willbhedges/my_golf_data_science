# Creekmoor Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 18

* page: `course_data/library/creekmoor/page.html` (2.5 MB); request `course_data/requests/course_page_creekmoor.json`; built 2026-11-02T19:50Z
* course: Creekmoor Golf Club (Raymore, MO), OSM relation/4249741; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Green (the two longest sets on the card (combination sets skipped)); page sets: Black, Green
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 13, 6, 8, 2 (4 asked of 14 framed holes)

Course-level reasons:

* 14 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +35 | aim: Driver +35 lands 326 yds out in rough (58 yds from fairway) |
| 2 | 4 | CHECK | Driver -0 | aim: Driver -0 lands 313 yds out in rough (47 yds from fairway) |
| 3 | 4 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box); aim: Driver +7 lands 291 yds out in rough (129 yds from fairway) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver +7 | aim: no fairway mapped on this hole; Driver lands in rough |
| 6 | 4 | CHECK | Driver -6 | aim: Driver -6 lands 299 yds out in rough (133 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver -22 | aim: Driver -22 lands 284 yds out in rough (133 yds from fairway) |
| 9 | 5 | CHECK | 4-wood -15 | aim: no fairway mapped on this hole; 4-wood lands in rough |
| 10 | 4 | CHECK | Driver -6 | aim: Driver -6 lands 312 yds out in rough (288 yds from fairway) |
| 11 | 4 | CHECK | Driver -26 | aim: Driver -26 lands 301 yds out in rough (52 yds from fairway) |
| 12 | 3 | PASS |  |  |
| 13 | 5 | CHECK | Driver +3 | aim: no fairway mapped on this hole; Driver lands in rough |
| 14 | 4 | CHECK | Driver -28 | aim: Driver -28 lands 308 yds out in rough (313 yds from fairway) |
| 15 | 4 | CHECK | Driver +0 | aim: Driver +0 lands 309 yds out in rough (252 yds from fairway) |
| 16 | 4 | CHECK | Driver -32 | aim: Driver -32 lands 284 yds out in rough (135 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +6 | aim: no fairway mapped on this hole; Driver lands in rough |

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +39 | aim: Driver +39 lands 324 yds out in rough (38 yds from fairway) |
| 2 | 4 | CHECK | 4-wood -4 (tie) | aim: 4-wood -4 lands 279 yds out in rough (54 yds from fairway) |
| 3 | 4 | CHECK | Driver +2 | aim: Driver +2 lands 302 yds out in rough (90 yds from fairway) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver +6 | aim: no fairway mapped on this hole; Driver lands in rough |
| 6 | 4 | CHECK | Driver -1 | aim: Driver -1 lands 303 yds out in rough (83 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver -26 | aim: Driver -26 lands 282 yds out in rough (99 yds from fairway) |
| 9 | 5 | CHECK | Driver -4 | aim: no fairway mapped on this hole; Driver lands in rough |
| 10 | 4 | CHECK | Driver +1 | aim: Driver +1 lands 317 yds out in rough (124 yds from fairway) |
| 11 | 4 | CHECK | Driver -35 | aim: Driver -35 lands 298 yds out in rough (29 yds from fairway) |
| 12 | 3 | PASS |  |  |
| 13 | 5 | CHECK | Driver +6 | aim: no fairway mapped on this hole; Driver lands in rough |
| 14 | 4 | CHECK | Driver -28 | aim: no fairway mapped on this hole; Driver lands in rough |
| 15 | 4 | CHECK | Driver +2 | aim: Driver +2 lands 309 yds out in rough (113 yds from fairway) |
| 16 | 4 | CHECK | Driver -25 | aim: Driver -25 lands 298 yds out in rough (67 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +2 | aim: no fairway mapped on this hole; Driver lands in rough |

