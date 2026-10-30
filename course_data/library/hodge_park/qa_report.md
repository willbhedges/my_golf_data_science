# Hodge Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18

* page: `course_data/library/hodge_park/page.html` (2.3 MB); request `course_data/requests/course_page_hodge_park.json`; built 2026-10-30T00:17Z
* course: Hodge Park Golf Course (Kansas City, MO), OSM way/195221873; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 17 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -0 | yardage: measured 414 vs card 425 (-11) |
| 2 | 4 | CHECK | Driver +21 | yardage: measured 332 vs card 347 (-15) |
| 3 | 3 | CHECK |  | yardage: measured 156 vs card 168 (-12) |
| 4 | 5 | CHECK | Driver -6 | yardage: measured 438 vs card 452 (-14) |
| 5 | 4 | PASS | Driver -10 |  |
| 6 | 4 | CHECK | 4-wood +13 | yardage: measured 278 vs card 304 (-26) |
| 7 | 3 | CHECK |  | yardage: measured 163 vs card 174 (-11) |
| 8 | 4 | CHECK | Driver -38 | yardage: measured 393 vs card 409 (-16) |
| 9 | 4 | PASS | Driver +40 (tie) |  |
| 10 | 4 | CHECK | 2-wood -40 | yardage: measured 375 vs card 405 (-30) |
| 11 | 5 | PASS | Driver +12 |  |
| 12 | 3 | CHECK |  | yardage: measured 164 vs card 193 (-29) |
| 13 | 4 | CHECK | Driver +9 | yardage: measured 369 vs card 388 (-19) |
| 14 | 4 | PASS | 4-wood -2 |  |
| 15 | 4 | CHECK | Driver +40 | yardage: measured 325 vs card 338 (-13) |
| 16 | 3 | CHECK |  | yardage: measured 177 vs card 192 (-15) |
| 17 | 5 | PASS | Driver +7 |  |
| 18 | 4 | CHECK | 4-wood +40 (tie) | aim: 4-wood +40 lands 281 yds out in rough (13 yds from fairway) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -2 | yardage: measured 340 vs card 380 (-40) |
| 2 | 4 | PASS | Driver +24 |  |
| 3 | 3 | CHECK |  | yardage: measured 124 vs card 148 (-24) |
| 4 | 5 | PASS | 4-wood +4 |  |
| 5 | 4 | CHECK | Driver -6 | yardage: measured 418 vs card 432 (-14) |
| 6 | 4 | PASS | 4-wood +12 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | 2-wood -40 (tie) | yardage: measured 359 vs card 388 (-29) |
| 9 | 4 | PASS | Driver +40 |  |
| 10 | 4 | CHECK | 4-wood -40 | yardage: measured 331 vs card 371 (-40); aim: 4-wood -40 lands 265 yds out in rough (8 yds from fairway) |
| 11 | 5 | CHECK | Driver +9 | yardage: measured 431 vs card 445 (-14) |
| 12 | 3 | CHECK |  | yardage: measured 147 vs card 172 (-25) |
| 13 | 4 | CHECK | Driver +16 | yardage: measured 347 vs card 376 (-29) |
| 14 | 4 | CHECK | 4-wood -4 (tie) | aim: 4-wood -4 lands 267 yds out in rough (13 yds from fairway) |
| 15 | 4 | PASS | 4-wood +40 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | CHECK | Driver -40 | yardage: measured 598 vs card 485 (+113) |
| 18 | 4 | CHECK | 4-wood +40 | yardage: measured 289 vs card 277 (+12); aim: 4-wood +40 lands 281 yds out in rough (19 yds from fairway) |

