# Drumm Farm Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 5, 8, 13

* page: `course_data/library/drumm_farm/page.html` (2.2 MB); request `course_data/requests/course_page_drumm_farm.json`; built 2026-11-02T19:52Z
* course: Drumm Farm Golf Club (Independence, MO), OSM way/316101757; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Tour, Championship (the two longest sets on the card (combination sets skipped)); page sets: Tour, Championship
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Tour tees, library check cards): holes 11, 2 (2 asked of 14 framed holes)

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Tour tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -2 |  |
| 2 | 4 | PASS | Driver +2 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -2 |  |
| 5 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -4 |  |
| 8 | 4 | CHECK | 2-wood -14 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box) |
| 9 | 5 | PASS | Driver -2 |  |
| 10 | 4 | PASS | Driver -0 |  |
| 11 | 4 | PASS | Driver +26 |  |
| 12 | 4 | PASS | Driver -11 |  |
| 13 | 4 | CHECK | 4-wood +3 | tee: tee marker not on an OSM tee box (walkback; 27 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -18 |  |
| 16 | 4 | PASS | 4-wood -3 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +5 |  |

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +0 |  |
| 2 | 4 | PASS | Driver +18 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -18 |  |
| 5 | 4 | PASS | Driver +3 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | 4-wood -4 (tie) |  |
| 8 | 4 | PASS | Driver -60 |  |
| 9 | 5 | PASS | Driver -1 |  |
| 10 | 4 | PASS | Driver +2 |  |
| 11 | 4 | PASS | 2-wood +40 (tie) |  |
| 12 | 4 | PASS | Driver -6 |  |
| 13 | 4 | PASS | 4-wood +4 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -16 |  |
| 16 | 4 | PASS | Driver +2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +4 |  |

