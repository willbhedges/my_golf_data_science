# Gamble Sands Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 2, 5, 7, 9, 11, 12, 14, 18

* page: `course_data/library/gamble_sands/page.html` (2.4 MB); request `course_data/requests/course_page_gamble_sands.json`; built 2026-11-26T17:19Z
* course: Gamble Sands Golf Course (Brewster, WA), OSM way/876550790; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Medal, Back (the two longest sets on the card (combination sets skipped)); page sets: Medal, Back
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [25, 40, 50] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-07-16; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Medal tees, library check cards): none (0 asked of 14 framed holes (priors: native_auto p; automatic band on 14 holes))

Course-level reasons:

* scorecard not matched (source golfify, flags ['3 hole(s) where a longer set is shorter than the next set: 12 Back 296 < Sands 306, 3 Sands 519 < Regular 591, 17 Sands 393 < Regular 411'])
* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Medal tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver -11 |  |
| 2 | 4 | PASS | Driver -9 |  |
| 3 | 5 | PASS | Driver +6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | CHECK | Driver +50 | wide_aim: Driver aim +54 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +28 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver -2 |  |
| 9 | 4 | PASS | Driver +14 |  |
| 10 | 3 | PASS |  |  |
| 11 | 4 | PASS | Driver +10 |  |
| 12 | 4 | CHECK | Driver +34 | tee: tee marker not on an OSM tee box (walkback; 29 yds from the nearest OSM tee box) |
| 13 | 5 | PASS | Driver -9 |  |
| 14 | 4 | CHECK | Driver +30 | tee: tee marker not on an OSM tee box (walkback; 354 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | Driver +3 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +24 |  |
| 18 | 5 | PASS | Driver -0 |  |

## Back tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood -10 | tee: tee marker not on an OSM tee box (walkback; 90 yds from the nearest OSM tee box) |
| 2 | 4 | CHECK | 2-wood -22 | tee: tee marker not on an OSM tee box (tee_axis; 11 yds from the nearest OSM tee box) |
| 3 | 5 | PASS | Driver +6 |  |
| 4 | 3 | PASS |  |  |
| 5 | 4 | PASS | Driver +38 |  |
| 6 | 3 | PASS |  |  |
| 7 | 5 | CHECK | Driver +30 | tee: tee marker not on an OSM tee box (walkback; 59 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver -2 |  |
| 9 | 4 | CHECK | Driver +48 | tee: tee marker not on an OSM tee box (walkback; 41 yds from the nearest OSM tee box); wide_aim: Driver aim +50 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 10 | 3 | PASS |  |  |
| 11 | 4 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (walkback; 26 yds from the nearest OSM tee box) |
| 12 | 4 | PASS | Driver +34 |  |
| 13 | 5 | PASS | Driver -8 |  |
| 14 | 4 | CHECK | Driver +21 | tee: tee marker not on an OSM tee box (walkback; 376 yds from the nearest OSM tee box) |
| 15 | 4 | PASS | Driver +4 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver +28 |  |
| 18 | 5 | CHECK | Driver -5 | tee: tee marker not on an OSM tee box (walkback; 76 yds from the nearest OSM tee box) |

