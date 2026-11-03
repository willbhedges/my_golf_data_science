# Troon North Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 3

* page: `course_data/library/troon_north/page.html` (6.6 MB); request `course_data/requests/course_page_troon_north.json`; built 2026-11-03T15:54Z
* course: Troon North Golf Club (Scottsdale, AZ), OSM relation/1389558; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-06-15; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -5 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | CHECK | 2-wood +19 | tee: tee marker not on an OSM tee box (tee_axis; 7 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | 4-wood +12 |  |
| 5 | 4 | PASS | Driver -1 |  |
| 6 | 4 | PASS | Long iron -2 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood +3 |  |
| 9 | 5 | PASS | Driver -0 (tie) |  |
| 10 | 4 | PASS | 4-wood -6 |  |
| 11 | 5 | PASS | 4-wood -10 |  |
| 12 | 4 | PASS | 4-wood -16 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | 4-wood -2 |  |
| 15 | 4 | PASS | 4-wood -14 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | 4-wood +12 |  |
| 18 | 4 | PASS | 4-wood -8 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -6 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | 2-wood +20 (tie) |  |
| 4 | 4 | PASS | 4-wood +8 |  |
| 5 | 4 | PASS | 4-wood -1 |  |
| 6 | 4 | PASS | Long iron -2 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood +2 |  |
| 9 | 5 | PASS | Driver +0 |  |
| 10 | 4 | PASS | 4-wood -4 |  |
| 11 | 5 | PASS | 4-wood -5 |  |
| 12 | 4 | PASS | 4-wood -12 |  |
| 13 | 3 | PASS |  |  |
| 14 | 5 | PASS | Long iron -3 |  |
| 15 | 4 | PASS | 4-wood -18 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | 4-wood +10 |  |
| 18 | 4 | PASS | Driver -2 |  |

