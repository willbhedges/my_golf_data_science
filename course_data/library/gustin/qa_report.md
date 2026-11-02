# A. L. Gustin Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 3, 4, 7, 11, 14, 16

* page: `course_data/library/gustin/page.html` (2.6 MB); request `course_data/requests/course_page_gustin.json`; built 2026-11-02T16:46Z
* course: A. L. Gustin Golf Course (Columbia, MO), OSM way/449108205; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-07-08; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 9, 1, 3, 12 (4 asked of 14 framed holes)

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +4 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +20 |  |
| 4 | 4 | CHECK | 4-wood +4 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -40 |  |
| 7 | 4 | CHECK | 4-wood -5 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 36 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | 4-wood -2 |  |
| 9 | 4 | PASS | Driver +2 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | CHECK | 4-wood +3 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 11 yds from the nearest OSM tee box) |
| 12 | 5 | PASS | Driver +7 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (lidar_pad; 183 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood -14 |  |
| 16 | 4 | CHECK | 2-wood +59 | aim: 2-wood +59 lands 304 yds out in sand (5 yds from fairway) |
| 17 | 4 | PASS | Driver +22 |  |
| 18 | 4 | PASS | 4-wood +0 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +10 (tie) |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | 2-wood +52 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 6 yds from the nearest OSM tee box) |
| 4 | 4 | PASS | 4-wood +6 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -60 |  |
| 7 | 4 | PASS | 2-wood -40 |  |
| 8 | 4 | PASS | 4-wood +8 |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | PASS | 4-wood +2 |  |
| 12 | 5 | PASS | Driver +12 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (lidar_pad; 150 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | 4-wood +22 |  |
| 16 | 4 | PASS | Long iron +12 |  |
| 17 | 4 | PASS | Driver +26 |  |
| 18 | 4 | PASS | 4-wood +0 |  |

