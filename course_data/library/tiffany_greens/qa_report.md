# Tiffany Greens Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 1, 10, 16

* page: `course_data/library/tiffany_greens/page.html` (2.4 MB); request `course_data/requests/course_page_tiffany_greens.json`; built 2026-10-30T00:36Z
* course: Tiffany Greens Golf Club (Kansas City, MO), OSM relation/1424708; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-10-31, 2026-11-01; grid temperatures [50, 60, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-06-07; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | 2-wood -10 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 4 | PASS | Driver +4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +2 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 2-wood -0 |  |
| 8 | 4 | PASS | Driver +10 |  |
| 9 | 5 | PASS | Driver -26 |  |
| 10 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | Driver -4 |  |
| 12 | 4 | PASS | 4-wood +4 |  |
| 13 | 4 | PASS | 4-wood +4 (tie) |  |
| 14 | 4 | PASS | Driver +12 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | PASS | Driver -19 (tie) |  |
| 17 | 4 | PASS | Driver -35 |  |
| 18 | 4 | PASS | 2-wood +28 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | 4-wood +1 | aim: 4-wood +1 lands 285 yds out in rough (7 yds from fairway) |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 4 | PASS | Driver +4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +13 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood -4 |  |
| 8 | 4 | PASS | Driver +9 |  |
| 9 | 5 | PASS | Driver -24 |  |
| 10 | 3 | PASS |  |  |
| 11 | 5 | PASS | Driver -18 |  |
| 12 | 4 | PASS | 4-wood +4 |  |
| 13 | 4 | PASS | 4-wood +5 (tie) |  |
| 14 | 4 | PASS | Driver +15 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | CHECK | Driver -40 | aim: Driver -40 lands 292 yds out in rough (23 yds from fairway) |
| 17 | 4 | PASS | Driver -40 |  |
| 18 | 4 | PASS | 4-wood +40 |  |

