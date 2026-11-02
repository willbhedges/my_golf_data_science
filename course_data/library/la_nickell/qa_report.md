# L.A. Nickell Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 4, 5, 7, 9, 10, 12, 13, 17, 18

* page: `course_data/library/la_nickell/page.html` (2.5 MB); request `course_data/requests/course_page_la_nickell.json`; built 2026-11-02T19:33Z
* course: L.A. Nickell Golf Course (Columbia, MO), OSM way/387047950; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-20; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): holes 12, 7, 3 (3 asked of 14 framed holes)

Course-level reasons:

* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -1 |  |
| 2 | 4 | CHECK | 4-wood +6 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | Driver -2 |  |
| 4 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; 27 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | 2-wood -36 (tie) | yardage: measured 313 vs card 325 (-12) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +0 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -6 (tie) |  |
| 9 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (walkback; 38 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 13 | 4 | CHECK | Driver -7 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | 4-wood -6 |  |
| 16 | 4 | PASS | 2-wood +40 |  |
| 17 | 4 | CHECK | 2-wood -40 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 18 | 4 | CHECK | 4-wood +5 | tee: tee marker not on an OSM tee box (walkback; 46 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -6 | aim: 4-wood -6 lands 281 yds out in rough (15 yds from fairway) |
| 2 | 4 | PASS | Driver +9 |  |
| 3 | 4 | PASS | Driver -3 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 2-wood -38 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver +2 (tie) |  |
| 9 | 4 | CHECK | 4-wood +3 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -17 | aim: Driver -17 lands 320 yds out in rough (7 yds from fairway) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +6 |  |
| 13 | 4 | PASS | Driver -3 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -40 |  |
| 16 | 4 | PASS | 2-wood +48 (tie) |  |
| 17 | 4 | PASS | 4-wood -60 |  |
| 18 | 4 | PASS | 4-wood -0 |  |

