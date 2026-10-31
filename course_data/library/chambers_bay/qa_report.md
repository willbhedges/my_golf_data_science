# Chambers Bay Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 8, 11, 12, 13, 14, 17

* page: `course_data/library/chambers_bay/page.html` (2.4 MB); request `course_data/requests/course_page_chambers_bay.json`; built 2026-10-31T05:23Z
* course: Chambers Bay Golf Course (University Place, WA), OSM way/26787026; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Navy, Sand (the two longest sets on the card (combination sets skipped)); page sets: Navy, Sand
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 8 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Navy tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +21 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | 4-wood -3 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 29 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver +16 |  |
| 5 | 4 | PASS | Driver +6 |  |
| 6 | 4 | PASS | 2-wood +14 (tie) |  |
| 7 | 4 | PASS | Driver +26 |  |
| 8 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (texture_pad; 8 yds from the nearest OSM tee box) |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood -8 |  |
| 11 | 4 | CHECK | Driver -22 | tee: tee marker not on an OSM tee box (lidar_pad; 43 yds from the nearest OSM tee box) |
| 12 | 4 | PASS | Driver +8 |  |
| 13 | 4 | PASS | Driver +4 |  |
| 14 | 4 | PASS | Driver -22 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | 4-wood +5 (tie) |  |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box); yardage: measured 159 vs card 172 (-13) |
| 18 | 5 | PASS | 4-wood +6 (tie) |  |

## Sand tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver +21 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box); par: par 5 vs card 4 |
| 2 | 4 | PASS | 4-wood -28 |  |
| 3 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 4 | 5 | PASS | Driver +20 |  |
| 5 | 4 | PASS | Driver -2 |  |
| 6 | 4 | PASS | 2-wood +14 (tie) |  |
| 7 | 4 | PASS | Driver +40 |  |
| 8 | 5 | PASS | Driver -5 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 4-wood -12 |  |
| 11 | 4 | CHECK | 2-wood -15 (tie) | tee: tee marker not on an OSM tee box (walkback; 66 yds from the nearest OSM tee box) |
| 12 | 4 | CHECK | 4-wood +1 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 28 yds from the nearest OSM tee box) |
| 13 | 4 | CHECK | Driver +6 | par: par 4 vs card 5 |
| 14 | 4 | CHECK | Driver -24 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +24 |  |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box); yardage: measured 159 vs card 172 (-13) |
| 18 | 5 | PASS | Driver +12 |  |

