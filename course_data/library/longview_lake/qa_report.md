# Fred Arbanas Golf Course: automatic page QA

**Status: needs confirm**

* page: `course_data/library/longview_lake/page.html` (2.5 MB); request `course_data/requests/course_page_longview_lake.json`; built 2026-11-03T05:48Z
* course: Fred Arbanas Golf Course (Kansas City, MO), OSM way/913710102; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Blue, Web (the two longest sets on the card (combination sets skipped)); page sets: Blue, Web
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-07; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Blue: holes sum to 6906 but the source says 6879 (+27): mixed card versions', 'White: holes sum to 6354 but the source says 6299 (+55): mixed card versions'])

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -14 |  |
| 2 | 4 | PASS | Driver +6 (tie) |  |
| 3 | 5 | PASS | Driver +5 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -2 |  |
| 6 | 4 | PASS | Driver +25 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood +4 |  |
| 9 | 4 | PASS | Driver -28 |  |
| 10 | 5 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +0 |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 5 | PASS | Driver -18 |  |
| 15 | 4 | PASS | Driver -22 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +14 |  |
| 18 | 4 | PASS | Driver -2 |  |

## Web tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -14 |  |
| 2 | 4 | PASS | Driver +6 (tie) |  |
| 3 | 5 | PASS | Driver +5 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -2 |  |
| 6 | 4 | PASS | Driver +25 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood +2 |  |
| 9 | 4 | PASS | Driver -28 |  |
| 10 | 5 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +0 |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 5 | PASS | Driver -18 |  |
| 15 | 4 | PASS | Driver -22 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +14 |  |
| 18 | 4 | PASS | Driver -2 |  |

