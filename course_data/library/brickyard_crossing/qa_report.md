# Brickyard Crossing Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 2, 12

* page: `course_data/library/brickyard_crossing/page.html` (2.3 MB); request `course_data/requests/course_page_brickyard_crossing.json`; built 2026-11-26T17:17Z
* course: Brickyard Crossing Golf Course (Indianapolis, IN), OSM relation/569616; holes: v2+structure (tier mapped_card); card: golfify (golfify)
* solved tee sets: Gold, Blue (the two longest sets on the card (combination sets skipped)); page sets: Gold, Blue
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [30, 40, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-21; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Gold tees, library check cards): none (0 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes not all mapped in OSM (hole method: v2+structure)
* 2 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -16 |  |
| 2 | 5 | PASS | 4-wood +14 (tie) |  |
| 3 | 4 | PASS | 4-wood +4 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +4 |  |
| 6 | 5 | PASS | Driver +3 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +12 |  |
| 9 | 4 | PASS | 4-wood +8 (tie) |  |
| 10 | 4 | PASS | Driver +0 (tie) |  |
| 11 | 4 | PASS | Driver -4 |  |
| 12 | 5 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (tee_axis; 49 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -7 |  |
| 15 | 5 | PASS | Driver -37 |  |
| 16 | 4 | PASS | Driver +2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -5 |  |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -4 |  |
| 2 | 5 | CHECK | Driver -13 | tee: tee marker not on an OSM tee box (tee_axis; 9 yds from the nearest OSM tee box) |
| 3 | 4 | PASS | Driver -14 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +7 |  |
| 6 | 5 | PASS | Driver +8 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | Driver +8 |  |
| 9 | 4 | PASS | Driver +20 (tie) |  |
| 10 | 4 | PASS | Driver -4 |  |
| 11 | 4 | PASS | 4-wood -8 (tie) |  |
| 12 | 5 | PASS | Driver -14 |  |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | 4-wood -7 (tie) |  |
| 15 | 5 | PASS | Driver -35 |  |
| 16 | 4 | PASS | 4-wood -5 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver -2 |  |

