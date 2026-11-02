# Pevely Farms Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 11, 16, 18

* page: `course_data/library/pevely_farms/page.html` (2.6 MB); request `course_data/requests/course_page_pevely_farms.json`; built 2026-11-01T21:04Z
* course: Pevely Farms Golf Course (Saint Louis, MO), OSM relation/5429230; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [50, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-18; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 |  |
| 2 | 5 | PASS | Driver -8 |  |
| 3 | 4 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | Driver -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood +5 |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +2 |  |
| 10 | 4 | PASS | Driver +16 (tie) |  |
| 11 | 4 | CHECK | Driver -6 (tie) | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 12 | 5 | PASS | Driver -1 |  |
| 13 | 4 | PASS | 4-wood -10 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +2 |  |
| 16 | 4 | CHECK | 2-wood +40 | aim: 2-wood +40 lands 297 yds out in rough (22 yds from fairway) |
| 17 | 4 | PASS | Driver -28 |  |
| 18 | 4 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +2 |  |
| 2 | 5 | PASS | Driver -6 |  |
| 3 | 4 | CHECK | 4-wood +8 | aim: 4-wood +8 lands 270 yds out in rough (7 yds from fairway) |
| 4 | 4 | PASS | Driver -6 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Long iron +1 |  |
| 7 | 4 | PASS | 4-wood +6 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +2 |  |
| 10 | 4 | PASS | Driver +27 |  |
| 11 | 4 | PASS | Driver -16 (tie) |  |
| 12 | 5 | PASS | Driver -8 |  |
| 13 | 4 | PASS | Long iron +3 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver +1 |  |
| 16 | 4 | CHECK | 2-wood +40 (tie) | aim: 2-wood +40 lands 297 yds out in rough (23 yds from fairway) |
| 17 | 4 | PASS | Driver -30 |  |
| 18 | 4 | PASS | Driver -37 |  |

