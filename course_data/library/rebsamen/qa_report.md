# Rebsamen Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 5, 6, 9, 12, 13, 18

* page: `course_data/library/rebsamen/page.html` (2.2 MB); request `course_data/requests/course_page_rebsamen.json`; built 2026-10-30T22:20Z
* course: Rebsamen Golf Course (Little Rock, AR), OSM way/77018704; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-08-17,2019-09-04; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Black: holes sum to 6995 but the source says 7033 (-38): mixed card versions', 'White: holes sum to 5911 but the source says 5889 (+22): mixed card versions'])
* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -37 |  |
| 2 | 5 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | par3_box: target box 0% on the green, centre OFF it |
| 4 | 4 | PASS | Driver -7 |  |
| 5 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (lidar_pad; 42 yds from the nearest OSM tee box) |
| 6 | 4 | CHECK | Driver -40 (tie) | aim: Driver -40 lands 307 yds out in rough (18 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver -2 |  |
| 9 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 32 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -6 |  |
| 11 | 4 | PASS | Driver -4 |  |
| 12 | 5 | PASS | Driver -6 |  |
| 13 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 32 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +5 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -3 |  |
| 18 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -40 (tie) | aim: Driver -40 lands 311 yds out in sand (4 yds from fairway) |
| 2 | 5 | PASS | Driver +4 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 4 | PASS | 4-wood +4 (tie) |  |
| 6 | 4 | CHECK | 4-wood -40 (tie) | aim: 4-wood -40 lands 270 yds out in rough (8 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +0 |  |
| 9 | 4 | PASS | 4-wood -6 |  |
| 10 | 4 | PASS | Driver -4 |  |
| 11 | 4 | PASS | Driver -2 |  |
| 12 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (lidar_pad; 6 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | 2-wood -35 (tie) |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +4 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | 2-wood +4 (tie) |  |
| 18 | 4 | PASS | Driver -4 |  |

