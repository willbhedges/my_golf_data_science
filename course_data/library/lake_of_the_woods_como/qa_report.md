# Lake of the Woods Golf Course: automatic page QA

**Status: needs confirm** — confirm holes 1, 3, 4, 5, 6, 7, 8, 9, 13, 14, 16, 17

* page: `course_data/library/lake_of_the_woods_como/page.html` (2.6 MB); request `course_data/requests/course_page_lake_of_the_woods_como.json`; built 2026-11-26T07:55Z
* course: Lake of the Woods Golf Course (Columbia, MO), OSM way/387184389; holes: osm (tier mapped_card); card: course_data/library/lake_of_the_woods_como/routed_card.json (file)
* solved tee sets: Blue, White (the two longest sets on the card (combination sets skipped)); page sets: Blue, White
* weather: forecast for 2026-11-28, 2026-11-29; grid temperatures [35, 45, 55] F; calm-day picks with 48 prior draws
* imagery on the page: 2022-06-20; package imagery 2022
* stages: vision `ok: vision_any/2 (multi-year NAIP + lidar point statistics, LightGBM on hand maps; lidar c`; OB `ok: ob_infer/1 (course outline + houses/parcels/roads, offsets fitted on Spirit Hollow han`

* native-grass questions (Blue tees, library check cards): none (0 asked of 14 framed holes (priors: native_auto p; automatic band off: course gate shut: 0% of sides >= 0.675 (< 25%)))

Course-level reasons:

* holes placed from aerial photos (OpenStreetMap does not map them all): none marked approximate
* 12 hole(s) with a CHECK

Checks per hole (tee on an OSM tee box; yardage within 10 of the card; par = card; tee shots: the calm pick lands on fairway / first cut and its pattern is at most 40% trees / water / OB; no printed tee-shot aim (calm book or forecast pick) more than 40 yds off the tee line; par 3s: the target box on the OSM green; the page renders in a phone and a desktop browser).

## Blue tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +6 | tee: tee marker not on an OSM tee box (walkback; 112 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | CHECK | 4-wood +6 | tee: tee marker not on an OSM tee box (tee_axis; 10 yds from the nearest OSM tee box) |
| 4 | 4 | CHECK | Driver +12 | tee: tee marker not on an OSM tee box (lidar_pad; 79 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | 4-wood -4 | tee: tee marker not on an OSM tee box (lidar_pad; 82 yds from the nearest OSM tee box) |
| 6 | 4 | CHECK | Driver -8 | tee: tee marker not on an OSM tee box (walkback; 84 yds from the nearest OSM tee box) |
| 7 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (tee_axis; 4 yds from the nearest OSM tee box) |
| 8 | 4 | CHECK | 4-wood -16 | tee: tee marker not on an OSM tee box (lidar_pad; 84 yds from the nearest OSM tee box) |
| 9 | 5 | CHECK | 4-wood +22 | yardage: measured 367 vs card 495 (-128) |
| 10 | 3 | PASS |  |  |
| 11 | 5 | PASS | Long iron +12 |  |
| 12 | 4 | PASS | Long iron -0 |  |
| 13 | 4 | CHECK | Driver -14 | tee: tee marker not on an OSM tee box (walkback; 109 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | 4-wood -39 | tee: tee marker not on an OSM tee box (tee_centroid_capped; 20 yds from the nearest OSM tee box); yardage: measured 304 vs card 377 (-73) |
| 15 | 4 | PASS | Long iron -0 |  |
| 16 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 84 yds from the nearest OSM tee box) |
| 17 | 3 | CHECK |  | tee: tee marker not on an OSM tee box (lidar_pad; 18 yds from the nearest OSM tee box) |
| 18 | 4 | PASS | Driver +6 (tie) |  |

## White tees

| hole | par | result | pick | reasons |
|---|---|---|---|---|
| 1 | 4 | CHECK | Driver +7 (tie) | tee: tee marker not on an OSM tee box (walkback; 97 yds from the nearest OSM tee box) |
| 2 | 3 | PASS |  |  |
| 3 | 4 | PASS | Long iron +12 |  |
| 4 | 4 | CHECK | Driver +11 | tee: tee marker not on an OSM tee box (lidar_pad; 77 yds from the nearest OSM tee box) |
| 5 | 4 | CHECK | Driver -4 | tee: tee marker not on an OSM tee box (lidar_pad; 85 yds from the nearest OSM tee box) |
| 6 | 4 | PASS | Driver -6 |  |
| 7 | 3 | PASS |  |  |
| 8 | 4 | CHECK | 4-wood -16 | tee: tee marker not on an OSM tee box (lidar_pad; 84 yds from the nearest OSM tee box) |
| 9 | 5 | CHECK | 4-wood +22 | yardage: measured 367 vs card 495 (-128) |
| 10 | 3 | PASS |  |  |
| 11 | 5 | PASS | Long iron +12 |  |
| 12 | 4 | PASS | Long iron -0 |  |
| 13 | 4 | CHECK | Driver -6 | tee: tee marker not on an OSM tee box (walkback; 98 yds from the nearest OSM tee box) |
| 14 | 4 | CHECK | 2-wood -37 | tee: tee marker not on an OSM tee box (walkback; 66 yds from the nearest OSM tee box); wide_aim: Driver aim -67 yds is more than 40 yds left of the tee line (dog-leg corner, wider aim bound): confirm the line on the map |
| 15 | 4 | PASS | Long iron -3 |  |
| 16 | 5 | CHECK | Driver +8 | tee: tee marker not on an OSM tee box (walkback; 82 yds from the nearest OSM tee box) |
| 17 | 3 | PASS |  |  |
| 18 | 4 | PASS | Driver +6 (tie) |  |

