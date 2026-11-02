# Sycamore Ridge Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 9, 13, 18

* page: `course_data/library/sycamore_ridge/page.html` (5.0 MB); request `course_data/requests/course_page_sycamore_ridge.json`; built 2026-11-02T13:08Z
* course: Sycamore Ridge Golf Club (Spring Hill, KS), OSM way/151985223; holes: osm (tier mapped_card); card: course_data/library/sycamore_ridge/card_review.json (file)
* solved tee sets: Black, Blue (tee sets of interest); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-17; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +8 |  |
| 2 | 5 | PASS | Driver -28 |  |
| 3 | 4 | PASS | 4-wood +0 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -9 |  |
| 6 | 4 | PASS | Driver -0 |  |
| 7 | 5 | PASS | Driver -1 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +8 |  |
| 10 | 4 | PASS | Driver +0 |  |
| 11 | 5 | PASS | Driver +0 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | 4-wood +0 | tee: tee marker not on an OSM tee box (tee_axis; 7 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +12 |  |
| 16 | 4 | PASS | Driver -12 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +58 | tee: tee marker not on an OSM tee box (tagged; 4 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +12 |  |
| 2 | 5 | PASS | Driver -40 |  |
| 3 | 4 | PASS | Driver -6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -32 |  |
| 6 | 4 | PASS | Driver +6 |  |
| 7 | 5 | PASS | 4-wood -1 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +2 (tie) | tee: tee marker not on an OSM tee box (tagged; 3 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver +8 |  |
| 11 | 5 | PASS | Driver -13 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +20 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +8 |  |
| 16 | 4 | PASS | Driver -12 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +58 |  |

