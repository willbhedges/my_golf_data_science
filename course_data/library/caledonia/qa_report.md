# Caledonia Golf & Fish Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 9, 10, 13, 14, 18

* page: `course_data/library/caledonia/page.html` (2.8 MB); request `course_data/requests/course_page_caledonia.json`; built 2026-10-31T03:53Z
* course: Caledonia Golf & Fish Club (Pawleys Island, SC), OSM way/342296678; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Pintail, Mallard (the two longest sets on the card (combination sets skipped)); page sets: Pintail, Mallard
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-05-01; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Pintail tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (walkback; 30 yds from the nearest OSM tee box) |
| 2 | 5 | PASS | Driver +4 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 10 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | 4-wood +1 |  |
| 5 | 4 | PASS | 4-wood +1 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +0 |  |
| 8 | 5 | PASS | Driver -15 |  |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 15 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver +2 | yardage: measured 542 vs card 553 (-11) |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood -27 |  |
| 13 | 4 | CHECK | 4-wood -38 | yardage: measured 385 vs card 398 (-13) |
| 14 | 4 | PASS | Driver -8 |  |
| 15 | 4 | PASS | Driver -20 (tie) |  |
| 16 | 4 | PASS | Driver +1 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | 4-wood +2 | tee: tee marker not on an OSM tee box (lidar_pad; 38 yds from the nearest OSM tee box); yardage: measured 396 vs card 383 (+13) |

## Mallard tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 5 | PASS | Driver +6 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +33 |  |
| 5 | 4 | PASS | Driver +11 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +0 |  |
| 8 | 5 | PASS | Driver -12 |  |
| 9 | 3 | PASS |  |  |
| 10 | 5 | PASS | Driver +5 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood -24 |  |
| 13 | 4 | PASS | 4-wood -40 |  |
| 14 | 4 | CHECK | 4-wood -8 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood -18 (tie) |  |
| 16 | 4 | PASS | Driver -1 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | 4-wood -3 | tee: tee marker not on an OSM tee box (walkback; 19 yds from the nearest OSM tee box) |

