# Tournament Players Club of Louisiana: automatic page QA

**Status: needs confirm** — confirm holes 16

* page: `course_data/library/tpc_louisiana/page.html` (4.9 MB); request `course_data/requests/course_page_tpc_louisiana.json`; built 2026-11-03T03:34Z
* course: Tournament Players Club of Louisiana (Waggaman, LA), OSM relation/4260277; holes: osm (tier mapped_card); card: course_data/library/tpc_louisiana/card_review.json (file)
* solved tee sets: PGA TOUR, Black (the two longest sets on the card (combination sets skipped)); page sets: PGA TOUR, Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-03; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (PGA TOUR tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## PGA TOUR tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +8 |  |
| 2 | 5 | PASS | Driver +8 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -13 |  |
| 5 | 4 | PASS | Driver -11 |  |
| 6 | 4 | PASS | Driver +8 (tie) |  |
| 7 | 5 | PASS | Driver +4 |  |
| 8 | 4 | PASS | 4-wood -6 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood +6 |  |
| 11 | 5 | PASS | Driver +8 |  |
| 12 | 4 | PASS | Driver +2 |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +0 |  |
| 16 | 4 | CHECK | Long iron -0 | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -15 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +4 |  |
| 2 | 5 | PASS | Driver +6 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -10 |  |
| 5 | 4 | PASS | Driver -16 (tie) |  |
| 6 | 4 | PASS | 4-wood +6 |  |
| 7 | 5 | PASS | Driver -0 |  |
| 8 | 4 | PASS | Driver +0 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood +4 (tie) |  |
| 11 | 5 | PASS | Driver +8 |  |
| 12 | 4 | PASS | Driver -4 |  |
| 13 | 4 | PASS | Driver -40 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -6 |  |
| 16 | 4 | CHECK | Driver +52 | wide_aim: Driver aim +59 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -10 |  |

