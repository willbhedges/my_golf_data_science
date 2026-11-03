# TPC Sawgrass: automatic page QA

**Status: needs confirm** — confirm holes 2, 6, 9, 12

* page: `course_data/library/tpc_sawgrass/page.html` (2.9 MB); request `course_data/requests/course_page_tpc_sawgrass.json`; built 2026-11-03T15:30Z
* course: TPC Sawgrass (Ponte Vedra Beach, FL), OSM relation/1783123; holes: osm (tier mapped_card); card: course_data/library/tpc_sawgrass/card_review.json (file)
* solved tee sets: The Players, Blue (the two longest sets on the card (combination sets skipped)); page sets: The Players, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [65, 75, 85] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-11-18; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (The Players tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## The Players tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +13 |  |
| 2 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 29 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +7 |  |
| 5 | 4 | PASS | Driver -13 |  |
| 6 | 4 | CHECK | Driver -1 (tie) | tee: tee marker not on an OSM tee box (walkback; 20 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver +10 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (lidar_pad; 24 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 4-wood -0 |  |
| 11 | 5 | PASS | Driver -4 |  |
| 12 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +6 |  |
| 15 | 4 | PASS | Driver -0 |  |
| 16 | 5 | PASS | Driver -0 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +12 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +8 |  |
| 2 | 5 | PASS | Driver -7 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 2-wood +12 |  |
| 5 | 4 | PASS | Driver -7 |  |
| 6 | 4 | PASS | Driver -8 |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -3 |  |
| 10 | 4 | PASS | 4-wood -6 |  |
| 11 | 5 | PASS | Driver -1 |  |
| 12 | 4 | PASS | Driver -18 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +1 (tie) |  |
| 15 | 4 | PASS | 2-wood +7 (tie) |  |
| 16 | 5 | PASS | Driver -18 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood +0 |  |

