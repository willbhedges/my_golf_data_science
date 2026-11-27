# Gaylord Springs Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 1, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 18

* page: `course_data/library/gaylord_springs/page.html` (4.5 MB); request `course_data/requests/course_page_gaylord_springs.json`; built 2026-11-26T23:28Z
* course: Gaylord Springs Golf Links (Nashville, TN), OSM way/499135540; holes: osm (tier mapped_card); card: course_data/library/gaylord_springs/routed_card.json (file)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-07-03; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (4 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 0 kept on the page's own picks (4 dropped))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): 2 marked approximate (6, 14)
* 14 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 33 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +12 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -2 | aim: Driver -2 lands 295 yds out in rough (32 yds from fairway) |
| 5 | 4 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (lidar_pad; 42 yds from the nearest OSM tee box); aim: Driver -32 lands 301 yds out in rough (197 yds from fairway) |
| 6 | 5 | CHECK | Driver -26 | yardage: measured 461 vs card 533 (-72); aim: Driver -26 lands 302 yds out in rough (91 yds from fairway) |
| 7 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 302 yds out in rough (15 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +16 | aim: Driver +16 lands 306 yds out in rough (22 yds from fairway) |
| 10 | 5 | CHECK | Driver -0 | aim: Driver -0 lands 306 yds out in rough (221 yds from fairway) |
| 11 | 4 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 276 yds out in rough (150 yds from fairway) |
| 12 | 5 | CHECK | Driver +34 | aim: Driver +34 lands 298 yds out in rough (140 yds from fairway) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood +48 | yardage: measured 278 vs card 335 (-57); wide_aim: 4-wood aim +60 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 4 | CHECK | Driver -16 | aim: Driver -16 lands 302 yds out in rough (93 yds from fairway) |
| 16 | 4 | PASS | Driver +29 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -12 | aim: Driver -12 lands 305 yds out in rough (113 yds from fairway) |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -2 |  |
| 2 | 4 | PASS | Driver +15 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -3 | aim: Driver -3 lands 292 yds out in rough (23 yds from fairway) |
| 5 | 4 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (lidar_pad; 31 yds from the nearest OSM tee box); aim: Driver -28 lands 310 yds out in rough (192 yds from fairway) |
| 6 | 5 | CHECK | Driver +20 | aim: Driver +20 lands 307 yds out in rough (113 yds from fairway) |
| 7 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 302 yds out in rough (24 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +16 | aim: Driver +16 lands 304 yds out in rough (14 yds from fairway) |
| 10 | 5 | CHECK | Driver -2 | aim: Driver -2 lands 305 yds out in rough (229 yds from fairway) |
| 11 | 4 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 278 yds out in rough (150 yds from fairway) |
| 12 | 5 | CHECK | Driver +32 | aim: Driver +32 lands 308 yds out in rough (167 yds from fairway) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood +40 | yardage: measured 267 vs card 320 (-53); aim: 4-wood +40 lands 268 yds out in rough (7 yds from fairway) |
| 15 | 4 | CHECK | Driver -12 | aim: Driver -12 lands 299 yds out in rough (78 yds from fairway) |
| 16 | 4 | CHECK | Driver +31 (tie) | aim: Driver +31 lands 313 yds out in rough (18 yds from fairway) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 18 | 4 | CHECK | Driver -19 | aim: Driver -19 lands 308 yds out in rough (91 yds from fairway) |

