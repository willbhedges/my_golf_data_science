# Audubon Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 5, 7, 9, 10, 11, 12, 13, 14, 18

* page: `course_data/library/audubon_park/page.html` (2.3 MB); request `course_data/requests/course_page_audubon_park.json`; built 2026-10-31T01:50Z
* course: Audubon Park Golf Course (New Orleans, LA), OSM way/27887431; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [60, 70, 85] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-03,2023-05-04; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 16 holes built vs the card's 18
* pars sum to 56, card 62
* 10 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +33 | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 3 | PASS |  |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 2-wood -9 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 134 yds from the nearest OSM tee box); yardage: measured 281 vs card 292 (-11) |
| 6 | 3 | PASS |  |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 105 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Long iron +37 (tie) | aim: Long iron +37 lands 223 yds out in rough (49 yds from fairway) |
| 10 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 300 yds out in rough (61 yds from fairway) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 286 yds from the nearest OSM tee box) |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 425 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 343 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver +15 | tee: tee marker not on an OSM tee box (tee_centroid; 166 yds from the nearest OSM tee box); aim: Driver +15 lands 298 yds out in rough (7 yds from fairway) |
| 16 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (lidar_pad; 278 yds from the nearest OSM tee box); aim: Driver +18 lands 305 yds out in rough (171 yds from fairway) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +12 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 86 yds from the nearest OSM tee box); aim: 4-wood +12 lands 268 yds out in rough (10 yds from fairway) |
| 2 | 3 | PASS |  |  |
| 3 | 3 | PASS |  |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | 4-wood -8 | tee: tee marker not on an OSM tee box (tee_axis; 138 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 63 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 5 | CHECK | Driver +40 | aim: Driver +40 lands 303 yds out in rough (62 yds from fairway) |
| 10 | 4 | CHECK | Driver +29 | aim: Driver +29 lands 296 yds out in rough (43 yds from fairway) |
| 11 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 304 yds from the nearest OSM tee box) |
| 12 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 413 yds from the nearest OSM tee box) |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 322 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | 4-wood +10 | tee: tee marker not on an OSM tee box (walkback; 145 yds from the nearest OSM tee box) |
| 16 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +25 | tee: tee marker not on an OSM tee box (lidar_pad; 256 yds from the nearest OSM tee box); aim: Driver +25 lands 300 yds out in rough (194 yds from fairway) |

