# Amana Colonies Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 7, 9, 13, 14, 17

* page: `course_data/library/amana_colonies/page.html` (5.8 MB); request `course_data/requests/course_page_amana_colonies.json`; built 2026-10-30T11:54Z
* course: Amana Colonies Golf Course (Amana, IA), OSM way/731221353; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +2 |  |
| 2 | 5 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | Driver -4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +2 (tie) |  |
| 6 | 5 | PASS | Driver +8 |  |
| 7 | 4 | CHECK | Driver -0 | aim: Driver -0 lands 321 yds out in rough (11 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +8 (tie) |  |
| 10 | 4 | PASS | 4-wood +28 (tie) |  |
| 11 | 5 | PASS | Driver +32 |  |
| 12 | 4 | PASS | Driver +1 |  |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 7 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver +11 (tie) | yardage: measured 335 vs card 350 (-15) |
| 15 | 5 | PASS | Driver +10 |  |
| 16 | 4 | PASS | Driver +7 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -13 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +3 |  |
| 2 | 5 | PASS | Driver -32 |  |
| 3 | 4 | PASS | Driver -3 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 (tie) |  |
| 6 | 5 | PASS | Driver +10 |  |
| 7 | 4 | CHECK | Driver -3 | aim: Driver -3 lands 322 yds out in sand (7 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +7 (tie) | aim: Driver +7 lands 306 yds out in rough (6 yds from fairway) |
| 10 | 4 | PASS | Driver +16 |  |
| 11 | 5 | PASS | Driver +30 |  |
| 12 | 4 | PASS | Driver -2 (tie) |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 5 | PASS | Driver +10 |  |
| 16 | 4 | PASS | Driver -2 |  |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver -12 |  |

