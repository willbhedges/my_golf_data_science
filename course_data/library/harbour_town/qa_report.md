# Harbour Town Golf Links: automatic page QA

**Status: needs confirm** — confirm holes 2, 3, 5, 7, 18

* page: `course_data/library/harbour_town/page.html` (6.3 MB); request `course_data/requests/course_page_harbour_town.json`; built 2026-11-26T19:07Z
* course: Harbour Town Golf Links (Hilton Head Island, SC), OSM relation/4813858; holes: osm (tier mapped_card); card: opengolfapi (opengolfapi)
* solved tee sets: Heritage, Blue (the two longest sets on the card (combination sets skipped)); page sets: Heritage, Blue
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [40, 50, 65] F; calm-day picks with 48 prior draws
* imagery on the page: 2025-05-22; package imagery 2021
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Heritage tees, library check cards): none (0 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* scorecard not matched (source opengolfapi, flags ['Heritage: holes sum to 7131 but the source says 7099 (+32): mixed card versions', 'Blue: holes sum to 6642 but the source says 6681 (-39): mixed card versions', 'White: holes sum to 6103 but the source says 6253 (-150): mixed card versions', 'Gold: holes sum to 5478 but the source says 5867 (-389): mixed card versions', 'Green: holes sum to 4760 but the source says 5084 (-324): mixed card versions'])
* 5 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Heritage tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | Driver +6 |  |
| 2 | 5 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (walkback_capped; 15 yds from the nearest OSM tee box); yardage: measured 515 vs card 544 (-29) |
| 3 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad; 106 yds from the nearest OSM tee box) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (lidar_pad; 22 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | 4-wood -4 |  |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 20 yds from the nearest OSM tee box) |
| 8 | 4 | PASS | Driver -3 (tie) |  |
| 9 | 4 | PASS | 4-wood -2 |  |
| 10 | 4 | PASS | 2-wood +6 (tie) |  |
| 11 | 4 | PASS | 4-wood +4 |  |
| 12 | 4 | PASS | 2-wood -12 (tie) |  |
| 13 | 4 | PASS | 4-wood -6 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -1 |  |
| 16 | 4 | PASS | Driver +8 |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (tee_axis; 12 yds from the nearest OSM tee box) |

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | PASS | 2-wood +6 |  |
| 2 | 5 | PASS | 4-wood -4 |  |
| 3 | 4 | CHECK | Driver +2 | tee: tee marker not on an OSM tee box (lidar_pad_capped; 86 yds from the nearest OSM tee box); yardage: measured 437 vs card 412 (+25) |
| 4 | 3 | PASS |  |  |
| 5 | 5 | PASS | Driver -26 |  |
| 6 | 4 | PASS | 4-wood -2 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | PASS | 4-wood -1 |  |
| 9 | 4 | PASS | Driver -32 |  |
| 10 | 4 | PASS | 4-wood -3 |  |
| 11 | 4 | PASS | 4-wood -2 |  |
| 12 | 4 | PASS | 4-wood -7 |  |
| 13 | 4 | PASS | Long iron -4 |  |
| 14 | 3 | PASS |  |  |
| 15 | 5 | PASS | Driver -2 |  |
| 16 | 4 | PASS | Driver -6 (tie) |  |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | 4-wood -3 |  |

