# Edgewood Tahoe Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 7, 8, 11, 12, 13, 14, 15

* page: `course_data/library/edgewood_tahoe/page.html` (2.7 MB); request `course_data/requests/course_page_edgewood_tahoe.json`; built 2026-10-31T02:08Z
* course: Edgewood Tahoe Golf Course (Lake Tahoe, NV), OSM way/63521167; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 50, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-08-14; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 8 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +8 |  |
| 2 | 4 | PASS | Driver +0 |  |
| 3 | 5 | PASS | Driver +10 |  |
| 4 | 5 | PASS | Driver +0 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -5 |  |
| 7 | 3 | CHECK |  | yardage: measured 158 vs card 169 (-11) |
| 8 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 15 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver +7 |  |
| 10 | 4 | PASS | Driver -0 |  |
| 11 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 12 | 3 | PASS |  |  |
| 13 | 4 | CHECK | Driver +19 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood -6 (tie) |  |
| 15 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback; 49 yds from the nearest OSM tee box) |
| 16 | 5 | PASS | Driver -4 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -2 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +18 |  |
| 2 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 3 | 5 | PASS | Driver +30 |  |
| 4 | 5 | PASS | Driver -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver -2 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +6 |  |
| 9 | 4 | PASS | Driver +10 |  |
| 10 | 4 | PASS | Driver +14 |  |
| 11 | 4 | PASS | Driver -8 |  |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 30 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | Driver +8 |  |
| 14 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (lidar_pad; 10 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood +3 |  |
| 16 | 5 | PASS | Driver -4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -12 |  |

