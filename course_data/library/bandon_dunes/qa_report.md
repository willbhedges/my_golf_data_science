# Bandon Dunes Golf Resort: automatic page QA

**Status: needs confirm** — confirm holes 1, 8, 10, 11

* page: `course_data/library/bandon_dunes/page.html` (3.9 MB); request `course_data/requests/course_page_bandon_dunes.json`; built 2026-11-03T11:12Z
* course: Bandon Dunes Golf Resort (Coos County, OR), OSM way/362513477; holes: osm (tier mapped_card); card: course_data/library/bandon_dunes/card_review.json (file)
* solved tee sets: Tournament, Black (the two longest sets on the card (combination sets skipped)); page sets: Tournament, Black
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-23; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Tournament tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Tournament tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (lidar_pad; 19 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +8 |  |
| 4 | 4 | PASS | Driver +5 |  |
| 5 | 4 | PASS | Driver -9 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver -14 |  |
| 8 | 4 | PASS | Driver +22 |  |
| 9 | 5 | PASS | Driver +34 |  |
| 10 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 25 yds from the nearest OSM tee box) |
| 11 | 4 | PASS | Driver -2 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -8 |  |
| 14 | 4 | PASS | 2-wood +18 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +36 |  |
| 17 | 4 | PASS | 4-wood -8 |  |
| 18 | 5 | PASS | Driver +8 |  |

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 16 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver +3 |  |
| 4 | 4 | PASS | Driver +25 |  |
| 5 | 4 | PASS | Driver -10 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | Driver -2 |  |
| 8 | 4 | CHECK | Driver +50 | wide_aim: Driver aim +57 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 9 | 5 | PASS | Driver +38 |  |
| 10 | 4 | PASS | Driver +12 |  |
| 11 | 4 | CHECK | Driver -3 | tee: tee marker not on an OSM tee box (walkback; 54 yds from the nearest OSM tee box) |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | Driver -8 |  |
| 14 | 4 | PASS | Driver +28 |  |
| 15 | 3 | PASS |  |  |
| 16 | 4 | PASS | Driver +36 |  |
| 17 | 4 | PASS | Driver -24 |  |
| 18 | 5 | PASS | Driver +4 |  |

