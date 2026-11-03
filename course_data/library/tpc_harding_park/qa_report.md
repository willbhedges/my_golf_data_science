# TPC Harding Park: automatic page QA

**Status: needs confirm** — confirm holes 5

* page: `course_data/library/tpc_harding_park/page.html` (2.2 MB); request `course_data/requests/course_page_tpc_harding_park.json`; built 2026-11-03T05:53Z
* course: TPC Harding Park (San Francisco, CA), OSM way/16753068; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Championship, Blue (the two longest sets on the card (combination sets skipped)); page sets: Championship, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-08-04; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Championship tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 (tie) |  |
| 2 | 4 | PASS | Driver -2 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -2 |  |
| 5 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback; 20 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver +0 |  |
| 7 | 4 | PASS | Driver -1 (tie) |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -2 |  |
| 10 | 5 | PASS | Driver +3 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +3 |  |
| 13 | 4 | PASS | Driver -5 |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 4 | PASS | Driver -7 |  |
| 16 | 4 | PASS | 4-wood -16 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -20 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 (tie) |  |
| 2 | 4 | PASS | Driver +3 |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -18 |  |
| 5 | 4 | PASS | Driver -9 |  |
| 6 | 4 | PASS | Driver -13 |  |
| 7 | 4 | PASS | Driver +2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver -4 |  |
| 10 | 5 | PASS | Driver +4 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +0 |  |
| 13 | 4 | PASS | Driver +4 |  |
| 14 | 4 | PASS | Driver -2 |  |
| 15 | 4 | PASS | Driver -7 |  |
| 16 | 4 | PASS | Driver -4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -30 |  |

