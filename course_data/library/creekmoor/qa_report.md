# Creekmoor Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 3

* page: `course_data/library/creekmoor/page.html` (2.5 MB); request `course_data/requests/course_page_creekmoor.json`; built 2026-11-03T04:35Z
* course: Creekmoor Golf Club (Raymore, MO), OSM relation/4249741; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Green (the two longest sets on the card (combination sets skipped)); page sets: Black, Green
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-09-22; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): holes 14 (1 asked of 14 framed holes; 1 kept on the page's own picks)

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +32 |  |
| 2 | 4 | PASS | 4-wood -4 |  |
| 3 | 4 | CHECK | Driver +10 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver +7 |  |
| 6 | 4 | PASS | Driver -4 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -22 |  |
| 9 | 5 | PASS | 4-wood -14 |  |
| 10 | 4 | PASS | Driver -2 |  |
| 11 | 4 | PASS | Driver -28 (tie) |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +2 |  |
| 14 | 4 | PASS | Driver -10 |  |
| 15 | 4 | PASS | Driver +2 |  |
| 16 | 4 | PASS | Driver -26 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +14 |  |

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +40 |  |
| 2 | 4 | PASS | 4-wood -0 |  |
| 3 | 4 | PASS | Driver +6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver +9 |  |
| 6 | 4 | PASS | Driver -0 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver -27 (tie) |  |
| 9 | 5 | PASS | Driver -2 |  |
| 10 | 4 | PASS | Driver +5 |  |
| 11 | 4 | PASS | Driver -36 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver +8 |  |
| 14 | 4 | PASS | Driver -22 |  |
| 15 | 4 | PASS | Driver +4 |  |
| 16 | 4 | PASS | Driver -24 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +2 |  |

