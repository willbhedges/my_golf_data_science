# WeaverRidge Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 5, 6, 10, 13

* page: `course_data/library/weaver_ridge/page.html` (6.1 MB); request `course_data/requests/course_page_weaver_ridge.json`; built 2026-11-03T01:40Z
* course: WeaverRidge Golf Club (Peoria, IL), OSM way/749257217; holes: osm (tier mapped_card); card: course_data/library/weaver_ridge/card_review.json (file)
* solved tee sets: Black, Gold (tee sets of interest); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-25; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 9, 7 (2 asked of 14 framed holes; 2 kept on the page's own picks)

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (tee_axis; 7 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +14 |  |
| 3 | 5 | PASS | Driver +8 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver +40 | yardage: measured 363 vs card 387 (-24); wide_aim: Driver aim +41 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 4 | PASS | 4-wood -3 |  |
| 7 | 4 | PASS | Driver +8 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | CHECK | 2-wood +46 (tie) | wide_aim: 2-wood aim +55 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 5 | PASS | Driver +1 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +2 |  |
| 15 | 4 | PASS | Driver -3 |  |
| 16 | 4 | PASS | Driver +6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | 4-wood +8 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -1 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +30 (tie) |  |
| 3 | 5 | PASS | Driver +3 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver +40 | wide_aim: Driver aim +41 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 4 | CHECK | 4-wood -5 | aim: 4-wood -5 lands 279 yds out in rough (12 yds from fairway) |
| 7 | 4 | PASS | Driver +11 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | CHECK | 4-wood +48 | oval: landing pattern 40% trees / water / OB (recovery 15%, water 21%, unverified 8%); wide_aim: 4-wood aim +56 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 5 | PASS | Driver +0 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +6 |  |
| 15 | 4 | PASS | 2-wood +8 (tie) |  |
| 16 | 4 | PASS | Driver +6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Long iron +10 |  |

