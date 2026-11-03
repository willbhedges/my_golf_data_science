# Dub's Dread Golf Club: automatic page QA

**Status: needs confirm** — confirm holes 7, 9, 13, 15

* page: `course_data/library/dubs_dread/page.html` (4.8 MB); request `course_data/requests/course_page_dubs_dread.json`; built 2026-11-02T23:54Z
* course: Dub's Dread Golf Club (Kansas City, KS), OSM way/505160823; holes: osm (tier mapped_card); card: course_data/library/dubs_dread/card_golfify.json (file)
* solved tee sets: Championship, Back (the two longest sets on the card (combination sets skipped)); page sets: Championship, Back
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [45, 60, 70] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-08-17; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Championship tees, library check cards): holes 7, 10, 2, 14 (6 asked of 14 framed holes; 4 kept on the page's own picks (2 dropped))

Course-level reasons:

* 4 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Championship tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +20 |  |
| 2 | 4 | PASS | Driver -8 |  |
| 3 | 4 | PASS | 4-wood -2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -19 |  |
| 6 | 4 | PASS | Driver -40 |  |
| 7 | 5 | PASS | Driver +28 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | 4-wood +8 (tie) | yardage: measured 397 vs card 418 (-21) |
| 10 | 4 | PASS | Driver +5 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | 2-wood -22 (tie) |  |
| 13 | 4 | CHECK | 4-wood -6 | tee: tee marker not on an OSM tee box (lidar_pad; 23 yds from the nearest OSM tee box) |
| 14 | 4 | PASS | Driver -4 |  |
| 15 | 4 | PASS | 2-wood -12 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +22 |  |
| 18 | 4 | PASS | 4-wood +4 (tie) |  |

## Back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 5 | PASS | Driver +30 |  |
| 2 | 4 | PASS | 4-wood -10 |  |
| 3 | 4 | PASS | Long iron -2 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver -30 |  |
| 6 | 4 | PASS | 4-wood -20 |  |
| 7 | 5 | CHECK | Driver +32 | tee: tee marker not on an OSM tee box (tee_axis; 3 yds from the nearest OSM tee box) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +21 (tie) |  |
| 10 | 4 | PASS | Driver +0 |  |
| 11 | 3 | PASS |  |  |
| 12 | 5 | PASS | 2-wood -40 |  |
| 13 | 4 | PASS | 4-wood +4 |  |
| 14 | 4 | PASS | Driver -2 |  |
| 15 | 4 | CHECK | Driver -60 | wide_aim: Driver aim -69 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 16 | 3 | PASS |  |  |
| 17 | 5 | PASS | Driver +26 |  |
| 18 | 4 | PASS | Driver +4 |  |

