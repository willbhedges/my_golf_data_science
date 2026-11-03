# Queenstown Harbor River Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 4, 5, 7, 9, 10, 12, 18

* page: `course_data/library/queenstown_harbor/page.html` (4.2 MB); request `course_data/requests/course_page_queenstown_harbor.json`; built 2026-11-03T16:14Z
* course: Queenstown Harbor River Course (Queenstown, MD), OSM way/1067525665; holes: osm (tier mapped_card); card: golfify (golfify)
* solved tee sets: Green, Gold (the two longest sets on the card (combination sets skipped)); page sets: Green, Gold
* weather: forecast for 2026-11-07, 2026-11-08; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2023-05-27; package imagery 2023
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Green tees, library check cards): none (not asked: no agent_layers in the request)

Course-level reasons:

* scorecard not matched (source golfify, flags ['1 hole(s) where a longer set is shorter than the next set: 12 Blue/Gold 307 < Gold 340'])
* 9 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Green tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | 4-wood +6 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 39 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | 2-wood +11 (tie) | tee: tee marker not on an OSM tee box (lidar_pad; 17 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | 4-wood +10 | tee: tee marker not on an OSM tee box (walkback; 22 yds from the nearest OSM tee box) |
| 5 | 5 | PASS | Driver -7 |  |
| 6 | 4 | PASS | Driver -2 |  |
| 7 | 5 | CHECK | 4-wood -4 | aim: 4-wood -4 lands 274 yds out in rough (10 yds from fairway) |
| 8 | 3 | PASS |  |  |
| 9 | 4 | PASS | Driver +8 |  |
| 10 | 4 | CHECK | Driver -7 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 37 yds from the nearest OSM tee box) |
| 11 | 5 | PASS | Driver -22 |  |
| 12 | 4 | CHECK | Driver -22 (tie) | tee: tee marker not on an OSM tee box (walkback; 39 yds from the nearest OSM tee box) |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -12 |  |
| 15 | 4 | PASS | Driver -1 |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Long iron -5 |  |
| 18 | 5 | PASS | Driver -2 |  |

## Gold tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +20 | aim: Driver +20 lands 299 yds out in sand (10 yds from fairway) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | 4-wood -48 | wide_aim: 4-wood aim -69 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 4 | 4 | PASS | Long iron +10 |  |
| 5 | 5 | CHECK | Driver -20 | tee: tee marker not on an OSM tee box (texture_pad; 18 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver -14 |  |
| 7 | 5 | PASS | Driver +8 |  |
| 8 | 3 | PASS |  |  |
| 9 | 4 | CHECK | Driver +49 (tie) | tee: tee marker not on an OSM tee box (walkback; 49 yds from the nearest OSM tee box); aim: Driver +49 lands 290 yds out in rough (10 yds from fairway); wide_aim: Driver aim +60 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 10 | 4 | PASS | Driver -14 |  |
| 11 | 5 | PASS | Driver -23 |  |
| 12 | 4 | CHECK | Driver +40 (tie) | aim: Driver +40 lands 303 yds out in rough (24 yds from fairway); wide_aim: Driver aim +40 yds is more than 40 yds right of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 13 | 3 | PASS |  |  |
| 14 | 4 | PASS | Driver -22 |  |
| 15 | 4 | PASS | 2-wood +26 (tie) |  |
| 16 | 3 | PASS |  |  |
| 17 | 4 | PASS | Driver -22 |  |
| 18 | 5 | CHECK | Driver +13 | tee: tee marker not on an OSM tee box (walkback; 35 yds from the nearest OSM tee box) |

