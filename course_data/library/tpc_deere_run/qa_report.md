# TPC Deere Run: automatic page QA

**Status: needs confirm** — confirm holes 6, 7

* page: `course_data/library/tpc_deere_run/page.html` (6.0 MB); request `course_data/requests/course_page_tpc_deere_run.json`; built 2026-11-03T01:38Z
* course: TPC Deere Run (Silvis, IL), OSM relation/12585470; holes: osm (tier mapped_card); card: course_data/library/tpc_deere_run/card_review.json (file)
* solved tee sets: Gold, Black (tee sets of interest); page sets: Gold, Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-07; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Gold tees, library check cards): holes 4, 17 (2 asked of 14 framed holes; 2 kept on the page's own picks)

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +8 |  |
| 2 | 5 | PASS | Driver -6 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +26 |  |
| 5 | 4 | PASS | Driver +1 |  |
| 6 | 4 | PASS | 4-wood +5 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 26 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood +3 |  |
| 9 | 4 | PASS | Driver +26 |  |
| 10 | 5 | PASS | Driver +13 |  |
| 11 | 4 | PASS | 4-wood +12 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -9 |  |
| 14 | 4 | PASS | 2-wood -15 (tie) |  |
| 15 | 4 | PASS | Driver -0 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +6 |  |
| 18 | 4 | PASS | Driver -40 (tie) |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +6 (tie) |  |
| 2 | 5 | PASS | Driver +7 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +22 |  |
| 5 | 4 | PASS | 2-wood +0 (tie) |  |
| 6 | 4 | CHECK | Driver +33 | aim: Driver +33 lands 307 yds out in rough (12 yds from fairway) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver +8 |  |
| 9 | 4 | PASS | Driver -2 |  |
| 10 | 5 | PASS | Driver +9 |  |
| 11 | 4 | PASS | 4-wood +12 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -6 |  |
| 14 | 4 | PASS | Driver -6 (tie) |  |
| 15 | 4 | PASS | 4-wood -2 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +2 |  |
| 18 | 4 | PASS | 4-wood -12 |  |

