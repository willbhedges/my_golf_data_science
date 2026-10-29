# Blue Hills Country Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 11

* page: `course_data/library/gate/gate_blue_hills/page.html` (5.4 MB); request `course_data/requests/course_page_gate_blue_hills.json`; built 2026-10-29T20:42Z
* course: Blue Hills Country Club (Kansas City, MO), OSM way/315837565; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (tee sets of interest + the longest other set (Blue)); page sets: Black, Blue
* weather: climate normals for 2026-10-27; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +4 |  |
| 2 | 4 | CHECK | 4-wood +8 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | 4-wood -4 |  |
| 4 | 4 | PASS | 2-wood +14 (tie) |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver -0 |  |
| 7 | 4 | PASS | 4-wood +2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood +9 |  |
| 10 | 4 | PASS | Driver -6 |  |
| 11 | 4 | PASS | Driver +2 (tie) |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +11 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -1 |  |
| 16 | 4 | PASS | Driver -1 |  |
| 17 | 4 | PASS | Driver +20 |  |
| 18 | 5 | PASS | 4-wood +16 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -2 |  |
| 2 | 4 | PASS | 4-wood +8 |  |
| 3 | 4 | PASS | 4-wood +2 |  |
| 4 | 4 | PASS | 4-wood +14 (tie) |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver -2 |  |
| 7 | 4 | PASS | 4-wood -2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +3 (tie) |  |
| 10 | 4 | PASS | Driver -12 |  |
| 11 | 4 | CHECK | Driver +4 | aim: Driver +4 lands 308 yds out in rough (7 yds from fairway) |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +3 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | 4-wood -1 (tie) |  |
| 16 | 4 | PASS | Driver -0 |  |
| 17 | 4 | PASS | 4-wood +23 |  |
| 18 | 5 | PASS | 4-wood -0 |  |

