# Eagle Bend Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 6, 7, 10, 14, 18

* page: `course_data/library/eagle_bend/page.html` (2.7 MB); request `course_data/requests/course_page_eagle_bend.json`; built 2026-11-21T04:10Z
* course: Eagle Bend Golf Course (Lawrence, KS), OSM way/151983193; holes: osm (tier mapped_card); card: course_data/library/eagle_bend/card_fix.json (file)
* solved tee sets: Blue, Gold (tee sets of interest + the longest other set (Gold)); page sets: Blue, Gold
* weather: forecast for 2026-11-21, 2026-11-22; grid temperatures [40, 55, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-07-29; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): holes 15, 2, 14, 11 (7 asked of 14 framed holes; 4 kept on the page's own picks (3 dropped))

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -10 |  |
| 2 | 4 | PASS | Driver +24 |  |
| 3 | 5 | PASS | Driver -2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -1 |  |
| 6 | 4 | PASS | Driver -10 |  |
| 7 | 5 | CHECK | Driver -1 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood -2 |  |
| 10 | 4 | PASS | Driver +16 |  |
| 11 | 4 | PASS | Driver -5 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -10 |  |
| 14 | 4 | PASS | Driver +16 |  |
| 15 | 4 | PASS | Driver -21 |  |
| 16 | 4 | PASS | Driver -8 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +2 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -7 |  |
| 2 | 4 | PASS | Driver +12 |  |
| 3 | 5 | PASS | Driver -14 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -3 |  |
| 6 | 4 | CHECK | Driver -16 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 7 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (walkback; 28 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -3 |  |
| 10 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver -4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -9 |  |
| 14 | 4 | CHECK | Driver +14 | yardage: measured 374 vs card 429 (-55) |
| 15 | 4 | PASS | Driver -20 |  |
| 16 | 4 | PASS | Driver -10 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver -11 | tee: tee marker not on an OSM tee box (walkback; 41 yds from the nearest OSM tee box) |

