# Tomahawk Hills Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 4, 6, 13

* page: `course_data/library/tomahawk_hills/page.html` (4.7 MB); request `course_data/requests/course_page_tomahawk_hills.json`; built 2026-10-30T03:40Z
* course: Tomahawk Hills Golf Course (Shawnee, KS), OSM way/117417596; holes: v2+structure (tier mapped_card); card: club_site (club_site)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -6 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | 4-wood -4 |  |
| 4 | 4 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | 4-wood -2 |  |
| 6 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 26 yds from the nearest OSM tee box) |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | PASS | Driver -4 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -24 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -19 |  |
| 13 | 4 | CHECK | 2-wood -14 (tie) | aim: 2-wood -14 lands 271 yds out in rough (8 yds from fairway) |
| 14 | 5 | PASS | Driver -12 |  |
| 15 | 5 | PASS | Driver +8 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -14 (tie) |  |
| 18 | 3 | PASS |  |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -6 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | 4-wood -5 |  |
| 4 | 4 | PASS | Driver +14 |  |
| 5 | 4 | PASS | Long iron -2 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -6 |  |
| 8 | 4 | PASS | 4-wood -2 (tie) |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -19 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -19 |  |
| 13 | 4 | PASS | 4-wood -10 |  |
| 14 | 5 | PASS | Driver -12 |  |
| 15 | 5 | PASS | Driver +3 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +8 |  |
| 18 | 3 | PASS |  |  |

