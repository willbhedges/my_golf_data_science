# St Andrews Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 5, 10, 15, 16

* page: `course_data/library/st_andrews_op/page.html` (5.2 MB); request `course_data/requests/course_page_st_andrews_op.json`; built 2026-10-30T03:26Z
* course: St Andrews Golf Club (Overland Park, KS), OSM way/68744841; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -22 |  |
| 2 | 4 | PASS | Driver -36 |  |
| 3 | 4 | PASS | Long iron -6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood -40 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | PASS | Driver -10 (tie) |  |
| 9 | 4 | PASS | Driver -8 |  |
| 10 | 5 | CHECK | Driver +23 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood -4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Long iron -2 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | 4-wood -40 | aim: 4-wood -40 lands 286 yds out in rough (9 yds from fairway); oval: landing pattern 51% trees / water / OB (recovery 51%) |
| 16 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -0 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -6 |  |
| 2 | 4 | PASS | 2-wood -38 |  |
| 3 | 4 | PASS | Long iron -8 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 4-wood -40 | aim: 4-wood -40 lands 260 yds out in rough (10 yds from fairway) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | PASS | Driver -10 |  |
| 9 | 4 | PASS | 4-wood -5 (tie) |  |
| 10 | 5 | PASS | Driver +32 |  |
| 11 | 4 | PASS | Long iron -4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Mid iron -0 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Long iron +3 |  |
| 16 | 4 | PASS | Driver +27 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +2 |  |

