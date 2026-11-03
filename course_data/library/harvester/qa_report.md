# The Harvester Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 6, 7, 8, 12, 13, 18

* page: `course_data/library/harvester/page.html` (4.7 MB); request `course_data/requests/course_page_harvester.json`; built 2026-11-02T23:01Z
* course: The Harvester Golf Club (Rhodes, IA), OSM way/325314320; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 60] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-09-02; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 14 Blue 155 < White 195'])
* 7 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +0 (tie) |  |
| 2 | 4 | CHECK | 4-wood +2 (tie) | wide_aim: Driver aim +53 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver +3 |  |
| 5 | 4 | PASS | Driver +0 (tie) |  |
| 6 | 5 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver +1 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood +0 |  |
| 10 | 4 | PASS | Driver +10 |  |
| 11 | 4 | PASS | Driver -17 |  |
| 12 | 4 | CHECK | Driver +18 (tie) | aim: Driver +18 lands 293 yds out in sand (4 yds from fairway) |
| 13 | 4 | PASS | Driver +2 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +9 |  |
| 16 | 4 | PASS | Driver -2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | 4-wood -12 | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +4 |  |
| 2 | 4 | CHECK | Driver +60 | wide_aim: Driver aim +60 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 3 | 3 | PASS |  |  |
| 4 | 5 | PASS | Driver -2 |  |
| 5 | 4 | PASS | Driver -7 |  |
| 6 | 5 | CHECK | Driver -12 | tee: tee marker not on an OSM tee box (tee_axis; 5 yds from the nearest OSM tee box) |
| 7 | 4 | CHECK | Driver +20 | tee: tee marker not on an OSM tee box (texture_pad; 22 yds from the nearest OSM tee box) |
| 8 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 9 | 4 | PASS | 4-wood +1 |  |
| 10 | 4 | PASS | Driver +8 |  |
| 11 | 4 | PASS | Driver -18 |  |
| 12 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 13 | 4 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (walkback; 16 yds from the nearest OSM tee box) |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver +6 |  |
| 16 | 4 | PASS | Driver -13 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | CHECK | 4-wood -14 | tee: tee marker not on an OSM tee box (tee_axis; 6 yds from the nearest OSM tee box) |

