# The Harvester Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 3, 6, 7, 8, 12, 13, 14, 16, 18

* page: `course_data/library/harvester/page.html` (4.8 MB); request `course_data/requests/course_page_harvester.json`; built 2026-10-30T11:51Z
* course: The Harvester Golf Club (Rhodes, IA), OSM way/325314320; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +1 (tie) |  |
| 2 | 4 | PASS | 4-wood +2 (tie) |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 50 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver +3 |  |
| 5 | 4 | PASS | 2-wood +1 (tie) |  |
| 6 | 5 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (walkback; 16 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver +2 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 2-wood -14 |  |
| 10 | 4 | PASS | Driver +10 |  |
| 11 | 4 | PASS | Driver -18 |  |
| 12 | 4 | CHECK | Driver +17 (tie) | aim: Driver +17 lands 293 yds out in sand (3 yds from fairway) |
| 13 | 4 | CHECK | Driver +0 | yardage: measured 409 vs card 390 (+19) |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 51 yds from the nearest OSM tee box) |
| 15 | 5 | PASS | Driver +9 |  |
| 16 | 4 | CHECK | Driver -4 | yardage: measured 497 vs card 480 (+17) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | 4-wood -12 | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 |  |
| 2 | 4 | PASS | Driver +40 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; 36 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver -3 |  |
| 5 | 4 | PASS | Driver -8 |  |
| 6 | 5 | PASS | Driver -6 |  |
| 7 | 4 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (texture_pad; 22 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | 4-wood +1 |  |
| 10 | 4 | PASS | Driver +8 |  |
| 11 | 4 | PASS | Driver -18 |  |
| 12 | 4 | CHECK | Driver +14 | yardage: measured 404 vs card 390 (+14) |
| 13 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback; 16 yds from the nearest OSM tee box) |
| 14 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 26 yds from the nearest OSM tee box) |
| 15 | 5 | PASS | Driver +6 |  |
| 16 | 4 | PASS | Driver -13 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | 4-wood -13 |  |

