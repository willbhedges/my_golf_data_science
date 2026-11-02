# Hodge Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 10, 12, 18

* page: `course_data/library/hodge_park/page.html` (2.3 MB); request `course_data/requests/course_page_hodge_park.json`; built 2026-11-02T19:34Z
* course: Hodge Park Golf Course (Kansas City, MO), OSM way/195221873; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): holes 2, 5 (2 asked of 14 framed holes)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -2 |  |
| 2 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (tagged; 3 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -10 |  |
| 5 | 4 | PASS | Driver -8 |  |
| 6 | 4 | PASS | Driver +18 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -30 |  |
| 9 | 4 | PASS | Driver +40 (tie) |  |
| 10 | 4 | CHECK | 4-wood -16 | tee: tee marker not on an OSM tee box (review; 18 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | Driver +12 |  |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tagged; 13 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | Driver +16 (tie) |  |
| 14 | 4 | PASS | 4-wood -4 |  |
| 15 | 4 | PASS | Mid iron -7 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +8 |  |
| 18 | 4 | PASS | 4-wood +52 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -2 |  |
| 2 | 4 | PASS | Driver +23 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | 4-wood +3 |  |
| 5 | 4 | PASS | Driver -6 |  |
| 6 | 4 | PASS | 4-wood +12 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -40 |  |
| 9 | 4 | PASS | Driver +45 |  |
| 10 | 4 | PASS | 4-wood -60 |  |
| 11 | 5 | PASS | Driver +12 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +10 |  |
| 14 | 4 | PASS | 4-wood -3 |  |
| 15 | 4 | PASS | Driver +52 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +6 |  |
| 18 | 4 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 280 yds out in rough (17 yds from fairway) |

