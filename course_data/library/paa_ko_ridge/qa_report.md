# Paa-Ko Ridge Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 18

* page: `course_data/library/paa_ko_ridge/page.html` (3.2 MB); request `course_data/requests/course_page_paa_ko_ridge.json`; built 2026-11-03T09:10Z
* course: Paa-Ko Ridge Golf Club (Sandia Park, NM), OSM relation/3585731; holes: osm (tier mapped_card); card: course_data/library/paa_ko_ridge/card_golfify.json (file)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-05-28; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +3 |  |
| 2 | 4 | PASS | 4-wood -9 |  |
| 3 | 5 | PASS | Driver -9 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -14 |  |
| 6 | 4 | PASS | Driver +6 (tie) |  |
| 7 | 4 | PASS | Driver -7 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +8 |  |
| 10 | 4 | PASS | Driver -11 (tie) |  |
| 11 | 4 | PASS | Driver -2 |  |
| 12 | 5 | PASS | Driver -6 |  |
| 13 | 4 | PASS | 4-wood -13 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -9 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +6 |  |
| 18 | 4 | CHECK | Driver -10 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -3 |  |
| 2 | 4 | PASS | 4-wood -10 |  |
| 3 | 5 | PASS | Driver -12 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -11 |  |
| 6 | 4 | PASS | Driver +8 |  |
| 7 | 4 | PASS | Driver -15 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +12 |  |
| 10 | 4 | PASS | 4-wood -6 |  |
| 11 | 4 | PASS | Driver -7 |  |
| 12 | 5 | PASS | Driver -6 |  |
| 13 | 4 | PASS | Driver -9 (tie) |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +7 (tie) |  |
| 18 | 4 | PASS | Driver -13 (tie) |  |

