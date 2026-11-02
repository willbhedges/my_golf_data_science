# Heritage Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 5, 7, 9, 18

* page: `course_data/library/heritage_park/page.html` (5.0 MB); request `course_data/requests/course_page_heritage_park.json`; built 2026-11-02T16:45Z
* course: Heritage Park Golf Course (Olathe, KS), OSM way/254360563; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-16; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +22 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +8 (tie) |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -32 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | CHECK | Driver -38 | tee: tee marker not on an OSM tee box (lidar_pad; 64 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver -8 |  |
| 9 | 5 | CHECK | Driver +31 | tee: tee marker not on an OSM tee box (lidar_pad; 65 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -32 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +18 |  |
| 13 | 4 | PASS | Driver -26 |  |
| 14 | 4 | PASS | Driver -22 |  |
| 15 | 5 | PASS | Driver -25 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +1 |  |
| 18 | 5 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (walkback; 38 yds from the nearest OSM tee box) |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Driver +11 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 2-wood -20 (tie) |  |
| 8 | 4 | PASS | Driver -8 |  |
| 9 | 5 | CHECK | Driver +32 | tee: tee marker not on an OSM tee box (walkback; 46 yds from the nearest OSM tee box) |
| 10 | 4 | PASS | Driver -15 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +15 |  |
| 13 | 4 | PASS | Driver -19 |  |
| 14 | 4 | PASS | Driver -24 |  |
| 15 | 5 | PASS | Driver -26 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -10 |  |
| 18 | 5 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |

