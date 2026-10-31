# Circling Raven Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 4, 5, 8, 9, 10, 12, 16

* page: `course_data/library/circling_raven/page.html` (3.1 MB); request `course_data/requests/course_page_circling_raven.json`; built 2026-10-30T21:58Z
* course: Circling Raven Golf Course (Worley, ID), OSM relation/13691362; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2013-08-27; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -15 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +40 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -4 |  |
| 5 | 5 | PASS | Driver +12 |  |
| 6 | 4 | PASS | Driver -6 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 9 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (tee_centroid; 20 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | 2-wood +40 (tie) |  |
| 11 | 4 | PASS | Driver +4 |  |
| 12 | 5 | CHECK | Driver +27 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +3 |  |
| 15 | 4 | PASS | Driver -8 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +1 |  |
| 18 | 4 | PASS | Driver -10 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -33 | tee: tee marker not on an OSM tee box (lidar_pad; 14 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | 4-wood +40 | tee: tee marker not on an OSM tee box (lidar_pad; 50 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (tee_axis; 22 yds from the nearest OSM tee box); yardage: measured 391 vs card 380 (+11) |
| 5 | 5 | CHECK | Driver +5 | tee: tee marker not on an OSM tee box (lidar_pad; 16 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver -12 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -1 |  |
| 9 | 4 | PASS | Driver +4 |  |
| 10 | 4 | CHECK | 4-wood +40 | tee: tee marker not on an OSM tee box (lidar_pad; 8 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver -6 |  |
| 12 | 5 | CHECK | Driver +18 | yardage: measured 548 vs card 535 (+13) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -5 |  |
| 15 | 4 | PASS | 4-wood -6 |  |
| 16 | 3 | CHECK |  | yardage: measured 162 vs card 176 (-14) |
| 17 | 5 | PASS | Driver -6 |  |
| 18 | 4 | PASS | 4-wood -8 (tie) |  |

