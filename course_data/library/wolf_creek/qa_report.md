# Wolf Creek Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 9, 11, 14

* page: `course_data/library/wolf_creek/page.html` (4.7 MB); request `course_data/requests/course_page_wolf_creek.json`; built 2026-10-31T01:56Z
* course: Wolf Creek Golf Club (Mesquite, NV), OSM way/676428903; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Challenger, Champions (the two longest sets on the card (combination sets skipped)); page sets: Challenger, Champions
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-08; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Challenger tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -22 |  |
| 2 | 4 | PASS | 4-wood -40 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 2-wood +8 (tie) |  |
| 5 | 5 | PASS | Driver -35 |  |
| 6 | 4 | PASS | 4-wood -36 (tie) |  |
| 7 | 4 | PASS | Driver +34 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | PASS | Driver +6 |  |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 12 | 5 | PASS | Driver -17 |  |
| 13 | 4 | PASS | Long iron +37 |  |
| 14 | 4 | CHECK | Driver -40 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box); aim: Driver -40 lands 322 yds out in sand (39 yds from fairway) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +7 |  |
| 17 | 5 | PASS | Driver +3 |  |
| 18 | 4 | PASS | Long iron +4 |  |

## Champions tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +2 |  |
| 2 | 4 | CHECK | 4-wood -40 | aim: 4-wood -40 lands 303 yds out in rough (9 yds from fairway) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 7 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Mid iron +9 |  |
| 5 | 5 | PASS | 4-wood -40 |  |
| 6 | 4 | PASS | Driver +40 (tie) |  |
| 7 | 4 | PASS | 2-wood +29 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +8 | aim: Driver +8 lands 290 yds out in sand (4 yds from fairway) |
| 10 | 4 | PASS | Driver +5 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver -20 |  |
| 13 | 4 | PASS | Long iron +26 |  |
| 14 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 319 yds out in sand (38 yds from fairway) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +4 |  |
| 17 | 5 | PASS | 2-wood +6 (tie) |  |
| 18 | 4 | PASS | Long iron +15 |  |

