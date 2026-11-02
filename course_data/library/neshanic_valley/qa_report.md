# Neshanic Valley Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 7, 15, 16, 17

* page: `course_data/library/neshanic_valley/page.html` (2.9 MB); request `course_data/requests/course_page_neshanic_valley.json`; built 2026-11-01T21:54Z
* course: Neshanic Valley Golf Course (Branchburg Township, NJ), OSM way/698906445; holes: v2+structure (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-20; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +8 |  |
| 2 | 4 | PASS | Driver +10 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -6 |  |
| 5 | 4 | PASS | Driver -0 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (lidar_pad; 30 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver +24 |  |
| 9 | 5 | PASS | Driver -14 |  |
| 10 | 4 | PASS | Driver -22 |  |
| 11 | 4 | PASS | Driver -28 (tie) |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +22 |  |
| 14 | 5 | PASS | Driver -34 |  |
| 15 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; 32 yds from the nearest OSM tee box) |
| 16 | 4 | CHECK | Driver +32 | tee: tee marker not on an OSM tee box (walkback; 46 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +8 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +3 |  |
| 2 | 4 | PASS | Driver +13 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -6 |  |
| 5 | 4 | PASS | Driver +2 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +13 |  |
| 8 | 4 | PASS | Driver +28 |  |
| 9 | 5 | PASS | Driver -11 |  |
| 10 | 4 | PASS | Driver -18 |  |
| 11 | 4 | PASS | Driver -29 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +27 |  |
| 14 | 5 | PASS | Driver -28 |  |
| 15 | 4 | PASS | Driver -34 |  |
| 16 | 4 | PASS | 2-wood +40 (tie) |  |
| 17 | 3 | CHECK |  | yardage: measured 198 vs card 187 (+11) |
| 18 | 5 | PASS | Driver +3 |  |

