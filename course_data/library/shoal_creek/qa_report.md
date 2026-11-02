# Shoal Creek Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 5, 6

* page: `course_data/library/shoal_creek/page.html` (2.3 MB); request `course_data/requests/course_page_shoal_creek.json`; built 2026-10-30T00:34Z
* course: Shoal Creek Golf Course (Kansas City, MO), OSM way/195221881; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -10 |  |
| 2 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (walkback; 32 yds from the nearest OSM tee box) |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood -0 |  |
| 5 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 197 yds from the nearest OSM tee box) |
| 6 | 4 | CHECK | 4-wood -23 (tie) | tee: tee marker not on an OSM tee box (walkback; 54 yds from the nearest OSM tee box) |
| 7 | 5 | PASS | Driver +6 |  |
| 8 | 4 | PASS | Driver -6 |  |
| 9 | 5 | PASS | Driver +2 |  |
| 10 | 4 | PASS | Driver +10 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood +2 |  |
| 13 | 5 | PASS | Driver +6 |  |
| 14 | 4 | PASS | 4-wood +1 |  |
| 15 | 4 | PASS | Driver -0 |  |
| 16 | 4 | PASS | Driver -10 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -4 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -18 |  |
| 2 | 4 | PASS | 2-wood +2 (tie) |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood +10 |  |
| 5 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (walkback; 149 yds from the nearest OSM tee box) |
| 6 | 4 | CHECK | Mid iron -12 | yardage: measured 278 vs card 333 (-55) |
| 7 | 5 | PASS | Driver +10 |  |
| 8 | 4 | PASS | Driver -2 |  |
| 9 | 5 | PASS | Driver -0 |  |
| 10 | 4 | PASS | Driver +8 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | 4-wood -0 |  |
| 13 | 5 | PASS | Driver +3 |  |
| 14 | 4 | PASS | 4-wood +7 |  |
| 15 | 4 | PASS | 2-wood +4 (tie) |  |
| 16 | 4 | PASS | Driver -7 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +2 |  |

