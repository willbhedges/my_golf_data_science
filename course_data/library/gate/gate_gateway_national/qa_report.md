# Gateway National Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 8, 10, 13

* page: `course_data/library/gate/gate_gateway_national/page.html` (4.3 MB); request `course_data/requests/course_page_gate_gateway_national.json`; built 2026-10-29T20:42Z
* course: Gateway National Golf Links (Madison, IL), OSM way/782435512; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Back, The Tips (tee sets of interest + the longest other set (The Tips)); page sets: Back, The Tips
* weather: climate normals for 2026-11-14, 2026-11-15; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-19; package imagery 2016
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -5 |  |
| 2 | 4 | PASS | Driver -1 |  |
| 3 | 5 | PASS | Driver -10 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -1 |  |
| 6 | 5 | PASS | Driver +6 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver -38 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 10 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver +8 |  |
| 10 | 4 | PASS | 2-wood -22 (tie) |  |
| 11 | 4 | PASS | Driver +22 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +10 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +10 |  |
| 16 | 4 | PASS | 2-wood -2 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +14 |  |

## The Tips tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -11 |  |
| 2 | 4 | PASS | Driver +10 |  |
| 3 | 5 | PASS | Driver -11 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +10 |  |
| 6 | 5 | PASS | Driver +10 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -38 |  |
| 9 | 4 | PASS | Driver -0 |  |
| 10 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback; 39 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver +22 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (lidar_pad; 41 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +26 |  |
| 16 | 4 | PASS | Driver +2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +16 |  |

