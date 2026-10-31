# Triggs Memorial Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 5, 15, 18

* page: `course_data/library/triggs_memorial/page.html` (5.2 MB); request `course_data/requests/course_page_triggs_memorial.json`; built 2026-10-31T03:54Z
* course: Triggs Memorial Golf Course (Providence, RI), OSM way/43150786; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-01; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 5 White (L) 316 < Gold 322'])
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +14 (tie) |  |
| 2 | 4 | PASS | Driver -10 |  |
| 3 | 4 | PASS | Driver +2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +40 |  |
| 6 | 5 | PASS | Driver +32 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -2 (tie) |  |
| 9 | 4 | PASS | Driver +1 |  |
| 10 | 5 | PASS | Driver -2 |  |
| 11 | 4 | PASS | Driver +2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -28 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +23 |  |
| 16 | 4 | PASS | Driver -40 |  |
| 17 | 4 | PASS | Driver -13 |  |
| 18 | 4 | PASS | Driver -9 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +12 |  |
| 2 | 4 | PASS | Driver -10 |  |
| 3 | 4 | PASS | Driver +0 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver +40 | aim: Driver +40 lands 308 yds out in sand (7 yds from fairway) |
| 6 | 5 | PASS | Driver +26 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -3 (tie) |  |
| 9 | 4 | PASS | Driver -1 |  |
| 10 | 5 | PASS | Driver -1 |  |
| 11 | 4 | PASS | 4-wood +1 (tie) |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -26 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | CHECK | Driver +9 | yardage: measured 457 vs card 496 (-39) |
| 16 | 4 | PASS | 2-wood -40 (tie) |  |
| 17 | 4 | PASS | Driver -16 |  |
| 18 | 4 | CHECK | Driver -9 (tie) | yardage: measured 379 vs card 399 (-20) |

