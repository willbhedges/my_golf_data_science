# Swope Memorial Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 5, 9

* page: `course_data/library/swope_memorial/page.html` (2.8 MB); request `course_data/requests/course_page_swope_memorial.json`; built 2026-11-02T03:11Z
* course: Swope Memorial Golf Course (Kansas City, MO), OSM way/68196001; holes: osm (tier mapped_card); card: course_data/library/swope_memorial/card_review.json (file)
* solved tee sets: Blue, White (tee sets of interest); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-07; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -5 |  |
| 2 | 4 | CHECK | Driver +7 | aim: Driver +7 lands 306 yds out in sand (9 yds from fairway) |
| 3 | 4 | PASS | 2-wood -6 (tie) |  |
| 4 | 4 | PASS | Driver +14 |  |
| 5 | 5 | CHECK | 4-wood -1 | tee: tee marker not on an OSM tee box (lidar_pad; 41 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +14 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (tee_axis; 13 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 4-wood +0 |  |
| 11 | 4 | PASS | Driver +2 (tie) |  |
| 12 | 5 | PASS | Driver +6 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +20 |  |
| 15 | 4 | PASS | Driver -18 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -1 |  |
| 18 | 4 | PASS | Driver +2 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -14 |  |
| 2 | 4 | PASS | Driver +6 |  |
| 3 | 4 | PASS | Long iron -7 |  |
| 4 | 4 | PASS | Driver +18 |  |
| 5 | 5 | CHECK | 4-wood +2 | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +19 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -0 |  |
| 10 | 4 | PASS | 4-wood -0 |  |
| 11 | 4 | PASS | Driver -2 |  |
| 12 | 5 | PASS | Driver +16 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +40 |  |
| 15 | 4 | PASS | 2-wood -29 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -5 |  |
| 18 | 4 | PASS | Driver -20 |  |

