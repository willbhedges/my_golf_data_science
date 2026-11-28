# Keller Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 16

* page: `course_data/library/keller/page.html` (4.8 MB); request `course_data/requests/course_page_keller.json`; built 2026-11-28T04:31Z
* course: Keller Golf Course (Maplewood, MN), OSM none/0; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-12-05, 2026-12-06; grid temperatures [25, 35, 45] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-03; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request and no native_auto p in the package)

Course-level reasons:

* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +20 |  |
| 2 | 4 | PASS | 4-wood -2 |  |
| 3 | 5 | PASS | Driver +0 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +10 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +2 (tie) |  |
| 8 | 4 | PASS | Driver -8 |  |
| 9 | 4 | PASS | Driver +4 (tie) |  |
| 10 | 5 | PASS | Driver -4 |  |
| 11 | 4 | PASS | 4-wood -0 (tie) |  |
| 12 | 5 | PASS | Driver -8 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 2-wood -0 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | PASS | Driver -4 |  |
| 17 | 4 | PASS | Driver +10 |  |
| 18 | 4 | PASS | Driver +2 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +45 (tie) | wide_aim: 4-wood aim +47 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 5 | PASS | Driver +1 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +10 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +2 |  |
| 8 | 4 | PASS | Driver -8 |  |
| 9 | 4 | PASS | 4-wood +4 |  |
| 10 | 5 | PASS | Driver -5 |  |
| 11 | 4 | PASS | 4-wood +1 |  |
| 12 | 5 | PASS | Driver -15 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood +0 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | CHECK | Driver -4 | yardage: measured 563 vs card 502 (+61) |
| 17 | 4 | PASS | Driver +12 |  |
| 18 | 4 | PASS | Driver +2 |  |

