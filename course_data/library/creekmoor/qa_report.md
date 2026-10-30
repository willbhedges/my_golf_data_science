# Creekmoor Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 18

* page: `course_data/library/creekmoor/page.html` (2.4 MB); request `course_data/requests/course_page_creekmoor.json`; built 2026-10-30T00:25Z
* course: Creekmoor Golf Club (Raymore, MO), OSM relation/4249741; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Green (the two longest sets on the card (combination sets skipped)); page sets: Black, Green
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 15 holes built vs the card's 18
* pars sum to 62, card 72
* 13 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 4 | CHECK | Driver +0 | aim: Driver +0 lands 326 yds out in rough (38 yds from fairway) |
| 3 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box); aim: Driver -40 lands 296 yds out in ob (137 yds from fairway); oval: landing pattern 88% trees / water / OB (ob 85%, unverified 6%) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -36 | yardage: measured 526 vs card 537 (-11); aim: no fairway mapped on this hole; Driver lands in rough |
| 6 | 4 | CHECK | Driver +12 | aim: Driver +12 lands 301 yds out in rough (131 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (lidar_pad; 74 yds from the nearest OSM tee box); aim: Driver -12 lands 297 yds out in rough (94 yds from fairway) |
| 9 | 5 | CHECK | Mid iron +40 | aim: Mid iron +40 lands 189 yds out in recovery (64 yds from fairway); oval: landing pattern 86% trees / water / OB (recovery 72%, ob 14%) |
| 10 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (lidar_pad; 191 yds from the nearest OSM tee box); aim: Driver -40 lands 288 yds out in rough (39 yds from fairway) |
| 11 | 4 | CHECK | Driver -38 | aim: Driver -38 lands 315 yds out in rough (50 yds from fairway) |
| 13 | 5 | CHECK | Driver +8 | aim: Driver +8 lands 291 yds out in rough (188 yds from fairway) |
| 14 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 312 yds out in rough (95 yds from fairway) |
| 15 | 4 | CHECK | Driver -12 | aim: Driver -12 lands 285 yds out in rough (143 yds from fairway) |
| 16 | 4 | CHECK | 4-wood +3 | tee: tee marker not on an OSM tee box (lidar_pad; 118 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; 4-wood lands in water; oval: landing pattern 100% trees / water / OB (water 35%, ob 65%) |
| 18 | 5 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (walkback; 29 yds from the nearest OSM tee box); aim: no fairway mapped on this hole; Driver lands in rough |

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 2 | 4 | CHECK | Driver -28 | aim: Driver -28 lands 322 yds out in sand (15 yds from fairway) |
| 3 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 302 yds out in ob (105 yds from fairway); oval: landing pattern 88% trees / water / OB (ob 85%, unverified 6%) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -39 | aim: no fairway mapped on this hole; Driver lands in rough |
| 6 | 4 | CHECK | Driver +30 | aim: Driver +30 lands 304 yds out in rough (85 yds from fairway) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | 2-wood -30 | aim: 2-wood -30 lands 282 yds out in rough (105 yds from fairway) |
| 9 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (lidar_pad; 42 yds from the nearest OSM tee box); aim: Driver +40 lands 293 yds out in ob (196 yds from fairway); oval: landing pattern 73% trees / water / OB (ob 69%, unverified 6%) |
| 10 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; 202 yds from the nearest OSM tee box); aim: Driver -40 lands 288 yds out in rough (22 yds from fairway) |
| 11 | 4 | CHECK | Driver -32 | aim: Driver -32 lands 312 yds out in rough (33 yds from fairway) |
| 13 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 44 yds from the nearest OSM tee box); aim: Driver +2 lands 284 yds out in rough (223 yds from fairway) |
| 14 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 311 yds out in rough (62 yds from fairway) |
| 15 | 4 | CHECK | Driver -4 | aim: Driver -4 lands 285 yds out in rough (131 yds from fairway) |
| 16 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (lidar_pad; 64 yds from the nearest OSM tee box); aim: Driver -40 lands 296 yds out in ob (100 yds from fairway); oval: landing pattern 75% trees / water / OB (water 41%, ob 31%, unverified 6%) |
| 18 | 5 | CHECK | Driver -6 | aim: no fairway mapped on this hole; Driver lands in rough |

