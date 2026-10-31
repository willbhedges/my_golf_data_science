# University Ridge Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 16

* page: `course_data/library/university_ridge/page.html` (2.3 MB); request `course_data/requests/course_page_university_ridge.json`; built 2026-10-31T05:23Z
* course: University Ridge Golf Course (Madison, WI), OSM way/23810848; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-26; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +22 |  |
| 2 | 5 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (walkback; 44 yds from the nearest OSM tee box) |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 43 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver -11 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver -28 |  |
| 7 | 4 | PASS | Driver -6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +10 |  |
| 10 | 4 | PASS | Driver -1 |  |
| 11 | 5 | PASS | Driver -2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +1 |  |
| 14 | 4 | PASS | 2-wood -6 (tie) |  |
| 15 | 4 | PASS | Driver +40 |  |
| 16 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -20 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +26 |  |
| 2 | 5 | PASS | Driver -37 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood +2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver -26 |  |
| 7 | 4 | PASS | Driver -25 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -8 |  |
| 10 | 4 | PASS | Driver -0 |  |
| 11 | 5 | PASS | Driver +8 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +3 |  |
| 14 | 4 | PASS | 4-wood -11 |  |
| 15 | 4 | PASS | 4-wood +40 |  |
| 16 | 5 | PASS | Driver +0 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -24 |  |

