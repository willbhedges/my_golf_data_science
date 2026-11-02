# Ironhorse Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 7, 11

* page: `course_data/library/ironhorse/page.html` (6.0 MB); request `course_data/requests/course_page_ironhorse.json`; built 2026-11-02T03:18Z
* course: Ironhorse Golf Club (Leawood, KS), OSM way/237531758; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +8 | yardage: measured 413 vs card 374 (+39) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +4 |  |
| 4 | 5 | PASS | Driver -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -1 (tie) |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 4 | PASS | 4-wood -7 |  |
| 9 | 5 | PASS | Driver -6 |  |
| 10 | 5 | PASS | Driver -6 |  |
| 11 | 4 | CHECK | 4-wood -26 | tee: tee marker not on an OSM tee box (walkback; 20 yds from the nearest OSM tee box) |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood -4 |  |
| 14 | 5 | PASS | Driver +28 |  |
| 15 | 4 | PASS | 4-wood -4 |  |
| 16 | 4 | PASS | Driver +16 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +4 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -24 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +3 |  |
| 4 | 5 | PASS | Driver +2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -3 |  |
| 7 | 4 | CHECK | Driver -36 | aim: Driver -36 lands 295 yds out in rough (9 yds from fairway) |
| 8 | 4 | PASS | 4-wood -14 |  |
| 9 | 5 | PASS | Driver -8 |  |
| 10 | 5 | PASS | Driver -4 |  |
| 11 | 4 | PASS | Driver +18 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +6 |  |
| 14 | 5 | PASS | Driver +30 |  |
| 15 | 4 | PASS | Driver -40 |  |
| 16 | 4 | PASS | Driver +18 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +3 |  |

