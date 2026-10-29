# Coldwater Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 2, 7, 8, 12, 17

* page: `course_data/library/gate/gate_coldwater/page.html` (5.0 MB); request `course_data/requests/course_page_gate_coldwater.json`; built 2026-10-29T20:46Z
* course: Coldwater Golf Links (Ames, IA), OSM way/44807109; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, Black (tee sets of interest + the longest other set (Black)); page sets: Blue, Black
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +2 |  |
| 2 | 4 | CHECK | Driver +1 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 3 | 5 | PASS | Driver -10 |  |
| 4 | 4 | PASS | Driver -16 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +6 |  |
| 7 | 5 | PASS | Driver +3 |  |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | 4-wood -40 (tie) |  |
| 10 | 4 | PASS | Driver -6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -1 |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 5 | PASS | Driver +4 |  |
| 15 | 4 | PASS | Driver -2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | CHECK | 4-wood +12 (tie) | yardage: measured 379 vs card 395 (-16) |
| 18 | 4 | PASS | Driver -8 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 4 | PASS | Driver +0 |  |
| 3 | 5 | PASS | Driver +1 |  |
| 4 | 4 | PASS | Driver -4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | Driver +9 |  |
| 7 | 5 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (walkback; 11 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 13 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | 2-wood -40 |  |
| 10 | 4 | PASS | Driver -0 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | Driver -1 |  |
| 14 | 5 | PASS | Driver +4 |  |
| 15 | 4 | PASS | Driver +1 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +9 |  |
| 18 | 4 | PASS | Driver -8 |  |

