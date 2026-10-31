# George Wright Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 5, 8, 10, 18

* page: `course_data/library/george_wright/page.html` (5.4 MB); request `course_data/requests/course_page_george_wright.json`; built 2026-10-31T01:57Z
* course: George Wright Golf Course (Hyde Park, MA), OSM way/29830747; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-07; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -10 |  |
| 2 | 4 | PASS | Driver -2 |  |
| 3 | 5 | PASS | Driver +4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +14 |  |
| 6 | 4 | PASS | Driver -10 |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 75 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver -0 |  |
| 10 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 10 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood +15 |  |
| 12 | 4 | PASS | Driver +22 |  |
| 13 | 4 | PASS | 4-wood +3 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +8 |  |
| 16 | 4 | PASS | 4-wood +10 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -6 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -12 |  |
| 2 | 4 | PASS | Driver -4 |  |
| 3 | 5 | PASS | Driver +2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 4-wood +16 | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver -16 |  |
| 7 | 4 | PASS | Driver +14 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 4 | PASS | 2-wood -15 (tie) |  |
| 11 | 4 | PASS | 4-wood +22 |  |
| 12 | 4 | PASS | 2-wood +20 (tie) |  |
| 13 | 4 | PASS | 4-wood +5 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +16 |  |
| 16 | 4 | PASS | 4-wood +14 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (lidar_pad; 29 yds from the nearest OSM tee box) |

