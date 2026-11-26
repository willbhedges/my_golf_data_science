# Forest Dunes Course: automatic page QA

**Status: auto-OK**

* page: `course_data/library/forest_dunes/page.html` (2.7 MB); request `course_data/requests/course_page_forest_dunes.json`; built 2026-11-26T17:18Z
* course: Forest Dunes Course (South Branch Township, MI), OSM way/1536953640; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: I, Ii (the two longest sets on the card (combination sets skipped)); page sets: I, Ii
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [25, 40, 50] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-09-09; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (I tees, library check cards): holes 1, 17 (2 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 4% of sides >= 0.675 (< 25%)); 2 kept on the page's own picks)

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## I tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +18 |  |
| 2 | 4 | PASS | Driver -9 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood +1 |  |
| 5 | 5 | PASS | Driver -10 |  |
| 6 | 4 | PASS | Driver -8 |  |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | PASS | 2-wood -10 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -10 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood -0 |  |
| 13 | 4 | PASS | 4-wood -3 |  |
| 14 | 4 | PASS | Driver -0 |  |
| 15 | 5 | PASS | Driver -4 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -37 |  |
| 18 | 5 | PASS | Driver -0 |  |

## Ii tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +32 |  |
| 2 | 4 | PASS | 4-wood -9 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood +9 |  |
| 5 | 5 | PASS | Driver -28 |  |
| 6 | 4 | PASS | Driver -4 |  |
| 7 | 5 | PASS | 4-wood -2 (tie) |  |
| 8 | 4 | PASS | 4-wood -2 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -8 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood -12 |  |
| 13 | 4 | PASS | Driver +0 |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 5 | PASS | Driver -2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | 4-wood -40 |  |
| 18 | 5 | PASS | Driver -10 |  |

