# Richter Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 9, 10

* page: `course_data/library/richter_park/page.html` (5.4 MB); request `course_data/requests/course_page_richter_park.json`; built 2026-10-30T22:05Z
* course: Richter Park Golf Course (Danbury, CT), OSM way/43434973; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-05; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 10 White (L) 160 < Gold 338'])
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 2-wood +32 |  |
| 2 | 5 | PASS | Driver -13 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 26 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (lidar_pad; 48 yds from the nearest OSM tee box); aim: Driver -5 lands 294 yds out in rough (7 yds from fairway) |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -4 |  |
| 7 | 5 | PASS | Driver +8 |  |
| 8 | 4 | PASS | 4-wood -1 (tie) |  |
| 9 | 4 | CHECK | Driver +4 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 10 | 4 | CHECK | Driver -30 | tee: tee marker not on an OSM tee box (walkback_capped; 26 yds from the nearest OSM tee box); yardage: measured 347 vs card 382 (-35) |
| 11 | 4 | PASS | 4-wood +4 |  |
| 12 | 5 | PASS | Driver +2 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +5 |  |
| 15 | 4 | PASS | Long iron +2 |  |
| 16 | 5 | PASS | 4-wood -2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +36 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +40 |  |
| 2 | 5 | PASS | Driver -10 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood -4 (tie) |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Long iron +8 |  |
| 7 | 5 | PASS | Driver +6 |  |
| 8 | 4 | PASS | 4-wood -2 |  |
| 9 | 4 | PASS | Driver +6 |  |
| 10 | 4 | CHECK | Mid iron +4 | aim: Mid iron +4 lands 185 yds out in rough (7 yds from fairway) |
| 11 | 4 | PASS | 4-wood +2 |  |
| 12 | 5 | PASS | Driver +10 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +0 |  |
| 15 | 4 | PASS | Long iron +0 |  |
| 16 | 5 | PASS | 4-wood -4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +40 |  |

