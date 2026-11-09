# Crow Canyon Country Club: automatic page QA

**Status: needs confirm** — confirm holes 13, 15, 16, 17

* page: `course_data/library/gate/gate_b20_crow_canyon/page.html` (3.0 MB); request `course_data/requests/course_page_b20_crow_canyon.json`; built 2026-11-09T21:35Z
* course: Crow Canyon Country Club (Danville, CA), OSM relation/3132092; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Black, Blue (the two longest sets on the card (combination sets skipped)); page sets: Black, Blue
* weather: forecast for 2026-11-14, 2026-11-15; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2018-07-15; package imagery 2018
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Black tees, library check cards): none (0 asked of 13 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Black tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -3 |  |
| 2 | 5 | PASS | 4-wood -2 |  |
| 3 | 4 | PASS | 4-wood +4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Mid iron +8 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +3 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood +2 |  |
| 10 | 4 | PASS | 4-wood +4 (tie) |  |
| 11 | 4 | PASS | 4-wood +3 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +16 |  |
| 15 | 4 | CHECK | Mid iron -12 | wide_aim: Driver aim +60 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 16 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad_capped; 30 yds from the nearest OSM tee box) |
| 17 | 4 | CHECK | 4-wood -5 | tee: tee marker not on an OSM tee box (walkback; 24 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Long iron +7 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -2 |  |
| 2 | 5 | PASS | Driver +8 |  |
| 3 | 4 | PASS | 4-wood +6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Mid iron +8 |  |
| 6 | 3 | PASS |  |  |
| 7 | 4 | PASS | 4-wood +3 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | 4-wood +4 |  |
| 10 | 4 | PASS | Driver +17 (tie) |  |
| 11 | 4 | PASS | 4-wood +4 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (lidar_pad; 21 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | 4-wood +18 |  |
| 15 | 4 | PASS | Mid iron -12 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | CHECK | 4-wood -6 | tee: tee marker not on an OSM tee box (walkback; 20 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Long iron +7 |  |

