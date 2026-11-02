# Prairie Highlands Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 11, 17

* page: `course_data/library/prairie_highlands/page.html` (4.7 MB); request `course_data/requests/course_page_prairie_highlands.json`; built 2026-11-02T16:38Z
* course: Prairie Highlands Golf Course (Olathe, KS), OSM relation/11701165; holes: osm (tier mapped_card); card: course_data/library/prairie_highlands/card_review.json (file)
* solved tee sets: Black, Blue (tee sets of interest); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-17; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -8 |  |
| 2 | 4 | PASS | Driver +6 |  |
| 3 | 4 | PASS | Driver +13 |  |
| 4 | 5 | PASS | Driver +10 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +6 |  |
| 7 | 4 | PASS | Driver +12 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +9 |  |
| 10 | 4 | PASS | 4-wood +4 |  |
| 11 | 4 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 12 | 5 | PASS | Driver +3 |  |
| 13 | 4 | PASS | Driver +6 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +5 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | CHECK | Driver -6 | aim: Driver -6 lands 308 yds out in sand (9 yds from fairway) |
| 18 | 4 | PASS | Driver -10 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver +18 |  |
| 3 | 4 | PASS | Driver -4 |  |
| 4 | 5 | PASS | Driver +4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -0 (tie) |  |
| 7 | 4 | PASS | Driver +13 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +11 |  |
| 10 | 4 | PASS | Driver +60 |  |
| 11 | 4 | PASS | Driver -0 |  |
| 12 | 5 | PASS | Driver +0 |  |
| 13 | 4 | PASS | Driver +12 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +6 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -16 |  |
| 18 | 4 | PASS | Driver -2 |  |

