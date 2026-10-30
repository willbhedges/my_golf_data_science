# The Jayhawk Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 10

* page: `course_data/library/jayhawk_club/page.html` (1.6 MB); request `course_data/requests/course_page_jayhawk_club.json`; built 2026-10-30T03:52Z
* course: The Jayhawk Club (Lawrence, KS), OSM relation/2053560; holes: structure (tier unmapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Green (the two longest sets on the card (combination sets skipped)); page sets: Black, Green
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-07-29; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: structure)
* 10 holes built vs the card's 18
* pars sum to 40, card 72
* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -3 |  |
| 2 | 5 | CHECK | Driver -26 | tee: tee marker not on an OSM tee box (walkback; 76 yds from the nearest OSM tee box); aim: Driver -26 lands 274 yds out in rough (36 yds from fairway) |
| 3 | 4 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (walkback; 112 yds from the nearest OSM tee box); aim: Driver +7 lands 321 yds out in rough (77 yds from fairway) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver -3 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box); yardage: measured 385 vs card 396 (-11); aim: Driver -3 lands 273 yds out in rough (90 yds from fairway) |
| 6 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (walkback; 108 yds from the nearest OSM tee box) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 42 yds from the nearest OSM tee box) |
| 8 | 5 | CHECK | 4-wood -32 | tee: tee marker not on an OSM tee box (walkback; 58 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver -12 |  |
| 10 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (lidar_pad; 59 yds from the nearest OSM tee box) |

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (lidar_pad; 8 yds from the nearest OSM tee box) |
| 2 | 5 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (walkback; 48 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 85 yds from the nearest OSM tee box); aim: Driver +2 lands 327 yds out in rough (42 yds from fairway) |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 6 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | 2-wood +9 | tee: tee marker not on an OSM tee box (lidar_pad; 14 yds from the nearest OSM tee box); aim: 2-wood +9 lands 259 yds out in rough (99 yds from fairway) |
| 6 | 4 | CHECK | 4-wood -12 | tee: tee marker not on an OSM tee box (walkback; 69 yds from the nearest OSM tee box) |
| 7 | 3 | PASS |  |  |
| 8 | 5 | CHECK | 4-wood -40 | aim: 4-wood -40 lands 276 yds out in rough (20 yds from fairway); oval: landing pattern 42% trees / water / OB (recovery 22%, water 20%) |
| 9 | 4 | PASS | Driver -10 |  |
| 10 | 4 | CHECK | 4-wood +9 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box) |

