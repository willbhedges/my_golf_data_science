# Swope Memorial Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 4, 6, 7, 9

* page: `course_data/library/swope_memorial/page.html` (2.8 MB); request `course_data/requests/course_page_swope_memorial.json`; built 2026-10-30T00:46Z
* course: Swope Memorial Golf Course (Kansas City, MO), OSM way/68196001; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-07; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -6 |  |
| 2 | 4 | CHECK | Driver +6 | aim: Driver +6 lands 306 yds out in sand (9 yds from fairway) |
| 3 | 4 | PASS | Long iron +40 |  |
| 4 | 4 | CHECK | Driver +17 | tee: tee marker not on an OSM tee box (walkback; 96 yds from the nearest OSM tee box); aim: Driver +17 lands 264 yds out in rough (22 yds from fairway) |
| 5 | 5 | PASS | Driver -0 |  |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 96 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | Driver +8 | aim: Driver +8 lands 308 yds out in sand (8 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -32 |  |
| 10 | 4 | PASS | 4-wood +0 |  |
| 11 | 4 | PASS | Driver +2 (tie) |  |
| 12 | 5 | PASS | Driver +6 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +22 |  |
| 15 | 4 | PASS | Driver -18 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -1 |  |
| 18 | 4 | PASS | Driver +3 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -14 |  |
| 2 | 4 | PASS | Driver +6 |  |
| 3 | 4 | CHECK | Long iron +14 | tee: tee marker not on an OSM tee box (walkback; 17 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback; 80 yds from the nearest OSM tee box); aim: Driver +14 lands 269 yds out in rough (27 yds from fairway) |
| 5 | 5 | PASS | Driver +1 |  |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 86 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver +2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver -30 | tee: tee marker not on an OSM tee box (lidar_pad; 10 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 4-wood -0 |  |
| 11 | 4 | PASS | Driver -2 |  |
| 12 | 5 | PASS | Driver +17 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +40 |  |
| 15 | 4 | PASS | 2-wood -30 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -6 |  |
| 18 | 4 | PASS | Driver -20 |  |

