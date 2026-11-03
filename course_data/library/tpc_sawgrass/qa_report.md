# TPC Sawgrass: automatic page QA

**Status: needs confirm** — confirm holes 4, 5, 14, 15

* page: `course_data/library/tpc_sawgrass/page.html` (2.9 MB); request `course_data/requests/course_page_tpc_sawgrass.json`; built 2026-11-03T06:47Z
* course: TPC Sawgrass (Ponte Vedra Beach, FL), OSM relation/1783123; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Tpc, Blue (the two longest sets on the card (combination sets skipped)); page sets: Tpc, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [65, 75, 85] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-11-18; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Tpc tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Tpc tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -2 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -10 |  |
| 4 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 5 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver +9 |  |
| 7 | 4 | PASS | Driver -22 |  |
| 8 | 5 | PASS | Driver -8 |  |
| 9 | 4 | PASS | Driver -1 (tie) |  |
| 10 | 4 | PASS | 4-wood -4 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood +16 |  |
| 13 | 4 | PASS | 4-wood +7 |  |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box); yardage: measured 185 vs card 203 (-18) |
| 15 | 4 | CHECK | 4-wood +4 | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box) |
| 16 | 5 | PASS | Driver -5 |  |
| 17 | 5 | PASS | Driver -16 |  |
| 18 | 4 | PASS | 4-wood -2 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -6 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver -10 |  |
| 4 | 4 | PASS | 2-wood +12 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood +2 |  |
| 7 | 4 | PASS | Driver -18 (tie) |  |
| 8 | 5 | PASS | Driver -12 |  |
| 9 | 4 | PASS | 2-wood +18 |  |
| 10 | 4 | PASS | 4-wood -4 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +34 |  |
| 13 | 4 | PASS | 4-wood +5 |  |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box); yardage: measured 167 vs card 193 (-26) |
| 15 | 4 | CHECK | 4-wood +26 | tee: tee marker not on an OSM tee box (lidar_pad; 48 yds from the nearest OSM tee box); aim: 4-wood +26 lands 275 yds out in rough (10 yds from fairway) |
| 16 | 5 | PASS | Driver -4 |  |
| 17 | 5 | PASS | Driver -18 |  |
| 18 | 4 | PASS | 4-wood -3 |  |

