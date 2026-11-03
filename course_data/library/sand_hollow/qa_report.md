# Sand Hollow Resort: automatic page QA

**Status: needs confirm** — confirm holes 4, 13, 17, 18

* page: `course_data/library/sand_hollow/page.html` (2.6 MB); request `course_data/requests/course_page_sand_hollow.json`; built 2026-11-03T15:11Z
* course: Sand Hollow Resort (Hurricane, UT), OSM relation/3580189; holes: osm (tier mapped_card); card: course_data/library/sand_hollow/card_review.json (file)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [50, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-09-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +13 |  |
| 2 | 5 | PASS | Driver +17 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 113 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Driver -2 |  |
| 6 | 4 | PASS | Driver -4 |  |
| 7 | 5 | PASS | Driver +10 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -8 |  |
| 10 | 5 | PASS | Driver +5 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -2 |  |
| 13 | 4 | PASS | Driver -6 |  |
| 14 | 4 | PASS | Driver +1 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +6 (tie) |  |
| 17 | 5 | PASS | Driver +2 |  |
| 18 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (lidar_pad; 8 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +16 |  |
| 2 | 5 | PASS | Driver +9 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (walkback; 89 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Driver +0 |  |
| 6 | 4 | PASS | Driver +2 |  |
| 7 | 5 | PASS | Driver +8 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -12 |  |
| 10 | 5 | PASS | Driver -14 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -6 |  |
| 13 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (lidar_pad; 12 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | Driver +5 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +16 |  |
| 17 | 5 | CHECK | Driver -8 | aim: Driver -8 lands 312 yds out in rough (8 yds from fairway) |
| 18 | 4 | PASS | Driver +10 |  |

