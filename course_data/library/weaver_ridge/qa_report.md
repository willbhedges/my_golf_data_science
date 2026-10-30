# WeaverRidge Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 5, 6, 10, 13

* page: `course_data/library/weaver_ridge/page.html` (6.1 MB); request `course_data/requests/course_page_weaver_ridge.json`; built 2026-10-30T12:24Z
* course: WeaverRidge Golf Club (Peoria, IL), OSM way/749257217; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Gold, Black (the two longest sets on the card (combination sets skipped)); page sets: Gold, Black
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-25; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Gold: holes sum to 6876 but the source says 6500 (+376): mixed card versions', 'Black: holes sum to 6280 but the source says 7000 (-720): mixed card versions', 'Green: holes sum to 5938 but the source says 6011 (-73): mixed card versions', 'White: holes sum to 5442 but the source says 5487 (-45): mixed card versions', 'Red: holes sum to 4891 but the source says 5046 (-155): mixed card versions'])
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -3 |  |
| 2 | 4 | PASS | Driver +21 |  |
| 3 | 5 | PASS | Driver +6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver +40 (tie) | tee: tee marker not on an OSM tee box (walkback; 67 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | 4-wood -7 |  |
| 7 | 4 | PASS | Driver +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | PASS | 4-wood +40 |  |
| 11 | 5 | PASS | Driver +0 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (lidar_pad; 14 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +6 |  |
| 15 | 4 | PASS | Driver +12 |  |
| 16 | 4 | PASS | Driver -7 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | 4-wood +9 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -7 |  |
| 2 | 4 | PASS | Driver +32 (tie) |  |
| 3 | 5 | PASS | Driver +2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 2-wood -36 (tie) |  |
| 6 | 4 | CHECK | 4-wood -4 | aim: 4-wood -4 lands 279 yds out in rough (12 yds from fairway) |
| 7 | 4 | PASS | Driver +10 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | CHECK | 4-wood +40 | oval: landing pattern 48% trees / water / OB (recovery 24%, water 24%) |
| 11 | 5 | PASS | 4-wood +0 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -18 |  |
| 14 | 4 | PASS | Driver +26 |  |
| 15 | 4 | PASS | 2-wood +17 |  |
| 16 | 4 | PASS | Driver -20 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -28 |  |

