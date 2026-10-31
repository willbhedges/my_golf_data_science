# Fred Arbanas Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9

* page: `course_data/library/longview_lake/page.html` (2.5 MB); request `course_data/requests/course_page_longview_lake.json`; built 2026-10-30T20:56Z
* course: Fred Arbanas Golf Course (Kansas City, MO), OSM way/913710102; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Blue, Web (the two longest sets on the card (combination sets skipped)); page sets: Blue, Web
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-07; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Blue: holes sum to 6906 but the source says 6879 (+27): mixed card versions', 'White: holes sum to 6354 but the source says 6299 (+55): mixed card versions'])
* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (walkback; 13 yds from the nearest OSM tee box); aim: Driver +26 lands 304 yds out in rough (56 yds from fairway) |
| 2 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; 104 yds from the nearest OSM tee box); aim: Driver +20 lands 284 yds out in rough (68 yds from fairway) |
| 3 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; 107 yds from the nearest OSM tee box); aim: Driver +16 lands 301 yds out in rough (25 yds from fairway) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 59 yds from the nearest OSM tee box) |
| 5 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 78 yds from the nearest OSM tee box); aim: Driver +2 lands 287 yds out in rough (59 yds from fairway) |
| 6 | 4 | CHECK | Long iron -20 | tee: tee marker not on an OSM tee box (walkback; 33 yds from the nearest OSM tee box); aim: Long iron -20 lands 227 yds out in rough (62 yds from fairway) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 8 | 4 | CHECK | 4-wood -8 | tee: tee marker not on an OSM tee box (walkback; 160 yds from the nearest OSM tee box); aim: 4-wood -8 lands 282 yds out in rough (96 yds from fairway) |
| 9 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback; 129 yds from the nearest OSM tee box); aim: Driver -10 lands 296 yds out in rough (52 yds from fairway) |
| 10 | 5 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -0 |  |
| 13 | 4 | PASS | Driver +3 |  |
| 14 | 5 | PASS | Driver -18 |  |
| 15 | 4 | PASS | Driver -22 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +14 |  |
| 18 | 4 | PASS | Driver -1 |  |

## Web tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (walkback; 13 yds from the nearest OSM tee box); aim: Driver +26 lands 304 yds out in rough (56 yds from fairway) |
| 2 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; 104 yds from the nearest OSM tee box); aim: Driver +20 lands 284 yds out in rough (68 yds from fairway) |
| 3 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; 107 yds from the nearest OSM tee box); aim: Driver +16 lands 301 yds out in rough (25 yds from fairway) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 59 yds from the nearest OSM tee box) |
| 5 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 78 yds from the nearest OSM tee box); aim: Driver +2 lands 287 yds out in rough (59 yds from fairway) |
| 6 | 4 | CHECK | Long iron -20 | tee: tee marker not on an OSM tee box (walkback; 33 yds from the nearest OSM tee box); aim: Long iron -20 lands 227 yds out in rough (62 yds from fairway) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 8 | 4 | CHECK | Long iron +6 | tee: tee marker not on an OSM tee box (walkback; 145 yds from the nearest OSM tee box); aim: Long iron +6 lands 230 yds out in rough (93 yds from fairway) |
| 9 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback; 129 yds from the nearest OSM tee box); aim: Driver -10 lands 296 yds out in rough (52 yds from fairway) |
| 10 | 5 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -0 |  |
| 13 | 4 | PASS | Driver +3 |  |
| 14 | 5 | PASS | Driver -18 |  |
| 15 | 4 | PASS | Driver -22 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +14 |  |
| 18 | 4 | PASS | Driver -1 |  |

