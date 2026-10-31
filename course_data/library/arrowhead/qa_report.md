# Arrowhead Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 4, 5, 12, 14, 16, 18

* page: `course_data/library/arrowhead/page.html` (5.4 MB); request `course_data/requests/course_page_arrowhead.json`; built 2026-10-30T21:55Z
* course: Arrowhead Golf Club (Littleton, CO), OSM way/296786618; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black Bear, Arrowhead (the two longest sets on the card (combination sets skipped)); page sets: Black Bear, Arrowhead
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-25; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 8 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black Bear tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +0 | tee: tee marker not on an OSM tee box (walkback; 161 yds from the nearest OSM tee box) |
| 2 | 5 | PASS | Driver -5 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 229 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | 4-wood +2 (tie) | tee: tee marker not on an OSM tee box (walkback; 193 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver +28 | aim: Driver +28 lands 297 yds out in rough (17 yds from fairway) |
| 6 | 4 | PASS | Driver -8 |  |
| 7 | 4 | PASS | Long iron -2 (tie) |  |
| 8 | 4 | PASS | Driver +5 (tie) |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver +2 (tie) |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +16 |  |
| 15 | 4 | PASS | Driver -12 |  |
| 16 | 5 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (lidar_pad; 55 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver -3 | aim: Driver -3 lands 275 yds out in rough (9 yds from fairway) |

## Arrowhead tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +0 | tee: tee marker not on an OSM tee box (texture_pad; 179 yds from the nearest OSM tee box) |
| 2 | 5 | PASS | Driver -4 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 228 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | 4-wood +6 | tee: tee marker not on an OSM tee box (walkback; 180 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver +31 | aim: Driver +31 lands 293 yds out in rough (14 yds from fairway) |
| 6 | 4 | PASS | Driver -4 |  |
| 7 | 4 | PASS | Long iron +0 |  |
| 8 | 4 | PASS | 4-wood +0 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood -4 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver +21 | aim: Driver +21 lands 302 yds out in sand (8 yds from fairway) |
| 15 | 4 | PASS | Driver -2 |  |
| 16 | 5 | PASS | Driver +6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | 4-wood -2 |  |

