# Annbriar Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 9, 13

* page: `course_data/library/annbriar/page.html` (5.1 MB); request `course_data/requests/course_page_annbriar.json`; built 2026-10-30T11:57Z
* course: Annbriar Golf Course (Waterloo, IL), OSM way/1466372251; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Hickory, Black (the two longest sets on the card (combination sets skipped)); page sets: Hickory, Black
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-18,2023-08-19; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Hickory tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -11 |  |
| 2 | 4 | PASS | Driver +4 |  |
| 3 | 4 | PASS | Driver -0 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver +15 |  |
| 6 | 4 | PASS | Driver -15 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -4 |  |
| 9 | 5 | PASS | Driver +33 |  |
| 10 | 4 | PASS | Driver +10 |  |
| 11 | 4 | PASS | 4-wood -32 |  |
| 12 | 4 | PASS | Driver +23 |  |
| 13 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (lidar_pad; 31 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | Driver -38 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -20 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +5 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -8 |  |
| 2 | 4 | PASS | Driver +5 |  |
| 3 | 4 | PASS | Driver -1 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver +30 |  |
| 6 | 4 | PASS | Driver -22 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -10 |  |
| 9 | 5 | CHECK | 2-wood +40 | tee: tee marker not on an OSM tee box (lidar_pad; 31 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver +21 |  |
| 11 | 4 | PASS | 4-wood -32 |  |
| 12 | 4 | PASS | Driver +26 |  |
| 13 | 4 | PASS | 2-wood +9 (tie) |  |
| 14 | 5 | PASS | 2-wood -33 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -24 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +12 |  |

