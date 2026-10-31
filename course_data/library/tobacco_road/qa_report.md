# Tobacco Road Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 5, 6, 9, 10, 11, 12, 13, 16, 17, 18

* page: `course_data/library/tobacco_road/page.html` (2.7 MB); request `course_data/requests/course_page_tobacco_road.json`; built 2026-10-31T03:46Z
* course: Tobacco Road Golf Club (Sanford, NC), OSM way/430227508; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Ripper, Disc (the two longest sets on the card (combination sets skipped)); page sets: Ripper, Disc
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-09-02; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 13 Points (L) 455 < Cultivator (L) 476'])
* 11 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Ripper tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +16 | tee: tee marker not on an OSM tee box (walkback; 110 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +3 (tie) |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -10 |  |
| 5 | 4 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box); aim: Driver -40 lands 275 yds out in rough (6 yds from fairway) |
| 6 | 3 | CHECK |  | yardage: measured 137 vs card 148 (-11) |
| 7 | 4 | PASS | Driver +1 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (walkback; 25 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -33 | tee: tee marker not on an OSM tee box (lidar_pad; 74 yds from the nearest OSM tee box) |
| 11 | 5 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | 2-wood -14 (tie) | tee: tee marker not on an OSM tee box (walkback; 41 yds from the nearest OSM tee box) |
| 13 | 5 | CHECK | Driver -26 | tee: tee marker not on an OSM tee box (walkback; 37 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | 2-wood +31 (tie) |  |
| 16 | 4 | CHECK | 2-wood -40 (tie) | tee: tee marker not on an OSM tee box (walkback; 51 yds from the nearest OSM tee box); aim: 2-wood -40 lands 266 yds out in sand (2 yds from fairway) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |

## Disc tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 103 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver +3 (tie) |  |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -12 |  |
| 5 | 4 | CHECK | Driver -40 | aim: Driver -40 lands 275 yds out in rough (9 yds from fairway) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +1 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | 4-wood +5 | yardage: measured 401 vs card 415 (-14) |
| 10 | 4 | CHECK | Driver -35 | tee: tee marker not on an OSM tee box (lidar_pad; 54 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | 4-wood +10 (tie) |  |
| 12 | 4 | CHECK | 4-wood -12 (tie) | tee: tee marker not on an OSM tee box (walkback; 34 yds from the nearest OSM tee box) |
| 13 | 5 | PASS | Driver -8 (tie) |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | 2-wood +31 (tie) |  |
| 16 | 4 | CHECK | 4-wood -40 (tie) | tee: tee marker not on an OSM tee box (walkback; 46 yds from the nearest OSM tee box) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +0 |  |

