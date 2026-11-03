# Colbert Hills Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 7, 13

* page: `course_data/library/colbert_hills/page.html` (5.5 MB); request `course_data/requests/course_page_colbert_hills.json`; built 2026-11-02T23:00Z
* course: Colbert Hills Golf Course (Manhattan, KS), OSM relation/13772939; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black/Blue, Silver (tee sets of interest); page sets: Black/Blue, Silver
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-20,2023-06-06; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black/Blue tees, library check cards): holes 16, 9 (4 asked of 14 framed holes; 2 kept on the page's own picks (2 dropped))

Course-level reasons:

* OSM greens 17 of 18 holes
* scorecard not matched (source opengolfapi, flags ['Purple: holes sum to 6432 but the source says 6452 (-20): mixed card versions'])
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black/Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -2 (tie) | yardage: measured 559 vs card 590 (-31); aim: Driver -2 lands 324 yds out in rough (8 yds from fairway) |
| 2 | 4 | PASS | Driver -15 |  |
| 3 | 4 | PASS | Driver -6 |  |
| 4 | 4 | PASS | 4-wood -14 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -2 |  |
| 7 | 5 | CHECK | Driver +16 | aim: Driver +16 lands 338 yds out in rough (12 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -5 |  |
| 10 | 5 | PASS | Driver +1 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -0 |  |
| 13 | 4 | CHECK | Driver +52 | wide_aim: Driver aim +52 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 14 | 4 | PASS | Driver +0 |  |
| 15 | 4 | PASS | Driver +8 |  |
| 16 | 5 | PASS | Driver -21 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -4 (tie) |  |

## Silver tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -6 (tie) | yardage: measured 544 vs card 578 (-34); aim: Driver -6 lands 316 yds out in rough (11 yds from fairway) |
| 2 | 4 | PASS | Driver -31 (tie) |  |
| 3 | 4 | CHECK | 4-wood -3 | aim: 4-wood -3 lands 262 yds out in rough (10 yds from fairway) |
| 4 | 4 | PASS | 4-wood -10 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +6 |  |
| 7 | 5 | PASS | Driver +20 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -14 |  |
| 10 | 5 | PASS | Driver +3 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +6 |  |
| 13 | 4 | CHECK | Driver +50 | aim: Driver +50 lands 302 yds out in sand (6 yds from fairway); wide_aim: Driver aim +51 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 14 | 4 | PASS | 4-wood -2 |  |
| 15 | 4 | PASS | Driver +11 |  |
| 16 | 5 | PASS | Driver -22 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +28 |  |

