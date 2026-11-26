# Kokopelli Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 5, 12

* page: `course_data/library/kokopelli/page.html` (4.9 MB); request `course_data/requests/course_page_kokopelli.json`; built 2026-11-26T07:52Z
* course: Kokopelli Golf Club (Marion, IL), OSM way/759870279; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Black, Gold (the two longest sets on the card (combination sets skipped)); page sets: Black, Gold
* weather: climate normals for 2026-11-28, 2026-11-29; grid temperatures [30, 40, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-17; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 16, 1 (4 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 2 kept on the page's own picks (2 dropped))

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -4 |  |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +6 |  |
| 5 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | 4-wood -2 |  |
| 7 | 4 | PASS | Driver -20 |  |
| 8 | 4 | PASS | Driver +4 |  |
| 9 | 5 | PASS | Driver -8 |  |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | Driver -16 |  |
| 12 | 5 | CHECK | Driver +18 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 13 | 4 | PASS | Driver -6 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -6 |  |
| 16 | 4 | PASS | Driver -4 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +35 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +10 |  |
| 2 | 4 | PASS | Driver -14 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | Driver +4 |  |
| 5 | 3 | PASS |  |  |
| 6 | 4 | PASS | 4-wood -2 |  |
| 7 | 4 | PASS | Driver -20 |  |
| 8 | 4 | PASS | Driver -4 |  |
| 9 | 5 | PASS | Driver -10 |  |
| 10 | 4 | PASS | Driver +9 |  |
| 11 | 4 | PASS | Driver -14 |  |
| 12 | 5 | PASS | Driver -7 |  |
| 13 | 4 | PASS | Driver -9 |  |
| 14 | 3 | PASS |  |  |
| 15 | 4 | PASS | Driver -6 |  |
| 16 | 4 | PASS | Driver -8 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +34 |  |

