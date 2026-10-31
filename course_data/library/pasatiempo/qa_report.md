# Pasatiempo Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 10, 14

* page: `course_data/library/pasatiempo/page.html` (2.7 MB); request `course_data/requests/course_page_pasatiempo.json`; built 2026-10-30T22:08Z
* course: Pasatiempo Golf Course (Santa Cruz, CA), OSM relation/13921737; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Middle, Forward (the two longest sets on the card (combination sets skipped)); page sets: Middle, Forward
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-05-27; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['9 hole(s) where a longer set is shorter than the next set: 1 Middle 440 < Forward 457, 2 Forward 376 < White/Green Combo 384, 4 Forward 343 < White/Green Combo 359, 5 Forward 156 < White/Green Combo 170'])
* pars sum to 70, card 72
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Middle tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -0 | yardage: measured 428 vs card 440 (-12) |
| 2 | 4 | PASS | 4-wood -10 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver +0 |  |
| 7 | 4 | PASS | Driver -10 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +12 |  |
| 10 | 4 | PASS | 4-wood +8 |  |
| 11 | 4 | PASS | Long iron +4 |  |
| 12 | 4 | PASS | 4-wood -14 |  |
| 13 | 5 | PASS | Driver -1 |  |
| 14 | 4 | CHECK | 4-wood +4 | tee: tee marker not on an OSM tee box (walkback; 34 yds from the nearest OSM tee box) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Long iron +3 |  |
| 17 | 4 | PASS | 4-wood +8 |  |
| 18 | 3 | PASS |  |  |

## Forward tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +1 | par: par 4 vs card 5 |
| 2 | 4 | PASS | 4-wood -6 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +10 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver -2 |  |
| 7 | 4 | PASS | Driver -11 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | 4-wood +8 |  |
| 10 | 4 | CHECK | 4-wood +8 | par: par 4 vs card 5 |
| 11 | 4 | PASS | Driver -40 |  |
| 12 | 4 | PASS | 4-wood -14 |  |
| 13 | 5 | PASS | Driver -10 |  |
| 14 | 4 | PASS | Driver -10 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Long iron +0 |  |
| 17 | 4 | PASS | Long iron +6 (tie) |  |
| 18 | 3 | PASS |  |  |

