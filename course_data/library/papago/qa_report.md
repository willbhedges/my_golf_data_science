# Papago Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 9, 10

* page: `course_data/library/papago/page.html` (4.3 MB); request `course_data/requests/course_page_papago.json`; built 2026-10-30T21:43Z
* course: Papago Golf Club (Phoenix, AZ), OSM way/51990955; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-15; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +8 |  |
| 3 | 4 | PASS | Driver -1 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -8 |  |
| 6 | 4 | PASS | Driver -30 |  |
| 7 | 4 | PASS | Driver +8 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +2 | yardage: measured 531 vs card 542 (-11) |
| 10 | 5 | PASS | Driver +10 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +17 |  |
| 13 | 4 | PASS | Driver -18 |  |
| 14 | 4 | PASS | Driver +8 |  |
| 15 | 5 | PASS | Driver +4 |  |
| 16 | 4 | PASS | Driver +12 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +17 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +4 |  |
| 2 | 4 | PASS | Driver -6 |  |
| 3 | 4 | PASS | Driver -4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -6 (tie) |  |
| 6 | 4 | PASS | Driver -26 |  |
| 7 | 4 | PASS | Driver -6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +14 |  |
| 10 | 5 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (lidar_pad; 7 yds from the nearest OSM tee box) |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +12 |  |
| 13 | 4 | PASS | Driver -30 |  |
| 14 | 4 | PASS | Driver -1 |  |
| 15 | 5 | PASS | Driver +4 |  |
| 16 | 4 | PASS | Driver +16 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +23 |  |

