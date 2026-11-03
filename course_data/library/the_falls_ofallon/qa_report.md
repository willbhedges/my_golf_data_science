# The Falls Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 2, 6, 16

* page: `course_data/library/the_falls_ofallon/page.html` (2.5 MB); request `course_data/requests/course_page_the_falls_ofallon.json`; built 2026-11-03T01:40Z
* course: The Falls Golf Club (O'Fallon, MO), OSM relation/3939928; holes: osm (tier mapped_card); card: course_data/library/the_falls_ofallon/card_review.json (file)
* solved tee sets: Blue, White (tee sets of interest); page sets: Blue, White
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-18; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): holes 15, 18 (3 asked of 13 framed holes; 2 kept on the page's own picks (1 dropped))

Course-level reasons:

* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood -2 |  |
| 2 | 4 | PASS | 4-wood +14 |  |
| 3 | 4 | PASS | Driver +32 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood -2 |  |
| 6 | 5 | CHECK | 4-wood -3 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 7 | 4 | PASS | Driver -14 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | 4-wood -3 (tie) |  |
| 10 | 4 | PASS | 4-wood +2 |  |
| 11 | 4 | PASS | 4-wood -8 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | 4-wood +0 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -6 |  |
| 16 | 4 | CHECK | Driver -46 | wide_aim: Driver aim -50 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +7 |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 4-wood +4 |  |
| 2 | 4 | CHECK | Driver +51 | tee: tee marker not on an OSM tee box (lidar_pad; 9 yds from the nearest OSM tee box); wide_aim: Driver aim +53 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 3 | 4 | PASS | Driver +36 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Long iron -2 |  |
| 6 | 5 | PASS | Driver -22 |  |
| 7 | 4 | PASS | Driver -30 |  |
| 8 | 3 | PASS |  |  |
| 9 | 5 | PASS | Driver +0 |  |
| 10 | 4 | PASS | Long iron +3 |  |
| 11 | 4 | PASS | Driver -1 |  |
| 12 | 3 | PASS |  |  |
| 13 | 4 | PASS | Driver -20 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -17 |  |
| 16 | 4 | CHECK | Driver -46 | wide_aim: Driver aim -51 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver +6 |  |

