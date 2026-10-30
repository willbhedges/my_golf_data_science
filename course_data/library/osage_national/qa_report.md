# Osage National Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 6, 7

* page: `course_data/library/osage_national/page.html` (2.5 MB); request `course_data/requests/course_page_osage_national.json`; built 2026-10-30T04:37Z
* course: Osage National Golf Club (Osage Beach, MO), OSM relation/5897058; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Palmer, Tournament (the two longest sets on the card (combination sets skipped)); page sets: Palmer, Tournament
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2016-08-04; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Palmer tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -5 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | 4-wood +4 | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 |  |
| 6 | 4 | CHECK | Driver +22 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 7 | 5 | CHECK | Driver +23 | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +14 |  |
| 10 | 4 | PASS | Driver +14 |  |
| 11 | 4 | PASS | Driver -8 |  |
| 12 | 4 | PASS | Driver -17 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -0 |  |
| 15 | 4 | PASS | Long iron -5 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -2 |  |
| 18 | 5 | PASS | Driver +2 |  |

## Tournament tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +10 |  |
| 2 | 4 | PASS | 4-wood +8 (tie) |  |
| 3 | 4 | PASS | Driver -9 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 |  |
| 6 | 4 | PASS | 4-wood +23 |  |
| 7 | 5 | PASS | Driver +12 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +20 |  |
| 10 | 4 | PASS | 4-wood +14 (tie) |  |
| 11 | 4 | PASS | Driver -4 (tie) |  |
| 12 | 4 | PASS | Driver -34 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver +0 |  |
| 15 | 4 | PASS | Long iron -1 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +2 |  |
| 18 | 5 | PASS | 4-wood +10 |  |

