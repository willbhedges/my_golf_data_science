# Memorial Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 4, 9, 13, 16, 17

* page: `course_data/library/memorial_park/page.html` (2.5 MB); request `course_data/requests/course_page_memorial_park.json`; built 2026-11-01T22:33Z
* course: Memorial Park Golf Course (Houston, TX), OSM relation/13729803; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [65, 75, 85] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-11-18; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['5 hole(s) where a longer set is shorter than the next set: 8 Blue 510 < White 554, 9 Blue 202 < White 378, 13 Blue 406 < White 480, 18 Blue 393 < White 410'])
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -8 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 35 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver +6 |  |
| 5 | 4 | PASS | Driver +1 |  |
| 6 | 4 | PASS | Driver -6 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +18 |  |
| 9 | 4 | PASS | Long iron -8 |  |
| 10 | 4 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +2 |  |
| 13 | 5 | PASS | 4-wood +2 (tie) |  |
| 14 | 4 | PASS | Driver -38 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | CHECK | Driver -0 | tee: tee marker not on an OSM tee box (texture_pad; 37 yds from the nearest OSM tee box) |
| 17 | 4 | PASS | 4-wood -8 (tie) |  |
| 18 | 4 | PASS | Driver +10 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -10 |  |
| 2 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box); yardage: measured 110 vs card 123 (-13) |
| 3 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (texture_pad; 86 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | Driver -24 | yardage: measured 364 vs card 376 (-12) |
| 5 | 4 | PASS | 4-wood -16 (tie) |  |
| 6 | 4 | PASS | Driver -16 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +16 |  |
| 9 | 4 | CHECK | Long iron -14 | tee: tee marker not on an OSM tee box (walkback_capped; 24 yds from the nearest OSM tee box); yardage: measured 227 vs card 378 (-151) |
| 10 | 4 | PASS | Driver +9 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +17 |  |
| 13 | 5 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | Driver +2 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | CHECK | Driver +7 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 17 | 4 | CHECK | Driver +0 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +7 |  |

