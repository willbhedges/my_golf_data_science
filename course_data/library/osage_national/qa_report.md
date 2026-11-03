# Osage National Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 6, 7

* page: `course_data/library/osage_national/page.html` (2.5 MB); request `course_data/requests/course_page_osage_national.json`; built 2026-11-02T23:22Z
* course: Osage National Golf Club (Osage Beach, MO), OSM relation/5897058; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Palmer, Tournament (the two longest sets on the card (combination sets skipped)); page sets: Palmer, Tournament
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2016-08-04; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Palmer tees, library check cards): holes 5, 11 (3 asked of 14 framed holes; 2 kept on the page's own picks (1 dropped))

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Palmer tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -1 |  |
| 2 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | 4-wood +4 | tee: tee marker not on an OSM tee box (lidar_pad; 44 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 |  |
| 6 | 4 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 7 | 5 | CHECK | Driver +9 | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +9 |  |
| 10 | 4 | PASS | Driver +14 |  |
| 11 | 4 | PASS | Driver -7 |  |
| 12 | 4 | PASS | Driver -8 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver -0 |  |
| 15 | 4 | PASS | Long iron -1 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -4 |  |
| 18 | 5 | PASS | Driver +0 |  |

## Tournament tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +4 (tie) |  |
| 2 | 4 | PASS | 4-wood +8 (tie) |  |
| 3 | 4 | PASS | Driver -10 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -18 |  |
| 6 | 4 | PASS | 4-wood +20 |  |
| 7 | 5 | PASS | Driver -0 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +16 |  |
| 10 | 4 | PASS | Driver +16 |  |
| 11 | 4 | PASS | Driver -4 (tie) |  |
| 12 | 4 | PASS | Driver -28 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Driver +0 |  |
| 15 | 4 | PASS | Long iron +2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -1 (tie) |  |
| 18 | 5 | PASS | Driver -6 |  |

