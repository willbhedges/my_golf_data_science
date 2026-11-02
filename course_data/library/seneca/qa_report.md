# Seneca Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 5, 6, 7, 8, 9, 10, 17

* page: `course_data/library/seneca/page.html` (2.9 MB); request `course_data/requests/course_page_seneca.json`; built 2026-11-01T22:01Z
* course: Seneca Golf Course (Louisville, KY), OSM way/59714994; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-18; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 10 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +36 | tee: tee marker not on an OSM tee box (walkback; 37 yds from the nearest OSM tee box); aim: Driver +36 lands 327 yds out in rough (23 yds from fairway) |
| 2 | 4 | CHECK | Mid iron +38 | tee: tee marker not on an OSM tee box (walkback_capped; 19 yds from the nearest OSM tee box); yardage: measured 93 vs card 412 (-319) |
| 3 | 5 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback_capped; 85 yds from the nearest OSM tee box); yardage: measured 296 vs card 586 (-290); aim: Driver +14 lands 278 yds out in rough (10 yds from fairway) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Long iron +7 | tee: tee marker not on an OSM tee box (walkback_capped; 92 yds from the nearest OSM tee box); yardage: measured 189 vs card 463 (-274); aim: Long iron +7 lands 204 yds out in rough (8 yds from fairway) |
| 6 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback_capped; 55 yds from the nearest OSM tee box); yardage: measured 370 vs card 397 (-27); aim: Driver -40 lands 303 yds out in rough (23 yds from fairway) |
| 7 | 5 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (walkback_capped; 142 yds from the nearest OSM tee box); yardage: measured 384 vs card 564 (-180); aim: Driver +5 lands 272 yds out in rough (13 yds from fairway) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; 13 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Mid iron +40 | tee: tee marker not on an OSM tee box (walkback_capped; 17 yds from the nearest OSM tee box); yardage: measured 99 vs card 320 (-221); aim: Mid iron +40 lands 197 yds out in rough (8 yds from fairway) |
| 10 | 5 | CHECK | Driver +30 | aim: Driver +30 lands 308 yds out in rough (32 yds from fairway) |
| 11 | 4 | PASS | Driver +14 |  |
| 12 | 4 | PASS | Driver +29 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +6 |  |
| 15 | 5 | PASS | Driver +8 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | CHECK | Driver -15 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +7 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (walkback; 71 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | Mid iron +38 | tee: tee marker not on an OSM tee box (walkback_capped; 19 yds from the nearest OSM tee box); yardage: measured 93 vs card 402 (-309) |
| 3 | 5 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (walkback_capped; 85 yds from the nearest OSM tee box); yardage: measured 296 vs card 535 (-239); aim: Driver +14 lands 278 yds out in rough (10 yds from fairway) |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Long iron +7 | tee: tee marker not on an OSM tee box (walkback_capped; 92 yds from the nearest OSM tee box); yardage: measured 189 vs card 428 (-239); aim: Long iron +7 lands 204 yds out in rough (8 yds from fairway) |
| 6 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback_capped; 55 yds from the nearest OSM tee box); aim: Driver -40 lands 303 yds out in rough (23 yds from fairway) |
| 7 | 5 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (walkback_capped; 142 yds from the nearest OSM tee box); yardage: measured 384 vs card 545 (-161); aim: Driver +5 lands 272 yds out in rough (13 yds from fairway) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; 13 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Mid iron +40 | tee: tee marker not on an OSM tee box (walkback_capped; 17 yds from the nearest OSM tee box); yardage: measured 99 vs card 299 (-200); aim: Mid iron +40 lands 197 yds out in rough (8 yds from fairway) |
| 10 | 5 | PASS | Driver +34 |  |
| 11 | 4 | PASS | Driver -12 |  |
| 12 | 4 | PASS | Driver +36 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +6 |  |
| 15 | 5 | PASS | Driver +29 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -32 |  |
| 18 | 4 | PASS | Driver +7 |  |

