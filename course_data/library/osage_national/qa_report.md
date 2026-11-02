# Osage National Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 6, 7

* page: `course_data/library/osage_national/page.html` (2.5 MB); request `course_data/requests/course_page_osage_national.json`; built 2026-11-02T13:46Z
* course: Osage National Golf Club (Osage Beach, MO), OSM relation/5897058; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Palmer, Tournament (the two longest sets on the card (combination sets skipped)); page sets: Palmer, Tournament
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2016-08-04; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Palmer tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -0 |  |
| 2 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | 4-wood +4 | tee: tee marker not on an OSM tee box (lidar_pad; 44 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 |  |
| 6 | 4 | CHECK | Driver +17 | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 7 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +12 |  |
| 10 | 4 | PASS | Driver +16 |  |
| 11 | 4 | PASS | Driver -7 |  |
| 12 | 4 | PASS | Driver -8 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -0 |  |
| 15 | 4 | PASS | Long iron -5 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -4 |  |
| 18 | 5 | PASS | Driver +1 |  |

## Tournament tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +4 (tie) |  |
| 2 | 4 | PASS | 4-wood +8 (tie) |  |
| 3 | 4 | PASS | Driver -10 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 |  |
| 6 | 4 | PASS | 4-wood +20 |  |
| 7 | 5 | PASS | Driver +2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +18 |  |
| 10 | 4 | PASS | Driver +19 (tie) |  |
| 11 | 4 | PASS | Driver -4 (tie) |  |
| 12 | 4 | PASS | Driver -31 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver +0 |  |
| 15 | 4 | PASS | Long iron -2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -1 (tie) |  |
| 18 | 5 | PASS | 4-wood +8 |  |

