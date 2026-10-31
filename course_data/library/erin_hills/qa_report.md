# Erin Hills: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 9, 10, 13, 14, 15, 16, 18

* page: `course_data/library/erin_hills/page.html` (2.1 MB); request `course_data/requests/course_page_erin_hills.json`; built 2026-10-31T05:21Z
* course: Erin Hills (Erin, WI), OSM way/172725497; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-24; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -26 | tee: tee marker not on an OSM tee box (lidar_pad; 99 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +4 |  |
| 3 | 4 | PASS | Driver +1 |  |
| 4 | 4 | PASS | Driver +3 |  |
| 5 | 4 | PASS | Driver +10 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver +11 |  |
| 8 | 4 | PASS | Driver +0 |  |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 91 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -7 | yardage: measured 517 vs card 504 (+13) |
| 11 | 4 | PASS | Driver -22 |  |
| 12 | 4 | PASS | Driver -8 |  |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 88 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | Driver +14 |  |
| 15 | 4 | CHECK | Driver -24 | tee: tee marker not on an OSM tee box (lidar_pad; 115 yds from the nearest OSM tee box) |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 218 yds from the nearest OSM tee box) |
| 17 | 4 | PASS | Driver +7 |  |
| 18 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad; 51 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (lidar_pad; 88 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +4 |  |
| 3 | 4 | CHECK | Driver -15 | tee: tee marker not on an OSM tee box (walkback; 43 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver +3 |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver +18 |  |
| 8 | 4 | PASS | Driver -18 |  |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 118 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (walkback; 7 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver -22 |  |
| 12 | 4 | PASS | Driver -26 |  |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 83 yds from the nearest OSM tee box) |
| 14 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (lidar_pad; 24 yds from the nearest OSM tee box) |
| 15 | 4 | CHECK | Driver -26 | tee: tee marker not on an OSM tee box (lidar_pad; 104 yds from the nearest OSM tee box) |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 198 yds from the nearest OSM tee box) |
| 17 | 4 | PASS | Driver +1 |  |
| 18 | 5 | PASS | Driver -2 |  |

