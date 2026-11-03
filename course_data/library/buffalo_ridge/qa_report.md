# Buffalo Ridge Springs Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 10, 16

* page: `course_data/library/buffalo_ridge/page.html` (2.6 MB); request `course_data/requests/course_page_buffalo_ridge.json`; built 2026-11-02T23:18Z
* course: Buffalo Ridge Springs Golf Course (Branson, MO), OSM way/399501608; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Buffalo, Gold (the two longest sets on the card (combination sets skipped)); page sets: Buffalo, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 55, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2020-07-08,2020-07-26; package imagery 2020
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Buffalo tees, library check cards): holes 18, 13 (2 asked of 13 framed holes; 2 kept on the page's own picks)

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 3 Silver (L) 315 < Silver 333'])
* 3 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Buffalo tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | CHECK | Driver -10 | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 2 | 4 | PASS | Driver -2 |  |
| 3 | 4 | PASS | Driver -14 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +4 (tie) |  |
| 6 | 4 | PASS | 4-wood -6 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +6 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | PASS | 2-wood -26 (tie) |  |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -13 |  |
| 13 | 4 | PASS | Driver -19 |  |
| 14 | 5 | PASS | Driver -8 |  |
| 15 | 4 | PASS | 4-wood +11 |  |
| 16 | 4 | PASS | Driver -2 |  |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -8 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver -2 |  |
| 2 | 4 | PASS | Driver -2 |  |
| 3 | 4 | PASS | Driver -25 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | 4-wood +4 (tie) |  |
| 6 | 4 | PASS | Driver -9 |  |
| 7 | 3 | PASS |  |  |
| 8 | 5 | PASS | Driver +0 |  |
| 9 | 3 | PASS |  |  |
| 10 | 4 | CHECK | 2-wood -54 (tie) | wide_aim: 2-wood aim -56 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 11 | 3 | PASS |  |  |
| 12 | 4 | PASS | Driver -14 |  |
| 13 | 4 | PASS | Driver -28 |  |
| 14 | 5 | PASS | Driver -5 |  |
| 15 | 4 | PASS | 4-wood +20 |  |
| 16 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (walkback; 31 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 5 | PASS | Driver -20 |  |

