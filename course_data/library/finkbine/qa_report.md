# Finkbine Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 8, 9, 10, 12, 13

* page: `course_data/library/finkbine/page.html` (2.8 MB); request `course_data/requests/course_page_finkbine.json`; built 2026-10-30T11:57Z
* course: Finkbine Golf Course (Iowa City, IA), OSM way/964660601; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-09-05; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 28 yds from the nearest OSM tee box) |
| 2 | 5 | PASS | Driver +8 |  |
| 3 | 4 | PASS | 4-wood +7 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +8 |  |
| 6 | 5 | PASS | Driver -6 |  |
| 7 | 4 | PASS | Driver +27 |  |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Driver +8 | yardage: measured 461 vs card 449 (+12) |
| 10 | 4 | CHECK | 4-wood -1 | tee: tee marker not on an OSM tee box (walkback; 31 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | Driver -1 |  |
| 12 | 4 | CHECK | 4-wood -40 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 18 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +8 |  |
| 15 | 5 | PASS | Driver -0 |  |
| 16 | 4 | PASS | Driver +4 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -30 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +10 | yardage: measured 387 vs card 401 (-14) |
| 2 | 5 | PASS | Driver +9 |  |
| 3 | 4 | PASS | Driver +18 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +8 |  |
| 6 | 5 | PASS | Driver -7 |  |
| 7 | 4 | PASS | Driver +30 (tie) |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood +4 |  |
| 10 | 4 | PASS | Driver -20 |  |
| 11 | 5 | PASS | Driver -10 |  |
| 12 | 4 | PASS | Long iron -28 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +7 |  |
| 15 | 5 | PASS | Driver +3 |  |
| 16 | 4 | PASS | Driver +12 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -14 (tie) |  |

