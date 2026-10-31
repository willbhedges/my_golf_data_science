# Leatherstocking Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 9, 15, 18

* page: `course_data/library/leatherstocking/page.html` (2.6 MB); request `course_data/requests/course_page_leatherstocking.json`; built 2026-10-31T03:36Z
* course: Leatherstocking Golf Course (Cooperstown, NY), OSM relation/19437352; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2015-08-17; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +16 |  |
| 2 | 4 | PASS | 4-wood +0 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 15 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver -2 |  |
| 5 | 4 | PASS | Driver -20 |  |
| 6 | 4 | PASS | Driver +22 |  |
| 7 | 4 | PASS | 4-wood +2 |  |
| 8 | 4 | PASS | 4-wood +9 |  |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 2-wood -10 |  |
| 11 | 5 | PASS | Driver -4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -8 |  |
| 14 | 4 | PASS | 2-wood +10 (tie) |  |
| 15 | 5 | PASS | Driver +4 |  |
| 16 | 4 | PASS | 4-wood -8 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +16 |  |
| 2 | 4 | PASS | 4-wood +5 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver +2 |  |
| 5 | 4 | PASS | 2-wood -19 (tie) |  |
| 6 | 4 | PASS | Driver +22 |  |
| 7 | 4 | PASS | 4-wood +5 |  |
| 8 | 4 | PASS | 4-wood +10 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -24 |  |
| 11 | 5 | PASS | Driver -4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -8 |  |
| 14 | 4 | PASS | Long iron +4 |  |
| 15 | 5 | CHECK | Driver +6 | aim: Driver +6 lands 300 yds out in sand (3 yds from fairway) |
| 16 | 4 | PASS | Long iron -1 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver -15 | tee: tee marker not on an OSM tee box (tee_axis; 8 yds from the nearest OSM tee box) |

