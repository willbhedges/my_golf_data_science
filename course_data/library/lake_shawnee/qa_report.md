# Lake Shawnee Golf Course: automatic page QA

**Status: blocked** — confirm holes 1, 2, 3, 5, 7, 9, 10, 11, 12, 14, 15, 18

* page: `course_data/library/lake_shawnee/page.html` (5.3 MB); request `course_data/requests/course_page_lake_shawnee.json`; built 2026-11-26T09:25Z
* course: Lake Shawnee Golf Course (Topeka, KS), OSM relation/2053245; holes: osm (tier mapped_card); card: course_data/library/lake_shawnee/routed_card.json (file)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-05-10; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (0 asked of 13 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): none marked approximate
* holes out of order: green-to-next-tee walks up to 890 yds, 1 over 500 (in order: under 800, at most 3 over 500); longest: 2->3 890, 1->2 363, 9->10 215
* 12 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -0 (tie) | yardage: measured 380 vs card 348 (+32) |
| 2 | 4 | CHECK | Driver +30 | yardage: measured 646 vs card 369 (+277); aim: Driver +30 lands 297 yds out in rough (129 yds from fairway) |
| 3 | 4 | CHECK | 2-wood +40 (tie) | yardage: measured 760 vs card 353 (+407); aim: 2-wood +40 lands 278 yds out in rough (74 yds from fairway) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (lidar_pad; 44 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | 4-wood -6 | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -6 (tie) |  |
| 9 | 5 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -52 | wide_aim: Driver aim -58 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; 47 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -50 | wide_aim: 2-wood aim -66 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 63 yds from the nearest OSM tee box) |
| 16 | 5 | PASS | Driver -0 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (review (kept: snap snapped 15 yds along OSM tee 152048999 would measure 441, another set's box, point 455, card 455); 15 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +4 (tie) | yardage: measured 377 vs card 334 (+43) |
| 2 | 4 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (review; 28 yds from the nearest OSM tee box); yardage: measured 665 vs card 330 (+335); aim: Driver +40 lands 291 yds out in rough (107 yds from fairway) |
| 3 | 4 | CHECK | Driver +18 | yardage: measured 787 vs card 320 (+467); aim: Driver +18 lands 294 yds out in rough (55 yds from fairway) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 30 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +18 |  |
| 8 | 4 | PASS | 4-wood -14 |  |
| 9 | 5 | PASS | Driver -4 |  |
| 10 | 4 | CHECK | 4-wood -48 (tie) | wide_aim: 2-wood aim -55 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 4 | PASS | Driver -17 |  |
| 12 | 4 | CHECK | 4-wood -40 | tee: tee marker not on an OSM tee box (tee_axis; 8 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -60 | aim: 4-wood -60 lands 268 yds out in recovery (9 yds from fairway); wide_aim: 4-wood aim -72 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 47 yds from the nearest OSM tee box) |
| 16 | 5 | PASS | Driver +4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -10 |  |

