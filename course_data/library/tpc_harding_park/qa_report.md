# TPC Harding Park: automatic page QA

**Status: needs confirm** — confirm holes 2, 4, 5, 6, 8, 9, 12

* page: `course_data/library/tpc_harding_park/page.html` (2.3 MB); request `course_data/requests/course_page_tpc_harding_park.json`; built 2026-11-01T22:24Z
* course: TPC Harding Park (San Francisco, CA), OSM way/16753068; holes: v2+structure (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Championship, Blue (the two longest sets on the card (combination sets skipped)); page sets: Championship, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-08-04; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -1 |  |
| 2 | 4 | CHECK | Mid iron -0 | tee: tee marker not on an OSM tee box (walkback_capped; 31 yds from the nearest OSM tee box); yardage: measured 181 vs card 449 (-268) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | CHECK | Driver +12 (tie) | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box); aim: Driver +12 lands 302 yds out in rough (14 yds from fairway) |
| 5 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback_capped; 35 yds from the nearest OSM tee box); yardage: measured 303 vs card 429 (-126) |
| 6 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (walkback_capped; 45 yds from the nearest OSM tee box); yardage: measured 370 vs card 473 (-103) |
| 7 | 4 | PASS | 4-wood -2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver -26 | tee: tee marker not on an OSM tee box (walkback; 122 yds from the nearest OSM tee box) |
| 10 | 5 | PASS | Driver +12 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +3 |  |
| 13 | 4 | PASS | Driver -5 |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 4 | PASS | Driver -7 |  |
| 16 | 4 | PASS | 4-wood -16 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +18 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -1 |  |
| 2 | 4 | CHECK | Mid iron -0 | tee: tee marker not on an OSM tee box (walkback_capped; 31 yds from the nearest OSM tee box); yardage: measured 181 vs card 430 (-249) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver +35 |  |
| 5 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback_capped; 35 yds from the nearest OSM tee box); yardage: measured 303 vs card 395 (-92) |
| 6 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (walkback_capped; 45 yds from the nearest OSM tee box); yardage: measured 370 vs card 440 (-70) |
| 7 | 4 | PASS | 4-wood -2 |  |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 23 yds from the nearest OSM tee box) |
| 9 | 5 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (walkback; 92 yds from the nearest OSM tee box) |
| 10 | 5 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | CHECK | Driver -1 | yardage: measured 464 vs card 480 (-16) |
| 13 | 4 | PASS | Driver +4 |  |
| 14 | 4 | PASS | Driver -2 |  |
| 15 | 4 | PASS | Driver -7 |  |
| 16 | 4 | PASS | Driver -4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +22 |  |

