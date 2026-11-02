# Arcadia Bluffs Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 5

* page: `course_data/library/arcadia_bluffs/page.html` (2.1 MB); request `course_data/requests/course_page_arcadia_bluffs.json`; built 2026-11-01T22:05Z
* course: Arcadia Bluffs Golf Club (Arcadia, MI), OSM way/293247442; holes: osm (tier mapped_card); card: allsquare (allsquare)
* solved tee sets: Champion, Blue (the two longest sets on the card (combination sets skipped)); page sets: Champion, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-09-01; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

Course-level reasons:

* 1 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Champion tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -25 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver -4 |  |
| 4 | 4 | PASS | Driver -4 (tie) |  |
| 5 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; 34 yds from the nearest OSM tee box) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver -4 |  |
| 8 | 4 | PASS | Driver +4 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver +13 |  |
| 11 | 5 | PASS | Driver +4 |  |
| 12 | 4 | PASS | Driver -4 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -35 |  |
| 15 | 5 | PASS | Driver -2 |  |
| 16 | 4 | PASS | Driver -7 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +10 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -18 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver -4 |  |
| 4 | 4 | PASS | Driver -4 (tie) |  |
| 5 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (lidar_pad; 34 yds from the nearest OSM tee box); yardage: measured 589 vs card 578 (+11) |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver +3 |  |
| 8 | 4 | PASS | Driver +15 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver +12 |  |
| 11 | 5 | PASS | Driver +6 |  |
| 12 | 4 | PASS | Driver -4 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -35 |  |
| 15 | 5 | PASS | Driver -11 |  |
| 16 | 4 | PASS | Driver -14 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +12 |  |

