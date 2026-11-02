# Annbriar Golf Course: automatic page QA

**Status: auto-OK**

* page: `course_data/library/annbriar/page.html` (5.1 MB); request `course_data/requests/course_page_annbriar.json`; built 2026-11-02T17:12Z
* course: Annbriar Golf Course (Waterloo, IL), OSM way/1466372251; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Hickory, Black (the two longest sets on the card (combination sets skipped)); page sets: Hickory, Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-18,2023-08-19; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Hickory tees, library check cards): none (not asked: no agent_layers in the request)

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Hickory tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -12 |  |
| 2 | 4 | PASS | Driver +2 |  |
| 3 | 4 | PASS | Driver -0 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver +14 |  |
| 6 | 4 | PASS | Driver -14 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -4 |  |
| 9 | 5 | PASS | Driver +32 |  |
| 10 | 4 | PASS | Driver +8 |  |
| 11 | 4 | PASS | 4-wood -32 |  |
| 12 | 4 | PASS | Driver +22 |  |
| 13 | 4 | PASS | Driver +8 |  |
| 14 | 5 | PASS | Driver -36 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -20 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +5 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -8 |  |
| 2 | 4 | PASS | Driver +6 |  |
| 3 | 4 | PASS | Driver -1 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver +28 |  |
| 6 | 4 | PASS | Driver -20 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -10 |  |
| 9 | 5 | PASS | Driver +32 |  |
| 10 | 4 | PASS | Driver +20 |  |
| 11 | 4 | PASS | 4-wood -32 |  |
| 12 | 4 | PASS | Driver +26 |  |
| 13 | 4 | PASS | 2-wood +8 (tie) |  |
| 14 | 5 | PASS | 2-wood -32 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -24 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +10 |  |

