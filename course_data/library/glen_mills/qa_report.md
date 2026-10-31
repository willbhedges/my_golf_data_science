# The Golf Course at Glen Mills: automatic page QA

**Status: needs confirm** — confirm holes 4, 9, 10, 12, 16

* page: `course_data/library/glen_mills/page.html` (2.5 MB); request `course_data/requests/course_page_glen_mills.json`; built 2026-10-31T03:49Z
* course: The Golf Course at Glen Mills (Thornbury Township, PA), OSM way/284570622; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-05-10,2022-05-17; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 15 holes built vs the card's 18
* pars sum to 59, card 71
* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +2 |  |
| 2 | 4 | PASS | Driver -10 |  |
| 3 | 4 | PASS | Driver -12 |  |
| 4 | 5 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box) |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver +10 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +16 |  |
| 9 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 64 yds from the nearest OSM tee box) |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 139 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood +2 (tie) |  |
| 12 | 4 | CHECK | Driver -9 | tee: tee marker not on an OSM tee box (lidar_pad; 7 yds from the nearest OSM tee box) |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver -13 |  |
| 18 | 4 | PASS | Driver +38 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 |  |
| 2 | 4 | PASS | Driver -18 |  |
| 3 | 4 | PASS | Driver -16 |  |
| 4 | 5 | CHECK | Driver -12 | aim: Driver -12 lands 307 yds out in rough (9 yds from fairway) |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver +16 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +16 |  |
| 9 | 4 | PASS | 4-wood +8 |  |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 133 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | 4-wood -12 (tie) |  |
| 12 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 8 yds from the nearest OSM tee box) |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 17 | 5 | PASS | Driver -14 |  |
| 18 | 4 | PASS | Driver +24 |  |

