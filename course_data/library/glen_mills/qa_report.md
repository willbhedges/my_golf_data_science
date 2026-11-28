# The Golf Course at Glen Mills: automatic page QA

**Status: needs confirm** — confirm holes 4, 6, 10, 12

* page: `course_data/library/glen_mills/page.html` (3.3 MB); request `course_data/requests/course_page_glen_mills.json`; built 2026-11-28T04:25Z
* course: The Golf Course at Glen Mills (Thornbury Township, PA), OSM way/284570622; holes: osm (tier mapped_card); card: course_data/library/glen_mills/routed_card.json (file)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-12-05, 2026-12-06; grid temperatures [35, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-05-10,2022-05-17; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (0 asked of 13 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): 1 marked approximate (12)
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +5 |  |
| 2 | 4 | PASS | Driver -23 |  |
| 3 | 4 | PASS | 4-wood -0 |  |
| 4 | 5 | PASS | Driver -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 5 | CHECK | Driver -35 | tee: tee marker not on an OSM tee box (walkback; 19 yds from the nearest OSM tee box) |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +14 |  |
| 9 | 4 | PASS | Driver +1 |  |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 27 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Long iron +7 (tie) |  |
| 12 | 4 | CHECK | 4-wood +8 | yardage: measured 277 vs card 339 (-62) |
| 13 | 4 | PASS | Driver -23 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -40 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +2 |  |
| 18 | 4 | PASS | Driver -6 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +8 |  |
| 2 | 4 | PASS | Driver -22 |  |
| 3 | 4 | PASS | Driver -12 |  |
| 4 | 5 | CHECK | Driver -10 | aim: Driver -10 lands 308 yds out in rough (12 yds from fairway) |
| 5 | 3 | PASS |  |  |
| 6 | 5 | PASS | Driver -24 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +14 |  |
| 9 | 4 | PASS | 4-wood -1 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | PASS | Long iron +6 (tie) |  |
| 12 | 4 | PASS | Driver +28 |  |
| 13 | 4 | PASS | Driver -22 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -40 |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +1 |  |
| 18 | 4 | PASS | Driver -8 |  |

