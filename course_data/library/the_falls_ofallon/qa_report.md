# The Falls Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 9, 10, 11, 13, 15, 16, 18

* page: `course_data/library/the_falls_ofallon/page.html` (2.6 MB); request `course_data/requests/course_page_the_falls_ofallon.json`; built 2026-10-30T04:37Z
* course: The Falls Golf Club (O'Fallon, MO), OSM relation/3939928; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-18; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 (tie) |  |
| 2 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 20 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | 4-wood -2 | tee: tee marker not on an OSM tee box (lidar_pad; 38 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood -2 |  |
| 6 | 5 | PASS | Driver -3 |  |
| 7 | 4 | PASS | Driver +2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | 4-wood +8 | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 11 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 41 yds from the nearest OSM tee box) |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver +6 (tie) | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | Driver +6 (tie) | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 16 | 4 | CHECK | Driver -34 | tee: tee marker not on an OSM tee box (lidar_pad; 33 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +17 | tee: tee marker not on an OSM tee box (walkback; 30 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -2 (tie) |  |
| 2 | 4 | PASS | 2-wood +16 (tie) |  |
| 3 | 4 | PASS | Driver +36 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood -4 |  |
| 6 | 5 | PASS | 4-wood -2 |  |
| 7 | 4 | PASS | 4-wood -4 (tie) |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -0 |  |
| 10 | 4 | PASS | 4-wood +2 |  |
| 11 | 4 | PASS | 4-wood -8 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +6 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -7 |  |
| 16 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 300 yds out in sand (4 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback; 18 yds from the nearest OSM tee box) |

