# Gaylord Springs Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 5, 7, 9, 11, 12, 14, 15

* page: `course_data/library/gaylord_springs/page.html` (4.6 MB); request `course_data/requests/course_page_gaylord_springs.json`; built 2026-11-26T09:41Z
* course: Gaylord Springs Golf Links (Nashville, TN), OSM way/499135540; holes: osm (tier mapped_card); card: course_data/library/gaylord_springs/routed_card.json (file)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-07-03; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 16 (4 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 1 kept on the page's own picks (3 dropped))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): 1 marked approximate (3)
* 8 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -5 |  |
| 2 | 4 | PASS | Driver +4 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box); aim: Driver +40 lands 300 yds out in rough (63 yds from fairway); oval: landing pattern 46% trees / water / OB (water 42%, unverified 9%) |
| 5 | 4 | CHECK | 2-wood -32 (tie) | wide_aim: 2-wood aim -59 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 5 | PASS | Driver +32 |  |
| 7 | 4 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 19 yds from the nearest OSM tee box) |
| 10 | 5 | PASS | Driver -5 |  |
| 11 | 4 | CHECK | 4-wood +38 | tee: tee marker not on an OSM tee box (lidar_pad; 12 yds from the nearest OSM tee box) |
| 12 | 5 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box); aim: Driver +6 lands 306 yds out in rough (132 yds from fairway) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -12 | aim: Driver -12 lands 294 yds out in rough (14 yds from fairway) |
| 15 | 4 | CHECK | Driver -4 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 99 yds from the nearest OSM tee box) |
| 16 | 4 | PASS | Driver +0 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -2 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver +5 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 301 yds out in rough (58 yds from fairway); oval: landing pattern 45% trees / water / OB (water 41%, unverified 9%) |
| 5 | 4 | CHECK | 4-wood -29 (tie) | wide_aim: 4-wood aim -50 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 5 | PASS | 2-wood +27 |  |
| 7 | 4 | PASS | Driver +40 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +15 |  |
| 10 | 5 | PASS | Driver -6 |  |
| 11 | 4 | PASS | 4-wood +14 |  |
| 12 | 5 | CHECK | Driver +32 | aim: Driver +32 lands 308 yds out in rough (165 yds from fairway) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |
| 15 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 78 yds from the nearest OSM tee box) |
| 16 | 4 | PASS | 2-wood +0 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 2-wood -2 (tie) |  |

