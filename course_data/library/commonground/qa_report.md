# CommonGround Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 4, 10, 16

* page: `course_data/library/commonground/page.html` (4.6 MB); request `course_data/requests/course_page_commonground.json`; built 2026-10-30T21:34Z
* course: CommonGround Golf Course (Aurora, CO), OSM way/113046166; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [40, 55, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-25; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* scorecard not matched (source allsquare, flags ['1 hole(s) where a longer set is shorter than the next set: 11 Black 529 < Black/Gold 539'])
* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (texture_pad; 38 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +10 |  |
| 4 | 4 | PASS | Driver +32 |  |
| 5 | 4 | PASS | Driver +15 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -16 |  |
| 8 | 4 | PASS | Driver +3 |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | CHECK | Driver +14 | tee: tee marker not on an OSM tee box (texture_pad; 38 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | Driver +4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +18 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -16 |  |
| 16 | 4 | CHECK | Driver +22 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +27 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -25 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +4 |  |
| 4 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 5 | 4 | PASS | Driver +6 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | PASS | Driver -10 |  |
| 8 | 4 | PASS | Driver +6 |  |
| 9 | 4 | PASS | Driver -4 |  |
| 10 | 4 | PASS | Driver -1 (tie) |  |
| 11 | 5 | PASS | Driver +2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver +18 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -8 |  |
| 16 | 4 | PASS | Driver +18 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +26 |  |

