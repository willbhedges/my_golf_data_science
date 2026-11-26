# Pinehurst No. 2: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/pinehurst/page.html` (6.2 MB); request `course_data/requests/course_page_pinehurst.json`; built 2026-11-26T18:53Z
* course: Pinehurst No. 2 (Pinehurst, NC), OSM way/1358696570; holes: osm (tier unmapped_card); card: allsquare (allsquare)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-07-27; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (not asked: no agent_layers in the request and no native_auto p in the package)

Course-level reasons:

* 17 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -9 | tee: tee marker not on an OSM tee box (walkback; 161 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (walkback; 316 yds from the nearest OSM tee box) |
| 3 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback; 267 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (walkback; 23 yds from the nearest OSM tee box) |
| 5 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback_capped; 198 yds from the nearest OSM tee box); yardage: measured 581 vs card 508 (+73) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | Driver +30 | tee: tee marker not on an OSM tee box (walkback; 204 yds from the nearest OSM tee box) |
| 8 | 5 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback; 351 yds from the nearest OSM tee box) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 276 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (walkback; 106 yds from the nearest OSM tee box) |
| 11 | 4 | CHECK | Driver -9 | tee: tee marker not on an OSM tee box (walkback; 268 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | Driver -40 (tie) | wide_aim: Driver aim -49 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 13 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (walkback; 381 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver +0 | tee: tee marker not on an OSM tee box (walkback; 72 yds from the nearest OSM tee box) |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 330 yds from the nearest OSM tee box) |
| 16 | 5 | CHECK | Driver -30 | tee: tee marker not on an OSM tee box (walkback; 205 yds from the nearest OSM tee box) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 292 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +16 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -8 (tie) | tee: tee marker not on an OSM tee box (walkback; 161 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (walkback_capped; 294 yds from the nearest OSM tee box); yardage: measured 477 vs card 411 (+66) |
| 3 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; 248 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | Driver -11 | tee: tee marker not on an OSM tee box (walkback; 63 yds from the nearest OSM tee box) |
| 5 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 292 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | Driver +36 | tee: tee marker not on an OSM tee box (walkback; 208 yds from the nearest OSM tee box) |
| 8 | 5 | CHECK | Driver +9 | tee: tee marker not on an OSM tee box (walkback; 331 yds from the nearest OSM tee box) |
| 9 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 250 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (walkback_capped; 72 yds from the nearest OSM tee box); yardage: measured 613 vs card 455 (+158) |
| 11 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 324 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 73 yds from the nearest OSM tee box) |
| 13 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback; 375 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (walkback; 79 yds from the nearest OSM tee box) |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 338 yds from the nearest OSM tee box) |
| 16 | 5 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (walkback; 175 yds from the nearest OSM tee box) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 269 yds from the nearest OSM tee box) |
| 18 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |

