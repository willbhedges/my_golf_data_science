# Cabot Citrus Farms: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 6, 7, 8, 9, 10, 11, 12, 15, 17

* page: `course_data/library/world_woods/page.html` (2.4 MB); request `course_data/requests/course_page_world_woods.json`; built 2026-11-03T00:13Z
* course: Cabot Citrus Farms ( Brooksville , FL), OSM way/410646892; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Silver (the two longest sets on the card (combination sets skipped)); page sets: Black, Silver
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [65, 80, 90] F; calm-day picks with 48 prior draws
* imagery on the page: 2021-11-30; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 1 Yellow(W) 300 < Green(M) 334'])
* 16 holes built vs the card's 18
* pars sum to 64, card 72
* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -32 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 54 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 63 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | 4-wood +40 |  |
| 6 | 5 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box); aim: Driver +40 lands 313 yds out in rough (7 yds from fairway); wide_aim: Driver aim +83 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 8 | 4 | CHECK | Driver +23 | tee: tee marker not on an OSM tee box (walkback; 49 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 48 yds from the nearest OSM tee box) |
| 11 | 4 | CHECK | Driver -10 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box); aim: Driver -10 lands 315 yds out in rough (34 yds from fairway) |
| 12 | 4 | CHECK | Driver -23 | tee: tee marker not on an OSM tee box (walkback; 77 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | Driver -26 |  |
| 15 | 4 | CHECK | 4-wood -16 | aim: 4-wood -16 lands 259 yds out in rough (103 yds from fairway); oval: landing pattern 46% trees / water / OB (recovery 46%) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (walkback; 98 yds from the nearest OSM tee box); aim: Driver +27 lands 303 yds out in rough (20 yds from fairway) |
| 18 | 4 | PASS | Driver -40 |  |

## Silver tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -30 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 4 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Long iron +40 |  |
| 6 | 5 | PASS | Driver -40 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver +32 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | Driver +9 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | CHECK | Driver +20 | aim: Driver +20 lands 316 yds out in rough (21 yds from fairway) |
| 12 | 4 | CHECK | Driver -24 | tee: tee marker not on an OSM tee box (walkback; 53 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | Driver -40 |  |
| 15 | 4 | CHECK | 2-wood -40 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 81 yds from the nearest OSM tee box); aim: 2-wood -40 lands 276 yds out in recovery (40 yds from fairway); oval: landing pattern 52% trees / water / OB (recovery 50%, unverified 4%) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | CHECK | Driver +28 | tee: tee marker not on an OSM tee box (walkback; 71 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver -33 |  |

