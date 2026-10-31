# Wintonbury Hills Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 5, 8, 9

* page: `course_data/library/wintonbury_hills/page.html` (3.8 MB); request `course_data/requests/course_page_wintonbury_hills.json`; built 2026-10-30T21:25Z
* course: Wintonbury Hills Golf Course (Bloomfield, CT), OSM way/296554921; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Green (the two longest sets on the card (combination sets skipped)); page sets: Black, Green
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [25, 40, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-02,2023-07-11; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -6 |  |
| 2 | 4 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (lidar_pad; 23 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver +9 |  |
| 5 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (tee_axis; 8 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver +1 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | Driver -3 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -1 |  |
| 14 | 4 | PASS | Driver +10 |  |
| 15 | 4 | PASS | Driver +2 (tie) |  |
| 16 | 4 | PASS | Driver -3 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +4 |  |

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -8 |  |
| 2 | 4 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (lidar_pad; 23 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver +8 |  |
| 5 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver +9 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +0 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | Driver -12 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +0 |  |
| 14 | 4 | PASS | Driver +6 |  |
| 15 | 4 | PASS | 4-wood +0 |  |
| 16 | 4 | PASS | Driver -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +4 |  |

