# Ed Oliver Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 3, 5, 7, 10, 14, 18

* page: `course_data/library/ed_oliver/page.html` (3.5 MB); request `course_data/requests/course_page_ed_oliver.json`; built 2026-10-30T21:35Z
* course: Ed Oliver Golf Club (Wilmington, DE), OSM way/82787084; holes: v2+structure (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Black, White (the two longest sets on the card (combination sets skipped)); page sets: Black, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-11; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +4 (tie) |  |
| 2 | 4 | PASS | Driver +3 |  |
| 3 | 4 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver +25 |  |
| 5 | 3 | CHECK |  | par3_box: target box 0% on the green, centre OFF it |
| 6 | 5 | PASS | Driver +22 |  |
| 7 | 4 | PASS | Driver +26 |  |
| 8 | 4 | PASS | Driver -15 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | CHECK | 4-wood +26 | tee: tee marker not on an OSM tee box (tee_axis; 65 yds from the nearest OSM tee box); yardage: measured 351 vs card 362 (-11) |
| 11 | 4 | PASS | 4-wood -32 |  |
| 12 | 4 | PASS | Driver +1 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -8 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood -25 |  |
| 16 | 4 | PASS | Driver +22 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +2 |  |
| 2 | 4 | PASS | Driver +4 |  |
| 3 | 4 | PASS | Driver +22 |  |
| 4 | 5 | PASS | Driver +22 |  |
| 5 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 6 | 5 | PASS | Driver +14 |  |
| 7 | 4 | CHECK | Driver +27 | aim: Driver +27 lands 294 yds out in rough (7 yds from fairway) |
| 8 | 4 | PASS | Driver -12 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | CHECK | 4-wood +26 | tee: tee marker not on an OSM tee box (tee_axis; 65 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood -30 |  |
| 12 | 4 | PASS | 2-wood +0 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -8 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood -25 |  |
| 16 | 4 | PASS | Driver +22 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -38 |  |

