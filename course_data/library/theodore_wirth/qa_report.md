# Theodore Wirth Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 4, 13, 18

* page: `course_data/library/theodore_wirth/page.html` (5.7 MB); request `course_data/requests/course_page_theodore_wirth.json`; built 2026-11-26T08:47Z
* course: Theodore Wirth Golf Course (Minneapolis, MN), OSM relation/20146766; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [30, 40, 50] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-03; package imagery 2025
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): holes 18 (1 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)); 1 kept on the page's own picks)

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Blue: holes sum to 6164 but the source says 6475 (-311): mixed card versions', 'White: holes sum to 5053 but the source says 6179 (-1126): mixed card versions'])
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -4 |  |
| 2 | 5 | PASS | Driver -16 |  |
| 3 | 4 | PASS | 4-wood -19 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood -2 |  |
| 6 | 5 | PASS | Driver +24 |  |
| 7 | 4 | PASS | Driver -18 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -10 |  |
| 10 | 4 | PASS | 4-wood -4 |  |
| 11 | 4 | PASS | Driver +20 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | CHECK | 2-wood -40 | wide_aim: Driver aim -47 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 14 | 4 | PASS | Driver +2 |  |
| 15 | 4 | PASS | Driver +0 |  |
| 16 | 5 | PASS | Driver +6 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +12 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Long iron -3 |  |
| 2 | 5 | PASS | Long iron +8 |  |
| 3 | 4 | PASS | Long iron -32 |  |
| 4 | 3 | CHECK |  | yardage: measured 223 vs card 153 (+70) |
| 5 | 4 | PASS | Driver +24 |  |
| 6 | 5 | PASS | 4-wood +22 |  |
| 7 | 4 | PASS | 4-wood -31 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver -12 |  |
| 10 | 4 | PASS | 4-wood +2 |  |
| 11 | 4 | PASS | Driver +22 |  |
| 12 | 3 | PASS |  |  |
| 13 | 5 | PASS | 4-wood -32 |  |
| 14 | 4 | PASS | 4-wood +2 |  |
| 15 | 4 | PASS | 2-wood -2 (tie) |  |
| 16 | 5 | PASS | 4-wood +7 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver +12 | yardage: measured 331 vs card 252 (+79) |

