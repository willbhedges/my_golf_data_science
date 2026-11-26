# Neshanic Valley Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 15, 16

* page: `course_data/library/neshanic_valley/page.html` (3.1 MB); request `course_data/requests/course_page_neshanic_valley.json`; built 2026-11-26T17:15Z
* course: Neshanic Valley Golf Course (Branchburg Township, NJ), OSM way/698906445; holes: v2+structure (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-20; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 7 (1 asked of 14 framed holes (priors: native_auto p; automatic band on 14 holes); 1 kept on the page's own picks)

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +6 |  |
| 2 | 4 | PASS | 4-wood +18 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -10 |  |
| 5 | 4 | PASS | Driver +2 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +18 |  |
| 8 | 4 | PASS | Driver +30 |  |
| 9 | 5 | PASS | Driver -14 |  |
| 10 | 4 | PASS | 4-wood -35 (tie) |  |
| 11 | 4 | PASS | 4-wood -30 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +18 |  |
| 14 | 5 | PASS | Driver -40 |  |
| 15 | 4 | CHECK | Driver -40 (tie) | tee: tee marker not on an OSM tee box (walkback; 32 yds from the nearest OSM tee box) |
| 16 | 4 | CHECK | 4-wood +36 | yardage: measured 335 vs card 382 (-47) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +6 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +10 |  |
| 2 | 4 | PASS | 4-wood +16 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -9 |  |
| 5 | 4 | PASS | 4-wood +2 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +6 |  |
| 8 | 4 | PASS | Driver +34 |  |
| 9 | 5 | PASS | Driver -10 |  |
| 10 | 4 | PASS | 4-wood -31 |  |
| 11 | 4 | PASS | 4-wood -40 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +30 |  |
| 14 | 5 | PASS | Driver -38 |  |
| 15 | 4 | PASS | 4-wood -40 |  |
| 16 | 4 | CHECK | Driver +45 | wide_aim: Driver aim +50 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | 4-wood +8 (tie) |  |

