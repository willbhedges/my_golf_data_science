# Eagle Bend Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 15, 18

* page: `course_data/library/eagle_bend/page.html` (2.4 MB); request `course_data/requests/course_page_eagle_bend.json`; built 2026-10-30T03:48Z
* course: Eagle Bend Golf Course (Lawrence, KS), OSM way/151983193; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-07-29; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 12 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -6 |  |
| 2 | 4 | PASS | Driver -26 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 178 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; 376 yds from the nearest OSM tee box); aim: Driver +40 lands 300 yds out in rough (150 yds from fairway) |
| 5 | 4 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box) |
| 6 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (walkback; 27 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 37 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 113 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver -5 |  |
| 12 | 5 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (walkback; 63 yds from the nearest OSM tee box); aim: Driver +5 lands 298 yds out in rough (78 yds from fairway) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 82 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | Driver -6 |  |
| 15 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; 29 yds from the nearest OSM tee box) |
| 16 | 5 | PASS | Driver -40 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | 4-wood +4 | tee: tee marker not on an OSM tee box (walkback; 32 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -10 |  |
| 2 | 4 | PASS | Driver +8 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 185 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; 361 yds from the nearest OSM tee box); aim: Driver +40 lands 300 yds out in rough (140 yds from fairway) |
| 5 | 4 | PASS | Driver -0 |  |
| 6 | 4 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver -22 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (walkback; 58 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver +16 |  |
| 11 | 4 | PASS | Driver -5 |  |
| 12 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 92 yds from the nearest OSM tee box); aim: Driver +2 lands 301 yds out in rough (61 yds from fairway) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 84 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 4 | PASS | Driver +22 |  |
| 16 | 5 | PASS | Driver -40 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +16 |  |

