# Troon North Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 5, 6, 7, 10, 13, 15, 16, 17, 18

* page: `course_data/library/troon_north/page.html` (6.6 MB); request `course_data/requests/course_page_troon_north.json`; built 2026-11-03T04:14Z
* course: Troon North Golf Club (Scottsdale, AZ), OSM relation/1389558; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-06-15; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -5 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (walkback_capped; 50 yds from the nearest OSM tee box); yardage: measured 417 vs card 556 (-139) |
| 4 | 4 | PASS | Driver +2 |  |
| 5 | 4 | PASS | Driver +13 |  |
| 6 | 4 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (walkback; 92 yds from the nearest OSM tee box) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood +14 |  |
| 9 | 5 | PASS | Driver +12 |  |
| 10 | 4 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | Driver +32 |  |
| 12 | 4 | PASS | Driver +8 (tie) |  |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | 4-wood -2 |  |
| 15 | 4 | PASS | 2-wood -32 (tie) |  |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 93 yds from the nearest OSM tee box) |
| 17 | 4 | CHECK | Driver -7 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 44 yds from the nearest OSM tee box); yardage: measured 467 vs card 495 (-28) |
| 18 | 4 | CHECK | Driver -31 | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box); aim: Driver -31 lands 317 yds out in rough (8 yds from fairway) |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -6 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (walkback_capped; 50 yds from the nearest OSM tee box); yardage: measured 417 vs card 544 (-127) |
| 4 | 4 | CHECK | 4-wood +2 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver +17 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 6 | 4 | CHECK | 2-wood +4 (tie) | tee: tee marker not on an OSM tee box (walkback; 90 yds from the nearest OSM tee box) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood +13 |  |
| 9 | 5 | PASS | Driver +10 |  |
| 10 | 4 | PASS | 4-wood -9 |  |
| 11 | 5 | PASS | Driver +32 |  |
| 12 | 4 | PASS | Driver +8 |  |
| 13 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 45 yds from the nearest OSM tee box) |
| 14 | 5 | PASS | Long iron -3 |  |
| 15 | 4 | CHECK | 4-wood -29 | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 88 yds from the nearest OSM tee box) |
| 17 | 4 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (lidar_pad; 34 yds from the nearest OSM tee box) |
| 18 | 4 | CHECK | Driver -34 | tee: tee marker not on an OSM tee box (lidar_pad; 26 yds from the nearest OSM tee box) |

