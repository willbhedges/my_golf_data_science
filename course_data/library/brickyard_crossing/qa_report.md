# Brickyard Crossing Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 12, 14, 15, 16, 18

* page: `course_data/library/brickyard_crossing/page.html` (2.1 MB); request `course_data/requests/course_page_brickyard_crossing.json`; built 2026-11-01T20:43Z
* course: Brickyard Crossing Golf Course (Indianapolis, IN), OSM relation/569616; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-21; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -18 |  |
| 2 | 5 | PASS | Driver +7 |  |
| 3 | 4 | PASS | 4-wood +2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 5 | PASS | Driver +4 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +12 |  |
| 9 | 4 | PASS | Driver +16 (tie) |  |
| 10 | 4 | PASS | Driver -0 |  |
| 11 | 4 | PASS | Driver -4 |  |
| 12 | 5 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (tee_axis; 49 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (lidar_pad; 126 yds from the nearest OSM tee box); aim: Driver -32 lands 292 yds out in rough (10 yds from fairway) |
| 15 | 5 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (lidar_pad; 48 yds from the nearest OSM tee box) |
| 16 | 4 | PASS | Driver +2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -6 |  |
| 2 | 5 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | Driver -16 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +8 (tie) |  |
| 6 | 5 | PASS | Driver +8 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +8 |  |
| 9 | 4 | PASS | Driver +22 (tie) |  |
| 10 | 4 | PASS | Driver -6 |  |
| 11 | 4 | PASS | 4-wood -8 (tie) |  |
| 12 | 5 | PASS | Driver -15 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (lidar_pad; 123 yds from the nearest OSM tee box); aim: Driver -16 lands 292 yds out in rough (10 yds from fairway) |
| 15 | 5 | CHECK | Driver +39 | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 16 | 4 | CHECK | Driver -12 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 10 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |

