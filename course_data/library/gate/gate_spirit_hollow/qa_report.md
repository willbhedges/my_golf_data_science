# Spirit Hollow Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 7, 9, 11, 13, 14, 15, 17, 18

* page: `course_data/library/gate/gate_spirit_hollow/page.html` (2.6 MB); request `course_data/requests/course_page_gate_spirit_hollow.json`; built 2026-10-29T21:19Z
* course: Spirit Hollow Golf Course (Burlington, IA), OSM relation/13353211; holes: osm (tier mapped_card); card: course_data/tees/scorecard.json (file)
* solved tee sets: Black, Gold (tee sets of interest + the longest other set (Gold)); page sets: Black, Gold
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-08-28; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 10 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -38 | aim: Driver -38 lands 326 yds out in rough (7 yds from fairway) |
| 2 | 5 | PASS | Driver -35 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -7 |  |
| 5 | 4 | PASS | Driver -14 |  |
| 6 | 4 | PASS | Driver -35 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver -24 |  |
| 9 | 4 | PASS | 4-wood +14 |  |
| 10 | 5 | PASS | Driver +2 |  |
| 11 | 4 | CHECK | 4-wood +2 | aim: 4-wood +2 lands 273 yds out in rough (11 yds from fairway) |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver +4 | aim: Driver +4 lands 303 yds out in rough (12 yds from fairway) |
| 14 | 4 | CHECK | Driver -40 (tie) | aim: Driver -40 lands 326 yds out in rough (14 yds from fairway) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | 4-wood -4 (tie) |  |
| 17 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 18 | 5 | PASS | Driver -4 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -20 |  |
| 2 | 5 | CHECK | Driver +40 | aim: Driver +40 lands 326 yds out in rough (33 yds from fairway); oval: landing pattern 48% trees / water / OB (recovery 33%, water 12%, unverified 6%) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -18 |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 4 | PASS | Driver -26 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box); yardage: measured 154 vs card 165 (-11) |
| 8 | 4 | PASS | Driver -10 |  |
| 9 | 4 | CHECK | Driver +17 | tee: tee marker not on an OSM tee box (lidar_pad; 4 yds from the nearest OSM tee box) |
| 10 | 5 | PASS | Driver +8 |  |
| 11 | 4 | PASS | 4-wood +2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -6 |  |
| 14 | 4 | PASS | Driver +4 |  |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 50 yds from the nearest OSM tee box) |
| 16 | 4 | PASS | Driver -3 |  |
| 17 | 4 | PASS | Driver -8 |  |
| 18 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box); aim: Driver +40 lands 321 yds out in rough (35 yds from fairway) |

