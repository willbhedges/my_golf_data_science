# Bulle Rock Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 4, 16, 17, 18

* page: `course_data/library/bulle_rock/page.html` (4.1 MB); request `course_data/requests/course_page_bulle_rock.json`; built 2026-10-31T01:46Z
* course: Bulle Rock Golf Club (Havre de Grace, MD), OSM way/70804218; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-27; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -21 |  |
| 2 | 5 | PASS | Driver +3 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 37 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Driver +8 |  |
| 6 | 4 | PASS | Driver +16 (tie) |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver -17 |  |
| 9 | 4 | PASS | Driver +2 |  |
| 10 | 4 | PASS | Driver -21 |  |
| 11 | 5 | PASS | Driver -6 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -2 |  |
| 14 | 4 | PASS | Driver +28 (tie) |  |
| 15 | 5 | PASS | Driver -5 |  |
| 16 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (lidar_pad; 42 yds from the nearest OSM tee box) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 24 yds from the nearest OSM tee box) |
| 18 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box) |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -28 |  |
| 2 | 5 | PASS | Driver +3 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver -6 |  |
| 5 | 4 | PASS | Driver -7 |  |
| 6 | 4 | PASS | 4-wood +10 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver -16 |  |
| 9 | 4 | PASS | Driver +40 |  |
| 10 | 4 | PASS | Driver -40 |  |
| 11 | 5 | PASS | Driver -20 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 4 | PASS | Driver +35 |  |
| 15 | 5 | PASS | Driver +0 |  |
| 16 | 4 | PASS | Driver +28 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -14 |  |

