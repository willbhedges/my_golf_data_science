# Kearney Hill Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 17

* page: `course_data/library/kearney_hill/page.html` (1.4 MB); request `course_data/requests/course_page_kearney_hill.json`; built 2026-10-31T01:46Z
* course: Kearney Hill Golf Links (Lexington, KY), OSM way/285529283; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black (the two longest sets on the card (combination sets skipped)); page sets: Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-29; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Black: holes sum to 7100 but the source says 7079 (+21): mixed card versions'])
* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +5 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +18 |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 4 | PASS | Driver +1 |  |
| 7 | 5 | PASS | Driver +4 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +8 |  |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | 4-wood +18 (tie) |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +18 |  |
| 14 | 5 | PASS | Driver -4 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | 2-wood +10 (tie) |  |
| 17 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 18 | 5 | PASS | Driver -1 |  |

