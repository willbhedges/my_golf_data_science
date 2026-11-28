# Brown Deer Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 15, 16, 18

* page: `course_data/library/brown_deer/page.html` (5.1 MB); request `course_data/requests/course_page_brown_deer.json`; built 2026-11-28T02:56Z
* course: Brown Deer Golf Club (Coralville, IA), OSM way/191258543; holes: osm (tier mapped_card); card: course_data/library/brown_deer/routed_card.json (file)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: climate normals for 2026-12-05, 2026-12-06; grid temperatures [20, 30, 45] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Gold tees, library check cards): holes 3 (1 asked of 13 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 1 kept on the page's own picks)

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): 1 marked approximate (16)
* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -25 |  |
| 2 | 5 | PASS | Driver -6 |  |
| 3 | 4 | PASS | Driver -8 |  |
| 4 | 5 | PASS | Driver +2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +13 |  |
| 7 | 4 | PASS | Driver -18 |  |
| 8 | 4 | PASS | Driver +5 |  |
| 9 | 3 | PASS |  |  |
| 10 | 5 | PASS | 4-wood -4 |  |
| 11 | 4 | PASS | 4-wood -2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 2-wood +24 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | Driver -26 | aim: Driver -26 lands 324 yds out in rough (18 yds from fairway) |
| 16 | 4 | CHECK | 4-wood -8 | tee: tee marker not on an OSM tee box (walkback_capped; 21 yds from the nearest OSM tee box); yardage: measured 337 vs card 459 (-122) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Long iron -38 | aim: Long iron -38 lands 233 yds out in rough (44 yds from fairway); wide_aim: Long iron aim -48 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Long iron -12 | yardage: measured 225 vs card 297 (-72) |
| 2 | 5 | PASS | Driver -9 |  |
| 3 | 4 | CHECK | Driver -15 | aim: Driver -15 lands 307 yds out in sand (6 yds from fairway) |
| 4 | 5 | PASS | Driver -2 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +24 |  |
| 7 | 4 | PASS | Driver -20 |  |
| 8 | 4 | PASS | Driver +8 |  |
| 9 | 3 | PASS |  |  |
| 10 | 5 | PASS | Driver -10 |  |
| 11 | 4 | PASS | Long iron +4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +24 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | Driver -29 | aim: Driver -29 lands 328 yds out in rough (25 yds from fairway) |
| 16 | 4 | PASS | 4-wood -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Mid iron -26 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box); aim: Mid iron -26 lands 206 yds out in rough (47 yds from fairway) |

