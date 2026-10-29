# Veenker Memorial Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 5, 7, 8, 10, 12, 15, 16, 18

* page: `course_data/library/gate/gate_veenker/page.html` (5.1 MB); request `course_data/requests/course_page_gate_veenker.json`; built 2026-10-29T21:10Z
* course: Veenker Memorial Golf Course (Ames, IA), OSM way/44804299; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, Gold (tee sets of interest + the longest other set (Gold)); page sets: Blue, Gold
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -9 |  |
| 2 | 4 | PASS | 4-wood +5 |  |
| 3 | 4 | CHECK | Driver +35 | yardage: measured 314 vs card 333 (-19); aim: Driver +35 lands 310 yds out in rough (22 yds from fairway); oval: landing pattern 41% trees / water / OB (recovery 41%, unverified 0%) |
| 4 | 4 | PASS | 4-wood -8 |  |
| 5 | 4 | CHECK | 4-wood +18 | aim: 4-wood +18 lands 280 yds out in rough (36 yds from fairway) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +3 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 14 yds from the nearest OSM tee box) |
| 9 | 5 | PASS | Driver +16 |  |
| 10 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 11 | 3 | PASS |  |  |
| 12 | 4 | CHECK | Driver +38 | yardage: measured 317 vs card 330 (-13); aim: Driver +38 lands 295 yds out in sand (6 yds from fairway) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +34 |  |
| 15 | 4 | CHECK | 4-wood +4 | aim: 4-wood +4 lands 273 yds out in rough (14 yds from fairway) |
| 16 | 5 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (lidar_pad; 76 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +6 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -12 |  |
| 2 | 4 | PASS | Driver -7 |  |
| 3 | 4 | CHECK | 2-wood +30 (tie) | tee: tee marker not on an OSM tee box (walkback; 12 yds from the nearest OSM tee box); aim: 2-wood +30 lands 281 yds out in rough (12 yds from fairway) |
| 4 | 4 | PASS | 4-wood -4 |  |
| 5 | 4 | CHECK | Long iron +14 | aim: Long iron +14 lands 231 yds out in rough (36 yds from fairway) |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver +0 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +36 |  |
| 10 | 5 | PASS | Driver +4 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +40 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver +30 |  |
| 15 | 4 | CHECK | 4-wood +40 | aim: 4-wood +40 lands 270 yds out in rough (11 yds from fairway) |
| 16 | 5 | PASS | Driver -6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |

