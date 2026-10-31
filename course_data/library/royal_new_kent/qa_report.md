# Royal New Kent Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 5, 9, 10

* page: `course_data/library/royal_new_kent/page.html` (2.9 MB); request `course_data/requests/course_page_royal_new_kent.json`; built 2026-10-31T04:54Z
* course: Royal New Kent Golf Club (Providence Forge, VA), OSM relation/6209148; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Invicta, Gold (the two longest sets on the card (combination sets skipped)); page sets: Invicta, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-08-26,2018-08-27; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Invicta tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -36 | tee: tee marker not on an OSM tee box (walkback; 18 yds from the nearest OSM tee box) |
| 2 | 5 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 275 yds out in rough (26 yds from fairway) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +4 |  |
| 5 | 5 | CHECK | Driver +22 | aim: Driver +22 lands 302 yds out in rough (14 yds from fairway) |
| 6 | 4 | PASS | Driver +10 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 2-wood +12 |  |
| 9 | 4 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 10 | 5 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 34 yds from the nearest OSM tee box); yardage: measured 560 vs card 584 (-24) |
| 11 | 4 | PASS | Driver -8 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +16 |  |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -16 |  |
| 17 | 5 | PASS | Driver -22 |  |
| 18 | 4 | PASS | Driver +2 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 2-wood -40 |  |
| 2 | 5 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 271 yds out in rough (31 yds from fairway) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +8 |  |
| 5 | 5 | CHECK | Driver +20 (tie) | aim: Driver +20 lands 300 yds out in rough (13 yds from fairway) |
| 6 | 4 | PASS | Driver +0 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 2-wood +22 (tie) |  |
| 9 | 4 | PASS | Driver +12 |  |
| 10 | 5 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 32 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver +2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +23 |  |
| 14 | 4 | PASS | Driver -8 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver -20 |  |
| 17 | 5 | PASS | Driver -16 |  |
| 18 | 4 | PASS | 4-wood +7 (tie) |  |

