# Seneca Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 4, 6, 7, 9, 10, 17

* page: `course_data/library/seneca/page.html` (2.9 MB); request `course_data/requests/course_page_seneca.json`; built 2026-11-03T05:55Z
* course: Seneca Golf Course (Louisville, KY), OSM way/59714994; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-18; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 4 | PASS | Driver +0 (tie) |  |
| 3 | 5 | PASS | Driver -12 |  |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Driver -6 |  |
| 6 | 4 | PASS | Driver +19 |  |
| 7 | 5 | CHECK | Driver -40 | aim: Driver -40 lands 305 yds out in rough (12 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -14 |  |
| 10 | 5 | CHECK | Driver +28 | aim: Driver +28 lands 308 yds out in rough (32 yds from fairway) |
| 11 | 4 | PASS | Driver +14 |  |
| 12 | 4 | PASS | Driver +28 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +5 |  |
| 15 | 5 | PASS | Driver +7 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +8 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +15 |  |
| 2 | 4 | PASS | 4-wood -0 (tie) |  |
| 3 | 5 | PASS | Driver +8 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -10 |  |
| 6 | 4 | CHECK | Driver +31 (tie) | aim: Driver +31 lands 301 yds out in rough (11 yds from fairway) |
| 7 | 5 | PASS | Driver -8 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver -11 | aim: Driver -11 lands 278 yds out in rough (7 yds from fairway) |
| 10 | 5 | PASS | Driver +34 |  |
| 11 | 4 | PASS | Driver -11 |  |
| 12 | 4 | PASS | Driver +34 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +5 |  |
| 15 | 5 | PASS | Driver +28 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -31 |  |
| 18 | 4 | PASS | Driver +7 |  |

