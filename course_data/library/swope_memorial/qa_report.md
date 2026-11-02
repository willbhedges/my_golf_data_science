# Swope Memorial Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 5, 12, 13

* page: `course_data/library/swope_memorial/page.html` (2.8 MB); request `course_data/requests/course_page_swope_memorial.json`; built 2026-11-02T06:23Z
* course: Swope Memorial Golf Course (Kansas City, MO), OSM way/68196001; holes: osm (tier mapped_card); card: course_data/library/swope_memorial/card_review.json (file)
* solved tee sets: Green, Bronze (tee sets of interest); page sets: Green, Bronze
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-07; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -8 |  |
| 2 | 4 | CHECK | Driver +8 | aim: Driver +8 lands 306 yds out in rough (11 yds from fairway) |
| 3 | 4 | PASS | Driver +10 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Long iron -1 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 2-wood -6 |  |
| 9 | 4 | PASS | Driver +14 |  |
| 10 | 4 | PASS | 4-wood +0 |  |
| 11 | 4 | PASS | 4-wood +2 |  |
| 12 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (lidar_pad; 24 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +14 |  |
| 15 | 4 | PASS | Driver -19 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -2 |  |
| 18 | 4 | PASS | Driver +2 |  |

## Bronze tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver +6 |  |
| 3 | 4 | PASS | Driver +15 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -0 |  |
| 6 | 4 | PASS | Driver +7 (tie) |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood -8 |  |
| 9 | 4 | PASS | Driver +18 |  |
| 10 | 4 | PASS | 4-wood -0 |  |
| 11 | 4 | PASS | Driver +2 (tie) |  |
| 12 | 5 | PASS | Driver +4 |  |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | Driver +24 |  |
| 15 | 4 | PASS | Driver -22 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -4 |  |
| 18 | 4 | PASS | Driver +4 |  |

