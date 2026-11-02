# L.A. Nickell Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 4, 5, 7, 9, 10, 12, 13, 16, 17, 18

* page: `course_data/library/la_nickell/page.html` (2.5 MB); request `course_data/requests/course_page_la_nickell.json`; built 2026-11-02T10:37Z
* course: L.A. Nickell Golf Course (Columbia, MO), OSM way/387047950; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 55, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-20; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 12 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +2 |  |
| 2 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | Driver -2 |  |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; 27 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | 2-wood -36 | yardage: measured 313 vs card 325 (-12) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver +1 (tie) |  |
| 9 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (walkback; 38 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -18 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 13 | 4 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -33 |  |
| 16 | 4 | CHECK | Driver +58 | oval: landing pattern 47% trees / water / OB (recovery 17%, ob 22%, unverified 16%) |
| 17 | 4 | CHECK | 2-wood -46 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 18 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 46 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +4 | aim: Driver +4 lands 307 yds out in rough (7 yds from fairway) |
| 2 | 4 | PASS | Driver +10 |  |
| 3 | 4 | PASS | Driver -2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 2-wood -38 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver +2 |  |
| 9 | 4 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -20 | aim: Driver -20 lands 320 yds out in rough (6 yds from fairway) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +6 |  |
| 13 | 4 | PASS | Driver -2 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -34 |  |
| 16 | 4 | PASS | 2-wood +50 |  |
| 17 | 4 | PASS | 2-wood -80 (tie) |  |
| 18 | 4 | PASS | 4-wood +0 |  |

