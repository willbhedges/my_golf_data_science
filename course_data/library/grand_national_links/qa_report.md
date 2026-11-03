# RTJ Grand National Golf: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 5, 10, 13, 17

* page: `course_data/library/grand_national_links/page.html` (2.7 MB); request `course_data/requests/course_page_grand_national_links.json`; built 2026-11-03T15:14Z
* course: RTJ Grand National Golf (Opelika, AL), OSM way/328838760; holes: osm (tier mapped_card); card: course_data/library/grand_national_links/card_review.json (file)
* solved tee sets: Purple, Orange (the two longest sets on the card (combination sets skipped)); page sets: Purple, Orange
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [55, 65, 75] F; calm-day picks with 48 prior draws
* imagery on the page: 2019-09-23; package imagery 2019
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Purple tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 6 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Purple tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback; 42 yds from the nearest OSM tee box) |
| 2 | 5 | PASS | Driver -6 |  |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 2-wood -32 |  |
| 5 | 4 | PASS | Driver +30 |  |
| 6 | 5 | PASS | Driver +2 |  |
| 7 | 4 | PASS | Driver -10 |  |
| 8 | 4 | PASS | 4-wood -0 (tie) |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | CHECK | 4-wood -31 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 8 yds from the nearest OSM tee box) |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +16 |  |
| 13 | 4 | CHECK | 4-wood -40 (tie) | aim: 4-wood -40 lands 270 yds out in rough (38 yds from fairway) |
| 14 | 4 | PASS | Driver -8 |  |
| 15 | 5 | PASS | Driver -2 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -6 (tie) |  |
| 18 | 4 | PASS | Driver -2 |  |

## Orange tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver -32 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 2 | 5 | CHECK | Driver -60 | wide_aim: Driver aim -63 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 3 | 3 | PASS |  |  |
| 4 | 4 | PASS | 4-wood -40 |  |
| 5 | 4 | CHECK | 4-wood +50 | wide_aim: 4-wood aim +59 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 5 | PASS | Driver +2 |  |
| 7 | 4 | PASS | Driver -7 |  |
| 8 | 4 | PASS | Long iron -2 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver -40 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | Driver +8 |  |
| 13 | 4 | CHECK | 4-wood -51 (tie) | aim: 4-wood -51 lands 270 yds out in rough (61 yds from fairway); wide_aim: 4-wood aim -51 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 14 | 4 | PASS | Driver +2 (tie) |  |
| 15 | 5 | PASS | Driver -25 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | CHECK | 4-wood -0 | tee: tee marker not on an OSM tee box (walkback; 19 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver -10 |  |

