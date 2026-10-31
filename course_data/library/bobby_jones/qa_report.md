# Bobby Jones Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 3, 4, 5, 6, 7, 8, 9

* page: `course_data/library/bobby_jones/page.html` (1.2 MB); request `course_data/requests/course_page_bobby_jones.json`; built 2026-10-30T22:17Z
* course: Bobby Jones Golf Club (Atlanta, GA), OSM way/29354026; holes: osm (tier unmapped_card); card: allsquare (allsquare)
* solved tee sets: 8, 7 (the two longest sets on the card (combination sets skipped)); page sets: 8, 7
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-09-10; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## 8 tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 2 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; OSM maps no tee boxes on this course) |
| 3 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 4 | 4 | CHECK | Driver +36 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 5 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 6 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 8 | 4 | CHECK | Driver -28 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 9 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |

## 7 tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -38 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 2 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (texture_pad; OSM maps no tee boxes on this course) |
| 3 | 4 | CHECK | Driver -2 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 4 | 4 | CHECK | Driver +36 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 5 | 5 | CHECK | Driver -40 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 6 | 4 | CHECK | Driver +26 | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; OSM maps no tee boxes on this course) |
| 8 | 4 | CHECK | Driver +40 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |
| 9 | 4 | CHECK | Driver +31 | tee: tee marker not on an OSM tee box (walkback; OSM maps no tee boxes on this course) |

