# Ironhorse Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 7, 11, 14, 18

* page: `course_data/library/ironhorse/page.html` (6.0 MB); request `course_data/requests/course_page_ironhorse.json`; built 2026-10-30T03:31Z
* course: Ironhorse Golf Club (Leawood, KS), OSM way/237531758; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* pars sum to 73, card 72
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +16 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +4 |  |
| 4 | 5 | PASS | Driver -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -0 (tie) |  |
| 7 | 4 | PASS | 4-wood +6 (tie) |  |
| 8 | 4 | PASS | 4-wood -8 |  |
| 9 | 5 | PASS | Driver -7 |  |
| 10 | 5 | PASS | Driver -6 |  |
| 11 | 4 | CHECK | 4-wood -26 | tee: tee marker not on an OSM tee box (walkback; 20 yds from the nearest OSM tee box) |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood -4 |  |
| 14 | 5 | PASS | Driver +28 |  |
| 15 | 4 | PASS | 4-wood -5 |  |
| 16 | 4 | PASS | Driver +17 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Mid iron +40 | yardage: measured 1607 vs card 475 (+1132); par: par 5 vs card 4; aim: Mid iron +40 lands 198 yds out in ob (34 yds from fairway); oval: landing pattern 83% trees / water / OB (recovery 2%, ob 81%) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -26 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +3 |  |
| 4 | 5 | PASS | Driver +2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -3 |  |
| 7 | 4 | CHECK | Driver -32 | aim: Driver -32 lands 295 yds out in rough (6 yds from fairway) |
| 8 | 4 | PASS | 4-wood -15 |  |
| 9 | 5 | PASS | Driver -8 |  |
| 10 | 5 | PASS | Driver -4 |  |
| 11 | 4 | PASS | Driver +18 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +6 |  |
| 14 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad; 15 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | Driver -40 |  |
| 16 | 4 | PASS | Driver +19 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Mid iron +40 | yardage: measured 1571 vs card 434 (+1137); par: par 5 vs card 4; aim: Mid iron +40 lands 198 yds out in ob (29 yds from fairway); oval: landing pattern 100% trees / water / OB (recovery 25%, ob 75%) |

