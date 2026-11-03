# Memorial Park Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 8, 13, 14, 16, 17

* page: `course_data/library/memorial_park/page.html` (2.4 MB); request `course_data/requests/course_page_memorial_park.json`; built 2026-11-03T11:06Z
* course: Memorial Park Golf Course (Houston, TX), OSM relation/13729803; holes: osm (tier mapped_card); card: course_data/library/memorial_park/card_review.json (file)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [60, 70, 80] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-11-18; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -8 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver -0 |  |
| 4 | 4 | PASS | Driver +10 |  |
| 5 | 4 | PASS | Driver +2 |  |
| 6 | 4 | PASS | Driver +4 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver +6 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +2 |  |
| 13 | 4 | PASS | Driver +7 |  |
| 14 | 5 | PASS | Driver -3 |  |
| 15 | 3 | PASS |  |  |
| 16 | 5 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (texture_pad; 27 yds from the nearest OSM tee box) |
| 17 | 4 | PASS | 4-wood -8 (tie) |  |
| 18 | 4 | PASS | Driver -3 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -10 |  |
| 2 | 3 | PASS |  |  |
| 3 | 5 | PASS | Driver -2 |  |
| 4 | 4 | PASS | Driver +4 (tie) |  |
| 5 | 4 | PASS | Driver -17 |  |
| 6 | 4 | PASS | Driver -8 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +16 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | Driver +9 |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver +17 |  |
| 13 | 4 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 78 yds from the nearest OSM tee box) |
| 14 | 5 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (walkback; 21 yds from the nearest OSM tee box) |
| 15 | 3 | PASS |  |  |
| 16 | 5 | PASS | Driver +30 |  |
| 17 | 4 | CHECK | Driver +3 (tie) | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box); aim: Driver +3 lands 295 yds out in rough (8 yds from fairway) |
| 18 | 4 | PASS | Driver +2 |  |

