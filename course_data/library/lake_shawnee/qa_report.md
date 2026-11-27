# Lake Shawnee Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 7, 10, 11, 12, 14, 18

* page: `course_data/library/lake_shawnee/page.html` (5.2 MB); request `course_data/requests/course_page_lake_shawnee.json`; built 2026-11-26T23:32Z
* course: Lake Shawnee Golf Course (Topeka, KS), OSM relation/2053245; holes: osm (tier mapped_card); card: course_data/library/lake_shawnee/routed_card.json (file)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: climate normals for 2026-11-28, 2026-11-29; grid temperatures [30, 40, 50] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-05-10; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (0 asked of 13 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): none marked approximate
* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +10 |  |
| 2 | 4 | PASS | 4-wood -4 |  |
| 3 | 4 | PASS | 4-wood -6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -4 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | 4-wood -6 | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -4 (tie) |  |
| 9 | 5 | PASS | Driver -2 |  |
| 10 | 4 | CHECK | Driver -52 | wide_aim: Driver aim -52 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 4 | CHECK | Driver -11 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; 47 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -49 | wide_aim: 4-wood aim -66 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 3 | PASS |  |  |
| 16 | 5 | PASS | Driver -1 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +11 (tie) |  |
| 2 | 4 | PASS | 4-wood +16 |  |
| 3 | 4 | PASS | Driver -15 (tie) |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -2 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +18 |  |
| 8 | 4 | PASS | 4-wood -14 |  |
| 9 | 5 | PASS | Driver -5 |  |
| 10 | 4 | CHECK | 4-wood -48 (tie) | wide_aim: 4-wood aim -48 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 4 | PASS | Driver -16 |  |
| 12 | 4 | PASS | 4-wood -40 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -60 | aim: 4-wood -60 lands 268 yds out in recovery (9 yds from fairway); wide_aim: 4-wood aim -60 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 3 | PASS |  |  |
| 16 | 5 | PASS | Driver +4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -10 |  |

