# Harbour Town Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 5, 7, 8, 16, 18

* page: `course_data/library/harbour_town/page.html` (3.0 MB); request `course_data/requests/course_page_harbour_town.json`; built 2026-11-01T22:44Z
* course: Harbour Town Golf Links (Hilton Head Island, SC), OSM relation/4813858; holes: v2+structure (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Heritage, Blue (the two longest sets on the card (combination sets skipped)); page sets: Heritage, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-05-07; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* scorecard not matched (source opengolfapi, flags ['Heritage: holes sum to 7131 but the source says 7099 (+32): mixed card versions', 'Blue: holes sum to 6642 but the source says 6681 (-39): mixed card versions', 'White: holes sum to 6103 but the source says 6253 (-150): mixed card versions', 'Gold: holes sum to 5478 but the source says 5867 (-389): mixed card versions', 'Green: holes sum to 4760 but the source says 5084 (-324): mixed card versions'])
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Heritage tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +7 |  |
| 2 | 5 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (walkback_capped; 15 yds from the nearest OSM tee box); yardage: measured 515 vs card 544 (-29) |
| 3 | 4 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (lidar_pad; 106 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -7 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | 4-wood -3 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 20 yds from the nearest OSM tee box); par3_box: target box 0% on the green, centre OFF it |
| 8 | 4 | CHECK | 4-wood +40 | tee: tee marker not on an OSM tee box (walkback_capped; 58 yds from the nearest OSM tee box); yardage: measured 429 vs card 467 (-38) |
| 9 | 4 | PASS | 4-wood -2 |  |
| 10 | 4 | PASS | 2-wood +5 (tie) |  |
| 11 | 4 | PASS | 4-wood -0 |  |
| 12 | 4 | PASS | 2-wood -12 (tie) |  |
| 13 | 4 | PASS | 4-wood -6 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +0 |  |
| 16 | 4 | CHECK | Long iron +40 (tie) | tee: tee marker not on an OSM tee box (walkback; 45 yds from the nearest OSM tee box); aim: Long iron +40 lands 220 yds out in rough (42 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -7 | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 2-wood +6 (tie) |  |
| 2 | 5 | PASS | 4-wood +2 |  |
| 3 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (tee_axis; 20 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -26 |  |
| 6 | 4 | PASS | 4-wood -0 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | 4-wood +40 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver -30 |  |
| 10 | 4 | PASS | 4-wood -5 |  |
| 11 | 4 | PASS | 4-wood -4 |  |
| 12 | 4 | PASS | 4-wood -6 |  |
| 13 | 4 | PASS | Long iron -4 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -1 |  |
| 16 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 302 yds out in recovery (34 yds from fairway); oval: landing pattern 46% trees / water / OB (recovery 21%, ob 24%, unverified 2%) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -2 |  |

