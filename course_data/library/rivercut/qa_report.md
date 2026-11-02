# Rivercut Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 15

* page: `course_data/library/rivercut/page.html` (2.4 MB); request `course_data/requests/course_page_rivercut.json`; built 2026-11-02T13:21Z
* course: Rivercut Golf Course (Springfield, MO), OSM relation/5981089; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-17; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +14 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | 4-wood +0 (tie) |  |
| 4 | 4 | PASS | Driver -0 |  |
| 5 | 5 | PASS | Driver -4 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver +5 |  |
| 8 | 4 | PASS | Driver -0 |  |
| 9 | 4 | PASS | Driver -0 |  |
| 10 | 5 | PASS | Driver -16 |  |
| 11 | 4 | PASS | Driver +8 |  |
| 12 | 4 | PASS | Driver -7 |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 4 | PASS | Driver +8 |  |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 16 | 4 | PASS | Driver +20 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -12 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +24 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +18 |  |
| 4 | 4 | PASS | 4-wood -2 (tie) |  |
| 5 | 5 | PASS | Driver -3 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver +6 |  |
| 8 | 4 | PASS | Driver -2 |  |
| 9 | 4 | PASS | Driver +1 |  |
| 10 | 5 | PASS | Driver -9 |  |
| 11 | 4 | PASS | Driver +14 (tie) |  |
| 12 | 4 | PASS | Driver -1 |  |
| 13 | 4 | PASS | Driver -9 |  |
| 14 | 4 | PASS | Driver +9 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | 2-wood +22 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -18 |  |

