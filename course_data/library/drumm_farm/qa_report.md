# Drumm Farm Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 7, 8, 13

* page: `course_data/library/drumm_farm/page.html` (2.2 MB); request `course_data/requests/course_page_drumm_farm.json`; built 2026-11-01T21:47Z
* course: Drumm Farm Golf Club (Independence, MO), OSM way/316101757; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Tour, Championship (the two longest sets on the card (combination sets skipped)); page sets: Tour, Championship
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Tour tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -2 |  |
| 2 | 4 | PASS | Driver +2 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +4 |  |
| 5 | 4 | PASS | Driver +7 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (review; 5 yds from the nearest OSM tee box) |
| 8 | 4 | CHECK | 2-wood -24 | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box) |
| 9 | 5 | PASS | Driver -2 |  |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | Driver +27 |  |
| 12 | 4 | PASS | Driver -0 |  |
| 13 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (walkback; 27 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -10 |  |
| 16 | 4 | PASS | 4-wood -2 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +4 |  |

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +0 |  |
| 2 | 4 | PASS | Driver +20 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -16 |  |
| 5 | 4 | PASS | Driver +3 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver -12 | aim: Driver -12 lands 306 yds out in rough (8 yds from fairway) |
| 8 | 4 | PASS | 4-wood -32 |  |
| 9 | 5 | PASS | Driver -1 |  |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | 2-wood +40 (tie) |  |
| 12 | 4 | PASS | Driver +2 |  |
| 13 | 4 | PASS | Driver +12 (tie) |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -4 |  |
| 16 | 4 | PASS | Driver +3 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +4 |  |

